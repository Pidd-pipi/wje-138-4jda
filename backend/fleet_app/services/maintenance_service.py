"""维保业务服务：保养到期占用、待处理预约同步、完工解除占用并重算。"""
from datetime import datetime
from zoneinfo import ZoneInfo

from django.db import transaction
from django.utils import timezone

from fleet_app.models import MaintenanceRecord, Vehicle
from fleet_app.services.maintenance_policy import (
    describe_reason,
    evaluate_due,
    next_due_point,
)

OPEN_STATUSES = ('Scheduled', 'InProgress')

SH_TZ = ZoneInfo('Asia/Shanghai')


def _today():
    return timezone.localdate()


def get_last_completed(vehicle_id):
    return (
        MaintenanceRecord.objects.filter(vehicle_id=vehicle_id, status='Completed')
        .order_by('-completed_at', '-date', '-id')
        .first()
    )


def get_open_record(vehicle_id):
    """最新一条未关闭的维保预约/施工单（同时存在时优先施工中）。"""
    in_progress = (
        MaintenanceRecord.objects.filter(vehicle_id=vehicle_id, status='InProgress')
        .order_by('-id')
        .first()
    )
    if in_progress:
        return in_progress
    return (
        MaintenanceRecord.objects.filter(vehicle_id=vehicle_id, status='Scheduled')
        .order_by('-id')
        .first()
    )


def evaluate_vehicle(vehicle, today=None):
    """计算车辆的保养占用状态。

    返回字段：due（是否到期）/ blocked（是否禁止调度）/ reasonCode /
    reasons / blockReason / lastMileage / lastDate / openRecordId。
    """
    today = today or _today()
    last = get_last_completed(vehicle.id)
    open_rec = get_open_record(vehicle.id)

    last_mileage = last.mileage if last else None
    last_date = last.date if last else None
    due, code, reasons = evaluate_due(
        current_mileage=vehicle.mileage,
        last_mileage=last_mileage,
        today=today,
        last_date=last_date,
    )

    # 已报废车辆不再受保养占用规则影响，其不可调度原因由调度环节单独说明
    if vehicle.status == 'Retired':
        due = False
        code = None
        reasons = []

    in_progress = open_rec is not None and open_rec.status == 'InProgress'
    blocked = due or in_progress
    block_reason = ''
    if due:
        block_reason = describe_reason(
            code,
            current_mileage=vehicle.mileage,
            last_mileage=last_mileage or 0,
            today=today,
            last_date=last_date,
        )
        block_reason = '保养到期：' + block_reason
    elif in_progress:
        block_reason = '车辆正在维修保养中，暂不可调度'

    return {
        'due': due,
        'blocked': blocked,
        'reasonCode': code,
        'reasons': reasons,
        'blockReason': block_reason,
        'lastMileage': last_mileage,
        'lastDate': last_date.isoformat() if last_date else None,
        'openRecordId': open_rec.id if open_rec else None,
        'openStatus': open_rec.status if open_rec else None,
    }


def sync_open_appointments(today=None):
    """超过 1 万公里或满 90 天，为车辆生成待处理预约（幂等）。"""
    today = today or _today()
    created = []
    for vehicle in Vehicle.objects.exclude(status='Retired'):
        state = evaluate_vehicle(vehicle, today)
        if state['due'] and state['openRecordId'] is None:
            record = MaintenanceRecord.objects.create(
                vehicle=vehicle,
                maintenance_type='Routine',
                items=['定期保养'],
                vendor='',
                date=today,
                mileage=vehicle.mileage,
                next_mileage=0,
                next_date=None,
                status='Scheduled',
                source='Auto',
            )
            created.append(record)
    return created


def _record_dict(record, state=None):
    state = state or {}
    completed = record.completed_at
    if completed is None and record.status == 'Completed' and record.date:
        completed = datetime.combine(record.date, datetime.min.time(), tzinfo=SH_TZ)
    is_open = record.status in OPEN_STATUSES
    return {
        'id': record.id,
        'vehicleId': record.vehicle_id,
        'plateNo': getattr(record.vehicle, 'plate_no', '') if record.vehicle_id else '',
        'type': record.maintenance_type,
        'items': list(record.items or []),
        'cost': record.cost,
        'vendor': record.vendor,
        'date': record.date.isoformat() if record.date else None,
        'mileage': record.mileage,
        'nextMileage': record.next_mileage,
        'nextDate': record.next_date.isoformat() if record.next_date else None,
        'status': record.status,
        'source': record.source,
        'completedAt': completed.isoformat() if completed else None,
        'due': is_open and state.get('due', False),
        'dueReasons': state.get('reasons', []) if is_open else [],
        'blockReason': state.get('blockReason', '') if is_open else '',
    }


def _record_state_map(today):
    states = {}
    for vehicle in Vehicle.objects.all():
        states[vehicle.id] = evaluate_vehicle(vehicle, today)
    return states


