import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Modal,
  Segmented,
  Space,
  Table,
  Tag,
  message
} from 'antd';
import { maintenanceApi, type MaintenanceCompletePayload } from '../api/maintenance';
import type { MaintenanceBlock, MaintenanceRecord } from '../types';
import { MaintenanceStage } from '../types';
import { CalendarCell } from '../components/common/CalendarCell';
import { StatusBadge } from '../components/common/StatusBadge';
import { EmptyState } from '../components/common/EmptyState';
import { PageShell } from './PageShell';

const STAGE_LABEL: Record<MaintenanceStage, string> = {
  [MaintenanceStage.Due]: '到期',
  [MaintenanceStage.Pending]: '待处理',
  [MaintenanceStage.Completed]: '已完成'
};

const TYPE_LABEL: Record<string, string> = {
  Routine: '常规保养',
  Repair: '维修',
  Emergency: '紧急维修',
  Inspection: '年检检查'
};

export function MaintenanceManage() {
  const [stage, setStage] = useState<MaintenanceStage>(MaintenanceStage.Due);
  const [records, setRecords] = useState<MaintenanceRecord[]>([]);
  const [blocks, setBlocks] = useState<MaintenanceBlock[]>([]);
  const [completing, setCompleting] = useState<MaintenanceRecord | null>(null);
  const [form] = Form.useForm<MaintenanceCompletePayload>();
  const [submitting, setSubmitting] = useState(false);

  const load = (nextStage = stage) => {
    maintenanceApi.list(nextStage).then(setRecords).catch(() => setRecords([]));
    maintenanceApi.blocks().then(setBlocks).catch(() => setBlocks([]));
  };

  useEffect(() => { load(stage); }, [stage]);

  const openRecords = useMemo(
    () => records.filter((r) => r.stage !== MaintenanceStage.Completed),
    [records]
  );
  const blockedList = useMemo(() => blocks.filter((b) => b.blocked), [blocks]);

  const submitComplete = async () => {
    const values = await form.validateFields();
    if (!completing) return;
    setSubmitting(true);
    try {
      await maintenanceApi.complete(completing.id, {
        ...values,
        completedAt: values.completedAt ? new Date(values.completedAt).toISOString() : undefined
      } as MaintenanceCompletePayload);
      message.success(`车辆 ${completing.plateNo} 保养已完工，占用解除`);
      setCompleting(null);
      form.resetFields();
      load();
    } catch (error) {
      message.error((error as Error).message || '提交失败');
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    { title: '车辆', dataIndex: 'plateNo' },
    { title: '类型', render: (_: unknown, r: MaintenanceRecord) => TYPE_LABEL[r.type] ?? r.type },
    {
      title: '上次保养',
      render: (_: unknown, r: MaintenanceRecord) =>
        r.stage === MaintenanceStage.Completed
          ? `${r.date} · ${r.mileage.toLocaleString()} km`
          : '尚未完成'
    },
    {
      title: '已行驶 / 间隔',
      render: (_: unknown, r: MaintenanceRecord) => (
        <Space direction="vertical" size={0}>
          <span>已行驶 {r.mileageDiff.toLocaleString()} km（阈值 10,000 km）</span>
          <span>当前里程 {r.currentMileage.toLocaleString()} km</span>
        </Space>
      )
    },
    { title: '维修厂', dataIndex: 'vendor', render: (v: string) => v || '—' },
    {
      title: '费用',
      dataIndex: 'cost',
      render: (cost: number) => (cost > 0 ? `¥${cost.toLocaleString()}` : '—')
    },
    {
      title: '下次保养',
      render: (_: unknown, r: MaintenanceRecord) =>
        `${r.nextMileage.toLocaleString()} km / ${r.nextDate || '—'}`
    },
    {
      title: '状态',
      render: (_: unknown, r: MaintenanceRecord) => (
        <StatusBadge status={r.stage} label={STAGE_LABEL[r.stage as MaintenanceStage]} />
      )
    },
    {
      title: '操作',
      render: (_: unknown, r: MaintenanceRecord) =>
        r.stage !== MaintenanceStage.Completed ? (
          <Button type="link" onClick={() => { setCompleting(r); form.setFieldsValue({ mileage: r.currentMileage, cost: undefined, vendor: r.vendor || undefined }); }}>
            完工提交
          </Button>
        ) : null
    }
  ];

  return (
    <PageShell title="维保管理">
      {blockedList.length > 0 && (
        <Alert
          style={{ marginBottom: 16 }}
          type="error"
          showIcon
          message={`${blockedList.length} 辆车保养到期，已被占用、不可调度`}
          description={
            <ul style={{ marginBottom: 0, paddingLeft: 18 }}>
              {blockedList.map((b) => (
                <li key={b.vehicleId}><b>{b.plateNo}</b>：{b.reason}</li>
              ))}
            </ul>
          }
        />
      )}

      <Card title="保养预约日历" style={{ marginBottom: 16 }}>
        {openRecords.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="grid grid-3">
            {openRecords.map((r) => (
              <CalendarCell
                key={r.id}
                date={r.nextDate || '—'}
                title={`${r.plateNo} · ${TYPE_LABEL[r.type] ?? r.type}（${r.nextMileage.toLocaleString()} km）`}
                due={r.stage === MaintenanceStage.Due}
              />
            ))}
          </div>
        )}
      </Card>

      <Card
        title="维保记录"
        extra={
          <Segmented
            value={stage}
            onChange={(value) => setStage(value as MaintenanceStage)}
            options={[
              { label: '到期', value: MaintenanceStage.Due },
              { label: '待处理', value: MaintenanceStage.Pending },
              { label: '已完成', value: MaintenanceStage.Completed }
            ]}
          />
        }
      >
        {stage === MaintenanceStage.Due && records.some((r) => r.reason) && (
          <Alert
            style={{ marginBottom: 12 }}
            type="warning"
            showIcon
            message="以下车辆为什么不能排班"
            description={
              <ul style={{ marginBottom: 0, paddingLeft: 18 }}>
                {records.filter((r) => r.reason).map((r) => (
                  <li key={r.id}><Tag color="red">{r.plateNo}</Tag>{r.reason}</li>
                ))}
              </ul>
            }
          />
        )}
        {records.length === 0 ? (
          <EmptyState />
        ) : (
          <Table rowKey="id" dataSource={records} columns={columns} pagination={false} />
        )}
      </Card>

      <Modal
        title={completing ? `完工提交 · ${completing.plateNo}` : '完工提交'}
        open={completing !== null}
        onCancel={() => { setCompleting(null); form.resetFields(); }}
        onOk={submitComplete}
        confirmLoading={submitting}
        okText="提交并解除占用"
        cancelText="取消"
      >
        {completing?.reason && <Alert type="warning" showIcon style={{ marginBottom: 12 }} message={completing.reason} />}
        <Form form={form} layout="vertical">
          <Form.Item
            name="mileage"
            label="完工时里程（km）"
            rules={[{ required: true, message: '请输入本次保养完成时的车辆里程' }]}
          >
            <InputNumber style={{ width: '100%' }} min={1} precision={0} placeholder="维修后里程读数" />
          </Form.Item>
          <Form.Item name="cost" label="维修费用（元）" rules={[{ required: true, message: '请输入维修费用' }]}>
            <InputNumber style={{ width: '100%' }} min={0} precision={2} placeholder="如 2100" />
          </Form.Item>
          <Form.Item name="vendor" label="维修厂">
            <Input placeholder="如 青浦维保站" />
          </Form.Item>
          <Form.Item
            name="completedAt"
            label="完成时间"
            rules={[{ required: true, message: '请选择完成时间' }]}
          >
            <Input type="datetime-local" />
          </Form.Item>
        </Form>
      </Modal>
    </PageShell>
  );
}
