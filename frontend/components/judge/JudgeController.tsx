'use client';
import React, { useEffect } from 'react';
import { Play, Square } from 'lucide-react';
import { useJudgeStore, DEMO_STEPS } from '../../store/judgeStore';
import { useJudgeShortcuts } from '../../hooks/useJudgeShortcuts';

// Demo Overlay Components
import { AIStoryPanel } from '../story/AIStoryPanel';
import { GuidedTourOverlay } from '../tour/GuidedTourOverlay';
import { AIExplanationPanel } from './AIExplanationPanel';
import { BusinessImpactPanel } from './BusinessImpactPanel';
import { BeforeAfterVisualizer } from './BeforeAfterVisualizer';
import { ConfidenceVisualization } from './ConfidenceVisualization';
import { HeroMomentOverlay } from './HeroMomentOverlay';

export const JudgeController: React.FC = () => {
  const { isJudgeMode, isAutoPlay, nextStep, tourStep, toggleAutoPlay } = useJudgeStore();

  // Initialize keyboard shortcuts (arrows to nav, space to play/pause)
  useJudgeShortcuts();

  // AutoPlay orchestration
  useEffect(() => {
    if (!isAutoPlay) return;
    
    if (tourStep > DEMO_STEPS.length) {
      toggleAutoPlay(); // Stop at the end
      return;
    }

    const currentMeta = DEMO_STEPS[tourStep - 1];
    if (!currentMeta) return;

    // Advance based on the specific duration for this step
    const timer = setTimeout(() => {
      nextStep();
    }, currentMeta.durationSeconds * 1000);

    return () => clearTimeout(timer);
  }, [isAutoPlay, tourStep, nextStep, toggleAutoPlay]);

  if (!isJudgeMode) return null;

  return (
    <>
      {/* ── Core ambient vignette for Judge Mode ── */}
      <div className="absolute inset-0 pointer-events-none z-40 bg-gradient-to-b from-black/60 via-transparent to-black/80" />
      
      {/* ── Central CTA when demo is active but paused (only on step 1) ── */}
      {!isAutoPlay && tourStep === 1 && (
        <div className="absolute top-28 left-1/2 -translate-x-1/2 z-50 animate-in fade-in zoom-in duration-500">
          <button 
            onClick={toggleAutoPlay}
            className="flex items-center gap-3 px-8 py-4 bg-cyan-600 hover:bg-cyan-500 text-white rounded-full shadow-[0_0_40px_rgba(6,182,212,0.4)] transition-all hover:scale-105 active:scale-95 border border-cyan-400/50 pointer-events-auto"
          >
            <Play className="w-5 h-5 fill-current" />
            <span className="font-bold uppercase tracking-widest text-sm">Start Guided Demo</span>
          </button>
        </div>
      )}

      {/* ── Unobtrusive top-right autoplay toggle (for steps 2+) ── */}
      {tourStep > 1 && (
        <button 
          onClick={toggleAutoPlay}
          className={`absolute top-20 right-6 z-[70] flex items-center gap-2 px-3 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-wider transition-colors shadow-lg pointer-events-auto border backdrop-blur-md ${
            isAutoPlay 
              ? 'bg-red-900/40 border-red-500/50 text-red-300 hover:bg-red-900/60' 
              : 'bg-cyan-900/40 border-cyan-500/50 text-cyan-300 hover:bg-cyan-900/60'
          }`}
        >
          {isAutoPlay ? (
             <><Square className="w-3 h-3 fill-current" /> Pause Demo</>
          ) : (
             <><Play className="w-3 h-3 fill-current" /> Resume Demo</>
          )}
        </button>
      )}

      {/* ── Overlays ── */}
      {/* 1. The Story (Cinematic text) */}
      <AIStoryPanel />
      
      {/* 2. Navigation (Timeline/Progress) */}
      <GuidedTourOverlay />
      
      {/* 3. Analytical Panels (Right side) */}
      <AIExplanationPanel />
      <ConfidenceVisualization />
      
      {/* 4. Action/Impact Panels (Left side) */}
      <BeforeAfterVisualizer />
      <BusinessImpactPanel />

      {/* 5. The Finale (Hero moment on Step 6) */}
      <HeroMomentOverlay />
    </>
  );
};
