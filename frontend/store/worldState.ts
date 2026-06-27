import { create } from 'zustand';
import { WebSocketManager, WSStatus } from '../services/ws';
import { WS_BASE } from '../services/api';

// Simplified Types based on backend schemas
export type Worker = { id: string; name: string; role: string; zone_id: string; status: string; current_ppe: string[] };
export type Zone = { id: string; name: string; hazard_level: string };
export type Sensor = { id: string; name: string; type: string; current_value: number; status: string; zone_id: string };
export type Hazard = { id: string; type: string; severity: string; zone_id: string };

interface WorldState {
  version: number;
  workers: Worker[];
  zones: Zone[];
  sensors: Sensor[];
  hazards: Hazard[];
  isLoaded: boolean;
  connectionStatus: WSStatus;
}

interface WorldStateStore extends WorldState {
  connect: () => void;
  disconnect: () => void;
}

let wsManager: WebSocketManager | null = null;

export const useWorldStateStore = create<WorldStateStore>((set) => ({
  version: 0,
  workers: [],
  zones: [],
  sensors: [],
  hazards: [],
  isLoaded: false,
  connectionStatus: 'disconnected',

  connect: () => {
    console.log("worldState connect called. wsManager is:", wsManager);
    if (wsManager) return;
    
    console.log("Creating new WebSocketManager for world state...");
    wsManager = new WebSocketManager(
      `${WS_BASE}/ws/world-state`,
      (data) => {
        set({
          version: data.version || 0,
          workers: data.workers || [],
          zones: data.zones || [],
          sensors: data.sensors || [],
          hazards: data.hazards || [],
          isLoaded: true,
        });
      },
      (status) => {
        set({ connectionStatus: status });
      }
    );
    
    wsManager.connect();
  },

  disconnect: () => {
    if (wsManager) {
      wsManager.disconnect();
      wsManager = null;
    }
  }
}));
