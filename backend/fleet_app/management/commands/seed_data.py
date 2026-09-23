"""初始化演示数据：车辆/司机 + 不同保养到期状态，便于验证占用与筛选。幂等。"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from fleet_app.models import Driver, MaintenanceRecord, Vehicle
from fleet_app.services.maintenance_service import sync_open_appointments


class Command(BaseCommand):
    help = '创建演示车辆、司机与维保记录（幂等）'

    def handle(self, *args, **options):
        today = timezone.localdate()

        if Vehicle.objects.exists():
            self.stdout.write('车辆数据已存在，跳过种子创建')
            return

        vehicles = [
            Vehicle(
                plate_no='沪A-7821', vehicle_type='冷链车', brand_model='东风天锦 KR',
                purchase_date='2023-03-12', insurance_expire_date=today + timedelta(days=120),
                inspection_expire_date=today + timedelta(days=180),
                status='Available', mileage=88210, tank_capacity=380, fuel_consumption=24.6,
            ),
            Vehicle(
                # 里程到期：距上次保养已行驶 12300 公里
                plate_no='苏E-5520', vehicle_type='重卡', brand_model='解放 J6P',
                purchase_date='2021-08-06', insurance_expire_date=today + timedelta(days=90),
                inspection_expire_date=today + timedelta(days=150),
                status='Available', mileage=212300, tank_capacity=520, fuel_consumption=31.2,
            ),
            Vehicle(
                # 日期到期：距上次保养已满 95 天（里程未超）
                plate_no='沪B-3309', vehicle_type='中卡', brand_model='福田欧马可 S5',
                purchase_date='2022-05-18', insurance_expire_date=today + timedelta(days=60),
                inspection_expire_date=today + timedelta(days=200),
                status='Available', mileage=61500, tank_capacity=300, fuel_consumption=19.8,
            ),
        ]
        Vehicle.objects.bulk_create(vehicles)

        Driver.objects.bulk_create([
            Driver(name='赵强', phone='13800000001', license_type='B2',
                   license_expire_date=today + timedelta(days=600),
                   hire_date='2022-01-10', status='Available',
                   driving_hours=3200, violation_count=1),
            Driver(name='孙晨', phone='13800000002', license_type='A2',
                   license_expire_date=today + timedelta(days=900),
                   hire_date='2021-11-16', status='Available',
                   driving_hours=4810, violation_count=0),
        ])

        # 沪A-7821：40 天前刚保养，里程 84000 → 未到期
        MaintenanceRecord.objects.create(
            vehicle=vehicles[0], maintenance_type='Routine', items=['机油', '轮胎检查'],
            cost=2100, vendor='青浦维保站', date=today - timedelta(days=40),
            mileage=84000, next_mileage=94000, next_date=today + timedelta(days=50),
            status='Completed', source='Manual',
            completed_at=timezone.now() - timedelta(days=40),
        )
        # 苏E-5520：30 天前保养，里程 200000 → 当前 212300，里程到期
        MaintenanceRecord.objects.create(
            vehicle=vehicles[1], maintenance_type='Routine', items=['机油机滤'],
            cost=2600, vendor='苏州园区维修厂', date=today - timedelta(days=30),
            mileage=200000, next_mileage=210000, next_date=today + timedelta(days=60),
            status='Completed', source='Manual',
            completed_at=timezone.now() - timedelta(days=30),
        )
        # 沪B-3309：95 天前保养，里程 59000 → 当前 61500（仅 2500 公里），日期到期
        MaintenanceRecord.objects.create(
            vehicle=vehicles[2], maintenance_type='Routine', items=['常规检查'],
            cost=1500, vendor='嘉定维保中心', date=today - timedelta(days=95),
            mileage=59000, next_mileage=69000, next_date=today - timedelta(days=5),
            status='Completed', source='Manual',
            completed_at=timezone.now() - timedelta(days=95),
        )

        created = sync_open_appointments(today)
        self.stdout.write(
            self.style.SUCCESS(
                f'种子数据完成：{len(vehicles)} 辆车，生成 {len(created)} 条到期保养预约'
            )
        )
