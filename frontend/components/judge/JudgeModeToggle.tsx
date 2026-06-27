'use client';
import React from 'react';
import { useJudgeStore } from '../../store/judgeStore';

export const JudgeModeToggle: React.FC = () => {
  const isJudgeMode = useJudgeStore(state => state.isJudgeMode);
  const toggleJudgeMode = useJudgeStore(state => state.toggleJudgeMode);

  return (
    <div 
      className="flex items-center gap-3 bg-slate-900 border border-slate-800 px-4 py-1.5 rounded-full shadow-sm"
      title="Guided Demo mode hides dev tools and presents the platform narrative."
    >
      <span className={`text-[10px] uppercase font-bold tracking-widest transition-colors ${!isJudgeMode ? 'text-slate-200' : 'text-slate-500'}`}>
        Live Sandbox
      </span>
      
      <button 
        onClick={toggleJudgeMode}
        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${isJudgeMode ? 'bg-cyan-500 shadow-[0_0_12px_rgba(6,182,212,0.5)]' : 'bg-slate-700'}`}
      >
        <span className="sr-only">Toggle Guided Demo Mode</span>
        <span
          className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${isJudgeMode ? 'translate-x-5' : 'translate-x-1'}`}
        />
      </button>

      <span className={`text-[10px] uppercase font-bold tracking-widest transition-colors ${isJudgeMode ? 'text-cyan-400' : 'text-slate-500'}`}>
        Guided Demo
      </span>
    </div>
  );
};
