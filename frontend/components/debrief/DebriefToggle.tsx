import React from 'react';
import { FileText } from 'lucide-react';
import { useDebriefStore } from '../../store/debriefStore';

export const DebriefToggle = React.memo(() => {
  const isDebriefOpen = useDebriefStore((state) => state.isDebriefOpen);
  const setDebriefOpen = useDebriefStore((state) => state.setDebriefOpen);

  return (
    <button
      onClick={() => setDebriefOpen(!isDebriefOpen)}
      className={`px-4 py-1.5 rounded-md text-xs font-bold uppercase tracking-wider transition-colors flex items-center gap-2 border ${
        isDebriefOpen
          ? 'bg-purple-500/20 border-purple-500 text-purple-300'
          : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700 hover:text-slate-200'
      }`}
    >
      <FileText className="w-4 h-4" />
      Incident Debrief
    </button>
  );
});

DebriefToggle.displayName = 'DebriefToggle';
