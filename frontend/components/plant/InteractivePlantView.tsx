import React, { useMemo } from 'react';
import { useWorldStateStore } from '../../store/worldState';

const HAZARD_COLORS: Record<string, { bg: string; border: string; label: string; glow: string }> = {
  CRITICAL: { bg: 'bg-red-500/10',    border: 'border-red-500/50',    label: 'text-red-400',    glow: 'shadow-[inset_0_0_20px_rgba(239,68,68,0.15)]'   },
  HIGH:     { bg: 'bg-amber-500/10',  border: 'border-amber-500/50',  label: 'text-amber-400',  glow: 'shadow-[inset_0_0_12px_rgba(245,158,11,0.10)]'  },
  MEDIUM:   { bg: 'bg-yellow-500/5',  border: 'border-yellow-500/30', label: 'text-yellow-400', glow: '' },
  LOW:      { bg: 'bg-slate-800/40',  border: 'border-slate-700/50',  label: 'text-slate-400',  glow: '' },
};

export const InteractivePlantView = React.memo(() => {
  const zones    = useWorldStateStore((state) => state.zones);
  const workers  = useWorldStateStore((state) => state.workers);
  const isLoaded = useWorldStateStore((state) => state.isLoaded);
  const connectionStatus = useWorldStateStore((state) => state.connectionStatus);

  console.log("InteractivePlantView rendered!");

  // PERF: Precompute zone → workers map once per workers update
  // Avoids O(W×Z) inline filter inside the zone render loop
  const workersByZone = useMemo(() => {
    const map: Record<string, typeof workers> = {};
    for (const w of workers) {
      if (!map[w.zone_id]) map[w.zone_id] = [];
      map[w.zone_id].push(w);
    }
    return map;
  }, [workers]);

  // Loading state
  if (!isLoaded) {
    const isError = connectionStatus === 'error';
    return (
      <div className="flex-1 flex items-center justify-center absolute inset-0">
        <div className="flex flex-col items-center gap-4">
          {isError ? (
            <>
              <div className="w-10 h-10 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center">
                <span className="text-red-400 text-lg">!</span>
              </div>
              <p className="text-xs text-red-400 font-mono tracking-widest uppercase">Backend Unreachable — Retrying…</p>
            </>
          ) : (
            <>
              <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-slate-500 font-mono tracking-widest uppercase">
                {connectionStatus === 'connecting' ? 'Connecting to World State…' : 'HELLO VISHNU!'}
              </p>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="absolute inset-0 p-8 overflow-hidden">

      {/* Background grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_70%,transparent_100%)] opacity-30 pointer-events-none" />

      <div className="relative w-full h-full border border-slate-800/50 rounded-xl bg-slate-900/20 shadow-2xl overflow-hidden p-6">

        {/* Header */}
        <div className="absolute top-4 left-4">
          <h2 className="text-sm font-bold text-slate-200 tracking-wider">Facility Overview Map</h2>
          <p className="text-[10px] text-cyan-500 uppercase tracking-widest">Live Feed Active</p>
        </div>

        {/* Zone count badge */}
        <div className="absolute top-4 right-4 flex items-center gap-3 text-[10px] font-mono text-slate-500">
          <span>{zones.length} zones</span>
          <span>·</span>
          <span className="text-emerald-400">{workers.length} workers</span>
        </div>

        {/* Zone Grid */}
        <div className="mt-12 grid grid-cols-2 md:grid-cols-3 gap-4 h-[calc(100%-4rem)]">
          {zones.map((zone, idx) => {
            const colors = HAZARD_COLORS[zone.hazard_level] ?? HAZARD_COLORS.LOW;
            const zoneWorkers = workersByZone[zone.id] ?? [];
            const isLarge = idx === 0;

            return (
              <div
                key={zone.id}
                className={`relative border rounded-lg p-4 transition-all duration-300 overflow-hidden
                  ${isLarge ? 'col-span-2 row-span-2' : ''}
                  ${colors.bg} ${colors.border} ${colors.glow}
                  hover:brightness-110`}
              >
                <div className="flex items-start justify-between">
                  <h3 className={`text-xs font-bold uppercase tracking-widest ${colors.label}`}>
                    {zone.name}
                  </h3>
                  {zone.hazard_level !== 'LOW' && (
                    <span className={`text-[9px] px-1.5 py-0.5 rounded border font-bold uppercase ${colors.bg} ${colors.border} ${colors.label}`}>
                      {zone.hazard_level}
                    </span>
                  )}
                </div>

                {/* Workers inside zone */}
                {zoneWorkers.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {zoneWorkers.map(w => (
                      <div
                        key={w.id}
                        title={`${w.name} — ${w.role}`}
                        className="w-4 h-4 rounded-full bg-emerald-500 border border-emerald-900 shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-pulse"
                      />
                    ))}
                  </div>
                )}

                {/* Worker count */}
                {zoneWorkers.length > 0 && (
                  <p className="absolute bottom-2 right-3 text-[9px] text-slate-600 font-mono">
                    {zoneWorkers.length}w
                  </p>
                )}
              </div>
            );
          })}
        </div>

        {/* Empty state */}
        {zones.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-xs text-slate-600 font-mono">No zones loaded.</p>
          </div>
        )}
      </div>
    </div>
  );
});

InteractivePlantView.displayName = 'InteractivePlantView';
