from fastapi import APIRouter
from typing import List
from compliance.models.schemas import ComplianceViolation, ComplianceStatus, ExpectedViolationDTO
from compliance.engine.core import compliance_engine

router = APIRouter(prefix="/compliance", tags=["Compliance Engine"])

def _map_violation_to_dto(v: ComplianceViolation) -> ExpectedViolationDTO:
    evidence_strings = []
    if v.evidence.supporting_sensors:
        evidence_strings.append(f"Sensors: {', '.join(v.evidence.supporting_sensors)}")
    if v.evidence.supporting_permits:
        evidence_strings.append(f"Permits: {', '.join(v.evidence.supporting_permits)}")
    if v.evidence.supporting_workers:
        evidence_strings.append(f"Workers: {', '.join(v.evidence.supporting_workers)}")
        
    recommendation = ""
    if v.corrective_actions:
        recommendation = v.corrective_actions[0].description

    return ExpectedViolationDTO(
        violation_id=v.violation_id,
        severity=v.severity.value,
        regulation=v.regulation_reference.document_id,
        section=v.regulation_reference.section,
        issue=v.description,
        evidence=evidence_strings,
        recommendation=recommendation
    )

@router.get("/status", response_model=ComplianceStatus)
async def get_compliance_status():
    return compliance_engine.get_status()

@router.get("/violations", response_model=List[ExpectedViolationDTO])
async def get_active_violations():
    return [_map_violation_to_dto(v) for v in compliance_engine.get_active_violations()]

@router.get("/reports", response_model=List[ExpectedViolationDTO]) # simplified report to just violations for now
async def get_compliance_reports():
    return [_map_violation_to_dto(v) for v in compliance_engine.get_history()]

@router.post("/validate")
async def trigger_validation():
    # Typically driven by pipeline
    return {"status": "USE_PIPELINE", "active_violations": len(compliance_engine.active_violations)}
