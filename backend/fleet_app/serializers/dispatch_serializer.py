from rest_framework import serializers


class DispatchCreateSerializer(serializers.Serializer):
    """创建调度单入参。"""

    vehicleId = serializers.IntegerField(required=False)
    driverId = serializers.IntegerField(required=False, allow_null=True)
    origin = serializers.CharField(required=False, allow_blank=True, default='')
    destination = serializers.CharField(required=False, allow_blank=True, default='')
    planDepartAt = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    planArriveAt = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    cargo = serializers.CharField(required=False, allow_blank=True, default='')
    weight = serializers.FloatField(required=False, default=0)
    freight = serializers.FloatField(required=False, default=0)
    note = serializers.CharField(required=False, allow_blank=True, default='')
