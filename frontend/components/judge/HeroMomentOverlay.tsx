'use client';
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useJudgeStore } from '../../store/judgeStore';
import { ShieldCheck } from 'lucide-react';

/**
 * Full-screen "SAFE" sweep that appears on Step 6 — the hero moment.
 * Uses a green radial gradient that expands from center and then fades,
 * leaving the UI with a subtle emerald tint.
 */
export const HeroMomentOverlay: React.FC = () => {
  const tourStep = useJudgeStore((s) => s.tourStep);

  return (
    <AnimatePresence>
      {tourStep === 6 && (
        <>
          {/* Sweep flash */}
          <motion.div
            key="sweep"
            className="absolute inset-0 z-[55] pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 0.45, 0] }}
            transition={{ duration: 1.8, times: [0, 0.3, 1], ease: 'easeOut' }}
            style={{
              background: 'radial-gradient(ellipse at center, rgba(16,185,129,0.4) 0%, transparent 70%)',
            }}
          />

          {/* Persistent ambient tint */}
          <motion.div
            key="tint"
            className="absolute inset-0 z-[54] pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.2, delay: 0.8 }}
            style={{
              background: 'radial-gradient(ellipse at center, rgba(16,185,129,0.06) 0%, transparent 65%)',
            }}
          />

          {/* "SAFE" badge — top center */}
          <motion.div
            key="badge"
            className="absolute top-20 left-1/2 -translate-x-1/2 z-[56] pointer-events-none"
            initial={{ opacity: 0, scale: 0.6, y: -12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4, type: 'spring', stiffness: 180 }}
          >
            <div className="flex items-center gap-3 bg-emerald-950/80 backdrop-blur-xl border border-emerald-500/50 rounded-full px-6 py-3 shadow-[0_0_40px_rgba(16,185,129,0.3)]">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span className="text-emerald-300 font-bold text-sm uppercase tracking-widest">
                Incident Prevented — All Systems Safe
              </span>
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
