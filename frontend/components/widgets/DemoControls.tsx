import { Play, Pause, Square, FastForward } from 'lucide-react';
import { useDemoStore } from '../../store/demo';
import { useJudgeStore } from '../../store/judgeStore';

export const DemoControls = () => {
  const { status, currentStage, activeNarration, startDemo, nextStage, pauseDemo, resetDemo } = useDemoStore();
  const isJudgeMode = useJudgeStore(s => s.isJudgeMode);

  if (isJudgeMode) return null;

  return (
    <div className="flex flex-col gap-2">
       {/* Narration Overlay if active */}
       {activeNarration && (
          <div className="fixed top-20 right-1/2 translate-x-1/2 z-50 bg-purple-900/90 border border-purple-500/50 p-4 rounded-xl shadow-2xl backdrop-blur-md max-w-xl text-center animate-in fade-in slide-in-from-top-4">
             <h4 className="text-[10px] text-purple-300 uppercase tracking-widest font-bold mb-1">AI Narration • Stage {currentStage}</h4>
             <p className="text-sm text-slate-100 font-medium">{activeNarration}</p>
          </div>
       )}

       <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 p-1.5 rounded-lg">
          {status === 'IDLE' ? (
             <button onClick={() => startDemo('DEMO_01')} className="px-3 py-1 bg-purple-600 hover:bg-purple-500 text-white rounded text-xs font-bold transition-colors flex items-center gap-1">
                <Play className="w-3 h-3 fill-current" /> Play Demo
             </button>
          ) : (
             <>
                <button onClick={resetDemo} className="p-1.5 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded transition-colors">
                   <Square className="w-4 h-4 fill-current" />
                </button>
                {status === 'PLAYING' ? (
                   <button onClick={pauseDemo} className="p-1.5 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded transition-colors">
                      <Pause className="w-4 h-4 fill-current" />
                   </button>
                ) : (
                   <button onClick={() => startDemo('DEMO_01')} className="p-1.5 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded transition-colors">
                      <Play className="w-4 h-4 fill-current" />
                   </button>
                )}
                <button onClick={nextStage} className="p-1.5 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded transition-colors flex items-center gap-1 text-[10px] font-bold">
                   <FastForward className="w-4 h-4 fill-current" /> NEXT
                </button>
             </>
          )}
          
          <div className="w-px h-4 bg-slate-700 mx-1" />
          <span className="text-[10px] font-mono text-purple-400 font-bold uppercase px-2">{status}</span>
       </div>
    </div>
  );
};
