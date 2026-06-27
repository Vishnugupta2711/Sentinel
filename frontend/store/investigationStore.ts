import { create } from 'zustand';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type ReportData = any;

interface InvestigationState {
  report: ReportData | null;
  setReport: (report: ReportData | null) => void;
  progress: number;
  stage: string;
  isInvestigating: boolean;
  startInvestigation: () => void;
  setProgress: (p: number, s: string) => void;
}

export const useInvestigationStore = create<InvestigationState>((set) => ({
  report: null,
  setReport: (report) => set({ report }),
  progress: 0,
  stage: '',
  isInvestigating: false,
  startInvestigation: () => set({ isInvestigating: true, progress: 0, stage: 'Initializing...', report: null }),
  setProgress: (progress, stage) => set({ progress, stage }),
}));
