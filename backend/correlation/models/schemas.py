from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from utils.uuid import generate_uuid
from utils.datetime import format_iso, utc_now


class CorrelationMethod(str, Enum):
    TEMPORAL_WINDOW = "temporal_window"
    ZONE_OVERLAP = "zone_overlap"
    SEVERITY_ESCALATION = "severity_escalation"
    CHAIN_REACTION = "chain_reaction"


class CompoundRiskLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AgentContribution(BaseModel):
    agent_name: str
    signal_type: str
    current_severity: str
    current_score: float
    trend: str = "stable"


class TemporalWindow(BaseModel):
    window_start: str
    window_end: str
    overlapping_signals: List[str]


class CompoundRiskAssessment(BaseModel):
    risk_id: str = Field(default_factory=generate_uuid)
    correlation_id: str
    level: CompoundRiskLevel
    score: float
    primary_zone: Optional[str] = None
    description: str
    method: CorrelationMethod
    contributing_signals: List[AgentContribution] = Field(default_factory=list)
    temporal_window: Optional[TemporalWindow] = None
    recommendations: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CorrelationResult(BaseModel):
    correlation_id: str = Field(default_factory=generate_uuid)
    assessments: List[CompoundRiskAssessment] = Field(default_factory=list)
    signal_count: int = 0
    agent_count: int = 0
    highest_level: CompoundRiskLevel = CompoundRiskLevel.NONE
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
