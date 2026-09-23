import { request } from '../utils/request';
import { apiPaths } from '../constants/apiPaths';
import type { DispatchOrder } from '../types';

export type DispatchCreatePayload = Omit<DispatchOrder, 'id' | 'orderNo' | 'status'> & {
  status?: DispatchOrder['status'];
};

export const dispatchApi = {
  list: (status?: string) =>
    request<DispatchOrder[]>(
      status && status !== 'all' ? `${apiPaths.dispatch}?status=${status}` : apiPaths.dispatch
    ),
  create: (payload: Partial<DispatchCreatePayload>) =>
    request<DispatchOrder>(apiPaths.dispatch, { method: 'POST', body: JSON.stringify(payload) })
};
