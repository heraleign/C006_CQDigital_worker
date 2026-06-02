import api from './api';

export const monthlyApi = {
  // Progress
  getProgress: (params?: any) => api.get('/monthly/progress', { params }),

  // Milestones
  getMilestones: (params?: any) => api.get('/monthly/milestones', { params }),
  updateMilestone: (id: string, data: any) => api.put(`/monthly/milestones/${id}`, data),

  // Running tasks
  getRunningTasks: (params?: any) => api.get('/monthly/running-tasks', { params }),

  // Tasks
  getTasks: (params?: any) => api.get('/monthly/tasks', { params }),
  createTask: (data: any) => api.post('/monthly/tasks', data),
  updateTask: (id: string, data: any) => api.put(`/monthly/tasks/${id}`, data),
  deleteTask: (id: string) => api.delete(`/monthly/tasks/${id}`),

  // Orchestration
  getOrchestration: (params?: any) => api.get('/monthly/orchestration', { params }),
  saveOrchestration: (data: any) => api.post('/monthly/orchestration', data),

  // Daily reports
  getDailyReports: (params?: any) => api.get('/monthly/daily-report', { params }),
  getDailyReportDetail: (id: string) => api.get(`/monthly/daily-report/${id}`),
  updateDailyReport: (id: string, data: any) => api.put(`/monthly/daily-report/${id}`, data),

  // Published reports
  getReports: (params?: any) => api.get('/monthly/reports', { params }),
  publishReport: (id: string, data?: any) => api.post(`/monthly/reports/${id}/publish`, data),
  scheduleReport: (data: any) => api.post('/monthly/reports/schedule', data),

  // Ledger Display (四级层次展示)
  getLedgerOverview: () => api.get('/monthly/ledger/overview'),

  // Config - Stages
  getStages: (params?: any) => api.get('/config/stages', { params }),
  createStage: (data: any) => api.post('/config/stages', data),
  updateStage: (id: string, data: any) => api.put(`/config/stages/${id}`, data),
  deleteStage: (id: string) => api.delete(`/config/stages/${id}`),

  // Config - Milestones
  getMilestones: (params?: any) => api.get('/config/milestones', { params }),
  createMilestone: (data: any) => api.post('/config/milestones', data),
  updateMilestone: (id: string, data: any) => api.put(`/config/milestones/${id}`, data),
  deleteMilestone: (id: string) => api.delete(`/config/milestones/${id}`),

  // Config - Work Plans
  getWorkPlans: (params?: any) => api.get('/config/work-plans', { params }),
  createWorkPlan: (data: any) => api.post('/config/work-plans', data),
  updateWorkPlan: (id: string, data: any) => api.put(`/config/work-plans/${id}`, data),
  deleteWorkPlan: (id: string) => api.delete(`/config/work-plans/${id}`),

  // Config - Tasks
  getTasks: (params?: any) => api.get('/config/tasks', { params }),
  createTask: (data: any) => api.post('/config/tasks', data),
  updateTask: (id: string, data: any) => api.put(`/config/tasks/${id}`, data),
  deleteTask: (id: string) => api.delete(`/config/tasks/${id}`),

  // Template parse
  parseTemplate: (data: { template: string }) => api.post('/config/parse-template', data),

  // Billing Progress
  getBillingCycles: () => api.get('/monthly/billing-progress/cycles'),
  getBillingGantt: (cycleId?: string) => api.get('/monthly/billing-progress/gantt', { params: { cycle_id: cycleId || '202605' } }),
  getBillingTasks: (cycleId?: string, page?: number, pageSize?: number) =>
    api.get('/monthly/billing-progress/tasks', { params: { cycle_id: cycleId || '202605', page: page || 1, page_size: pageSize || 500 } }),
  createBillingTask: (data: any) => api.post('/monthly/billing-progress/tasks', data),
  updateBillingTask: (taskId: number, data: any) => api.put(`/monthly/billing-progress/tasks/${taskId}`, data),
  deleteBillingTask: (taskId: number) => api.delete(`/monthly/billing-progress/tasks/${taskId}`),
  updateBillingTaskStatus: (taskId: number, status: string, actualEnd?: string) =>
    api.put(`/monthly/billing-progress/tasks/${taskId}/status`, { status, actual_end: actualEnd }),
  generateBillingBrief: (cycleId?: string) => api.post('/monthly/billing-progress/brief', { cycle_id: cycleId || '202605' }),
  importBillingTasks: (cycleId: string, tasks: any[]) =>
    api.post('/monthly/billing-progress/import', { cycle_id: cycleId, tasks }),
};
