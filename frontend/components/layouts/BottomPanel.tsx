import React from 'react';
import { Pause, SkipBack, SkipForward, Clock } from 'lucide-react';
import { useWorldStateStore } from '../../store/worldState';

export const BottomPanel = React.memo(() => {
  const version    = useWorldStateStore((state) => state.version);
  const isLoaded   = useWorldStateStore((state) => state.isLoaded);
  const connectionStatus = useWorldStateStore((state) => state.connectionStatus);

  const isLive = connectionStatus === 'connected' && isLoaded;

  return (
    <div className="flex flex-col h-full bg-slate-950 p-4">

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
          <Clock className="w-4 h-4 text-slate-400" />
          Timeline &amp; Replay
        </h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-mono">{isLive ? 'Live Sync' : 'Waiting...'}</span>
          <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`} />
        </div>
      </div>

      {/* Controls & Scrubber */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <button disabled className="p-2 bg-slate-800 hover:bg-slate-700 rounded-md text-slate-600 transition-colors disabled:cursor-not-allowed">
            <SkipBack className="w-4 h-4" />
          </button>
          <button disabled className="p-2 bg-cyan-600/40 rounded-md text-cyan-400/60 transition-colors disabled:cursor-not-allowed">
            <Pause className="w-5 h-5 fill-current" />
          </button>
          <button disabled className="p-2 bg-slate-800 hover:bg-slate-700 rounded-md text-slate-600 transition-colors disabled:cursor-not-allowed">
            <SkipForward className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 relative h-8 flex items-center group">
          {/* Scrubber track */}
          <div className="absolute inset-x-0 h-1 bg-slate-800 rounded-full overflow-hidden">
            {/* Live: always at 100% */}
            <div className={`h-full rounded-full ${isLive ? 'bg-cyan-500 w-full' : 'bg-slate-700 w-0 transition-all duration-500'}`} />
          </div>
          {/* Playhead at right when live */}
          {isLive && (
            <div className="absolute right-0 w-3 h-6 bg-slate-200 rounded-sm shadow-md -ml-1.5" />
          )}
        </div>

        <div className="w-28 text-right">
          <span className="text-sm font-mono text-cyan-400">
            {isLoaded ? `T+${version}` : 'T+——'}
          </span>
        </div>
      </div>

      {/* Live event log — reads from world state version as a live indicator */}
      <div className="flex-1 mt-4 border border-slate-800 bg-slate-900/50 rounded-md p-3 overflow-y-auto">
        <p className="text-xs text-slate-500 font-mono mb-2">System Event Log</p>
        {isLoaded ? (
          <p className="text-[10px] text-slate-400 font-mono">
            [WORLD] State advanced to tick {version}
          </p>
        ) : (
          <p className="text-[10px] text-slate-600 font-mono animate-pulse">
            [{connectionStatus.toUpperCase()}] Waiting for world state...
          </p>
        )}
      </div>
    </div>
  );
});

BottomPanel.displayName = 'BottomPanel';
