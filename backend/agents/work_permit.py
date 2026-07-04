from typing import List, Optional
from datetime import datetime
import structlog
from agents.base import BaseAgent, AgentSignal
from world_state.snapshot.models import WorldState
from world.models.enums import HazardType
from intelligence.contracts.context import IntelligenceContext

logger = structlog.get_logger(__name__)

HOT_WORK_TYPES = {"HOT_WORK", "WELDING", "GRINDING", "CUTTING", "BRAZING"}
CONFINED_SPACE_TYPES = {"CONFINED_SPACE", "TANK_ENTRY", "EXCAVATION"}


class WorkPermitAgent(BaseAgent):
    def name(self) -> str:
        return "work_permit"

    def priority(self) -> int:
        return 10

    async def analyze(self, world_state: Optional[WorldState], context: IntelligenceContext) -> List[AgentSignal]:
        signals: List[AgentSignal] = []
        if not world_state:
            return signals

        active_permits = [p for p in world_state.permits if hasattr(p, 'valid_until')]
        if not active_permits:
            return signals

        active_hazards_by_zone: dict = {}
        for h in world_state.hazards:
            if h.is_active and h.hazard_type in (HazardType.GAS_LEAK, HazardType.FIRE):
                zone = h.zone_id if hasattr(h, 'zone_id') and h.zone_id else None
                if zone:
                    active_hazards_by_zone.setdefault(zone, []).append(h)

        for permit in active_permits:
            permit_type = (permit.permit_type or "").upper()
            zone_id = None
            if hasattr(permit, 'zone_id') and permit.zone_id:
                zone_id = permit.zone_id
            elif hasattr(permit, 'assigned_to'):
                for w in world_state.workers:
                    if w.id == permit.assigned_to or (hasattr(w, 'name') and w.name == permit.assigned_to):
                        zone_id = w.zone_id
                        break

            if permit_type in HOT_WORK_TYPES:
                severity = "LOW"
                score = 10.0
                description = f"Hot work permit active: {permit.permit_type}"

                if zone_id and zone_id in active_hazards_by_zone:
                    for hazard in active_hazards_by_zone[zone_id]:
                        if hazard.hazard_type == HazardType.GAS_LEAK:
                            severity = "CRITICAL"
                            score = 95.0
                            description = f"CRITICAL: Hot work ({permit.permit_type}) active in {zone_id} with active gas leak!"
                        elif hazard.hazard_type == HazardType.FIRE:
                            severity = "HIGH"
                            score = 80.0
                            description = f"HIGH: Hot work ({permit.permit_type}) active in {zone_id} with fire hazard present"
                else:
                    for zone in world_state.zones:
                        if zone_id and zone.id == zone_id and hasattr(zone, 'hazard_level') and zone.hazard_level in ("HIGH", "CRITICAL"):
                            severity = "MEDIUM"
                            score = 40.0
                            description = f"Hot work in high-hazard zone {zone_id}"
                            break

                signals.append(AgentSignal(
                    agent_name="work_permit",
                    signal_type="HOT_WORK_ACTIVE",
                    severity=severity,
                    zone_id=zone_id,
                    description=description,
                    score=score,
                    metadata={
                        "permit_id": permit.id if hasattr(permit, 'id') else str(id(permit)),
                        "permit_type": permit.permit_type,
                        "zone_id": zone_id,
                        "is_overlapping_hazard": zone_id in active_hazards_by_zone,
                    }
                ))

            if permit_type in CONFINED_SPACE_TYPES:
                gas_hazards_in_zone = []
                if zone_id and zone_id in active_hazards_by_zone:
                    gas_hazards_in_zone = [h for h in active_hazards_by_zone[zone_id] if h.hazard_type == HazardType.GAS_LEAK]

                if gas_hazards_in_zone:
                    signals.append(AgentSignal(
                        agent_name="work_permit",
                        signal_type="CONFINED_SPACE_GAS_RISK",
                        severity="CRITICAL",
                        zone_id=zone_id,
                        description=f"CRITICAL: Confined space entry ({permit.permit_type}) in {zone_id} with active toxic gas hazard",
                        score=92.0,
                        metadata={
                            "permit_id": permit.id if hasattr(permit, 'id') else str(id(permit)),
                            "permit_type": permit.permit_type,
                            "zone_id": zone_id,
                            "gas_hazards": len(gas_hazards_in_zone),
                        }
                    ))
                else:
                    signals.append(AgentSignal(
                        agent_name="work_permit",
                        signal_type="CONFINED_SPACE_ACTIVE",
                        severity="MEDIUM",
                        zone_id=zone_id,
                        description=f"Confined space entry active: {permit.permit_type} in {zone_id or 'unknown zone'}",
                        score=25.0,
                        metadata={
                            "permit_id": permit.id if hasattr(permit, 'id') else str(id(permit)),
                            "permit_type": permit.permit_type,
                            "zone_id": zone_id,
                        }
                    ))

        return signals


work_permit_agent = WorkPermitAgent()
