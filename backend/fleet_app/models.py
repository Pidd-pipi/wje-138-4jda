from django.db import models

class Vehicle(models.Model):
    plate_no = models.CharField(max_length=32)
    vehicle_type = models.CharField(max_length=32)
    brand_model = models.CharField(max_length=80)
    purchase_date = models.DateField(null=True)
    insurance_expire_date = models.DateField(null=True)
    inspection_expire_date = models.DateField(null=True)
    status = models.CharField(max_length=24)
    mileage = models.IntegerField(default=0)
    tank_capacity = models.FloatField(default=0)
    fuel_consumption = models.FloatField(default=0)

class Driver(models.Model):
    name = models.CharField(max_length=40)
    phone = models.CharField(max_length=32)
    license_type = models.CharField(max_length=8)
    license_expire_date = models.DateField(null=True)
    hire_date = models.DateField(null=True)
    status = models.CharField(max_length=24)
    driving_hours = models.IntegerField(default=0)
    violation_count = models.IntegerField(default=0)

class DispatchOrder(models.Model):
    order_no = models.CharField(max_length=40)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='dispatch_orders')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, related_name='dispatch_orders')
    origin = models.CharField(max_length=120)
    destination = models.CharField(max_length=120)
    plan_depart_at = models.DateTimeField(null=True)
    plan_arrive_at = models.DateTimeField(null=True)
    actual_depart_at = models.DateTimeField(null=True)
    actual_arrive_at = models.DateTimeField(null=True)
    cargo = models.CharField(max_length=160)
    weight = models.FloatField(default=0)
    freight = models.FloatField(default=0)
    status = models.CharField(max_length=24)
    creator_id = models.IntegerField(default=1)
    note = models.TextField(blank=True)

class MaintenanceRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=24)
    items = models.JSONField(default=list)
    cost = models.FloatField(default=0)
    vendor = models.CharField(max_length=120, blank=True, default='')
    date = models.DateField(null=True)
    mileage = models.IntegerField(default=0)
    next_mileage = models.IntegerField(default=0)
    next_date = models.DateField(null=True)
    # Scheduled=已预约待施工（系统按里程/日期生成或人工创建），InProgress=施工中，Completed=已完成
    status = models.CharField(max_length=24, default='Scheduled')
    # Auto=系统按保养规则生成的待处理预约，Manual=人工登记
    source = models.CharField(max_length=16, default='Manual')
    completed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class FuelRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='fuel_records')
    date = models.DateField(null=True)
    liters = models.FloatField(default=0)
    unit_price = models.FloatField(default=0)
    total_amount = models.FloatField(default=0)
    mileage = models.IntegerField(default=0)
    station = models.CharField(max_length=120)
    payment_method = models.CharField(max_length=24)
