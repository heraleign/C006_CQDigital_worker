import api from './api';

export const dashboardApi = {
  getSummary: (params?: any) => api.get('/dashboard/summary', { params }),
  getTrends: (params?: any) => api.get('/dashboard/trends', { params }),
  getRecentAlerts: (params?: any) => api.get('/dashboard/recent-alerts', { params }),
};
