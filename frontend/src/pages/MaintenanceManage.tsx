import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Button,
  Card,
  Col,
  Radio,
  Row,
  Space,
  Statistic,
  Table,
  Tag,
  message
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { PageShell } from './PageShell';
import { EmptyState } from '../components/common/EmptyState';
import { StatusBadge } from '../components/common/StatusBadge';
import { CompleteMaintenanceModal } from '../components/maintenance/CompleteMaintenanceModal';
import { useMaintenanceStore } from '../stores/maintenanceStore';
import type { MaintenanceDueReason, MaintenanceFilter, MaintenanceRecord } from '../types';

const FILTER_OPTIONS: { value: MaintenanceFilter; label: string }[] = [
  { value: 'due', label: '到期占用' },
  { value: 'pending', label: '待处理预约' },
  { value: 'completed', label: '已完成' },
  { value: 'all', label: '全部' }
];

const REASON_LABELS: Record<MaintenanceDueReason, string> = {
  MileageDue: '里程超 10,000 km',
  DateDue: '距上次保养满 90 天',
  MileageAndDateDue: '里程与日期双到期'
};

export function MaintenanceManage() {
  const { records, filter, loading, load, setFilter, start } = useMaintenanceStore();
  const [current, setCurrent] = useState<MaintenanceRecord | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    load('due').catch(() => undefined);
  }, [load]);

  const totalCost = useMemo(
    () => records.reduce((sum, record) => sum + (record.cost || 0), 0),
    [records]
  );
  const blockedCount = useMemo(
    () => records.filter((record) => record.due || record.status === 'InProgress').length,
    [records]
  );

  const handleStart = async (record: MaintenanceRecord) => {
    try {
      await start(record.id);
      message.success(`已开工：${record.plateNo}`);
    } catch (error) {
      message.error(error instanceof Error ? error.message : '开工失败');
    }
  };

  const openComplete = (record: MaintenanceRecord) => {
    setCurrent(record);
    setModalOpen(true);
  };

  const columns: ColumnsType<MaintenanceRecord> = [
    { title: '车牌号', dataIndex: 'plateNo', width: 110 },
    {
      title: '类型 / 项目',
      render: (_, record) => (
        <Space size={4} wrap>
          <Tag>{record.type}</Tag>
          <span>{record.items.join('、') || '—'}</span>
        </Space>
      )
    },
    { title: '保养日期', dataIndex: 'date', width: 115 },
    {
      title: '保养里程',
      dataIndex: 'mileage',
      width: 110,
      render: (value: number) => `${(value || 0).toLocaleString()} km`
    },
    {
      title: '下次保养',
      width: 180,
      render: (_, record) =>
        record.nextMileage || record.nextDate
          ? `${record.nextMileage ? `${record.nextMileage.toLocaleString()} km` : '—'} / ${record.nextDate ?? '—'}`
          : '—'
    },
    { title: '费用', dataIndex: 'cost', width: 100, render: (value: number) => `¥${value.toLocaleString()}` },
    {
      title: '状态',
      width: 100,
      render: (_, record) => (
        <Space size={4}>
          <StatusBadge status={record.status} />
          {record.source === 'Auto' && <Tag color="purple">系统生成</Tag>}
        </Space>
      )
    },
    {
      title: '不能排班的原因',
      render: (_, record) => {
        if (record.status === 'Completed') return <span style={{ color: '#999' }}>—</span>;
        if (record.status === 'InProgress') {
          return <Alert type="info" showIcon message="车辆正在维修保养中，暂不可调度" />;
        }
        if (record.due) {
          return (
            <Alert
              type="warning"
              showIcon
              message={
                <Space size={4} wrap>
                  {record.dueReasons.map((reason) => (
                    <Tag key={reason} color="red">
                      {REASON_LABELS[reason]}
                    </Tag>
                  ))}
                </Space>
              }
              description={record.blockReason}
              style={{ padding: '4px 10px' }}
            />
          );
        }
        return <span style={{ color: '#999' }}>未到期，可正常排班</span>;
      }
    },
    {
      title: '操作',
      width: 180,
      fixed: 'right',
      render: (_, record) =>
        record.status === 'Completed' ? (
          <span style={{ color: '#999' }}>已闭环</span>
        ) : (
          <Space>
            {record.status === 'Scheduled' && (
              <Button size="small" onClick={() => handleStart(record)}>
                开工
              </Button>
            )}
            <Button type="primary" size="small" onClick={() => openComplete(record)}>
              完工提交
            </Button>
          </Space>
        )
    }
  ];

  return (
    <PageShell title="维保管理">
      {filter === 'due' && blockedCount > 0 && (
        <Alert
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
          message={`当前有 ${blockedCount} 辆车保养到期或维修中，调度中心无法为其派单`}
        />
      )}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card>
            <Statistic title="当前视图占用车辆" value={blockedCount} suffix="辆" />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="当前视图费用合计" value={totalCost} precision={0} prefix="¥" />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="保养规则" value="10,000 km / 90 天" />
          </Card>
        </Col>
      </Row>
      <Card
        title="保养记录"
        extra={
          <Radio.Group
            value={filter}
            onChange={(event) => load(event.target.value as MaintenanceFilter)}
            optionType="button"
            buttonStyle="solid"
            options={FILTER_OPTIONS}
          />
        }
      >
        <Table
          rowKey="id"
          loading={loading}
          dataSource={records}
          columns={columns}
          scroll={{ x: 1100 }}
          pagination={{ pageSize: 10 }}
          locale={{ emptyText: <EmptyState /> }}
        />
      </Card>
      <CompleteMaintenanceModal
        record={current}
        open={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </PageShell>
  );
}
