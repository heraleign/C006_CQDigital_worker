import api from './api';

export const rootCauseApi = {
  // Knowledge base
  getKnowledge: (params?: any) => api.get('/root-cause/knowledge', { params }),
  createKnowledge: (data: any) => api.post('/root-cause/knowledge', data),
  updateKnowledge: (id: string, data: any) => api.put(`/root-cause/knowledge/${id}`, data),
  deleteKnowledge: (id: string) => api.delete(`/root-cause/knowledge/${id}`),
  getKnowledgeDetail: (id: string) => api.get(`/root-cause/knowledge/${id}`),

  // Analysis
  getAnalysis: (params?: any) => api.get('/root-cause/analysis', { params }),
  createAnalysis: (data: any) => api.post('/root-cause/analysis', data),
  getAnalysisDetail: (id: string, params?: any) => api.get(`/root-cause/analysis/${id}`, { params }),

  // Cases
  getCases: (params?: any) => api.get('/root-cause/cases', { params }),
  createCase: (data: any) => api.post('/root-cause/cases', data),
  updateCase: (id: string, data: any) => api.put(`/root-cause/cases/${id}`, data),
  deleteCase: (id: string) => api.delete(`/root-cause/cases/${id}`),

  // Suggestions
  getSuggestions: (params?: any) => api.get('/root-cause/suggestions', { params }),
  createSuggestion: (data: any) => api.post('/root-cause/suggestions', data),
  updateSuggestion: (id: string, data: any) => api.put(`/root-cause/suggestions/${id}`, data),
  adoptSuggestion: (id: string) => api.patch(`/root-cause/suggestions/${id}/adopt`),
  ignoreSuggestion: (id: string) => api.patch(`/root-cause/suggestions/${id}/ignore`),

  // Lineage
  getLineage: (params?: any) => api.get('/root-cause/lineage', { params }),

  // Analysis paths
  getAnalysisPaths: (params?: any) => api.get('/root-cause/analysis-paths', { params }),

  // Task list
  getTaskList: (params?: any) => api.get('/root-cause/task-list', { params }),
};
