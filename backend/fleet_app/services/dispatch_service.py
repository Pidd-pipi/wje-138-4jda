"""调度单服务：创建调度单前校验车辆是否被保养到期占用。"""
from django.utils import timezone

from fleet_app.models import DispatchOrder, Driver, Vehicle
from fleet_app.services.maintenance_service import evaluate_vehicle


class VehicleMaintenanceBlocked(Exception):
    """车辆因保养到期/维修中被占用，不允许调度。"""

    def __init__(self, vehicle, state):
        self.vehicle = vehicle
        self.state = state
        super().__init__(state['blockReason'])


def _parse_dt(value):
    if not value:
        return None
    if isinstance(value, str):
        value = value.replace('/', '-')
        try:
            parsed = timezone.datetime.fromisoformat(value)
        except ValueError:
            return None
    else:
        parsed = value
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _order_dict(order):
    return {
        'id': order.id,
        'orderNo': order.order_no,
        'vehicleId': order.vehicle_id,
        'driverId': order.driver_id,
        'origin': order.origin,
        'destination': order.destination,
        'planDepartAt': order.plan_depart_at.isoformat() if order.plan_depart_at else None,
        'planArriveAt': order.plan_arrive_at.isoformat() if order.plan_arrive_at else None,
        'actualDepartAt': order.actual_depart_at.isoformat() if order.actual_depart_at else None,
        'actualArriveAt': order.actual_arrive_at.isoformat() if order.actual_arrive_at else None,
        'cargo': order.cargo,
        'weight': order.weight,
        'freight': order.freight,
        'status': order.status,
        'creatorId': order.creator_id,
        'note': order.note,
    }


def list_orders(status=None, vehicle_id=None):
    orders = DispatchOrder.objects.select_related('vehicle', 'driver').order_by(
        '-id'
    )
    if status and status != 'all':
        orders = orders.filter(status=status)
    if vehicle_id:
        orders = orders.filter(vehicle_id=vehicle_id)
    return [_order_dict(order) for order in orders]


def check_vehicle_dispatchable(vehicle_id):
    """返回 (vehicle, state)；车辆不可调度时抛出异常，调度单不保存。"""
    vehicle = Vehicle.objects.get(id=vehicle_id)
    if vehicle.status == 'Retired':
        raise ValueError(f'车辆 {vehicle.plate_no} 已报废，不能调度')
    state = evaluate_vehicle(vehicle)
    if state['blocked']:
        raise VehicleMaintenanceBlocked(vehicle, state)
    return vehicle, state


def create_order(payload):
    vehicle, _ = check_vehicle_dispatchable(payload['vehicleId'])

    if 'driverId' in payload and payload['driverId']:
        Driver.objects.get(id=payload['driverId'])

    today = timezone.localdate().strftime('%Y%m%d')
    seq = DispatchOrder.objects.filter(order_no__startswith=f'DSP-{today}-').count() + 1
    order_no = f'DSP-{today}-{seq:04d}'

    order = DispatchOrder.objects.create(
        order_no=order_no,
        vehicle=vehicle,
        driver_id=payload.get('driverId'),
        origin=payload.get('origin', ''),
        destination=payload.get('destination', ''),
        plan_depart_at=_parse_dt(payload.get('planDepartAt')),
        plan_arrive_at=_parse_dt(payload.get('planArriveAt')),
        cargo=payload.get('cargo', ''),
        weight=payload.get('weight', 0) or 0,
        freight=payload.get('freight', 0) or 0,
        status=payload.get('status', 'Pending'),
        creator_id=payload.get('creatorId', 1),
        note=payload.get('note', ''),
    )
    return _order_dict(order)
