import { MaintenanceType } from './enums';
import type { MaintenanceDueReason } from './vehicle';

export type MaintenanceStatus = 'Scheduled' | 'InProgress' | 'Completed';
export type MaintenanceSource = 'Auto' | 'Manual';
/** 页面筛选视图：due=到期占用中，pending=待处理（未到期预约），completed=已完成 */
export type MaintenanceFilter = 'due' | 'pending' | 'completed' | 'all';

export type MaintenanceRecord = {
  id: number;
  vehicleId: number;
  plateNo: string;
  type: MaintenanceType;
  items: string[];
  cost: number;
  vendor: string;
  date: string;
  mileage: number;
  nextMileage: number;
  nextDate: string;
  status: MaintenanceStatus;
  source: MaintenanceSource;
  completedAt: string | null;
  due: boolean;
  dueReasons: MaintenanceDueReason[];
  blockReason: string;
};

export type MaintenanceCompletePayload = {
  mileage: number;
  cost: number;
  completedAt: string;
  vendor?: string;
  items?: string[];
  maintenanceType?: MaintenanceType;
};

export type MaintenanceCreatePayload = {
  vehicleId: number;
  type: MaintenanceType;
  items: string[];
  cost: number;
  vendor: string;
  date?: string | null;
  mileage?: number;
  nextMileage?: number;
  nextDate?: string | null;
};
