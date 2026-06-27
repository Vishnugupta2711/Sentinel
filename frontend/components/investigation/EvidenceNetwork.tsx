import React from 'react';
import { useInvestigationStore } from '../../store/investigationStore';
import { Activity, Camera, FileText } from 'lucide-react';

export const EvidenceNetwork = React.memo(() => {
  const { report } = useInvestigationStore();
  
  if (!report || !report.evidence) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
      <h3 className="text-sm font-bold text-slate-100 mb-4 uppercase tracking-wider">Evidence Network</h3>
      <div className="space-y-4">
        {report.evidence.map((ev: { id: string; source: string; timestamp: string; description: string; traceability_link: string; confidence: number; }) => {
          let Icon = Activity;
          if (ev.source.includes('Timeline')) Icon = Activity;
          if (ev.source.includes('Vision')) Icon = Camera;
          if (ev.source.includes('Compliance')) Icon = FileText;

          return (
            <div key={ev.id} className="flex items-start gap-4 p-3 bg-slate-950 rounded-md border border-slate-800">
              <div className="p-2 bg-slate-900 rounded-md">
                <Icon className="w-5 h-5 text-emerald-400" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-emerald-400">{ev.id} - {ev.source}</span>
                  <span className="text-[10px] text-slate-500 font-mono">{ev.timestamp}</span>
                </div>
                <p className="text-sm text-slate-300">{ev.description}</p>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-[10px] text-slate-500 font-mono break-all">{ev.traceability_link}</span>
                  <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded">Conf: {ev.confidence * 100}%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
});

EvidenceNetwork.displayName = 'EvidenceNetwork';
