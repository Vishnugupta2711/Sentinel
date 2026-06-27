from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import datetime

class RootCause(BaseModel):
    category: str  # Human, Equipment, Environment, Process, Permit, Management
    description: str
    confidence: float
    evidence_ids: List[str]

class Evidence(BaseModel):
    id: str
    source: str  # e.g., "Chronos", "Sensor_1", "Vision"
    description: str
    confidence: float
    timestamp: Optional[str] = None

class ComplianceMapping(BaseModel):
    regulation: str  # OISD, Factories Act, DGMS, etc.
    section: str
    requirement: str
    status: str
    corrective_action: str

class LessonsLearned(BaseModel):
    immediate_actions: List[str]
    short_term: List[str]
    long_term: List[str]
    training: List[str]
    engineering: List[str]
    maintenance: List[str]
    policy: List[str]

class BusinessImpact(BaseModel):
    workers_protected: int
    downtime_prevented_hours: int
    financial_loss_prevented: float
    environmental_impact_avoided: str
    regulatory_penalties_avoided: float
    estimated_insurance_savings: float

class TimelineEvent(BaseModel):
    timestamp: str
    t_minus: str
    event_type: str
    description: str

class DebriefReport(BaseModel):
    report_id: str
    incident_title: str
    incident_type: str
    incident_severity: str
    affected_zone: str
    affected_workers: int
    estimated_probability: float
    outcome: str
    key_decisions: List[str]
    estimated_loss_prevented: float
    decision_time_ms: float
    
    root_causes: List[RootCause]
    timeline: List[TimelineEvent]
    ai_explanation: Dict[str, str]
    evidence: List[Evidence]
    compliance: List[ComplianceMapping]
    lessons_learned: LessonsLearned
    business_impact: BusinessImpact
    
    generated_at: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")
