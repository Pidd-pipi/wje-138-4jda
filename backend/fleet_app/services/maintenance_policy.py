"""保养到期判定与占用规则（纯函数，不直接读写数据）。

规则：
- 以车辆最近一条已完成保养记录作为"上次保养"。
- 当前里程 - 上次保养里程 >= 10000，或 距上次保养日期满 90 天 -> 到期。
- 到期车辆生成/挂起一条待处理预约（Scheduled），并被占用、不可调度。
- 维修人员提交里程/费用/完成时间后预约完工，按新里程重算下次预约，占用解除。
"""
from datetime import timedelta
from fleet_app.services.fleet_data import DAYS_INTERVAL, MILEAGE_INTERVAL

MILEAGE_REASON = 'mileage'
DATE_REASON = 'date'

REASON_TEXT = {
    MILEAGE_REASON: '距上次保养已超过10000公里',
    DATE_REASON: '距上次保养已满90天',
}

# 列表筛选分段：Due=到期（占用中） / Pending=待处理预约（未到期） / Completed=已完成
STAGE_DUE = 'Due'
STAGE_PENDING = 'Pending'
STAGE_COMPLETED = 'Completed'


def mileage_overdue(last_record, vehicle):
    return vehicle['mileage'] - last_record['mileage'] >= MILEAGE_INTERVAL


def days_overdue(last_record, today):
    return (today - last_record['date']).days >= DAYS_INTERVAL


def due_reasons(last_record, vehicle, today):
    """返回触发到期的原因码列表，未到期为空。"""
    reasons = []
    if mileage_overdue(last_record, vehicle):
        reasons.append(MILEAGE_REASON)
    if days_overdue(last_record, today):
        reasons.append(DATE_REASON)
    return reasons


def block_reason_text(reasons):
    return '保养到期，车辆已被占用，暂不可调度：' + '；'.join(
        REASON_TEXT[code] for code in reasons
    )


def record_stage(record, blocked):
    """记录所属筛选分段。

    Scheduled 记录按当前车辆是否被占用细分为 Due / Pending。
    """
    if record['status'] != 'Scheduled':
        return STAGE_COMPLETED
    return STAGE_DUE if blocked else STAGE_PENDING


def next_threshold(mileage, completed_at):
    """按完工里程与完工日期重算下次保养阈值。"""
    return mileage + MILEAGE_INTERVAL, completed_at + timedelta(days=DAYS_INTERVAL)
