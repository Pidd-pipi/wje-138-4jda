import { useEffect, useState } from 'react';
import { Alert, Button, Card, Form, Input, InputNumber, Modal, Select, Table, Tag, message } from 'antd';
import { dispatchApi } from '../api/dispatch';
import { driverApi } from '../api/driver';
import { vehicleApi } from '../api/vehicle';
import type { DispatchOrder, Driver, Vehicle } from '../types';
import { StatusBadge } from '../components/common/StatusBadge';
import { Timeline } from '../components/common/Timeline';
import { PageShell } from './PageShell';

type CreateForm = {
  vehicleId: number;
  driverId?: number;
  origin: string;
  destination: string;
  planDepartAt: string;
  planArriveAt?: string;
  cargo: string;
  weight?: number;
  freight?: number;
};

export function DispatchCenter() {
  const [orders, setOrders] = useState<DispatchOrder[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [open, setOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm<CreateForm>();
  const selectedVehicleId = Form.useWatch('vehicleId', form);
  const selectedVehicle = vehicles.find((v) => v.id === selectedVehicleId);

  const load = () => {
    dispatchApi.list().then(setOrders).catch(() => setOrders([]));
    vehicleApi.list<Vehicle>().then(setVehicles).catch(() => setVehicles([]));
    driverApi.list<Driver>().then(setDrivers).catch(() => setDrivers([]));
  };

  useEffect(() => { load(); }, []);

  const submit = async () => {
    const values = await form.validateFields();
    setSubmitting(true);
    try {
      // 保养到期车辆后端会拒绝并说明原因，调度单不会保存
      await dispatchApi.create({
        ...values,
        planDepartAt: values.planDepartAt ? values.planDepartAt.replace('T', ' ') : undefined,
        planArriveAt: values.planArriveAt ? values.planArriveAt.replace('T', ' ') : undefined
      });
      message.success('调度单已创建');
      setOpen(false);
      form.resetFields();
      load();
    } catch (error) {
      message.error((error as Error).message || '创建调度单失败');
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    { title: '单号', dataIndex: 'orderNo' },
    {
      title: '车辆',
      render: (_: unknown, r: DispatchOrder) => {
        const vehicle = vehicles.find((v) => v.id === r.vehicleId);
        return (
          <span>
            {vehicle?.plateNo ?? r.vehicleId}
            {vehicle?.maintenanceBlocked && <Tag color="red" style={{ marginLeft: 6 }}>保养到期</Tag>}
          </span>
        );
      }
    },
    { title: '司机', render: (_: unknown, r: DispatchOrder) => drivers.find((d) => d.id === r.driverId)?.name ?? r.driverId },
    { title: '路线', render: (_: unknown, r: DispatchOrder) => `${r.origin} → ${r.destination}` },
    { title: '状态', render: (_: unknown, r: DispatchOrder) => <StatusBadge status={r.status} /> }
  ];

  return (
    <PageShell title="调度中心">
      <div className="grid grid-2">
        <Card
          title="调度单"
          extra={<Button type="primary" onClick={() => setOpen(true)}>创建调度单</Button>}
        >
          <Table rowKey="id" dataSource={orders} columns={columns} pagination={false} />
        </Card>
        <Card title="运输时间线">
          <Timeline items={['创建调度单', '指派车辆与司机', '开始运输', '完成运输']} />
        </Card>
      </div>

      <Modal
        title="创建调度单"
        open={open}
        onCancel={() => { setOpen(false); form.resetFields(); }}
        onOk={submit}
        confirmLoading={submitting}
        okText="保存调度单"
        cancelText="取消"
      >
        {selectedVehicle?.maintenanceBlocked && (
          <Alert
            style={{ marginBottom: 12 }}
            type="error"
            showIcon
            message={`车辆 ${selectedVehicle.plateNo} 不能调度`}
            description={selectedVehicle.maintenanceReason}
          />
        )}
        <Form form={form} layout="vertical">
          <Form.Item
            name="vehicleId"
            label="车辆"
            rules={[{ required: true, message: '请选择车辆' }]}
          >
            <Select
              placeholder="选择车辆"
              options={vehicles.map((v) => ({
                value: v.id,
                disabled: v.maintenanceBlocked,
                label: `${v.plateNo} · ${v.brandModel}${v.maintenanceBlocked ? `（不可调度：${v.maintenanceReason}）` : ''}`
              }))}
            />
          </Form.Item>
          <Form.Item name="driverId" label="司机">
            <Select
              allowClear
              placeholder="选择司机"
              options={drivers.map((d) => ({
                value: d.id,
                label: `${d.name} · ${d.status}`,
                disabled: d.status !== 'Available'
              }))}
            />
          </Form.Item>
          <Form.Item name="origin" label="出发地" rules={[{ required: true, message: '请输入出发地' }]}>
            <Input placeholder="如 上海青浦仓" />
          </Form.Item>
          <Form.Item name="destination" label="目的地" rules={[{ required: true, message: '请输入目的地' }]}>
            <Input placeholder="如 杭州萧山仓" />
          </Form.Item>
          <Form.Item name="planDepartAt" label="计划出发时间" rules={[{ required: true, message: '请选择计划出发时间' }]}>
            <Input type="datetime-local" />
          </Form.Item>
          <Form.Item name="planArriveAt" label="计划到达时间">
            <Input type="datetime-local" />
          </Form.Item>
          <Form.Item name="cargo" label="货物描述">
            <Input placeholder="如 冷链食品" />
          </Form.Item>
          <Form.Item name="weight" label="重量（kg）">
            <InputNumber style={{ width: '100%' }} min={0} precision={0} />
          </Form.Item>
          <Form.Item name="freight" label="运费（元）">
            <InputNumber style={{ width: '100%' }} min={0} precision={2} />
          </Form.Item>
        </Form>
      </Modal>
    </PageShell>
  );
}
