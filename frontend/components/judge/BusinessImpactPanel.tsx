'use client';
import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { useJudgeStore } from '../../store/judgeStore';
import { TrendingUp, Clock, DollarSign } from 'lucide-react';

function useCountUp(target: number, duration = 1800, decimals = 0) {
  const [value, setValue] = useState(0);
  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setValue(0);
    const start = performance.now();
    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(parseFloat((eased * target).toFixed(decimals)));
      if (progress < 1) frameRef.current = requestAnimationFrame(tick);
    };
    frameRef.current = requestAnimationFrame(tick);
    return () => { if (frameRef.current) cancelAnimationFrame(frameRef.current); };
  }, [target, duration, decimals]);

  return value;
}

interface StatCardProps {
  icon: React.ElementType;
  label: string;
  children: React.ReactNode;
  delay?: number;
}

const StatCard: React.FC<StatCardProps> = ({ icon: Icon, label, children, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
    className="flex items-center gap-3"
  >
    <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0">
      <Icon className="w-4 h-4 text-emerald-400" />
    </div>
    <div className="flex flex-col">
      <span className="text-[10px] text-slate-500 uppercase tracking-wider font-medium">{label}</span>
      <div className="text-lg font-bold text-white leading-none mt-0.5">{children}</div>
    </div>
  </motion.div>
);

export const BusinessImpactPanel: React.FC = () => {
  const tourStep = useJudgeStore((s) => s.tourStep);

  const workers    = useCountUp(1, 1000, 0);
  const downtime   = useCountUp(8.5, 1600, 1);
  const savings    = useCountUp(2.4, 2000, 1);
  const aiLatency  = useCountUp(14, 1200, 0);
  const humanTime  = useCountUp(270, 1800, 0); // 4.5 min in seconds

  if (tourStep < 6) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: -32 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="absolute top-1/2 left-6 -translate-y-1/2 w-72 bg-black/80 backdrop-blur-xl border border-emerald-500/20 rounded-2xl p-6 shadow-[0_0_60px_rgba(16,185,129,0.15)] z-50 pointer-events-none"
    >
      <div className="flex items-center gap-2 mb-5 pb-3 border-b border-emerald-900/50">
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-widest">Impact Summary</h3>
      </div>

      <div className="flex flex-col gap-5">
        <StatCard icon={TrendingUp} label="Workers Protected" delay={0.1}>
          {workers} <span className="text-emerald-400 text-sm">person</span>
        </StatCard>

        <StatCard icon={Clock} label="Downtime Avoided" delay={0.2}>
          {downtime} <span className="text-emerald-400 text-sm">hrs</span>
        </StatCard>

        <StatCard icon={DollarSign} label="Financial Loss Prevented" delay={0.35}>
          <span className="text-emerald-400 text-2xl">${savings}M</span>
        </StatCard>

        <div className="pt-3 border-t border-white/5">
          <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">Decision Speed</p>
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-center">
              <span className="text-[10px] text-slate-500">Sentinel</span>
              <span className="text-lg font-bold text-cyan-400">{aiLatency}ms</span>
            </div>
            <div className="flex-1 flex items-center">
              <div className="flex-1 h-px bg-slate-800" />
              <span className="text-[9px] text-slate-600 px-2">vs</span>
              <div className="flex-1 h-px bg-slate-800" />
            </div>
            <div className="flex flex-col items-center">
              <span className="text-[10px] text-slate-500">Human</span>
              <span className="text-lg font-bold text-slate-400">{humanTime}s</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
