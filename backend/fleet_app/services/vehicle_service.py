"""车辆档案与保养占用状态查询。"""
from fleet_app.models import Vehicle
from fleet_app.services.maintenance_service import evaluate_vehicle


def _vehicle_dict(vehicle, state=None):
    state = state or {}
    return {
        'id': vehicle.id,
        'plateNo': vehicle.plate_no,
        'type': vehicle.vehicle_type,
        'brandModel': vehicle.brand_model,
        'purchaseDate': vehicle.purchase_date.isoformat() if vehicle.purchase_date else None,
        'insuranceExpireDate': vehicle.insurance_expire_date.isoformat() if vehicle.insurance_expire_date else None,
        'inspectionExpireDate': vehicle.inspection_expire_date.isoformat() if vehicle.inspection_expire_date else None,
        'status': vehicle.status,
        'mileage': vehicle.mileage,
        'tankCapacity': vehicle.tank_capacity,
        'fuelConsumption': vehicle.fuel_consumption,
        'maintenanceBlocked': state.get('blocked', False),
        'maintenanceDue': state.get('due', False),
        'blockReason': state.get('blockReason', ''),
        'lastMaintenanceMileage': state.get('lastMileage'),
        'lastMaintenanceDate': state.get('lastDate'),
        'openMaintenanceRecordId': state.get('openRecordId'),
    }


def list_vehicles():
    vehicles = list(Vehicle.objects.all().order_by('id'))
    result = []
    for vehicle in vehicles:
        result.append(_vehicle_dict(vehicle, evaluate_vehicle(vehicle)))
    return result


def get_vehicle(vehicle_id):
    vehicle = Vehicle.objects.get(id=vehicle_id)
    return _vehicle_dict(vehicle, evaluate_vehicle(vehicle))
