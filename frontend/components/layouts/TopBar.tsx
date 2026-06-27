import { Activity, Bell, ShieldAlert, User, Zap, WifiOff, Wifi } from 'lucide-react';
import React from 'react';
import { useWorldStateStore } from '../../store/worldState';
import { DemoControls } from '../widgets/DemoControls';
import { JudgeModeToggle } from '../judge/JudgeModeToggle';
import { DebriefToggle } from '../debrief/DebriefToggle';

export const TopBar = React.memo(() => {
  const isLoaded = useWorldStateStore((state) => state.isLoaded);
  const version = useWorldStateStore((state) => state.version);
  const connectionStatus = useWorldStateStore((state) => state.connectionStatus);

  const statusConfig = {
    connected:    { label: 'System Online',  dot: 'bg-emerald-500 animate-pulse', icon: Wifi,    iconColor: 'text-emerald-400' },
    connecting:   { label: 'Connecting...',  dot: 'bg-amber-500 animate-pulse',   icon: Wifi,    iconColor: 'text-amber-400'   },
    disconnected: { label: 'Disconnected',   dot: 'bg-slate-600',                 icon: WifiOff, iconColor: 'text-slate-500'   },
    error:        { label: 'Connection Error', dot: 'bg-red-500 animate-pulse',   icon: WifiOff, iconColor: 'text-red-400'     },
  }[connectionStatus] ?? { label: 'Connecting...', dot: 'bg-amber-500', icon: Wifi, iconColor: 'text-amber-400' };

  return (
    <div className="h-full px-6 flex items-center justify-between">
      {/* Left: Brand */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-sm bg-cyan-500/10 border border-cyan-500/50 flex items-center justify-center">
          <Zap className="w-5 h-5 text-cyan-400" />
        </div>
        <div>
          <h1 className="font-bold text-lg tracking-wider text-slate-100 leading-none">SENTINEL</h1>
          <p className="text-[10px] uppercase tracking-widest text-cyan-500 font-semibold mt-1">Mission Control</p>
        </div>
      </div>

      {/* Center: System Status */}
      <div className="flex items-center gap-6 px-8 py-2 rounded-full bg-slate-900 border border-slate-800">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${statusConfig.dot}`} />
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            {statusConfig.label}
          </span>
        </div>
        <div className="w-px h-4 bg-slate-700" />
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-slate-400" />
          <span className="text-xs font-mono text-slate-300">
            {isLoaded ? `TICK: ${version.toString().padStart(6, '0')}` : 'TICK: ——————'}
          </span>
        </div>
      </div>

      {/* Demo Controls + Judge Toggle */}
      <div className="ml-6 flex-1 flex justify-center gap-6">
        <JudgeModeToggle />
        <DemoControls />
        <DebriefToggle />
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-4">
        <button className="px-4 py-1.5 bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 rounded-md text-xs font-bold uppercase tracking-wider transition-colors flex items-center gap-2">
          <ShieldAlert className="w-4 h-4" />
          Emergency
        </button>
        <div className="w-px h-6 bg-slate-800 mx-2" />
        <button className="relative p-2 text-slate-400 hover:text-slate-200 transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-cyan-500" />
        </button>
        <button className="p-2 text-slate-400 hover:text-slate-200 transition-colors">
          <User className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
});

TopBar.displayName = 'TopBar';
