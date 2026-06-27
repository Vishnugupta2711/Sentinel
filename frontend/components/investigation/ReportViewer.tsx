import React, { useState } from 'react';
import { useInvestigationStore } from '../../store/investigationStore';
import ReactMarkdown from 'react-markdown';
import { Download } from 'lucide-react';

export const ReportViewer = React.memo(() => {
  const { report } = useInvestigationStore();
  const [activeTab, setActiveTab] = useState<'executive' | 'technical'>('executive');
  
  if (!report) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg flex flex-col h-full">
      <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-950 rounded-t-lg">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setActiveTab('executive')}
            className={`px-4 py-2 text-sm font-semibold uppercase tracking-wider rounded transition-colors ${activeTab === 'executive' ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-500 hover:text-slate-300'}`}
          >
            Executive Summary
          </button>
          <button 
            onClick={() => setActiveTab('technical')}
            className={`px-4 py-2 text-sm font-semibold uppercase tracking-wider rounded transition-colors ${activeTab === 'technical' ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-500 hover:text-slate-300'}`}
          >
            Technical Appendix
          </button>
        </div>
        <button className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-bold uppercase transition-colors">
          <Download className="w-4 h-4" />
          Export PDF
        </button>
      </div>
      
      <div className="p-8 overflow-y-auto flex-1">
        <article className="prose prose-invert prose-emerald max-w-none">
          <ReactMarkdown>
            {activeTab === 'executive' ? report.executive_summary : report.technical_appendix}
          </ReactMarkdown>
        </article>
      </div>
    </div>
  );
});

ReportViewer.displayName = 'ReportViewer';
