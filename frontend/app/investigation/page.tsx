"use client";

import React, { useEffect } from 'react';
import { useInvestigationStore } from '../../store/investigationStore';
import { TopBar } from '../../components/layouts/TopBar';
import { InvestigationPipeline } from '../../components/investigation/InvestigationPipeline';
import { EvidenceNetwork } from '../../components/investigation/EvidenceNetwork';
import { ReportViewer } from '../../components/investigation/ReportViewer';
import { Search } from 'lucide-react';

export default function InvestigationPage() {
  const { startInvestigation, setProgress, setReport, report, isInvestigating } = useInvestigationStore();

  useEffect(() => {
    // If not investigating and no report, start one (simulation for the demo)
    if (!isInvestigating && !report) {
      startInvestigation();
      let p = 0;
      const interval = setInterval(() => {
        p += 11.1; // 9 stages roughly
        if (p <= 11) setProgress(p, "STAGE 1: Evidence Collection");
        else if (p <= 22) setProgress(p, "STAGE 2: Timeline Reconstruction");
        else if (p <= 33) setProgress(p, "STAGE 3: Event Correlation");
        else if (p <= 44) setProgress(p, "STAGE 4: Root Cause Analysis");
        else if (p <= 55) setProgress(p, "STAGE 5: Decision Audit");
        else if (p <= 66) setProgress(p, "STAGE 6: Compliance Audit");
        else if (p <= 77) setProgress(p, "STAGE 7: Business Impact Assessment");
        else if (p <= 88) setProgress(p, "STAGE 8: Preventive Recommendations");
        else setProgress(p, "STAGE 9: Finalizing Report");

        if (p >= 100) {
          clearInterval(interval);
          fetch('http://localhost:8000/api/v1/investigation/start', { method: 'POST' })
            .then(() => fetch('http://localhost:8000/api/v1/investigation/latest'))
            .then(res => res.json())
            .then(data => {
              if(data && data.investigation_id) {
                setReport(data);
              } else {
                console.error("Invalid response", data);
              }
            })
            .catch(console.error);
        }
      }, 500);
      return () => clearInterval(interval);
    }
  }, [isInvestigating, report, startInvestigation, setProgress, setReport]);

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-200 overflow-hidden font-sans">
      <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md shrink-0 z-50">
        <TopBar />
      </header>

      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
              <Search className="w-8 h-8 text-emerald-400" />
              Sentinel AI Incident Investigation Platform (SAIIP)
            </h1>
          </div>

          {isInvestigating && !report && (
            <div className="mt-20">
              <InvestigationPipeline />
            </div>
          )}

          {report && (
            <div className="grid grid-cols-12 gap-8 h-[800px]">
              <div className="col-span-4 h-full overflow-y-auto">
                <EvidenceNetwork />
              </div>
              <div className="col-span-8 h-full">
                <ReportViewer />
              </div>
            </div>
          )}
          
        </div>
      </main>
    </div>
  );
}
