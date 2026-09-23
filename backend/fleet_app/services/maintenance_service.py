"""维保业务：到期占用同步、记录查询筛选、维修人员完工解除占用。"""
from datetime import date, datetime

from fleet_app.services import fleet_data
from fleet_app.services.errors import BusinessValidationError
from fleet_app.services.maintenance_policy import (
    block_reason_text,
    due_reasons,
    next_threshold,
    record_stage,
)


def _iso(value):
    return value.isoformat() if value else ''


def _latest_completed(vehicle_id):
    return max(
        (r for r in fleet_data.MAINTENANCE.values()
         if r['vehicle_id'] == vehicle_id and r['status'] == 'Completed'),
        key=lambda r: (r['date'], r['id']),
        default=None,
    )


def _open_appointment(vehicle_id):
    return next(
        (r for r in fleet_data.MAINTENANCE.values()
         if r['vehicle_id'] == vehicle_id and r['status'] == 'Scheduled'),
        None,
    )


def sync_due_appointments(today=None):
    """读取每辆车上次保养的里程/日期，到期则生成待处理预约并占用车辆。

    返回 vehicle_id -> 到期原因码列表（空列表表示未被占用）。
    """
    today = today or date.today()
    blocks = {}
    for vehicle in fleet_data.VEHICLES.values():
        last_record = _latest_completed(vehicle['id'])
        reasons = due_reasons(last_record, vehicle, today) if last_record else []
        blocks[vehicle['id']] = reasons
        if not reasons:
            continue
        appointment = _open_appointment(vehicle['id'])
        if appointment is None:
            # 到期自动生成一条待处理预约，阈值沿用上次保养推算
            appointment = {
                'id': fleet_data.next_maintenance_id(),
                'vehicle_id': vehicle['id'],
                'maintenance_type': 'Routine',
                'items': ['到期保养（自动生成）'],
                'cost': 0,
                'vendor': '',
                'date': None,
                'mileage': last_record['mileage'],
                'next_mileage': last_record['next_mileage'],
                'next_date': last_record['next_date'],
                'status': 'Scheduled',
            }
            fleet_data.MAINTENANCE[appointment['id']] = appointment
        # 到期车辆占用：写回车辆状态，供车辆卡片/排班提示使用
        if vehicle['status'] != 'Maintenance':
            vehicle['status'] = 'Maintenance'
    return blocks


def get_blocks(today=None):
    """同步到期占用，并返回每辆车的占用明细（含原因）。"""
    blocks = sync_due_appointments(today)
    result = []
    for vehicle_id, reasons in blocks.items():
        vehicle = fleet_data.VEHICLES[vehicle_id]
        result.append({
            'vehicleId': vehicle_id,
            'plateNo': vehicle['plate_no'],
            'blocked': bool(reasons),
            'reasonCodes': reasons,
            'reason': block_reason_text(reasons) if reasons else '',
        })
    return result


def block_map(today=None):
    return {item['vehicleId']: item for item in get_blocks(today)}


def _serialize_record(record, blocks):
    vehicle = fleet_data.VEHICLES[record['vehicle_id']]
    blocked = bool(blocks.get(record['vehicle_id']))
    last_record = _latest_completed(record['vehicle_id'])
    mileage_diff = vehicle['mileage'] - last_record['mileage'] if last_record else 0
    return {
        'id': record['id'],
        'vehicleId': record['vehicle_id'],
        'plateNo': vehicle['plate_no'],
        'type': record['maintenance_type'],
        'items': record['items'],
        'cost': record['cost'],
        'vendor': record['vendor'],
        'date': _iso(record['date']),
        'mileage': record['mileage'],
        'nextMileage': record['next_mileage'],
        'nextDate': _iso(record['next_date']),
        'status': record['status'],
        'stage': record_stage(record, blocked),
        'mileageDiff': mileage_diff,
        'currentMileage': vehicle['mileage'],
        'reason': block_reason_text(blocks.get(record['vehicle_id'], [])) if blocked else '',
    }


def list_records(stage=None, vehicle_id=None, today=None):
    blocks = sync_due_appointments(today)
    records = sorted(
        fleet_data.MAINTENANCE.values(),
        key=lambda r: (r['date'] or r['next_date'] or date.min, r['id']),
        reverse=True,
    )
    if vehicle_id is not None:
        records = [r for r in records if r['vehicle_id'] == vehicle_id]
    if stage:
        records = [
            r for r in records
            if record_stage(r, bool(blocks[r['vehicle_id']])) == stage
        ]
    return [_serialize_record(r, blocks) for r in records]


def complete_appointment(record_id, payload, completed_at=None):
    """维修人员提交里程、费用和完成时间：解除占用并按新里程重算下次预约。"""
    today = completed_at or date.today()
    if isinstance(today, datetime):
        today = today.date()
    sync_due_appointments(today)

    record = fleet_data.MAINTENANCE.get(record_id)
    if record is None:
        raise BusinessValidationError('维保记录不存在')
    if record['status'] != 'Scheduled':
        raise BusinessValidationError('该预约已处理，无需重复提交')

    mileage = payload.get('mileage')
    cost = payload.get('cost', 0)
    vendor = (payload.get('vendor') or '').strip()
    items = payload.get('items') or ['常规保养']
    if not isinstance(items, list):
        items = [str(items)]
    if mileage is None or int(mileage) <= 0:
        raise BusinessValidationError('请填写本次保养完成时的车辆里程')

    vehicle = fleet_data.VEHICLES[record['vehicle_id']]
    mileage = int(mileage)
    last_record = _latest_completed(vehicle['id'])
    if last_record and mileage < last_record['mileage']:
        raise BusinessValidationError(
            f'本次里程不能小于上次保养里程（{last_record["mileage"]} km）'
        )
    if mileage < vehicle['mileage']:
        raise BusinessValidationError(
            f'本次里程不能小于车辆当前里程（{vehicle["mileage"]} km）'
        )

    # 1) 待处理预约 -> 已完成，解除占用
    record.update({
        'maintenance_type': payload.get('maintenanceType', 'Routine'),
        'items': items,
        'cost': float(cost or 0),
        'vendor': vendor or '未登记维修厂',
        'date': today,
        'mileage': mileage,
        'status': 'Completed',
    })

    # 2) 同步车辆里程并解除占用
    vehicle['mileage'] = mileage
    if vehicle['status'] == 'Maintenance':
        vehicle['status'] = 'Available'

    # 3) 按新里程重算下次预约（待处理，未到期前不占用车辆）
    next_mileage, next_due_date = next_threshold(mileage, today)
    record['next_mileage'] = next_mileage
    record['next_date'] = next_due_date
    new_appointment_id = fleet_data.next_maintenance_id()
    fleet_data.MAINTENANCE[new_appointment_id] = {
        'id': new_appointment_id,
        'vehicle_id': vehicle['id'],
        'maintenance_type': 'Routine',
        'items': ['下次保养（按本次里程重算）'],
        'cost': 0,
        'vendor': '',
        'date': None,
        'mileage': mileage,
        'next_mileage': next_mileage,
        'next_date': next_due_date,
        'status': 'Scheduled',
    }

    return _serialize_record(record, {})
