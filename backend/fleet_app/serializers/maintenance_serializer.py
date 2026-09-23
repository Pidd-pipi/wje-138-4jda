from rest_framework import serializers


class MaintenanceCompleteSerializer(serializers.Serializer):
    """维修人员完工提交：里程、费用、完成时间。"""

    mileage = serializers.IntegerField(min_value=1)
    cost = serializers.FloatField(min_value=0, required=False, default=0)
    vendor = serializers.CharField(required=False, allow_blank=True, default='')
    completedAt = serializers.DateTimeField(required=False, allow_null=True)
    maintenanceType = serializers.CharField(required=False, default='Routine')
    items = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
