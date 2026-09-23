import { create } from 'zustand';
import type {
  MaintenanceCompletePayload,
  MaintenanceFilter,
  MaintenanceRecord
} from '../types';
import { maintenanceApi } from '../api/maintenance';

type MaintenanceState = {
  records: MaintenanceRecord[];
  filter: MaintenanceFilter;
  loading: boolean;
  setRecords: (records: MaintenanceRecord[]) => void;
  setFilter: (filter: MaintenanceFilter) => void;
  load: (filter?: MaintenanceFilter, vehicleId?: number) => Promise<void>;
  start: (id: number) => Promise<MaintenanceRecord>;
  complete: (id: number, payload: MaintenanceCompletePayload) => Promise<unknown>;
};

export const useMaintenanceStore = create<MaintenanceState>((set, get) => ({
  records: [],
  filter: 'due',
  loading: false,
  setRecords: (records) => set({ records }),
  setFilter: (filter) => set({ filter }),
  load: async (filter, vehicleId) => {
    const nextFilter = filter ?? get().filter;
    set({ loading: true });
    try {
      const records = await maintenanceApi.list(nextFilter, vehicleId);
      set({ records, filter: nextFilter });
    } finally {
      set({ loading: false });
    }
  },
  start: async (id) => {
    const record = await maintenanceApi.start(id);
    await get().load();
    return record;
  },
  complete: async (id, payload) => {
    const result = await maintenanceApi.complete(id, payload);
    await get().load();
    return result;
  }
}));
