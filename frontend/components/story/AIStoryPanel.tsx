'use client';
import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useJudgeStore, DEMO_STEPS } from '../../store/judgeStore';

const ACCENT_CLASSES: Record<string, { text: string; sub: string; bar: string }> = {
  cyan:    { text: 'text-cyan-300',    sub: 'text-slate-300', bar: 'bg-cyan-500'    },
  amber:   { text: 'text-amber-300',   sub: 'text-slate-300', bar: 'bg-amber-500'   },
  red:     { text: 'text-red-300',     sub: 'text-slate-300', bar: 'bg-red-500'     },
  purple:  { text: 'text-purple-300',  sub: 'text-slate-300', bar: 'bg-purple-500'  },
  emerald: { text: 'text-emerald-300', sub: 'text-white',     bar: 'bg-emerald-500' },
};

export const AIStoryPanel: React.FC = () => {
  const tourStep    = useJudgeStore((s) => s.tourStep);
  const isJudgeMode = useJudgeStore((s) => s.isJudgeMode);
  
  // Track previous step in state to avoid accessing ref during render
  const [prevStep, setPrevStep] = React.useState(tourStep);
  const [direction, setDirection] = React.useState(1);

  if (tourStep !== prevStep) {
    setDirection(tourStep > prevStep ? 1 : -1);
    setPrevStep(tourStep);
  }

  if (!isJudgeMode) return null;

  const meta        = DEMO_STEPS[tourStep - 1] || DEMO_STEPS[0];
  const accent      = ACCENT_CLASSES[meta.accentColor] ?? ACCENT_CLASSES.cyan;

  return (
    /* Cinematic headline — single card, bottom-anchored above the tour nav */
    <div className="absolute bottom-28 left-1/2 -translate-x-1/2 w-full max-w-3xl px-4 pointer-events-none z-50">
      <AnimatePresence mode="wait" custom={direction}>
        <motion.div
          key={tourStep}
          custom={direction}
          initial={{ opacity: 0, y: direction * 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: direction * -20 }}
          transition={{ duration: 0.45, ease: 'easeOut' }}
          className="bg-black/70 backdrop-blur-xl border border-white/10 rounded-2xl px-8 py-5 shadow-2xl"
        >
          {/* Step badge */}
          <div className="flex items-center gap-3 mb-3">
            <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full border ${accent.bar}/30 border-current ${accent.text}`}>
              {meta.chapter}
            </span>
            <span className="text-[10px] text-slate-600 font-mono">
              {tourStep} / {DEMO_STEPS.length}
            </span>
          </div>

          {/* Headline */}
          <h2 className={`text-2xl font-bold leading-tight mb-2 ${accent.text}`}>
            {meta.headline}
          </h2>

          {/* Sub-headline */}
          <p className={`text-sm leading-relaxed ${accent.sub} opacity-80`}>
            {meta.subHeadline}
          </p>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};
