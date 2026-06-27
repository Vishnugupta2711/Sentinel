import React, { useEffect } from 'react';
import { useDebriefStore } from '../../store/debriefStore';
import { Loader2, FileText, Download, CheckCircle, Clock } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export const DebriefDashboard = React.memo(() => {
  const { isDebriefOpen, report, setReport, progress, stage, setProgress } = useDebriefStore();
  const [markdown, setMarkdown] = React.useState<string>('');
  const [generating, setGenerating] = React.useState(false);

  useEffect(() => {
    if (isDebriefOpen && !report && !generating) {
      setGenerating(true);
      // Simulate WebSocket progress
      let p = 0;
      const interval = setInterval(() => {
        p += 25;
        if (p <= 25) setProgress(p, "Reconstructing Timeline...");
        else if (p <= 50) setProgress(p, "Running Root Cause Analysis...");
        else if (p <= 75) setProgress(p, "Mapping Compliance...");
        else setProgress(p, "Generating Final Report...");
        
        if (p >= 100) {
          clearInterval(interval);
          // Fetch the report
          fetch('http://localhost:8000/api/v1/debrief/latest')
            .then(r => r.json())
            .then(data => {
              setReport(data);
              return fetch(`http://localhost:8000/api/v1/debrief/report/${data.report_id}`);
            })
            .then(r => r.json())
            .then(data => {
              setMarkdown(data.markdown);
              setGenerating(false);
            })
            .catch(err => {
              console.error(err);
              setGenerating(false);
            });
        }
      }, 800);
      return () => clearInterval(interval);
    }
  }, [isDebriefOpen, report, generating, setProgress, setReport]);

  if (!isDebriefOpen) return null;

  return (
    <div className="absolute inset-0 z-40 bg-slate-950 flex flex-col p-8 overflow-y-auto">
      <div className="max-w-5xl mx-auto w-full">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
            <FileText className="w-8 h-8 text-purple-400" />
            AI Incident Debrief Engine
          </h1>
          {report && (
            <button className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-md flex items-center gap-2 text-sm font-semibold transition-colors">
              <Download className="w-4 h-4" />
              Export PDF
            </button>
          )}
        </div>

        {generating && (
          <div className="flex flex-col items-center justify-center py-32 space-y-6">
            <Loader2 className="w-12 h-12 text-purple-500 animate-spin" />
            <div className="text-center">
              <p className="text-xl text-slate-200 font-semibold mb-2">Analyzing Incident</p>
              <p className="text-purple-400 text-sm animate-pulse">{stage}</p>
            </div>
            <div className="w-64 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-purple-500 transition-all duration-500 ease-out" 
                style={{ width: `${progress}%` }} 
              />
            </div>
          </div>
        )}

        {report && !generating && (
          <div className="grid grid-cols-3 gap-8">
            {/* Left Column: Metrics & RCA */}
            <div className="col-span-1 space-y-6">
              
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Executive Overview</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-[10px] text-slate-500 uppercase">Outcome</p>
                    <p className="text-sm font-semibold text-emerald-400 flex items-center gap-1"><CheckCircle className="w-4 h-4"/> {report.outcome}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-slate-500 uppercase">Estimated Loss Prevented</p>
                    <p className="text-2xl font-bold text-white">${report.estimated_loss_prevented.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-slate-500 uppercase">Decision Latency</p>
                    <p className="text-sm font-mono text-cyan-400 flex items-center gap-1"><Clock className="w-4 h-4"/> {report.decision_time_ms.toFixed(2)} ms</p>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Root Cause Analysis</h3>
                <div className="space-y-4">
                  {report.root_causes.map((rc: { category: string; confidence: number; description: string; }, idx: number) => (
                    <div key={idx} className="border-l-2 border-amber-500 pl-3">
                      <p className="text-xs font-bold text-amber-400">{rc.category} (Conf: {rc.confidence * 100}%)</p>
                      <p className="text-sm text-slate-300 mt-1">{rc.description}</p>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Business Impact</h3>
                <div className="grid grid-cols-2 gap-4">
                   <div>
                    <p className="text-[10px] text-slate-500 uppercase">Workers Protected</p>
                    <p className="text-lg font-bold text-emerald-400">{report.business_impact.workers_protected}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-slate-500 uppercase">Downtime Avoided</p>
                    <p className="text-lg font-bold text-emerald-400">{report.business_impact.downtime_prevented_hours}h</p>
                  </div>
                </div>
              </div>

            </div>

            {/* Right Column: Full Markdown Report */}
            <div className="col-span-2 bg-slate-900 border border-slate-800 rounded-lg p-8 h-[800px] overflow-y-auto">
               <article className="prose prose-invert prose-purple max-w-none prose-h1:text-2xl prose-h2:text-xl prose-h2:mt-8 prose-h2:border-b prose-h2:border-slate-800 prose-h2:pb-2">
                 <ReactMarkdown>{markdown}</ReactMarkdown>
               </article>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

DebriefDashboard.displayName = 'DebriefDashboard';
