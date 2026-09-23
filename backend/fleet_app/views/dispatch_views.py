from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from fleet_app.serializers.dispatch_serializer import DispatchCreateSerializer
from fleet_app.services.dispatch_service import create_order, list_orders
from fleet_app.services.errors import BusinessValidationError


@api_view(['GET', 'POST'])
def dispatch_orders(request):
    if request.method == 'POST':
        serializer = DispatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = create_order(serializer.validated_data)
        except BusinessValidationError as exc:
            # 保养到期等业务拦截：说明原因，调度单不保存
            return Response({'detail': exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        return Response(order, status=201)
    return Response(list_orders())
