import { create } from 'zustand';
import { WebSocketManager } from '../services/ws';
import { api } from '../services/api';
import { WS_BASE } from '../services/api';

export type DemoStage = {
    stage_num: number;
    name: string;
    narration: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    actions: any[];
}

interface DemoState {
  status: string;
  activeScenarioId: string | null;
  currentStage: number;
  activeNarration: string | null;
  connect: () => void;
  disconnect: () => void;
  startDemo: (scenarioId: string) => Promise<void>;
  nextStage: () => Promise<void>;
  pauseDemo: () => Promise<void>;
  resetDemo: () => Promise<void>;
}

let wsDemo: WebSocketManager | null = null;

export const useDemoStore = create<DemoState>((set) => ({
  status: 'IDLE',
  activeScenarioId: null,
  currentStage: 0,
  activeNarration: null,

  connect: () => {
    if (!wsDemo) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      wsDemo = new WebSocketManager(`${WS_BASE}/ws/demo/`, (data: any) => {
        if (data.event === "ScenarioStageChanged") {
            set({
                status: 'PLAYING',
                activeScenarioId: data.scenario_id,
                currentStage: data.stage_num,
                activeNarration: data.narration
            });
        } else if (data.event === "DemoCompleted") {
            set({ status: 'COMPLETED', activeNarration: "Demo completed successfully." });
        }
      });
      wsDemo.connect();
    }
  },

  disconnect: () => {
    wsDemo?.disconnect();
    wsDemo = null;
  },

  startDemo: async (scenarioId: string) => {
    try {
      await api.post('/demo/start', { scenario_id: scenarioId });
    } catch (err) {
      console.error('[Demo] Failed to start:', err);
    }
  },

  nextStage: async () => {
    try {
      await api.post('/demo/next', {});
    } catch (err) {
      console.error('[Demo] Failed to advance:', err);
    }
  },

  pauseDemo: async () => {
    try {
      await api.post('/demo/pause', {});
      set({ status: 'PAUSED' });
    } catch (err) {
      console.error('[Demo] Failed to pause:', err);
    }
  },

  resetDemo: async () => {
    try {
      await api.post('/demo/reset', {});
      set({ status: 'IDLE', activeScenarioId: null, currentStage: 0, activeNarration: null });
    } catch (err) {
      console.error('[Demo] Failed to reset:', err);
    }
  }
}));
