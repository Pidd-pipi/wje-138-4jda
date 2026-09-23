import { request } from '../utils/request';
import { apiPaths } from '../constants/apiPaths';
import type {
  MaintenanceCompletePayload,
  MaintenanceCreatePayload,
  MaintenanceFilter,
  MaintenanceRecord
} from '../types';

export const maintenanceApi = {
  list: (filter: MaintenanceFilter = 'all', vehicleId?: number) => {
    const params = new URLSearchParams();
    if (filter !== 'all') params.set('filter', filter);
    if (vehicleId) params.set('vehicleId', String(vehicleId));
    const query = params.toString();
    return request<MaintenanceRecord[]>(`${apiPaths.maintenance}${query ? `?${query}` : ''}`);
  },
  create: (payload: MaintenanceCreatePayload) =>
    request<MaintenanceRecord>(apiPaths.maintenance, {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  start: (id: number) =>
    request<MaintenanceRecord>(apiPaths.maintenanceStart(id), { method: 'POST' }),
  complete: (id: number, payload: MaintenanceCompletePayload) =>
    request<{ completed: MaintenanceRecord; nextAppointment: MaintenanceRecord }>(
      apiPaths.maintenanceComplete(id),
      { method: 'POST', body: JSON.stringify(payload) }
    )
};
