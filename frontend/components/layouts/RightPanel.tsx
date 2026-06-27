import React from 'react';
import { useIntelligenceStore } from '../../store/intelligence';
import { Activity, ShieldAlert, Video, FileText, BrainCircuit, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const EmptyState = ({ label }: { label: string }) => (
  <p className="text-xs text-slate-600 italic">{label}</p>
);

const SectionHeader = ({ icon: Icon, label, color }: { icon: React.ElementType; label: string; color: string }) => (
  <div className="flex items-center gap-2 mb-3">
    <Icon className={`w-4 h-4 ${color}`} />
    <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">{label}</h3>
  </div>
);

export const RightPanel = React.memo(() => {
  const visionEvents           = useIntelligenceStore((s) => s.visionEvents);
  const complianceViolations   = useIntelligenceStore((s) => s.complianceViolations);
  const plannerRecommendations = useIntelligenceStore((s) => s.plannerRecommendations);
  const riskAssessments        = useIntelligenceStore((s) => s.riskAssessments);
  const connectionStatus       = useIntelligenceStore((s) => s.connectionStatus);

  const isConnecting = connectionStatus === 'connecting';

  return (
    <div className="flex flex-col h-full overflow-hidden bg-slate-900/40">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
          <BrainCircuit className="w-4 h-4 text-purple-400" />
          Intelligence Feed
        </h2>
        {isConnecting && (
          <Loader2 className="w-3 h-3 text-slate-500 animate-spin" />
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">

        {/* Planner Recommendations */}
        <section>
          <SectionHeader icon={Activity} label="Active Counterfactuals" color="text-emerald-400" />
          <div className="space-y-2">
            <AnimatePresence>
              {plannerRecommendations.slice(0, 2).map((plan) => (
                <motion.div
                  key={plan.plan_id}
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.25 }}
                  className="p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-md"
                >
                  <p className="text-xs font-medium text-emerald-300">{plan.scenario_name}</p>
                  <p className="text-[10px] text-slate-400 mt-1">Score: {plan.score.toFixed(2)}</p>
                </motion.div>
              ))}
            </AnimatePresence>
            {plannerRecommendations.length === 0 && <EmptyState label="No active plans." />}
          </div>
        </section>

        {/* Vision Events */}
        <section>
          <SectionHeader icon={Video} label="Vision Events" color="text-cyan-400" />
          <div className="space-y-2">
            <AnimatePresence>
              {visionEvents.slice(0, 3).map((v) => (
                <motion.div
                  key={v.event_id}
                  initial={{ opacity: 0, x: 16 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="p-2 border-l-2 border-cyan-500 bg-slate-900/50 text-xs"
                >
                  <span className="font-mono text-[10px] text-cyan-500">
                    {v.timestamp?.split('T')[1]?.slice(0, 8) ?? '--:--:--'}
                  </span>
                  <p className="text-slate-300 mt-0.5">{v.description}</p>
                </motion.div>
              ))}
            </AnimatePresence>
            {visionEvents.length === 0 && <EmptyState label="No vision events detected." />}
          </div>
        </section>

        {/* Compliance Violations */}
        <section>
          <SectionHeader icon={FileText} label="Compliance" color="text-red-400" />
          <div className="space-y-2">
            <AnimatePresence>
              {complianceViolations.slice(0, 2).map((v) => (
                <motion.div
                  key={v.violation_id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="p-2 border border-red-500/20 bg-red-500/5 rounded text-xs"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-red-400 font-bold">{v.severity}</span>
                    <span className="text-[9px] text-slate-600 font-mono">
                      {v.timestamp?.split('T')[1]?.slice(0, 8) ?? ''}
                    </span>
                  </div>
                  <p className="text-slate-300">{v.description}</p>
                </motion.div>
              ))}
            </AnimatePresence>
            {complianceViolations.length === 0 && <EmptyState label="No compliance violations." />}
          </div>
        </section>

        {/* Compound Risk */}
        <section>
          <SectionHeader icon={ShieldAlert} label="Compound Risk" color="text-amber-400" />
          <div className="space-y-2">
            {riskAssessments.slice(0, 2).map((r) => (
              <div key={r.risk_id} className="p-2 border-l-2 border-amber-500 bg-amber-500/5 text-xs">
                <p className="text-amber-300 font-medium">{r.risk_type.replace(/_/g, ' ')}</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex-1 h-1 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-500 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(r.risk_score, 100)}%` }}
                    />
                  </div>
                  <span className="text-slate-400 text-[10px] font-mono shrink-0">
                    {r.risk_score.toFixed(1)}/100
                  </span>
                </div>
              </div>
            ))}
            {riskAssessments.length === 0 && <EmptyState label="No risks detected." />}
          </div>
        </section>

      </div>
    </div>
  );
});

RightPanel.displayName = 'RightPanel';
