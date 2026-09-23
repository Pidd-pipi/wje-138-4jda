import { request } from '../utils/request';
import { apiPaths } from '../constants/apiPaths';
import type { MaintenanceBlock, MaintenanceRecord } from '../types';
import { MaintenanceStage } from '../types';

export type MaintenanceCompletePayload = {
  mileage: number;
  cost?: number;
  vendor?: string;
  completedAt?: string;
  maintenanceType?: string;
  items?: string[];
};

export const maintenanceApi = {
  list: (stage?: MaintenanceStage) => {
    const query = stage ? `?stage=${stage}` : '';
    return request<MaintenanceRecord[]>(`${apiPaths.maintenance}${query}`);
  },
  blocks: () => request<MaintenanceBlock[]>(apiPaths.maintenanceBlocks),
  complete: (id: number, payload: MaintenanceCompletePayload) =>
    request<MaintenanceRecord>(apiPaths.maintenanceComplete(id), {
      method: 'POST',
      body: JSON.stringify(payload)
    })
};
