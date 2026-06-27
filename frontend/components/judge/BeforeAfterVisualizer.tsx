'use client';
import React from 'react';
import { motion } from 'framer-motion';
import { useJudgeStore } from '../../store/judgeStore';
import { AlertTriangle, CheckCircle2, ArrowRight } from 'lucide-react';

export const BeforeAfterVisualizer: React.FC = () => {
  const tourStep = useJudgeStore((s) => s.tourStep);
  if (tourStep !== 5) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: -32 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -32 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      className="absolute top-1/2 left-6 -translate-y-1/2 w-80 bg-black/80 backdrop-blur-xl border border-white/10 rounded-2xl p-5 shadow-2xl z-50 pointer-events-none"
    >
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-white/5">
        <ArrowRight className="w-4 h-4 text-purple-400" />
        <h3 className="text-xs font-bold text-white tracking-widest uppercase">Counterfactual Simulation</h3>
      </div>

      <div className="flex gap-3">
        {/* No Intervention */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.15 }}
          className="flex-1 flex flex-col items-center gap-2 bg-red-950/40 border border-red-900/60 rounded-xl p-3"
        >
          <span className="text-[9px] text-red-400 font-bold uppercase tracking-widest">No Action</span>
          <div className="w-12 h-12 rounded-full bg-red-900/30 border border-red-700/50 flex items-center justify-center animate-pulse">
            <AlertTriangle className="w-6 h-6 text-red-500" />
          </div>
          <div className="text-center">
            <span className="text-white font-bold text-sm block">Explosion</span>
            <span className="text-red-400 font-black text-lg">91%</span>
          </div>
          <div className="w-full text-center">
            <span className="text-[9px] text-red-500/80 block">3 workers injured</span>
            <span className="text-[9px] text-red-500/80 block">Plant shutdown</span>
            <span className="text-[9px] text-red-500/80 block">$8M+ loss</span>
          </div>
        </motion.div>

        {/* Separator */}
        <div className="flex items-center">
          <div className="flex flex-col items-center gap-1">
            <div className="w-px h-8 bg-white/5" />
            <span className="text-[9px] text-slate-600 font-mono">vs</span>
            <div className="w-px h-8 bg-white/5" />
          </div>
        </div>

        {/* Evacuate */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="flex-1 flex flex-col items-center gap-2 bg-emerald-950/40 border border-emerald-900/60 rounded-xl p-3"
        >
          <span className="text-[9px] text-emerald-400 font-bold uppercase tracking-widest">Evacuate</span>
          <div className="w-12 h-12 rounded-full bg-emerald-900/30 border border-emerald-700/50 flex items-center justify-center">
            <CheckCircle2 className="w-6 h-6 text-emerald-500" />
          </div>
          <div className="text-center">
            <span className="text-white font-bold text-sm block">Safe Op.</span>
            <span className="text-emerald-400 font-black text-lg">96%</span>
          </div>
          <div className="w-full text-center">
            <span className="text-[9px] text-emerald-500/80 block">0 injuries</span>
            <span className="text-[9px] text-emerald-500/80 block">Plant continues</span>
            <span className="text-[9px] text-emerald-500/80 block">$2.4M saved</span>
          </div>
        </motion.div>
      </div>

      {/* Decision time */}
      <div className="mt-4 pt-3 border-t border-white/5 text-center">
        <span className="text-[10px] text-slate-500">AI decision latency</span>
        <div className="text-cyan-400 font-bold text-lg">14ms</div>
      </div>
    </motion.div>
  );
};
