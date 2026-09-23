import { Tag } from 'antd';

const STATUS_META: Record<string, { color: string; label: string }> = {
  Available: { color: 'green', label: '可用' },
  OnTrip: { color: 'blue', label: '运输中' },
  Maintenance: { color: 'orange', label: '维保中' },
  Retired: { color: 'default', label: '已报废' },
  Pending: { color: 'default', label: '待处理' },
  Assigned: { color: 'blue', label: '已指派' },
  InProgress: { color: 'orange', label: '进行中' },
  Completed: { color: 'green', label: '已完成' },
  Cancelled: { color: 'default', label: '已取消' },
  Scheduled: { color: 'gold', label: '已预约' }
};

export function StatusBadge({ status }: { status: string }) {
  const meta = STATUS_META[status];
  if (meta) return <Tag color={meta.color}>{meta.label}</Tag>;
  const color = status.includes('Available') || status.includes('Completed')
    ? 'green'
    : status.includes('Maintenance') || status.includes('InProgress')
      ? 'orange'
      : 'blue';
  return <Tag color={color}>{status}</Tag>;
}
