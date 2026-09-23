"""保养到期规则：里程超 1 万公里或距上次保养满 90 天即到期。

仅承载纯规则计算，不读写数据库，供 maintenance_service 与 dispatch_service 复用。
"""
from datetime import date, timedelta

MAINTENANCE_MILEAGE_INTERVAL = 10000
MAINTENANCE_DAYS_INTERVAL = 90

REASON_MILEAGE = 'MileageDue'
REASON_DATE = 'DateDue'
REASON_BOTH = 'MileageAndDateDue'


def evaluate_due(*, current_mileage, last_mileage, today, last_date):
    """返回 (是否到期, 原因列表)。从未保养（last_date 为空）时不判定到期。"""
    reasons = []
    if last_mileage is not None and current_mileage - last_mileage > MAINTENANCE_MILEAGE_INTERVAL:
        reasons.append(REASON_MILEAGE)
    if last_date is not None:
        if isinstance(last_date, date):
            days_elapsed = (today - last_date).days
        else:
            days_elapsed = (today - date.fromisoformat(str(last_date))).days
        if days_elapsed >= MAINTENANCE_DAYS_INTERVAL:
            reasons.append(REASON_DATE)
    due = bool(reasons)
    code = REASON_BOTH if len(reasons) == 2 else (reasons[0] if reasons else None)
    return due, code, reasons


def describe_reason(code, *, current_mileage=0, last_mileage=0, today=None, last_date=None):
    """将到期原因码翻译为调度中心可直接展示的中文说明。"""
    messages = []
    if code in (REASON_MILEAGE, REASON_BOTH):
        messages.append(
            f'距上次保养已行驶 {current_mileage - last_mileage} 公里，'
            f'超过 {MAINTENANCE_MILEAGE_INTERVAL} 公里保养间隔'
        )
    if code in (REASON_DATE, REASON_BOTH) and last_date is not None:
        if isinstance(last_date, date):
            iso_date = last_date.isoformat()
            days_elapsed = (today - last_date).days if today else None
        else:
            iso_date = str(last_date)
            days_elapsed = (today - date.fromisoformat(iso_date)).days if today else None
        messages.append(
            f'上次保养日期 {iso_date}，距今已满 {days_elapsed} 天'
            f'（{MAINTENANCE_DAYS_INTERVAL} 天到期）'
        )
    return '；'.join(messages)


def next_due_point(mileage, completed_on):
    """维修人员提交完成信息后，按新里程重算下次预约。"""
    return {
        'next_mileage': mileage + MAINTENANCE_MILEAGE_INTERVAL,
        'next_date': completed_on + timedelta(days=MAINTENANCE_DAYS_INTERVAL),
    }
