import { useEffect, useState } from 'react';
import { Alert, Card, List, Tag } from 'antd';
import { vehicleApi } from '../api/vehicle';
import type { Vehicle } from '../types';
import { VehicleCard } from '../components/common/VehicleCard';
import { EmptyState } from '../components/common/EmptyState';
import { PageShell } from './PageShell';

export function VehicleManage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);

  useEffect(() => {
    vehicleApi.list().then(setVehicles).catch(() => setVehicles([]));
  }, []);

  const blockedVehicles = vehicles.filter((vehicle) => vehicle.maintenanceBlocked);

  return (
    <PageShell title="车辆管理">
      {blockedVehicles.length > 0 && (
        <Alert
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
          message={`${blockedVehicles.length} 辆车因保养到期/维修中被占用，不能排班`}
        />
      )}
      <div className="grid grid-3">
        {vehicles.map((vehicle) => (
          <VehicleCard vehicle={vehicle} key={vehicle.id} />
        ))}
      </div>
      {vehicles.length === 0 && <EmptyState />}
      <Card title="不可排班车辆说明" style={{ marginTop: 16 }}>
        <List
          dataSource={blockedVehicles}
          locale={{ emptyText: '没有车辆被保养占用' }}
          renderItem={(vehicle) => (
            <List.Item>
              <List.Item.Meta
                title={
                  <span>
                    {vehicle.plateNo} <Tag color="red">禁止排班</Tag>
                  </span>
                }
                description={vehicle.blockReason}
              />
            </List.Item>
          )}
        />
      </Card>
      <Card title="油耗趋势" style={{ marginTop: 16 }}>各车油耗趋势图预留，与油耗分析页使用同一数据。</Card>
    </PageShell>
  );
}
