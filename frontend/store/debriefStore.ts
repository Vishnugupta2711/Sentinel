import { create } from 'zustand';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type ReportData = any;

interface DebriefState {
  isDebriefOpen: boolean;
  setDebriefOpen: (open: boolean) => void;
  report: ReportData | null;
  setReport: (report: ReportData | null) => void;
  progress: number;
  stage: string;
  setProgress: (p: number, s: string) => void;
}

export const useDebriefStore = create<DebriefState>((set) => ({
  isDebriefOpen: false,
  setDebriefOpen: (open) => set({ isDebriefOpen: open }),
  report: null,
  setReport: (report) => set({ report }),
  progress: 0,
  stage: '',
  setProgress: (progress, stage) => set({ progress, stage }),
}));
