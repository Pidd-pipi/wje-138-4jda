from rest_framework import serializers

from fleet_app.models import Vehicle

VEHICLE_STATUSES = ('Available', 'OnTrip', 'Maintenance', 'Retired')
VEHICLE_TYPES = ('轻卡', '中卡', '重卡', '冷链车', '危化车')


class VehicleCreateSerializer(serializers.Serializer):
    plateNo = serializers.CharField(required=True, max_length=32)
    type = serializers.ChoiceField(choices=VEHICLE_TYPES, default='轻卡')
    brandModel = serializers.CharField(required=False, allow_blank=True, default='')
    purchaseDate = serializers.DateField(required=False, allow_null=True)
    insuranceExpireDate = serializers.DateField(required=False, allow_null=True)
    inspectionExpireDate = serializers.DateField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=VEHICLE_STATUSES, default='Available')
    mileage = serializers.IntegerField(required=False, min_value=0, default=0)
    tankCapacity = serializers.FloatField(required=False, min_value=0, default=0)
    fuelConsumption = serializers.FloatField(required=False, min_value=0, default=0)
