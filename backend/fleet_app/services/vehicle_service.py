"""车辆业务：车辆列表附带保养占用状态，供车辆卡片与调度中心判断排班。"""
from fleet_app.services import fleet_data
from fleet_app.services.maintenance_service import block_map


def _iso(value):
    return value.isoformat() if value else ''


def _serialize_vehicle(vehicle, blocks):
    block = blocks.get(vehicle['id'], {})
    return {
        'id': vehicle['id'],
        'plateNo': vehicle['plate_no'],
        'type': vehicle['type'],
        'brandModel': vehicle['brand_model'],
        'purchaseDate': _iso(vehicle['purchase_date']),
        'insuranceExpireDate': _iso(vehicle['insurance_expire_date']),
        'inspectionExpireDate': _iso(vehicle['inspection_expire_date']),
        'status': vehicle['status'],
        'mileage': vehicle['mileage'],
        'tankCapacity': vehicle['tank_capacity'],
        'fuelConsumption': vehicle['fuel_consumption'],
        'maintenanceBlocked': block.get('blocked', False),
        'maintenanceReason': block.get('reason', ''),
        'maintenanceReasonCodes': block.get('reasonCodes', []),
    }


def list_vehicles():
    blocks = block_map()
    return [_serialize_vehicle(vehicle, blocks) for vehicle in fleet_data.VEHICLES.values()]
