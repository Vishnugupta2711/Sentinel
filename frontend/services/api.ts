const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || 'ws://127.0.0.1:8000/api/v1';

export { WS_BASE };

export const api = {
  get: async (endpoint: string) => {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
    return res.json();
  },
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  post: async (endpoint: string, body: any) => {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
    return res.json();
  }
};

export const queries = {
  worldState: () => api.get('/world_state/snapshot'),
  hazardGraph: () => api.get('/graph/latest'),
  complianceStatus: () => api.get('/compliance/status'),
  complianceViolations: () => api.get('/compliance/violations'),
  plannerLatest: () => api.get('/planner/latest'),
  riskLatest: () => api.get('/risk/latest'),
  chronosLatest: () => api.get('/chronos/latest'),
  visionEvents: () => api.get('/vision/events')
};
