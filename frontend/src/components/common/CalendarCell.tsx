import { Badge, Card } from 'antd';
export function CalendarCell({ date, title, due }: { date: string; title: string; due?: boolean }) {
  return (
    <Card size="small" style={due ? { borderColor: '#ff4d4f', boxShadow: '0 0 0 1px #ff4d4f' } : undefined}>
      <Badge status={due ? 'error' : 'processing'} text={due ? `${date}（已到期）` : date} />
      <div>{title}</div>
    </Card>
  );
}
