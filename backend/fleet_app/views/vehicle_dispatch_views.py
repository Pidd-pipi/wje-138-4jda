from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from fleet_app.models import Vehicle
from fleet_app.services.dispatch_service import (
    VehicleMaintenanceBlocked,
    check_vehicle_dispatchable,
)


@api_view(['GET'])
def vehicle_dispatch_check(request, vehicle_id):
    """调度中心选车时预检：返回车辆能否排班及不能排班的原因。"""
    try:
        vehicle, state = check_vehicle_dispatchable(vehicle_id)
    except VehicleMaintenanceBlocked as exc:
        v = exc.vehicle
        return Response(
            {
                'vehicleId': v.id,
                'plateNo': v.plate_no,
                'dispatchable': False,
                'reasonCode': exc.state['reasonCode'],
                'reasons': exc.state['reasons'],
                'message': exc.state['blockReason'],
                'maintenanceRecordId': exc.state['openRecordId'],
            },
            status=status.HTTP_409_CONFLICT,
        )
    except Vehicle.DoesNotExist:
        return Response(
            {'code': 'NOT_FOUND', 'message': '车辆不存在'},
            status=status.HTTP_404_NOT_FOUND,
        )
    except ValueError as exc:
        return Response(
            {
                'vehicleId': vehicle.id,
                'plateNo': vehicle.plate_no,
                'dispatchable': False,
                'message': str(exc),
            },
            status=status.HTTP_409_CONFLICT,
        )
    return Response(
        {
            'vehicleId': vehicle.id,
            'plateNo': vehicle.plate_no,
            'dispatchable': True,
            'message': '',
        }
    )
