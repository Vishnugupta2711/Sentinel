import { create } from 'zustand';
import { WebSocketManager, WSStatus } from '../services/ws';
import { WS_BASE } from '../services/api';

export type VisionEvent = { event_id: string; event_type: string; severity: string; description: string; timestamp: string };
export type ComplianceViolation = { violation_id: string; severity: string; description: string; timestamp: string };
export type PlannerRecommendation = { plan_id: string; scenario_name: string; score: number };
export type RiskAssessment = { risk_id: string; risk_type: string; severity: string; risk_score: number };
export type ChronosPrediction = { prediction_id: string; horizon_minutes: number };
export type CorrelationAssessment = { risk_id: string; level: string; score: number; primary_zone: string; description: string; recommendations: string[]; timestamp: string };
export type Alert = { alert_id: string; title: string; description: string; priority: string; status: string; source_agent: string; score: number; zone_id: string; timestamp: string };
export type RAGResult = { query: string; documents: { title: string; section: string; content: string; relevance_score: number }[]; incidents: { incident: { title: string; severity: string; root_cause: string }; relevance_score: number }[] };

interface IntelligenceState {
  visionEvents: VisionEvent[];
  complianceViolations: ComplianceViolation[];
  plannerRecommendations: PlannerRecommendation[];
  riskAssessments: RiskAssessment[];
  chronosPredictions: ChronosPrediction[];
  correlationAssessments: CorrelationAssessment[];
  alerts: Alert[];
  ragResults: RAGResult[];
  connectionStatus: WSStatus;
}

interface IntelligenceStore extends IntelligenceState {
  connect: () => void;
  disconnect: () => void;
}

let wsVision: WebSocketManager | null = null;
let wsCompliance: WebSocketManager | null = null;
let wsPlanner: WebSocketManager | null = null;
let wsRisk: WebSocketManager | null = null;
let wsChronos: WebSocketManager | null = null;
let wsCorrelation: WebSocketManager | null = null;
let wsAlerts: WebSocketManager | null = null;
let wsRAG: WebSocketManager | null = null;

export const useIntelligenceStore = create<IntelligenceStore>((set) => ({
  visionEvents: [],
  complianceViolations: [],
  plannerRecommendations: [],
  riskAssessments: [],
  chronosPredictions: [],
  correlationAssessments: [],
  alerts: [],
  ragResults: [],
  connectionStatus: 'disconnected',

  connect: () => {
    const statusHandler = (status: WSStatus) => set({ connectionStatus: status });

    if (!wsVision) {
      wsVision = new WebSocketManager(`${WS_BASE}/ws/vision/`, (data) => {
        set((state) => ({ visionEvents: [data, ...state.visionEvents].slice(0, 50) }));
      }, statusHandler);
      wsVision.connect();
    }
    if (!wsCompliance) {
      wsCompliance = new WebSocketManager(`${WS_BASE}/ws/compliance/`, (data) => {
        if (data.event === "VIOLATION_DETECTED" && data.violation) {
          set((state) => ({ complianceViolations: [data.violation, ...state.complianceViolations].slice(0, 50) }));
        }
      });
      wsCompliance.connect();
    }
    if (!wsPlanner) {
      wsPlanner = new WebSocketManager(`${WS_BASE}/ws/planner/`, (data) => {
        if (data.event === "NEW_RECOMMENDATION" && data.plan) {
           set((state) => ({ plannerRecommendations: [data.plan, ...state.plannerRecommendations].slice(0, 10) }));
        }
      });
      wsPlanner.connect();
    }
    if (!wsRisk) {
      wsRisk = new WebSocketManager(`${WS_BASE}/ws/risk/`, (data) => {
        if (data.event === "NEW_RISK_DETECTED" && data.risk) {
          set((state) => ({ riskAssessments: [data.risk, ...state.riskAssessments].slice(0, 20) }));
        }
      });
      wsRisk.connect();
    }
    if (!wsChronos) {
        wsChronos = new WebSocketManager(`${WS_BASE}/ws/chronos/`, (data) => {
            set((state) => ({ chronosPredictions: [data, ...state.chronosPredictions].slice(0, 10) }));
        });
        wsChronos.connect();
    }
    if (!wsCorrelation) {
      wsCorrelation = new WebSocketManager(`${WS_BASE}/ws/correlation/`, (data) => {
        if (data.event === "CORRELATION_UPDATED" && data.result) {
          const assessments = (data.result.assessments || []).map((a: { risk_id?: string; correlation_id?: string; [key: string]: unknown }) => ({
            risk_id: a.risk_id || a.correlation_id || '',
            level: a.level || 'NONE',
            score: a.score || 0,
            primary_zone: a.primary_zone || '',
            description: a.description || '',
            recommendations: a.recommendations || [],
            timestamp: a.timestamp || new Date().toISOString(),
          }));
          set((state) => ({ correlationAssessments: [...assessments, ...state.correlationAssessments].slice(0, 20) }));
        }
      });
      wsCorrelation.connect();
    }
    if (!wsAlerts) {
      wsAlerts = new WebSocketManager(`${WS_BASE}/ws/alerts/`, (data) => {
        if (data.event === "NEW_ALERT" && data.alert) {
          set((state) => ({ alerts: [data.alert, ...state.alerts].slice(0, 30) }));
        }
      });
      wsAlerts.connect();
    }
    if (!wsRAG) {
      wsRAG = new WebSocketManager(`${WS_BASE}/ws/rag/`, (data) => {
        if (data.event === "RAG_RETRIEVED" && data.result) {
          set((state) => ({ ragResults: [data.result, ...state.ragResults].slice(0, 10) }));
        }
      });
      wsRAG.connect();
    }
  },

  disconnect: () => {
    wsVision?.disconnect(); wsVision = null;
    wsCompliance?.disconnect(); wsCompliance = null;
    wsPlanner?.disconnect(); wsPlanner = null;
    wsRisk?.disconnect(); wsRisk = null;
    wsChronos?.disconnect(); wsChronos = null;
    wsCorrelation?.disconnect(); wsCorrelation = null;
    wsAlerts?.disconnect(); wsAlerts = null;
    wsRAG?.disconnect(); wsRAG = null;
  }
}));
