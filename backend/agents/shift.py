from typing import List, Optional, Dict
from datetime import datetime, timedelta, timezone
import structlog
from agents.base import BaseAgent, AgentSignal
from world_state.snapshot.models import WorldState
from intelligence.contracts.context import IntelligenceContext

logger = structlog.get_logger(__name__)

SHIFT_PATTERNS = {
    "DAY":   {"start": 6,  "end": 14},
    "EVENING": {"start": 14, "end": 22},
    "NIGHT": {"start": 22, "end": 6},
}


class ShiftAgent(BaseAgent):
    def name(self) -> str:
        return "shift"

    def priority(self) -> int:
        return 8

    async def analyze(self, world_state: Optional[WorldState], context: IntelligenceContext) -> List[AgentSignal]:
        signals: List[AgentSignal] = []
        if not world_state:
            return signals

        now = datetime.now(timezone.utc)
        current_hour = now.hour

        current_shift_name = self._detect_current_shift(current_hour)

        workers_by_shift: Dict[str, list] = {}
        for w in world_state.workers:
            s = w.shift if hasattr(w, 'shift') and w.shift else "UNKNOWN"
            workers_by_shift.setdefault(s, []).append(w)

        total_workers = len(world_state.workers)
        if total_workers == 0:
            return signals

        on_duty = workers_by_shift.get(current_shift_name, [])
        off_duty = total_workers - len(on_duty)

        if off_duty > 0 and len(on_duty) == 0:
            signals.append(AgentSignal(
                agent_name="shift",
                signal_type="SHIFT_UNDERSTAFFED",
                severity="HIGH",
                zone_id=None,
                description=f"Critical understaffing: {off_duty} workers assigned but 0 on duty for {current_shift_name} shift",
                score=85.0,
                metadata={
                    "current_shift": current_shift_name,
                    "expected_workers": total_workers,
                    "on_duty": len(on_duty),
                    "off_duty": off_duty,
                }
            ))

        zones_after_dark = set()
        for w in on_duty:
            if hasattr(w, 'zone_id') and w.zone_id:
                zones_after_dark.add(w.zone_id)

        if current_shift_name == "NIGHT":
            for zone_id in zones_after_dark:
                zone = next((z for z in world_state.zones if hasattr(z, 'id') and z.id == zone_id), None)
                if zone:
                    hazard_level = zone.hazard_level if hasattr(zone, 'hazard_level') else "LOW"
                    zone_workers = [w for w in on_duty if hasattr(w, 'zone_id') and w.zone_id == zone_id]
                    if hazard_level in ("HIGH", "CRITICAL") and len(zone_workers) < 2:
                        signals.append(AgentSignal(
                            agent_name="shift",
                            signal_type="NIGHT_ZONE_UNDERSTAFFED",
                            severity="MEDIUM",
                            zone_id=zone_id,
                            description=f"Night shift understaffing in {zone_id}: {len(zone_workers)} worker(s) in high-hazard zone",
                            score=55.0,
                            metadata={
                                "zone_id": zone_id,
                                "hazard_level": hazard_level,
                                "worker_count": len(zone_workers),
                                "current_shift": current_shift_name,
                            }
                        ))

        self._detect_handover_gaps(world_state, current_shift_name, signals)

        return signals

    def _detect_current_shift(self, hour: int) -> str:
        for name, pattern in SHIFT_PATTERNS.items():
            if pattern["start"] <= hour < pattern["end"]:
                return name
        return "NIGHT"

    def _detect_handover_gaps(self, world_state: WorldState, current_shift: str, signals: List[AgentSignal]) -> None:
        if current_shift in ("EVENING", "NIGHT"):
            prev_shift = {"EVENING": "DAY", "NIGHT": "EVENING"}.get(current_shift, "DAY")
            prev_workers = [w for w in world_state.workers if hasattr(w, 'shift') and w.shift == prev_shift]
            curr_workers = [w for w in world_state.workers if hasattr(w, 'shift') and w.shift == current_shift]

            if prev_workers and curr_workers:
                for pw in prev_workers:
                    for cw in curr_workers:
                        if (hasattr(pw, 'zone_id') and hasattr(cw, 'zone_id')
                                and pw.zone_id == cw.zone_id
                                and pw.zone_id is not None):
                            break

                prev_zones = {w.zone_id for w in prev_workers if hasattr(w, 'zone_id') and w.zone_id}
                curr_zones = {w.zone_id for w in curr_workers if hasattr(w, 'zone_id') and w.zone_id}
                missing_zones = prev_zones - curr_zones

                for zone_id in missing_zones:
                    signals.append(AgentSignal(
                        agent_name="shift",
                        signal_type="HANDOVER_GAP",
                        severity="MEDIUM",
                        zone_id=zone_id,
                        description=f"Shift handover gap in {zone_id}: covered during {prev_shift} but uncovered for {current_shift}",
                        score=45.0,
                        metadata={
                            "zone_id": zone_id,
                            "previous_shift": prev_shift,
                            "current_shift": current_shift,
                        }
                    ))


shift_agent = ShiftAgent()
