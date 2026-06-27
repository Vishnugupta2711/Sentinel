import React from 'react';
import { useWorldStateStore } from '../../store/worldState';
import { Users, Map, Cpu, TriangleAlert } from 'lucide-react';

const HazardBadge = ({ level }: { level: string }) => {
  const config: Record<string, string> = {
    CRITICAL: 'bg-red-500/20 text-red-400 border-red-500/40',
    HIGH:     'bg-amber-500/20 text-amber-400 border-amber-500/40',
    MEDIUM:   'bg-yellow-500/20 text-yellow-400 border-yellow-500/40',
    LOW:      'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
  };
  const cls = config[level] ?? 'bg-slate-800 text-slate-500 border-slate-700';
  return (
    <span className={`text-[9px] px-1.5 py-0.5 rounded border font-bold uppercase tracking-wide ${cls}`}>
      {level}
    </span>
  );
};

// Skeleton loader for when data is not yet loaded
const SkeletonRow = () => (
  <div className="h-4 bg-slate-800 rounded animate-pulse w-full" />
);

export const LeftPanel = React.memo(() => {
  const workers = useWorldStateStore((state) => state.workers);
  const zones   = useWorldStateStore((state) => state.zones);
  const sensors = useWorldStateStore((state) => state.sensors);
  const hazards = useWorldStateStore((state) => state.hazards);
  const isLoaded = useWorldStateStore((state) => state.isLoaded);
  const connectionStatus = useWorldStateStore((state) => state.connectionStatus);

  const isError = connectionStatus === 'error';
  const isConnecting = !isLoaded && connectionStatus === 'connecting';

  if (isError) {
    return (
      <div className="flex flex-col h-full p-4 items-center justify-center gap-3">
        <div className="w-10 h-10 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center">
          <TriangleAlert className="w-5 h-5 text-red-400" />
        </div>
        <p className="text-xs text-red-400 font-medium text-center">Backend unreachable.<br/>Retrying…</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full p-4 space-y-4">
      <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Plant Hierarchy</h2>

      {/* Zones */}
      <div className="p-3 bg-slate-900/50 rounded-lg border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Map className="w-4 h-4 text-cyan-400" />
            <span className="text-sm font-medium text-slate-300">Zones</span>
          </div>
          <span className="text-xs font-mono text-cyan-400">{isLoaded ? zones.length : '—'}</span>
        </div>
        <div className="flex flex-col gap-1.5 mt-2">
          {isConnecting ? (
            <><SkeletonRow /><SkeletonRow /></>
          ) : (
            zones.slice(0, 5).map(z => (
              <div key={z.id} className="text-xs text-slate-500 flex justify-between items-center">
                <span className="truncate pr-2">{z.name}</span>
                <HazardBadge level={z.hazard_level} />
              </div>
            ))
          )}
        </div>
      </div>

      {/* Workers */}
      <div className="p-3 bg-slate-900/50 rounded-lg border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-medium text-slate-300">Workers Active</span>
          </div>
          <span className="text-xs font-mono text-emerald-400">{isLoaded ? workers.length : '—'}</span>
        </div>
        <div className="flex flex-col gap-1 mt-2">
          {isConnecting ? (
            <><SkeletonRow /><SkeletonRow /><SkeletonRow /></>
          ) : (
            workers.slice(0, 5).map(w => (
              <div key={w.id} className="text-xs text-slate-500 flex justify-between items-center">
                <span className="truncate pr-2">{w.name}</span>
                <span className="text-[10px] uppercase text-slate-600 shrink-0">{w.role}</span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Sensors */}
      <div className="p-3 bg-slate-900/50 rounded-lg border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-slate-300">Sensors</span>
          </div>
          <span className="text-xs font-mono text-blue-400">{isLoaded ? sensors.length : '—'}</span>
        </div>
        {isConnecting && <SkeletonRow />}
        {isLoaded && sensors.length === 0 && (
          <p className="text-xs text-slate-600 mt-1">No sensor data.</p>
        )}
        {isLoaded && sensors.slice(0, 3).map(s => (
          <div key={s.id} className="text-[10px] text-slate-600 flex justify-between mt-1">
            <span className="truncate pr-1">{s.name}</span>
            <span className="font-mono text-blue-500 shrink-0">{s.current_value.toFixed(1)}</span>
          </div>
        ))}
      </div>

      {/* Hazards */}
      <div className="p-3 bg-slate-900/50 rounded-lg border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <TriangleAlert className="w-4 h-4 text-amber-400" />
            <span className="text-sm font-medium text-slate-300">Active Hazards</span>
          </div>
          <span className={`text-xs font-mono ${hazards.length > 0 ? 'text-red-400' : 'text-amber-400'}`}>
            {isLoaded ? hazards.length : '—'}
          </span>
        </div>
        {isConnecting && <SkeletonRow />}
        {isLoaded && hazards.length === 0 && (
          <p className="text-xs text-slate-600 mt-1">No active hazards.</p>
        )}
        {isLoaded && hazards.slice(0, 3).map(h => (
          <div key={h.id} className="text-xs text-slate-500 flex justify-between items-center mt-1">
            <span className="truncate pr-2">{h.type.replace(/_/g, ' ')}</span>
            <HazardBadge level={h.severity} />
          </div>
        ))}
      </div>
    </div>
  );
});

LeftPanel.displayName = 'LeftPanel';
