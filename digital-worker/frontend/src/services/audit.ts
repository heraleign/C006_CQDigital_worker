import api from './api';

export const auditApi = {
  getFields: (params?: any) => api.get('/audit/fields', { params }),
  createField: (data: any) => api.post('/audit/fields', data),
  updateField: (id: string, data: any) => api.put(`/audit/fields/${id}`, data),
  deleteField: (id: string) => api.delete(`/audit/fields/${id}`),

  getDatasources: () => api.get('/audit/datasources'),
  getSchemas: (ds: string) => api.get('/audit/schemas', { params: { datasource_code: ds } }),
  getTables: (ds: string, schema: string) => api.get('/audit/tables', { params: { datasource_code: ds, schema_code: schema } }),
  getFieldsByTable: (ds: string, schema: string, table: string) =>
    api.get('/audit/fields-by-table', { params: { datasource_code: ds, schema_code: schema, table_code: table } }),

  generateRules: (data: any) => api.post('/audit/rules/ai-generate', data),
  getGenerateStatus: (id: string) => api.get(`/audit/rules/ai-generate/${id}/status`),

  confirmRule: (ruleId: string, data?: any) => api.put(`/audit/rules/${ruleId}/confirm`, data),
  rejectRule: (ruleId: string) => api.put(`/audit/rules/${ruleId}/reject`),
  batchConfirmRules: (ids: string[]) => api.post('/audit/rules/batch-confirm', { rule_ids: ids }),

  getRules: (params?: any) => api.get('/audit/rules', { params }),
  createRule: (data: any) => api.post('/audit/rules', data),
  updateRule: (id: string, data: any) => api.put(`/audit/rules/${id}`, data),
  deleteRule: (id: string) => api.delete(`/audit/rules/${id}`),

  getTasks: (params?: any) => api.get('/audit/tasks', { params }),
  createTask: (data: any) => api.post('/audit/tasks', data),
  executeTask: (id: string) => api.post(`/audit/tasks/${id}/execute`),
  deleteTask: (id: string) => api.delete(`/audit/tasks/${id}`),

  getAlerts: (params?: any) => api.get('/audit/alerts', { params }),
  handleAlert: (id: string, data: any) => api.put(`/audit/alerts/${id}/handle`, data),

  getResultStats: (params?: any) => api.get('/audit/results/statistics', { params }),
  getResultTrend: (params?: any) => api.get('/audit/results/trend', { params }),
  getResultDistribution: (params?: any) => api.get('/audit/results/distribution', { params }),
  getResultDetails: (params?: any) => api.get('/audit/results/details', { params }),

  getReports: (params?: any) => api.get('/audit/reports', { params }),
  generateReport: (data: any) => api.post('/audit/reports/generate', data),

  getImportanceConfigs: (params?: any) => api.get('/audit/importance-configs', { params }),
  createImportanceConfig: (data: any) => api.post('/audit/importance-configs', data),
  updateImportanceConfig: (id: string, data: any) => api.put(`/audit/importance-configs/${id}`, data),

  getUpgradeRules: (params?: any) => api.get('/audit/upgrade-rules', { params }),
  createUpgradeRule: (data: any) => api.post('/audit/upgrade-rules', data),
  updateUpgradeRule: (id: string, data: any) => api.put(`/audit/upgrade-rules/${id}`, data),
  deleteUpgradeRule: (id: string) => api.delete(`/audit/upgrade-rules/${id}`),
};
