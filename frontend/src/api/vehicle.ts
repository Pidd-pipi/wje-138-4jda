import { request } from '../utils/request';
import { apiPaths } from '../constants/apiPaths';
import type { DispatchCheck, Vehicle } from '../types';

export const vehicleApi = {
  list: () => request<Vehicle[]>(apiPaths.vehicles),
  dispatchCheck: (id: number) =>
    request<DispatchCheck>(apiPaths.vehicleDispatchCheck(id))
};
