from typing import List
from compliance.rules.base import BaseComplianceRule
from compliance.models.schemas import (
    ComplianceViolation, ViolationSeverity, ComplianceEvidence, CorrectiveAction
)
from compliance.documents.kb import knowledge_base
from world_state.snapshot.models import WorldState
from world.models.enums import Status

class MissingPPERule(BaseComplianceRule):
    @property
    def rule_id(self) -> str:
        return "COMP-PPE-001"

    def evaluate(self, state: WorldState) -> List[ComplianceViolation]:
        violations = []
        # Find High/Critical hazard zones
        hazardous_zones = [z.id for z in state.zones if z.hazard_level in ["HIGH", "CRITICAL"]]
        
        required_ppe = {"Hard Hat", "Safety Goggles"}
        
        for worker in state.workers:
            if worker.zone_id in hazardous_zones and worker.status == Status.ONLINE:
                missing = required_ppe - set(worker.current_ppe)
                if missing:
                    evidence = ComplianceEvidence(
                        supporting_workers=[worker.id],
                        world_state_version=state.version
                    )
                    
                    corrective = CorrectiveAction(
                        description=f"Evacuate worker {worker.id} or provide {', '.join(missing)} immediately.",
                        priority="P1",
                        responsible_department="Safety",
                        deadline_minutes=5,
                        estimated_risk_reduction=50.0
                    )
                    
                    violation = ComplianceViolation(
                        severity=ViolationSeverity.MAJOR,
                        description=f"Worker {worker.name} missing required PPE ({', '.join(missing)}) in hazardous zone.",
                        regulation_reference=knowledge_base.get_internal_ppe_policy(),
                        evidence=evidence,
                        corrective_actions=[corrective]
                    )
                    violations.append(violation)
                    
        return violations

class OISDHotWorkGasRule(BaseComplianceRule):
    @property
    def rule_id(self) -> str:
        return "COMP-OISD-117-001"

    def evaluate(self, state: WorldState) -> List[ComplianceViolation]:
        violations = []
        
        high_gas_sensors = [s for s in state.sensors if s.sensor_type == "GAS" and s.status in [Status.WARNING, Status.CRITICAL]]
        active_hot_work = [p for p in state.permits if p.permit_type == "HOT_WORK" and p.status == Status.ONLINE]
        
        for permit in active_hot_work:
            worker = next((w for w in state.workers if w.id == permit.assigned_to), None)
            if worker and worker.zone_id:
                # Are there any high gas sensors in this zone?
                zone_sensors = [s for s in high_gas_sensors if s.zone_id == worker.zone_id]
                if zone_sensors:
                    evidence = ComplianceEvidence(
                        supporting_sensors=[s.id for s in zone_sensors],
                        supporting_permits=[permit.id],
                        supporting_workers=[worker.id],
                        world_state_version=state.version
                    )
                    
                    corrective = CorrectiveAction(
                        description=f"Revoke permit {permit.id} and halt hot work immediately.",
                        priority="P0",
                        responsible_department="Operations",
                        deadline_minutes=1,
                        estimated_risk_reduction=95.0
                    )
                    
                    violation = ComplianceViolation(
                        severity=ViolationSeverity.CRITICAL,
                        description="Active Hot Work permit in zone with combustible gas concentration.",
                        regulation_reference=knowledge_base.get_oisd_117_hot_work(),
                        evidence=evidence,
                        corrective_actions=[corrective]
                    )
                    violations.append(violation)
                    
        return violations
