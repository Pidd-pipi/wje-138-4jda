import { create } from 'zustand';
import type { Vehicle } from '../types';

type VehicleState = {
  vehicles: Vehicle[];
  setVehicles: (vehicles: Vehicle[]) => void;
  getById: (id: number | null | undefined) => Vehicle | undefined;
};

export const useVehicleStore = create<VehicleState>((set, get) => ({
  vehicles: [],
  setVehicles: (vehicles) => set({ vehicles }),
  getById: (id) => get().vehicles.find((v) => v.id === id)
}));
