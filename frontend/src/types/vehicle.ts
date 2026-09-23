import { VehicleStatus } from './enums';

export type MaintenanceDueReason = 'MileageDue' | 'DateDue' | 'MileageAndDateDue';

export type Vehicle = {
  id: number;
  plateNo: string;
  type: string;
  brandModel: string;
  purchaseDate: string;
  insuranceExpireDate: string;
  inspectionExpireDate: string;
  status: VehicleStatus;
  mileage: number;
  tankCapacity: number;
  fuelConsumption: number;
  /** 保养到期或维修中导致被占用，不能调度 */
  maintenanceBlocked: boolean;
  /** 已越过 1 万公里 / 90 天门槛 */
  maintenanceDue: boolean;
  blockReason: string;
  lastMaintenanceMileage: number | null;
  lastMaintenanceDate: string | null;
  openMaintenanceRecordId: number | null;
};

export type DispatchCheck = {
  vehicleId: number;
  plateNo: string;
  dispatchable: boolean;
  reasonCode?: MaintenanceDueReason | null;
  reasons?: MaintenanceDueReason[];
  message: string;
  maintenanceRecordId?: number | null;
};
