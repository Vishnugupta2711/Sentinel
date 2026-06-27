'use client';
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useJudgeStore } from '../../store/judgeStore';
import { BrainCircuit } from 'lucide-react';

interface Metric {
  label: string;
  value: number; // 0–100
  displayValue: string;
  color: string;
  trackColor: string;
}

const STEP_METRICS: Record<number, Metric[]> = {
  3: [
    { label: 'Explosion Probability', value: 91, displayValue: '91%', color: '#ef4444', trackColor: 'rgba(239,68,68,0.15)' },
    { label: 'Prediction Confidence', value: 88, displayValue: '88%', color: '#3b82f6', trackColor: 'rgba(59,130,246,0.15)' },
    { label: 'Evidence Strength',     value: 100, displayValue: '100%', color: '#10b981', trackColor: 'rgba(16,185,129,0.15)' },
  ],
  4: [
    { label: 'Compound Risk Score',   value: 94, displayValue: '94 / 100', color: '#ef4444', trackColor: 'rgba(239,68,68,0.15)' },
    { label: 'Hot Work Overlap',      value: 100, displayValue: 'ACTIVE', color: '#f59e0b', trackColor: 'rgba(245,158,11,0.15)' },
    { label: 'Worker Exposure Risk',  value: 87, displayValue: '87%', color: '#ef4444', trackColor: 'rgba(239,68,68,0.15)' },
  ],
  5: [
    { label: 'Plan Confidence',       value: 96, displayValue: '96%', color: '#a855f7', trackColor: 'rgba(168,85,247,0.15)' },
    { label: 'Interventions Simulated', value: 100, displayValue: '14', color: '#8b5cf6', trackColor: 'rgba(139,92,246,0.15)' },
    { label: 'Outcome: Safe Op.',     value: 100, displayValue: '✓', color: '#10b981', trackColor: 'rgba(16,185,129,0.15)' },
  ],
};

const Bar: React.FC<{ metric: Metric }> = ({ metric }) => {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between items-center">
        <span className="text-xs text-slate-400">{metric.label}</span>
        <span className="text-xs font-bold" style={{ color: metric.color }}>{metric.displayValue}</span>
      </div>
      <div className="h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: metric.trackColor }}>
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: metric.color }}
          initial={{ width: '0%' }}
          animate={{ width: `${metric.value}%` }}
          transition={{ duration: 1.2, ease: 'easeOut', delay: 0.3 }}
        />
      </div>
    </div>
  );
};

export const ConfidenceVisualization: React.FC = () => {
  const tourStep = useJudgeStore((s) => s.tourStep);
  const metrics  = STEP_METRICS[tourStep];

  return (
    <AnimatePresence mode="wait">
      {metrics && (
        <motion.div
          key={tourStep}
          initial={{ opacity: 0, x: 24 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 24 }}
          transition={{ duration: 0.4 }}
          className="absolute bottom-32 right-6 w-64 bg-black/75 backdrop-blur-xl border border-white/10 rounded-xl p-4 shadow-2xl z-50 pointer-events-none"
        >
          <div className="flex items-center gap-2 mb-4 pb-2 border-b border-white/5">
            <BrainCircuit className="w-4 h-4 text-blue-400 shrink-0" />
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest">AI Confidence</h3>
          </div>
          <div className="flex flex-col gap-4">
            {metrics.map((m) => <Bar key={m.label} metric={m} />)}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
