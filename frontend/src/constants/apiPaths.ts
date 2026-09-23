export const apiPaths = {
  vehicles: '/api/vehicles/',
  drivers: '/api/drivers/',
  dispatch: '/api/dispatch-orders/',
  maintenance: '/api/maintenance-records/',
  maintenanceComplete: (id: number) => `/api/maintenance-records/${id}/complete/`,
  maintenanceBlocks: '/api/maintenance-blocks/',
  fuel: '/api/fuel-records/'
} as const;
