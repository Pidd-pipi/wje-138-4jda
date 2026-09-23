from rest_framework import serializers

DISPATCH_STATUSES = ('Pending', 'Assigned', 'InProgress', 'Completed', 'Cancelled')


class DispatchCreateSerializer(serializers.Serializer):
    vehicleId = serializers.IntegerField(required=True)
    driverId = serializers.IntegerField(required=False, allow_null=True)
    origin = serializers.CharField(required=True, max_length=120)
    destination = serializers.CharField(required=True, max_length=120)
    planDepartAt = serializers.DateTimeField(required=False, allow_null=True)
    planArriveAt = serializers.DateTimeField(required=False, allow_null=True)
    cargo = serializers.CharField(required=False, allow_blank=True, default='')
    weight = serializers.FloatField(required=False, min_value=0, default=0)
    freight = serializers.FloatField(required=False, min_value=0, default=0)
    status = serializers.ChoiceField(choices=DISPATCH_STATUSES, default='Pending')
    creatorId = serializers.IntegerField(required=False, default=1)
    note = serializers.CharField(required=False, allow_blank=True, default='')
