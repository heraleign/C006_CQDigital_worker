import api from './api';

export const hermesApi = {
  /** Simple chat with Hermes Agent (for the playground demo). */
  chat: (data: { message: string; system_prompt?: string }) =>
    api.post('/hermes/chat', data, { timeout: 60000 }),

  /** Submit root cause analysis to Hermes Agent (async, returns immediately). */
  analyzeRootCause: (data: {
    task_id: string;
    problem_description?: string;
    acct_month?: string;
  }) => api.post('/hermes/analyze-root-cause', data, { timeout: 15000 }),

  /** Poll analysis result by task_id. */
  getAnalysisStatus: (taskId: string) =>
    api.get(`/hermes/analysis/${taskId}`, { timeout: 10000 }),

  /** Execute a registered skill by code. */
  executeSkill: (data: { skill_code: string; params?: Record<string, any> }) =>
    api.post('/hermes/execute-skill', data, { timeout: 60000 }),

  /** Check Hermes Agent connectivity. */
  health: () => api.get('/hermes/health', { timeout: 10000 }),

  /** Get project definition with all skills as OpenAI function tools. */
  getProjectDefinition: () =>
    api.get('/hermes/project/definition', { timeout: 10000 }),

  /** Get all skills as OpenAI-compatible function tool definitions. */
  getProjectSkills: () =>
    api.get('/hermes/project/skills', { timeout: 10000 }),

  /** Register a single skill as a callable tool in Hermes Agent. */
  registerSkill: (data: { skill_code: string }) =>
    api.post('/hermes/register-skill', data, { timeout: 30000 }),

  /** Unregister a skill from Hermes Agent. */
  unregisterSkill: (data: { skill_code: string }) =>
    api.post('/hermes/unregister-skill', data, { timeout: 30000 }),
};
