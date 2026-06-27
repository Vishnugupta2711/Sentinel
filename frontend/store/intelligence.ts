import { create } from 'zustand';
import { WebSocketManager, WSStatus } from '../services/ws';
import { WS_BASE } from '../services/api';

export type VisionEvent = { event_id: string; event_type: string; severity: string; description: string; timestamp: string };
export type ComplianceViolation = { violation_id: string; severity: string; description: string; timestamp: string };
export type PlannerRecommendation = { plan_id: string; scenario_name: string; score: number };
export type RiskAssessment = { risk_id: string; risk_type: string; severity: string; risk_score: number };
export type ChronosPrediction = { prediction_id: string; horizon_minutes: number };

interface IntelligenceState {
  visionEvents: VisionEvent[];
  complianceViolations: ComplianceViolation[];
  plannerRecommendations: PlannerRecommendation[];
  riskAssessments: RiskAssessment[];
  chronosPredictions: ChronosPrediction[];
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

export const useIntelligenceStore = create<IntelligenceStore>((set) => ({
  visionEvents: [],
  complianceViolations: [],
  plannerRecommendations: [],
  riskAssessments: [],
  chronosPredictions: [],
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
        // Backend sends "NEW_RECOMMENDATION" event, not "PLAN_GENERATED"
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
  },

  disconnect: () => {
    wsVision?.disconnect(); wsVision = null;
    wsCompliance?.disconnect(); wsCompliance = null;
    wsPlanner?.disconnect(); wsPlanner = null;
    wsRisk?.disconnect(); wsRisk = null;
    wsChronos?.disconnect(); wsChronos = null;
  }
}));
