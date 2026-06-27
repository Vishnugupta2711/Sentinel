import { create } from 'zustand';

export interface StepMeta {
  num: number;
  chapter: string;
  headline: string;
  subHeadline: string;
  durationSeconds: number;
  accentColor: 'cyan' | 'amber' | 'red' | 'purple' | 'emerald';
}

export const DEMO_STEPS: StepMeta[] = [
  {
    num: 1,
    chapter: 'Platform Overview',
    headline: 'The Living Digital Twin',
    subHeadline: 'Ingesting 14 live camera feeds, 200+ IoT sensors, and 40 worker telemetry streams — in real time.',
    durationSeconds: 8,
    accentColor: 'cyan',
  },
  {
    num: 2,
    chapter: 'Anomaly Detected',
    headline: 'Gas Concentration Rising — Sector 4',
    subHeadline: 'IoT Sensor ID-44 detected a methane concentration increase over 9 minutes. Traditional SCADA would have flagged this 4 minutes later.',
    durationSeconds: 8,
    accentColor: 'amber',
  },
  {
    num: 3,
    chapter: 'AI Prediction',
    headline: '91% Explosion Probability in 5 Minutes',
    subHeadline: 'Chronos forecasting engine mapped gas cloud trajectory against worker positions. No human analyst could process this in time.',
    durationSeconds: 9,
    accentColor: 'red',
  },
  {
    num: 4,
    chapter: 'Compound Risk',
    headline: 'Risk Score: 94 — Critical',
    subHeadline: 'An active Hot Work Permit in the gas expansion zone compounded the risk. The AI connected dots across 3 separate data streams simultaneously.',
    durationSeconds: 9,
    accentColor: 'red',
  },
  {
    num: 5,
    chapter: 'AI Recommendation',
    headline: 'Counterfactual: Evacuate Sector 4',
    subHeadline: 'After simulating 14 interventions in 14ms, the optimal action was identified — targeted evacuation without full plant shutdown.',
    durationSeconds: 10,
    accentColor: 'purple',
  },
  {
    num: 6,
    chapter: 'Incident Prevented',
    headline: 'Zero Injuries. $2.4M Saved.',
    subHeadline: 'Worker safely evacuated 90 seconds before gas reached ignition source. Plant remained operational. Sentinel made the right call — faster than any human.',
    durationSeconds: 12,
    accentColor: 'emerald',
  },
];

export interface JudgeState {
  isJudgeMode: boolean;
  tourStep: number;
  isAutoPlay: boolean;
  storyEvents: string[];

  toggleJudgeMode: () => void;
  nextStep: () => void;
  prevStep: () => void;
  goToStep: (step: number) => void;
  resetDemo: () => void;
  toggleAutoPlay: () => void;
  addStoryEvent: (event: string) => void;
  clearStoryEvents: () => void;
}

export const useJudgeStore = create<JudgeState>((set) => ({
  isJudgeMode: false,
  tourStep: 1,
  isAutoPlay: false,
  storyEvents: [],

  toggleJudgeMode: () => set((state) => ({ isJudgeMode: !state.isJudgeMode, tourStep: 1, isAutoPlay: false })),

  nextStep: () => set((state) => ({
    tourStep: Math.min(state.tourStep + 1, DEMO_STEPS.length),
  })),

  prevStep: () => set((state) => ({
    tourStep: Math.max(state.tourStep - 1, 1),
  })),

  goToStep: (step: number) => set(() => ({
    tourStep: Math.max(1, Math.min(step, DEMO_STEPS.length)),
    isAutoPlay: false,
  })),

  resetDemo: () => set(() => ({
    tourStep: 1,
    isAutoPlay: false,
    storyEvents: [],
  })),

  toggleAutoPlay: () => set((state) => ({ isAutoPlay: !state.isAutoPlay })),

  addStoryEvent: (event) => set((state) => {
    const newEvents = [...state.storyEvents, event];
    if (newEvents.length > 5) newEvents.shift();
    return { storyEvents: newEvents };
  }),

  clearStoryEvents: () => set({ storyEvents: [] }),
}));
