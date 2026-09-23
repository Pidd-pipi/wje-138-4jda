import { Tag } from 'antd';
export function StatusBadge({ status, label }: { status: string; label?: string }) {
  const color = status.includes('Due') || status.includes('Blocked')
    ? 'red'
    : status.includes('Available') || status.includes('Completed')
      ? 'green'
      : status.includes('Maintenance') || status.includes('InProgress') || status.includes('Pending')
        ? 'orange'
        : 'blue';
  return <Tag color={color}>{label ?? status}</Tag>;
}
