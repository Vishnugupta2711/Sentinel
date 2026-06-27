'use client';
import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useJudgeStore, DEMO_STEPS } from '../../store/judgeStore';
import { Info } from 'lucide-react';

interface ExplanationData {
  what: string;
  why: string;
  detail?: string;
  severity?: 'info' | 'warning' | 'critical' | 'success';
}

const EXPLANATIONS: Record<number, ExplanationData> = {
  2: {
    what: 'Gas Leak Detected',
    why: 'Sensor anomaly in Sector 4',
    detail: 'IoT Stream ID-44 — CH₄ concentration: 2.3% LEL → 8.7% LEL over 9 minutes',
    severity: 'warning',
  },
  3: {
    what: 'Trajectory Mapped',
    why: 'Gas expansion overlaps worker route',
    detail: 'Chronos forecaster: 91% explosion probability in T+5min at ignition source coordinates',
    severity: 'critical',
  },
  4: {
    what: 'Compound Risk Triggered',
    why: 'Hot Work Permit active in expansion zone',
    detail: 'Risk Score 94/100 — 3 simultaneous threat vectors identified across separate data streams',
    severity: 'critical',
  },
  5: {
    what: 'Optimal Counterfactual Found',
    why: '14 interventions simulated in 14ms',
    detail: 'Evacuate Sector 4 only — avoids injury without full shutdown. Score delta: +62 vs no action',
    severity: 'info',
  },
  6: {
    what: 'Incident Prevented',
    why: 'Worker cleared zone 90s before ignition',
    detail: 'World State nominal. All sensor readings returning to baseline. Zero injuries recorded.',
    severity: 'success',
  },
};

const SEVERITY_STYLES = {
  info:     { border: 'border-blue-500/30',    accent: 'text-blue-400',    bg: 'bg-blue-500/5'    },
  warning:  { border: 'border-amber-500/30',   accent: 'text-amber-400',   bg: 'bg-amber-500/5'   },
  critical: { border: 'border-red-500/30',     accent: 'text-red-400',     bg: 'bg-red-500/5'     },
  success:  { border: 'border-emerald-500/30', accent: 'text-emerald-400', bg: 'bg-emerald-500/5' },
};

export const AIExplanationPanel: React.FC = () => {
  const tourStep = useJudgeStore((s) => s.tourStep);

  const data = EXPLANATIONS[tourStep];
  if (!data) return null;

  const style = SEVERITY_STYLES[data.severity ?? 'info'];

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={tourStep}
        initial={{ opacity: 0, x: 24 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 24 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className={`absolute top-1/2 right-6 -translate-y-1/2 w-72 bg-black/80 backdrop-blur-xl border rounded-2xl p-5 shadow-2xl z-50 pointer-events-none ${style.border} ${style.bg}`}
      >
        {/* Header */}
        <div className="flex items-start gap-2 mb-4 pb-3 border-b border-white/5">
          <Info className={`w-4 h-4 shrink-0 mt-0.5 ${style.accent}`} />
          <div>
            <h3 className={`text-sm font-bold leading-snug ${style.accent}`}>{data.what}</h3>
            <p className="text-xs text-slate-400 mt-0.5">{data.why}</p>
          </div>
        </div>

        {/* Detail */}
        {data.detail && (
          <p className="text-xs text-slate-300 leading-relaxed">
            {data.detail}
          </p>
        )}

        {/* Step label */}
        <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between">
          <span className="text-[9px] text-slate-600 uppercase tracking-widest">
            {DEMO_STEPS[tourStep - 1]?.chapter}
          </span>
          <span className={`text-[9px] font-bold uppercase tracking-widest ${style.accent}`}>
            {data.severity}
          </span>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
