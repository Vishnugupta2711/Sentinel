import React from 'react';
import { useInvestigationStore } from '../../store/investigationStore';
import { Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

export const InvestigationPipeline = React.memo(() => {
  const { progress, stage, isInvestigating } = useInvestigationStore();
  
  if (!isInvestigating || progress >= 100) return null;

  return (
    <div className="flex flex-col items-center justify-center p-12 bg-slate-900 rounded-xl border border-slate-800">
      <Loader2 className="w-16 h-16 text-emerald-500 animate-spin mb-6" />
      <h2 className="text-2xl font-bold text-slate-100 mb-2">Autonomous Investigation in Progress</h2>
      <p className="text-emerald-400 font-mono mb-8">{stage}</p>
      
      <div className="w-full max-w-2xl bg-slate-950 rounded-full h-4 overflow-hidden border border-slate-800">
        <motion.div
          className="h-full bg-emerald-500 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
      <p className="mt-4 text-xs text-slate-500 font-mono">{progress.toFixed(0)}% Complete</p>
    </div>
  );
});

InvestigationPipeline.displayName = 'InvestigationPipeline';