def list_records(filter_status=None, vehicle_id=None, today=None):
    """按视图筛选返回维保记录：due=到期 / pending=待处理 / completed=已完成。"""
    today = today or _today()
    sync_open_appointments(today)

    records = MaintenanceRecord.objects.select_related('vehicle').order_by(
        '-date', '-id'
    )
    if vehicle_id:
        records = records.filter(vehicle_id=vehicle_id)

    states = _record_state_map(today)
    result = []
    for record in records:
        state = states.get(record.vehicle_id, {})
        if filter_status == 'due':
            # 到期：已越过里程/日期门槛、正在占用车辆的预约与施工单
            if record.status == 'Scheduled' and state.get('due'):
                result.append(_record_dict(record, state))
            elif record.status == 'InProgress':
                result.append(_record_dict(record, state))
        elif filter_status == 'pending':
            # 待处理：尚未到期的预约，等待日后施工
            if record.status == 'Scheduled' and not state.get('due'):
                result.append(_record_dict(record, state))
        elif filter_status == 'completed':
            if record.status == 'Completed':
                result.append(_record_dict(record, state))
        else:
            result.append(_record_dict(record, state))
    return result


def start_record(record_id):
    """维修人员接单：待处理预约转为施工中（占用状态不变）。"""
    record = MaintenanceRecord.objects.select_related('vehicle').get(id=record_id)
    if record.status == 'Completed':
        raise ValueError('该维保记录已完成，不能再次开工')
    record.status = 'InProgress'
    record.save(update_fields=['status'])
    if record.vehicle.status == 'Available':
        record.vehicle.status = 'Maintenance'
        record.vehicle.save(update_fields=['status'])
    state = evaluate_vehicle(record.vehicle)
    return _record_dict(record, state)


@transaction.atomic
def complete_record(record_id, payload, completed_at=None):
    """维修人员提交里程、费用、完成时间：解除占用并按新里程重算下次预约。"""
    today = _today()
    record = MaintenanceRecord.objects.select_for_update().select_related(
        'vehicle'
    ).get(id=record_id)
    if record.status == 'Completed':
        raise ValueError('该维保记录已完成，不能重复提交')

    vehicle = Vehicle.objects.select_for_update().get(id=record.vehicle_id)
    new_mileage = payload['mileage']
    last = get_last_completed(vehicle.id)
    if last and new_mileage < last.mileage:
        raise ValueError(f'提交里程不能小于上次保养里程 {last.mileage} 公里')

    completed_on = completed_at or payload['completedAt']
    if timezone.is_naive(completed_on):
        completed_on = timezone.make_aware(completed_on, SH_TZ)
    completed_date = completed_on.astimezone(SH_TZ).date()

    # 关闭本次工单（维修人员提交的字段覆盖预约内容）
    record.status = 'Completed'
    record.maintenance_type = payload.get('maintenanceType', record.maintenance_type)
    if payload.get('items'):
        record.items = payload['items']
    if payload.get('vendor'):
        record.vendor = payload['vendor']
    record.cost = payload.get('cost', 0)
    record.mileage = new_mileage
    record.date = completed_date
    record.completed_at = completed_on
    point = next_due_point(new_mileage, completed_date)
    record.next_mileage = point['next_mileage']
    record.next_date = point['next_date']
    record.save()

    # 同步车辆累计里程，车辆恢复可调度状态
    if new_mileage > vehicle.mileage:
        vehicle.mileage = new_mileage
    if vehicle.status == 'Maintenance':
        vehicle.status = 'Available'
    vehicle.save()

    # 清除其它系统生成的未关闭预约；人工登记的预约保留
    MaintenanceRecord.objects.filter(
        vehicle=vehicle, status__in=OPEN_STATUSES
    ).exclude(id=record.id).exclude(source='Manual').delete()

    # 按新里程/完成时间重算下次保养预约
    next_record = MaintenanceRecord.objects.create(
        vehicle=vehicle,
        maintenance_type='Routine',
        items=['定期保养'],
        vendor='',
        date=point['next_date'],
        mileage=new_mileage,
        next_mileage=0,
        next_date=None,
        status='Scheduled',
        source='Auto',
    )
    state = evaluate_vehicle(vehicle, today)
    return _record_dict(record, state), _record_dict(next_record, state)


@transaction.atomic
def create_record(payload):
    """人工登记维保记录（车辆管理/维保单创建入口）。"""
    vehicle = Vehicle.objects.get(id=payload['vehicleId'])
    record = MaintenanceRecord.objects.create(
        vehicle=vehicle,
        maintenance_type=payload['type'],
        items=payload['items'],
        cost=payload['cost'],
        vendor=payload['vendor'],
        date=payload['date'] or _today(),
        mileage=payload['mileage'] or vehicle.mileage,
        next_mileage=payload['nextMileage'],
        next_date=payload['nextDate'],
        status='Scheduled',
        source='Manual',
    )
    state = evaluate_vehicle(vehicle)
    return _record_dict(record, state)
