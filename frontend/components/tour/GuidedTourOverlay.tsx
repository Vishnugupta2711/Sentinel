'use client';
import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, Keyboard } from 'lucide-react';
import { useJudgeStore, DEMO_STEPS } from '../../store/judgeStore';

export const GuidedTourOverlay: React.FC = () => {
  const tourStep   = useJudgeStore((s) => s.tourStep);
  const isAutoPlay = useJudgeStore((s) => s.isAutoPlay);
  const nextStep   = useJudgeStore((s) => s.nextStep);
  const prevStep   = useJudgeStore((s) => s.prevStep);
  const goToStep   = useJudgeStore((s) => s.goToStep);

  // Countdown progress within the current step (only during autoplay)
  const [elapsed, setElapsed] = useState(0);
  const currentMeta = DEMO_STEPS[tourStep - 1];
  const stepDuration = currentMeta.durationSeconds;

  useEffect(() => {
    const timeout = setTimeout(() => setElapsed(0), 0);
    if (!isAutoPlay) return () => clearTimeout(timeout);
    const interval = setInterval(() => {
      setElapsed((e) => Math.min(e + 0.1, stepDuration));
    }, 100);
    return () => {
      clearTimeout(timeout);
      clearInterval(interval);
    };
  }, [tourStep, isAutoPlay, stepDuration]);

  const progress = isAutoPlay ? (elapsed / stepDuration) * 100 : 0;

  return (
    <>
      {/* ── Top-of-screen progress bar ──────────────────────────────── */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-white/5 z-[60] pointer-events-none">
        <motion.div
          className="h-full bg-cyan-500"
          style={{ width: `${((tourStep - 1) / (DEMO_STEPS.length - 1)) * 100}%` }}
          transition={{ duration: 0.4 }}
        />
      </div>

      {/* ── Autoplay step timer bar ─────────────────────────────────── */}
      <AnimatePresence>
        {isAutoPlay && (
          <motion.div
            key={tourStep}
            className="absolute top-0.5 left-0 right-0 h-0.5 bg-cyan-400/40 z-[61] pointer-events-none origin-left"
            initial={{ scaleX: 0 }}
            animate={{ scaleX: progress / 100 }}
            style={{ transformOrigin: 'left' }}
            transition={{ duration: 0.1, ease: 'linear' }}
          />
        )}
      </AnimatePresence>

      {/* ── Chapter pill nav ────────────────────────────────────────── */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-50 flex flex-col items-center gap-3">
        <div className="flex items-center gap-2 bg-black/80 backdrop-blur-xl border border-white/10 rounded-full px-4 py-2 shadow-2xl">

          {/* Prev */}
          <button
            onClick={prevStep}
            disabled={tourStep === 1}
            className="p-1.5 text-slate-400 hover:text-white disabled:opacity-20 transition-colors rounded-full hover:bg-white/10"
            aria-label="Previous step"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          {/* Chapter pills */}
          <div className="flex gap-1.5 mx-1">
            {DEMO_STEPS.map((step) => {
              const isActive = tourStep === step.num;
              const isDone   = tourStep > step.num;
              return (
                <button
                  key={step.num}
                  onClick={() => goToStep(step.num)}
                  title={step.chapter}
                  className={`relative h-7 rounded-full transition-all duration-300 overflow-hidden
                    ${isActive
                      ? 'w-28 bg-cyan-500/20 border border-cyan-500/50 px-3'
                      : isDone
                        ? 'w-7 bg-cyan-900/40 border border-cyan-700/50'
                        : 'w-7 bg-slate-800 border border-slate-700 hover:border-slate-500'
                    }`}
                >
                  {isActive ? (
                    <span className="text-[10px] font-bold text-cyan-300 uppercase tracking-wider whitespace-nowrap">
                      {step.chapter}
                    </span>
                  ) : isDone ? (
                    <span className="text-cyan-500 text-[10px] font-bold">✓</span>
                  ) : (
                    <span className="text-slate-600 text-xs font-mono">{step.num}</span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Next */}
          <button
            onClick={nextStep}
            disabled={tourStep === DEMO_STEPS.length}
            className="p-1.5 text-slate-400 hover:text-white disabled:opacity-20 transition-colors rounded-full hover:bg-white/10"
            aria-label="Next step"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Keyboard hint */}
        <div className="flex items-center gap-1.5 text-[9px] text-slate-600 font-mono">
          <Keyboard className="w-3 h-3" />
          <span>← → to navigate · Space to pause</span>
        </div>
      </div>
    </>
  );
};
