from typing import List
from pydantic import BaseModel, Field
import datetime

class EvidenceItem(BaseModel):
    id: str
    source: str
    timestamp: str
    description: str
    confidence: float
    traceability_link: str

class TimelineNode(BaseModel):
    t_minus: str
    timestamp: str
    event_type: str
    description: str
    related_evidence_ids: List[str]

class EventCorrelation(BaseModel):
    source_event: str
    target_event: str
    relationship: str
    confidence: float

class RootCause(BaseModel):
    category: str
    methodology: str  # e.g., "5 Whys", "Fault Tree"
    description: str
    confidence: float
    evidence_ids: List[str]

class DecisionAudit(BaseModel):
    engine_name: str
    decision_made: str
    latency_ms: float
    accuracy_score: float
    alternative_actions_considered: List[str]

class ComplianceFinding(BaseModel):
    framework: str
    section: str
    evidence_ids: List[str]
    corrective_action: str
    status: str

class ImpactAssessment(BaseModel):
    lives_protected: int
    downtime_prevented_hours: int
    financial_loss_prevented: float
    environmental_impact_avoided: str
    insurance_savings: float
    regulatory_penalties_avoided: float
    equipment_protected: List[str]

class Recommendation(BaseModel):
    category: str  # Engineering, Admin, Training, Maintenance, Policy
    priority: str
    owner: str
    description: str
    expected_risk_reduction: str

class InvestigationReport(BaseModel):
    investigation_id: str = Field(default_factory=lambda: f"INV-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    incident_type: str
    status: str
    generated_at: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    
    evidence: List[EvidenceItem]
    timeline: List[TimelineNode]
    correlations: List[EventCorrelation]
    root_causes: List[RootCause]
    decisions: List[DecisionAudit]
    compliance: List[ComplianceFinding]
    impact: ImpactAssessment
    recommendations: List[Recommendation]
    
    executive_summary: str = ""
    technical_appendix: str = ""
