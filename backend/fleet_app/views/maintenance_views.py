from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from fleet_app.models import MaintenanceRecord
from fleet_app.serializers.maintenance_serializer import (
    MaintenanceCompleteSerializer,
    MaintenanceCreateSerializer,
)
from fleet_app.services import maintenance_service


@api_view(['GET', 'POST'])
def maintenance_records(request):
    """GET 支持 filter=due/pending/completed 与 vehicleId；POST 人工登记。"""
    if request.method == 'POST':
        serializer = MaintenanceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = maintenance_service.create_record(serializer.validated_data)
        return Response(record, status=status.HTTP_201_CREATED)

    filter_status = request.GET.get('filter')
    vehicle_id = request.GET.get('vehicleId')
    records = maintenance_service.list_records(
        filter_status=filter_status, vehicle_id=vehicle_id
    )
    return Response(records)


@api_view(['POST'])
def maintenance_start(request, record_id):
    """维修人员接单开工。"""
    try:
        record = maintenance_service.start_record(record_id)
    except MaintenanceRecord.DoesNotExist:
        return Response(
            {'code': 'NOT_FOUND', 'message': '维保记录不存在'},
            status=status.HTTP_404_NOT_FOUND,
        )
    except ValueError as exc:
        return Response(
            {'code': 'INVALID_STATE', 'message': str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(record)


@api_view(['POST'])
def maintenance_complete(request, record_id):
    """维修人员提交里程、费用、完成时间，解除占用并重算下次预约。"""
    serializer = MaintenanceCompleteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        completed, next_record = maintenance_service.complete_record(
            record_id, serializer.validated_data
        )
    except MaintenanceRecord.DoesNotExist:
        return Response(
            {'code': 'NOT_FOUND', 'message': '维保记录不存在'},
            status=status.HTTP_404_NOT_FOUND,
        )
    except ValueError as exc:
        return Response(
            {'code': 'INVALID_MILEAGE', 'message': str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response({'completed': completed, 'nextAppointment': next_record})
