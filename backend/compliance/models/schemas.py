from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from utils.uuid import generate_uuid
from utils.datetime import format_iso, utc_now

class RegulationBody(str, Enum):
    OISD = "OISD"
    DGMS = "DGMS"
    FACTORIES_ACT = "FACTORIES_ACT"
    INTERNAL_SOP = "INTERNAL_SOP"

class ViolationSeverity(str, Enum):
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"

class RegulationReference(BaseModel):
    document_id: str
    body: RegulationBody
    title: str
    section: str
    clause_text: str

class CorrectiveAction(BaseModel):
    action_id: str = Field(default_factory=generate_uuid)
    description: str
    priority: str
    responsible_department: str
    deadline_minutes: int
    estimated_risk_reduction: float

class ComplianceEvidence(BaseModel):
    supporting_sensors: List[str] = Field(default_factory=list)
    supporting_permits: List[str] = Field(default_factory=list)
    supporting_workers: List[str] = Field(default_factory=list)
    supporting_timeline_events: List[str] = Field(default_factory=list)
    world_state_version: int

class ComplianceViolation(BaseModel):
    violation_id: str = Field(default_factory=generate_uuid)
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    severity: ViolationSeverity
    description: str
    regulation_reference: RegulationReference
    evidence: ComplianceEvidence
    corrective_actions: List[CorrectiveAction]

class ComplianceStatus(BaseModel):
    is_compliant: bool
    active_violations: int
    critical_violations: int
    last_audit_time: str

class ExpectedViolationDTO(BaseModel):
    violation_id: str
    severity: str
    regulation: str
    section: str
    issue: str
    evidence: List[str]
    recommendation: str
