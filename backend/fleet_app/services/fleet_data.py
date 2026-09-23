"""进程内内存数据层与种子数据。

项目尚未接数据库迁移，各 service 原先直接返回字面量。为支撑
"保养到期 -> 占用车辆 -> 完工解除" 的有状态流程，这里集中存放
车辆 / 司机 / 维保 / 调度单的内存数据，service 层统一读写本模块。
"""
from datetime import date, datetime, timedelta

# 保养周期：超过 10000 公里或距上次保养满 90 天即为到期
MILEAGE_INTERVAL = 10000
DAYS_INTERVAL = 90

_today = date.today()

# id -> 车辆
VEHICLES = {
    1: {
        'id': 1,
        'plate_no': '沪A-7821',
        'type': '冷链车',
        'brand_model': '东风天锦 KR',
        'purchase_date': date(2023, 3, 12),
        'insurance_expire_date': date(_today.year, 9, 30),
        'inspection_expire_date': date(_today.year, 11, 20),
        'status': 'Available',
        'mileage': 88210,
        'tank_capacity': 380,
        'fuel_consumption': 24.6,
    },
    2: {
        'id': 2,
        'plate_no': '苏E-5520',
        'type': '重卡',
        'brand_model': '解放 J6P',
        'purchase_date': date(2021, 8, 6),
        'insurance_expire_date': date(_today.year, 7, 15),
        'inspection_expire_date': date(_today.year, 8, 22),
        'status': 'Available',
        'mileage': 210430,
        'tank_capacity': 520,
        'fuel_consumption': 31.2,
    },
}

DRIVERS = {
    1: {
        'id': 1, 'name': '赵强', 'phone': '13800000001', 'license_type': 'B2',
        'license_expire_date': date(2028, 5, 1), 'hire_date': date(2022, 1, 10),
        'status': 'Available', 'driving_hours': 3200, 'violation_count': 1,
    },
    2: {
        'id': 2, 'name': '孙晨', 'phone': '13800000002', 'license_type': 'A2',
        'license_expire_date': date(2029, 4, 18), 'hire_date': date(2021, 11, 16),
        'status': 'OnTrip', 'driving_hours': 4810, 'violation_count': 0,
    },
}

# 历史已完成的保养记录（上次保养的里程与日期的依据）
MAINTENANCE = {
    1: {
        'id': 1, 'vehicle_id': 1, 'maintenance_type': 'Routine',
        'items': ['机油', '机滤', '轮胎检查'], 'cost': 2100, 'vendor': '青浦维保站',
        'date': _today - timedelta(days=95), 'mileage': 76800,
        'next_mileage': 76800 + MILEAGE_INTERVAL, 'next_date': _today - timedelta(days=5),
        'status': 'Completed',
    },
    2: {
        'id': 2, 'vehicle_id': 2, 'maintenance_type': 'Routine',
        'items': ['机油', '刹车检查'], 'cost': 1600, 'vendor': '苏州园区维修厂',
        'date': _today - timedelta(days=20), 'mileage': 207200,
        'next_mileage': 207200 + MILEAGE_INTERVAL, 'next_date': _today + timedelta(days=70),
        'status': 'Completed',
    },
}

ORDERS = {
    1: {
        'id': 1, 'order_no': 'DSP-20260612-0001', 'vehicle_id': 1, 'driver_id': 1,
        'origin': '上海青浦仓', 'destination': '杭州萧山仓',
        'plan_depart_at': datetime(2026, 6, 12, 9, 0), 'plan_arrive_at': datetime(2026, 6, 12, 13, 30),
        'actual_depart_at': None, 'actual_arrive_at': None,
        'cargo': '冷链食品', 'weight': 8200, 'freight': 7200,
        'status': 'Assigned', 'creator_id': 1, 'note': '优先发车',
    },
    2: {
        'id': 2, 'order_no': 'DSP-20260612-0002', 'vehicle_id': 2, 'driver_id': 2,
        'origin': '苏州园区', 'destination': '宁波北仑',
        'plan_depart_at': datetime(2026, 6, 12, 14, 0), 'plan_arrive_at': datetime(2026, 6, 12, 20, 30),
        'actual_depart_at': None, 'actual_arrive_at': None,
        'cargo': '建筑材料', 'weight': 16000, 'freight': 9800,
        'status': 'InProgress', 'creator_id': 1, 'note': '',
    },
}

# 自增主键与单号序号
_next_maintenance_id = 3
_next_order_id = 3
_order_seq = 3


def next_maintenance_id():
    global _next_maintenance_id
    value = _next_maintenance_id
    _next_maintenance_id += 1
    return value


def next_order_identity():
    global _next_order_id, _order_seq
    order_id = _next_order_id
    order_no = f'DSP-{date.today():%Y%m%d}-{_order_seq:04d}'
    _next_order_id += 1
    _order_seq += 1
    return order_id, order_no
