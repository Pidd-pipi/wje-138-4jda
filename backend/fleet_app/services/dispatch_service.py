"""调度业务：创建调度单前校验车辆保养占用，到期车辆不予保存。"""
from datetime import datetime

from fleet_app.services import fleet_data
from fleet_app.services.errors import BusinessValidationError
from fleet_app.services.maintenance_service import block_map


def _parse_dt(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.strptime(value, '%Y-%m-%d %H:%M')


def _iso(value):
    return value.strftime('%Y-%m-%d %H:%M') if value else None


def _serialize_order(order):
    return {
        'id': order['id'],
        'orderNo': order['order_no'],
        'vehicleId': order['vehicle_id'],
        'driverId': order['driver_id'],
        'origin': order['origin'],
        'destination': order['destination'],
        'planDepartAt': _iso(order['plan_depart_at']),
        'planArriveAt': _iso(order['plan_arrive_at']),
        'actualDepartAt': _iso(order['actual_depart_at']),
        'actualArriveAt': _iso(order['actual_arrive_at']),
        'cargo': order['cargo'],
        'weight': order['weight'],
        'freight': order['freight'],
        'status': order['status'],
        'creatorId': order['creator_id'],
        'note': order['note'],
    }


def list_orders():
    return [_serialize_order(order) for order in fleet_data.ORDERS.values()]


def create_order(payload):
    blocks = block_map()

    vehicle_id = payload.get('vehicleId')
    vehicle = fleet_data.VEHICLES.get(vehicle_id) if vehicle_id is not None else None
    if vehicle is None:
        raise BusinessValidationError('请选择需要调度的车辆')
    block = blocks.get(vehicle_id, {})
    if block.get('blocked'):
        # 到期车辆不能调度：说明原因，调度单不保存
        raise BusinessValidationError(
            f"车辆 {vehicle['plate_no']} 不可调度。{block['reason']}"
        )

    driver_id = payload.get('driverId')
    if driver_id is not None and driver_id not in fleet_data.DRIVERS:
        raise BusinessValidationError('所选司机不存在')

    order_id, order_no = fleet_data.next_order_identity()
    order = {
        'id': order_id,
        'order_no': order_no,
        'vehicle_id': vehicle_id,
        'driver_id': driver_id,
        'origin': payload.get('origin', ''),
        'destination': payload.get('destination', ''),
        'plan_depart_at': _parse_dt(payload.get('planDepartAt')),
        'plan_arrive_at': _parse_dt(payload.get('planArriveAt')),
        'actual_depart_at': None,
        'actual_arrive_at': None,
        'cargo': payload.get('cargo', ''),
        'weight': float(payload.get('weight', 0) or 0),
        'freight': float(payload.get('freight', 0) or 0),
        'status': 'Pending',
        'creator_id': payload.get('creatorId', 1),
        'note': payload.get('note', ''),
    }
    fleet_data.ORDERS[order_id] = order
    return _serialize_order(order)
