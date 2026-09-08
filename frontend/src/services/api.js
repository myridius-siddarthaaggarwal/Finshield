import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach token if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('finshield_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  getUsers: () => api.get('/auth/users'),
  login: (email, password) => api.post('/auth/login', { email, password }),
  switchPersona: (userId) => api.post('/auth/switch-persona', { user_id: userId }),
};

export const casesApi = {
  getCases: (params) => api.get('/cases', { params }),
  getCaseDetail: (id) => api.get(`/cases/${id}`),
  createCase: (data) => api.post('/cases', data),
};

export const assessmentApi = {
  overrideDimension: (caseId, payload) => api.post(`/ai-assessment/${caseId}/override`, payload),
  simulateWhatIf: (caseId, payload) => api.post(`/ai-assessment/${caseId}/simulate-what-if`, payload),
  escalate: (caseId, payload) => api.post(`/ai-assessment/${caseId}/escalate`, payload),
  chatCopilot: (caseId, message) => api.post(`/ai-assessment/${caseId}/chat`, { case_id: caseId, message }),
};

export const committeeApi = {
  castVote: (caseId, payload) => api.post(`/committee/${caseId}/vote`, payload),
  finalizeDecision: (caseId, payload) => api.post(`/committee/${caseId}/finalize`, payload),
};

export const auditApi = {
  getAuditEvents: (caseId) => api.get('/audit', { params: { case_id: caseId } }),
};

export const evaluationApi = {
  getTokenTelemetry: (caseId) => api.get('/evaluation/tokens', { params: { case_id: caseId } }),
  getJudgementMatrix: () => api.get('/evaluation/judgement-matrix'),
  getBenchmarks: () => api.get('/evaluation/benchmarks'),
  getBeforeAfter: () => api.get('/evaluation/before-after'),
};

export const dataLayerApi = {
  getGeographyRisk: () => api.get('/data-layer/geography-risk'),
  getRegulatoryFrameworks: () => api.get('/data-layer/regulatory-frameworks'),
  getControlLibrary: () => api.get('/data-layer/control-library'),
  getRiskTaxonomies: () => api.get('/data-layer/risk-taxonomies'),
};

export default api;
