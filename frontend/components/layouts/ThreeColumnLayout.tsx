import React from 'react';
import { useJudgeStore } from '../../store/judgeStore';
import { JudgeController } from '../judge/JudgeController';
import { DebriefDashboard } from '../debrief/DebriefDashboard';

export const ThreeColumnLayout = ({
  topBar,
  leftPanel,
  centerPanel,
  rightPanel,
  bottomPanel
}: {
  topBar: React.ReactNode;
  leftPanel: React.ReactNode;
  centerPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  bottomPanel: React.ReactNode;
}) => {
  const isJudgeMode = useJudgeStore(state => state.isJudgeMode);

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-200 overflow-hidden font-sans relative">
      <JudgeController />
      <DebriefDashboard />
      
      {/* Top Bar - Fixed Height */}
      <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md shrink-0 z-50">
        {topBar}
      </header>

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Fixed Width */}
        {!isJudgeMode && (
          <aside className="w-80 border-r border-slate-800 bg-slate-900/30 overflow-y-auto shrink-0 z-40 transition-all">
            {leftPanel}
          </aside>
        )}

        {/* Center Panel - Fluid */}
        <main className="flex-1 flex flex-col min-w-0 bg-slate-950/50 relative overflow-hidden">
          <div className="flex-1 relative">
            {centerPanel}
          </div>
          
          {/* Bottom Panel */}
          {!isJudgeMode && (
            <div className="h-64 border-t border-slate-800 bg-slate-900/80 backdrop-blur-md shrink-0 z-30 overflow-y-auto transition-all">
              {bottomPanel}
            </div>
          )}
        </main>

        {/* Right Panel - Fixed Width */}
        {!isJudgeMode && (
          <aside className="w-96 border-l border-slate-800 bg-slate-900/30 overflow-y-auto shrink-0 z-40 transition-all">
            {rightPanel}
          </aside>
        )}
      </div>
    </div>
  );
};

