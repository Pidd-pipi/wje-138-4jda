import { Alert, Card } from 'antd';
import type { Vehicle } from '../../types';
import { StatusBadge } from './StatusBadge';

export function VehicleCard({ vehicle }: { vehicle: Vehicle }) {
  return (
    <Card
      size="small"
      title={vehicle.plateNo}
      extra={<StatusBadge status={vehicle.status} />}
    >
      <p style={{ marginBottom: 4 }}>{vehicle.brandModel}</p>
      <p style={{ marginBottom: vehicle.maintenanceBlocked ? 12 : 0 }}>
        {vehicle.mileage.toLocaleString()} km
      </p>
      {vehicle.maintenanceBlocked && (
        <Alert
          type="warning"
          showIcon
          message="保养占用，禁止排班"
          description={vehicle.blockReason}
          style={{ padding: '6px 10px' }}
        />
      )}
    </Card>
  );
}
