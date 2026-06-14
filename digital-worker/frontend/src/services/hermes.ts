import api from './api';

export const hermesApi = {
  /** Simple chat with Hermes Agent (for the playground demo). */
  chat: (data: { message: string; system_prompt?: string }) =>
    api.post('/hermes/chat', data, { timeout: 60000 }),

  /** Root cause analysis via Hermes Agent (5 min timeout). */
  analyzeRootCause: (data: {
    task_id: string;
    problem_description?: string;
    acct_month?: string;
  }) => api.post('/hermes/analyze-root-cause', data, { timeout: 300000 }),

  /** Check Hermes Agent connectivity. */
  health: () => api.get('/hermes/health', { timeout: 10000 }),
};
