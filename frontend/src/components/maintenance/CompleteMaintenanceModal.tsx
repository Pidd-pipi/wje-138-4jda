import { Form, Input, InputNumber, Modal, Select, DatePicker, message } from 'antd';
import dayjs from 'dayjs';
import { useState } from 'react';
import { useMaintenanceStore } from '../../stores/maintenanceStore';
import type { MaintenanceRecord } from '../../types';

type FormValues = {
  mileage: number;
  cost: number;
  completedAt: dayjs.Dayjs;
  vendor?: string;
  items?: string[];
};

export function CompleteMaintenanceModal({
  record,
  open,
  onClose
}: {
  record: MaintenanceRecord | null;
  open: boolean;
  onClose: () => void;
}) {
  const [form] = Form.useForm<FormValues>();
  const [submitting, setSubmitting] = useState(false);
  const complete = useMaintenanceStore((s) => s.complete);

  const handleOk = async () => {
    const values = await form.validateFields();
    setSubmitting(true);
    try {
      if (!record) return;
      await complete(record.id, {
        mileage: values.mileage,
        cost: values.cost ?? 0,
        completedAt: values.completedAt.format('YYYY-MM-DDTHH:mm:ss'),
        vendor: values.vendor,
        items: values.items
      });
      message.success('保养已完成，车辆占用解除，下次预约已重算');
      form.resetFields();
      onClose();
    } catch (error) {
      const reason = error instanceof Error ? error.message : '提交失败';
      message.error(reason);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      title={record ? `完工提交 · ${record.plateNo}` : '完工提交'}
      open={open}
      onOk={handleOk}
      onCancel={onClose}
      confirmLoading={submitting}
      okText="提交并解除占用"
      cancelText="取消"
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          cost: record?.cost || 0,
          vendor: record?.vendor || '',
          items: record?.items || [],
          completedAt: dayjs()
        }}
      >
        <Form.Item
          name="mileage"
          label="完工里程（km）"
          rules={[{ required: true, message: '请输入维修完成时车辆里程' }]}
          extra="提交后按该里程重算下次保养（+10,000 公里），并同步车辆累计里程"
        >
          <InputNumber min={0} style={{ width: '100%' }} placeholder="例如 213000" />
        </Form.Item>
        <Form.Item name="cost" label="维修费用（元）">
          <InputNumber min={0} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item
          name="completedAt"
          label="完成时间"
          rules={[{ required: true, message: '请选择完成时间' }]}
        >
          <DatePicker showTime style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item name="vendor" label="维修厂">
          <Input placeholder="例如 青浦维保站" />
        </Form.Item>
        <Form.Item name="items" label="维修项目">
          <Select mode="tags" placeholder="输入项目后回车，如：机油、轮胎检查" />
        </Form.Item>
      </Form>
    </Modal>
  );
}
