import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Button,
  Card,
  Col,
  Form,
  Input,
  InputNumber,
  Row,
  Select,
  Space,
  Table,
  Tabs,
  Tag,
  message
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { dispatchApi } from '../api/dispatch';
import { driverApi } from '../api/driver';
import { vehicleApi } from '../api/vehicle';
import { StatusBadge } from '../components/common/StatusBadge';
import { Timeline } from '../components/common/Timeline';
import { PageShell } from './PageShell';
import { ApiError } from '../utils/request';
import type { DispatchOrder, Driver, Vehicle } from '../types';

type CreateFormValues = {
  vehicleId: number;
  driverId?: number;
  origin: string;
  destination: string;
  cargo?: string;
  weight?: number;
  freight?: number;
};

export function DispatchCenter() {
  const [orders, setOrders] = useState<DispatchOrder[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState<number>();
  const [orderStatus, setOrderStatus] = useState('all');
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm<CreateFormValues>();

  const loadOrders = (status = 'all') =>
    dispatchApi.list(status).then(setOrders).catch(() => setOrders([]));

  useEffect(() => {
    vehicleApi.list().then(setVehicles).catch(() => setVehicles([]));
    driverApi.list<Driver>().then(setDrivers).catch(() => setDrivers([]));
    loadOrders();
  }, []);

  const selectedVehicle = vehicles.find((v) => v.id === selectedVehicleId);
  const blockedVehicles = useMemo(
    () => vehicles.filter((v) => v.maintenanceBlocked),
    [vehicles]
  );

  const availableDrivers = drivers.filter((driver) => driver.status === 'Available');

  const handleCreate = async (values: CreateFormValues) => {
    // 保养占用车辆：选用时即说明原因，不向后端提交，调度单不保存
    const vehicle = vehicles.find((v) => v.id === values.vehicleId);
    if (vehicle?.maintenanceBlocked) {
      message.error({
        content: `调度单未保存：${vehicle.blockReason}`,
        duration: 6
      });
      return;
    }
    setSubmitting(true);
    try {
      await dispatchApi.create(values);
      message.success('调度单已保存');
      form.resetFields();
      setSelectedVehicleId(undefined);
      await loadOrders(orderStatus);
      vehicleApi.list().then(setVehicles).catch(() => undefined);
    } catch (error) {
      // 保养到期占用：后端返回 409 与原因，调度单不会保存
      if (error instanceof ApiError && error.code === 'VEHICLE_MAINTENANCE_BLOCKED') {
        message.error({ content: `调度单未保存：${error.message}`, duration: 6 });
      } else {
        message.error(error instanceof Error ? error.message : '创建调度单失败');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const orderColumns: ColumnsType<DispatchOrder> = [
    { title: '单号', dataIndex: 'orderNo', width: 180 },
    {
      title: '车辆',
      render: (_, order) => {
        const vehicle = vehicles.find((v) => v.id === order.vehicleId);
        return vehicle ? `${vehicle.plateNo} · ${vehicle.brandModel}` : `车辆#${order.vehicleId}`;
      }
    },
    {
      title: '司机',
      render: (_, order) => drivers.find((d) => d.id === order.driverId)?.name ?? '—'
    },
    { title: '路线', render: (_, r) => `${r.origin} → ${r.destination}` },
    { title: '货物', dataIndex: 'cargo' },
    {
      title: '状态',
      width: 110,
      render: (_, r) => <StatusBadge status={r.status} />
    }
  ];

  const blockedColumns: ColumnsType<Vehicle> = [
    { title: '车牌号', dataIndex: 'plateNo', width: 110 },
    { title: '车型', dataIndex: 'type', width: 90 },
    {
      title: '上次保养',
      width: 200,
      render: (_, v) =>
        v.lastMaintenanceDate
          ? `${v.lastMaintenanceDate} · ${(v.lastMaintenanceMileage ?? 0).toLocaleString()} km`
          : '暂无保养记录'
    },
    {
      title: '为什么不能排班',
      render: (_, v) => (
        <Alert
          type="error"
          showIcon
          message={v.maintenanceDue ? '保养到期，已生成待处理预约' : '车辆维修保养中'}
          description={v.blockReason}
          style={{ padding: '4px 10px' }}
        />
      )
    }
  ];

  return (
    <PageShell title="调度中心">
      {blockedVehicles.length > 0 && (
        <Alert
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
          message={`有 ${blockedVehicles.length} 辆车因保养到期/维修中被占用，不能派去跑长途`}
        />
      )}
      <Row gutter={16}>
        <Col span={10}>
          <Card title="创建调度单">
            <Form form={form} layout="vertical" onFinish={handleCreate}>
              <Form.Item
                name="vehicleId"
                label="车辆"
                rules={[{ required: true, message: '请选择车辆' }]}
                extra="带「保养占用」标记的车辆不能排班"
              >
                <Select
                  placeholder="选择车辆"
                  onChange={(value) => setSelectedVehicleId(value)}
                  options={vehicles.map((v) => ({
                    value: v.id,
                    label: `${v.plateNo} · ${v.brandModel}${v.maintenanceBlocked ? '（保养占用）' : v.status !== 'Available' ? `（${v.status}）` : ''}`,
                    disabled: v.status === 'Retired'
                  }))}
                />
              </Form.Item>
              {selectedVehicle?.maintenanceBlocked && (
                <Alert
                  type="error"
                  showIcon
                  style={{ marginBottom: 12 }}
                  message="该车辆当前不能调度，调度单不会保存"
                  description={
                    <Space direction="vertical" size={4}>
                      <span>{selectedVehicle.blockReason}</span>
                      <span>
                        上次保养：{selectedVehicle.lastMaintenanceDate ?? '无'} ·{' '}
                        {(selectedVehicle.lastMaintenanceMileage ?? 0).toLocaleString()} km，当前{' '}
                        {selectedVehicle.mileage.toLocaleString()} km
                      </span>
                      {selectedVehicle.openMaintenanceRecordId && (
                        <Tag color="red">
                          待处理维保预约 #{selectedVehicle.openMaintenanceRecordId}
                        </Tag>
                      )}
                    </Space>
                  }
                />
              )}
              <Form.Item
                name="driverId"
                label="司机"
                rules={[{ required: true, message: '请选择司机' }]}
              >
                <Select
                  placeholder="选择司机"
                  options={availableDrivers.map((d) => ({
                    value: d.id,
                    label: `${d.name} · ${d.licenseType}`
                  }))}
                />
              </Form.Item>
              <Space style={{ display: 'flex' }}>
                <Form.Item name="origin" label="出发地" rules={[{ required: true }]} style={{ flex: 1 }}>
                  <Input placeholder="上海青浦仓" />
                </Form.Item>
                <Form.Item name="destination" label="目的地" rules={[{ required: true }]} style={{ flex: 1 }}>
                  <Input placeholder="杭州萧山仓" />
                </Form.Item>
              </Space>
              <Form.Item name="cargo" label="货物描述">
                <Input placeholder="冷链食品" />
              </Form.Item>
              <Space style={{ display: 'flex' }}>
                <Form.Item name="weight" label="重量（kg）" style={{ flex: 1 }}>
                  <InputNumber min={0} style={{ width: '100%' }} />
                </Form.Item>
                <Form.Item name="freight" label="运费（元）" style={{ flex: 1 }}>
                  <InputNumber min={0} style={{ width: '100%' }} />
                </Form.Item>
              </Space>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={submitting}
                danger={!!selectedVehicle?.maintenanceBlocked}
              >
                {selectedVehicle?.maintenanceBlocked ? '保存调度单（车辆被占用，将被拒绝且不保存）' : '保存调度单'}
              </Button>
            </Form>
          </Card>
        </Col>
        <Col span={14}>
          <Card title="运输时间线" style={{ marginBottom: 16 }}>
            <Timeline items={['创建调度单', '指派车辆与司机', '开始运输', '完成运输']} />
          </Card>
          <Card title="不可排班车辆及原因" style={{ marginBottom: 16 }}>
            <Table
              rowKey="id"
              size="small"
              dataSource={blockedVehicles}
              columns={blockedColumns}
              pagination={false}
              locale={{ emptyText: '当前没有被保养占用的车辆' }}
            />
          </Card>
        </Col>
      </Row>
      <Card style={{ marginTop: 16 }}>
        <Tabs
          activeKey={orderStatus}
          onChange={(key) => {
            setOrderStatus(key);
            loadOrders(key);
          }}
          items={[
            { key: 'all', label: '全部' },
            { key: 'Pending', label: '待处理' },
            { key: 'Assigned', label: '已指派' },
            { key: 'InProgress', label: '进行中' },
            { key: 'Completed', label: '已完成' }
          ]}
        />
        <Table rowKey="id" dataSource={orders} columns={orderColumns} pagination={{ pageSize: 8 }} />
      </Card>
    </PageShell>
  );
}
