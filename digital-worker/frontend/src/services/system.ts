import api from './api';

export const systemApi = {
  // Tools
  getTools: (params?: any) => api.get('/settings/tools', { params }),
  createTool: (data: any) => api.post('/settings/tools', data),
  updateTool: (id: string, data: any) => api.put(`/settings/tools/${id}`, data),
  deleteTool: (id: string) => api.delete(`/settings/tools/${id}`),

  // Prompts
  getPrompts: (params?: any) => api.get('/settings/prompts', { params }),
  createPrompt: (data: any) => api.post('/settings/prompts', data),
  updatePrompt: (id: string, data: any) => api.put(`/settings/prompts/${id}`, data),
  deletePrompt: (id: string) => api.delete(`/settings/prompts/${id}`),

  // Users
  getUsers: (params?: any) => api.get('/settings/users', { params }),
  createUser: (data: any) => api.post('/settings/users', data),
  updateUser: (id: string, data: any) => api.put(`/settings/users/${id}`, data),
  deleteUser: (id: string) => api.delete(`/settings/users/${id}`),

  // Notifications
  getNotifications: (params?: any) => api.get('/settings/notifications', { params }),
  updateNotification: (id: string, data: any) => api.put(`/settings/notifications/${id}`, data),
};
