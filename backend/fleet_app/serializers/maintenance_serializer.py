from rest_framework import serializers

MAINTENANCE_STATUSES = ('Scheduled', 'InProgress', 'Completed')
MAINTENANCE_TYPES = ('Routine', 'Repair', 'Emergency', 'Inspection')


class MaintenanceCompleteSerializer(serializers.Serializer):
    """维修人员完工提交：里程、费用、完成时间。"""
    mileage = serializers.IntegerField(required=True, min_value=0)
    cost = serializers.FloatField(required=False, min_value=0, default=0)
    completedAt = serializers.DateTimeField(required=True)
    vendor = serializers.CharField(required=False, allow_blank=True, default='')
    items = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    maintenanceType = serializers.ChoiceField(
        choices=MAINTENANCE_TYPES, required=False, default='Routine'
    )


class MaintenanceCreateSerializer(serializers.Serializer):
    vehicleId = serializers.IntegerField(required=True)
    type = serializers.ChoiceField(choices=MAINTENANCE_TYPES, default='Routine')
    items = serializers.ListField(child=serializers.CharField(), default=list)
    cost = serializers.FloatField(min_value=0, default=0)
    vendor = serializers.CharField(allow_blank=True, default='')
    date = serializers.DateField(required=False, allow_null=True, default=None)
    mileage = serializers.IntegerField(min_value=0, default=0)
    nextMileage = serializers.IntegerField(min_value=0, default=0)
    nextDate = serializers.DateField(required=False, allow_null=True, default=None)
