import api from './api';

export const assistantApi = {
  sendMessage: (data: { session_id?: string; message: string }) => api.post('/assistant/chat', data),
  getSessions: (params?: any) => api.get('/assistant/sessions', { params }),
  getMessages: (params?: any) => api.get('/assistant/chat', { params }),
  createSession: (data?: any) => api.post('/assistant/sessions', data),
  deleteSession: (id: string) => api.delete(`/assistant/sessions/${id}`),
};
