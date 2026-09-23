from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from fleet_app.serializers.maintenance_serializer import MaintenanceCompleteSerializer
from fleet_app.services.errors import BusinessValidationError
from fleet_app.services.maintenance_service import (
    complete_appointment,
    get_blocks,
    list_records,
)


@api_view(['GET'])
def maintenance_blocks(request):
    """各车辆保养占用情况（车辆为什么不能排班）。"""
    return Response(get_blocks())


@api_view(['GET'])
def maintenance_records(request):
    """维保记录，支持 stage=Due/Pending/Completed 与 vehicleId 筛选。"""
    stage = request.GET.get('stage') or None
    vehicle_id = request.GET.get('vehicleId')
    vehicle_id = int(vehicle_id) if vehicle_id else None
    return Response(list_records(stage=stage, vehicle_id=vehicle_id))


@api_view(['POST'])
def maintenance_complete(request, record_id):
    """维修人员提交里程、费用和完成时间，完工后解除占用并重算下次预约。"""
    serializer = MaintenanceCompleteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    try:
        record = complete_appointment(
            record_id, data, completed_at=data.get('completedAt')
        )
    except BusinessValidationError as exc:
        return Response({'detail': exc.detail}, status=status.HTTP_400_BAD_REQUEST)
    return Response(record)
