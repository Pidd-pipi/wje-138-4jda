import { VehicleStatus } from './enums';
export type Vehicle = { id: number; plateNo: string; type: string; brandModel: string; purchaseDate: string; insuranceExpireDate: string; inspectionExpireDate: string; status: VehicleStatus; mileage: number; tankCapacity: number; fuelConsumption: number;
  /** 是否因保养到期被占用、不可排班 */
  maintenanceBlocked: boolean;
  /** 不能排班的具体原因 */
  maintenanceReason: string;
  maintenanceReasonCodes: string[];
};
