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
  getLedgerOverview: (params?: { acct_month?: string }) => api.get('/monthly/ledger/overview', { params }),

  // Config - Stages
  getStages: (params?: any) => api.get('/monthly/config/stages', { params }),
  createStage: (data: any) => api.post('/monthly/config/stages', data),
  updateStage: (id: string, data: any) => api.put(`/monthly/config/stages/${id}`, data),
  deleteStage: (id: string) => api.delete(`/monthly/config/stages/${id}`),

  // Config - Milestones
  getConfigMilestones: (params?: any) => api.get('/monthly/config/milestones', { params }),
  createConfigMilestone: (data: any) => api.post('/monthly/config/milestones', data),
  updateConfigMilestone: (id: string, data: any) => api.put(`/monthly/config/milestones/${id}`, data),
  deleteConfigMilestone: (id: string) => api.delete(`/monthly/config/milestones/${id}`),

  // Config - Work Plans
  getConfigWorkPlans: (params?: any) => api.get('/monthly/config/work-plans', { params }),
  createConfigWorkPlan: (data: any) => api.post('/monthly/config/work-plans', data),
  updateConfigWorkPlan: (id: string, data: any) => api.put(`/monthly/config/work-plans/${id}`, data),
  deleteConfigWorkPlan: (id: string) => api.delete(`/monthly/config/work-plans/${id}`),

  // Config - Tasks
  getConfigTasks: (params?: any) => api.get('/monthly/config/tasks', { params }),
  createConfigTask: (data: any) => api.post('/monthly/config/tasks', data),
  updateConfigTask: (id: string, data: any) => api.put(`/monthly/config/tasks/${id}`, data),
  deleteConfigTask: (id: string) => api.delete(`/monthly/config/tasks/${id}`),

  // Template parse
  parseTemplate: (data: { template: string }) => api.post('/monthly/config/parse-template', data),

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
