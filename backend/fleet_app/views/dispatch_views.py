from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from fleet_app.serializers.dispatch_serializer import DispatchCreateSerializer
from fleet_app.services.dispatch_service import (
    VehicleMaintenanceBlocked,
    create_order,
    list_orders,
)


@api_view(['GET', 'POST'])
def dispatch_orders(request):
    if request.method == 'POST':
        serializer = DispatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = create_order(serializer.validated_data)
        except VehicleMaintenanceBlocked as exc:
            # 车辆被保养到期占用：说明原因，调度单不保存
            return Response(
                {
                    'code': 'VEHICLE_MAINTENANCE_BLOCKED',
                    'message': exc.state['blockReason'],
                    'vehicleId': exc.vehicle.id,
                    'plateNo': exc.vehicle.plate_no,
                    'reasons': exc.state['reasons'],
                    'reasonCode': exc.state['reasonCode'],
                    'maintenanceRecordId': exc.state['openRecordId'],
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(order, status=status.HTTP_201_CREATED)

    query_status = request.GET.get('status')
    vehicle_id = request.GET.get('vehicleId')
    return Response(list_orders(status=query_status, vehicle_id=vehicle_id))
