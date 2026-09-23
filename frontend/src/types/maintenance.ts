import { MaintenanceStage, MaintenanceType } from './enums';
export type MaintenanceRecord = {
  id: number;
  vehicleId: number;
  plateNo: string;
  type: MaintenanceType;
  items: string[];
  cost: number;
  vendor: string;
  date: string;
  /** 本次保养完工时的里程读数 */
  mileage: number;
  nextMileage: number;
  nextDate: string;
  status: 'Scheduled' | 'InProgress' | 'Completed';
  /** 筛选分段：到期 / 待处理 / 已完成 */
  stage: MaintenanceStage;
  /** 距上次保养已行驶里程 */
  mileageDiff: number;
  currentMileage: number;
  /** 到期占用原因（仅 Due 记录有值） */
  reason: string;
};

export type MaintenanceBlock = {
  vehicleId: number;
  plateNo: string;
  blocked: boolean;
  reasonCodes: string[];
  reason: string;
};
