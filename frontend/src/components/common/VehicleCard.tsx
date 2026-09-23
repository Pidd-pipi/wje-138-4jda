import { Alert, Card } from 'antd';
import type { Vehicle } from '../../types';
import { StatusBadge } from './StatusBadge';

export function VehicleCard({ vehicle }: { vehicle: Vehicle }) {
  return (
    <Card
      size="small"
      title={vehicle.plateNo}
      extra={<StatusBadge status={vehicle.maintenanceBlocked ? 'Blocked' : vehicle.status} label={vehicle.maintenanceBlocked ? '保养到期' : vehicle.status} />}
    >
      <p>{vehicle.brandModel}</p>
      <p>{vehicle.mileage.toLocaleString()} km</p>
      {vehicle.maintenanceBlocked && (
        <Alert type="error" showIcon message="暂不可排班" description={vehicle.maintenanceReason} />
      )}
    </Card>
  );
}
