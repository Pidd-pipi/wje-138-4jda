export const apiPaths = {
  vehicles: '/api/vehicles/',
  vehicleDispatchCheck: (id: number) => `/api/vehicles/${id}/dispatch-check/`,
  drivers: '/api/drivers/',
  dispatch: '/api/dispatch-orders/',
  maintenance: '/api/maintenance-records/',
  maintenanceStart: (id: number) => `/api/maintenance-records/${id}/start/`,
  maintenanceComplete: (id: number) => `/api/maintenance-records/${id}/complete/`,
  fuel: '/api/fuel-records/'
} as const;
