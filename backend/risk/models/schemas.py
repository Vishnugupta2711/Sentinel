from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from utils.uuid import generate_uuid
from utils.datetime import format_iso, utc_now

class RiskType(str, Enum):
    GAS_LEAK = "GAS_LEAK"
    EXPLOSION = "EXPLOSION"
    FIRE = "FIRE"
    CHEMICAL_EXPOSURE = "CHEMICAL_EXPOSURE"
    PRESSURE_BUILDUP = "PRESSURE_BUILDUP"
    ELECTRICAL_HAZARD = "ELECTRICAL_HAZARD"
    CONFINED_SPACE = "CONFINED_SPACE"
    HEAT_STRESS = "HEAT_STRESS"
    EQUIPMENT_FAILURE = "EQUIPMENT_FAILURE"
    PERMIT_CONFLICT = "PERMIT_CONFLICT"
    SIMULTANEOUS_OPERATIONS = "SIMULTANEOUS_OPERATIONS"
    WORKER_FATIGUE = "WORKER_FATIGUE"
    PPE_VIOLATION = "PPE_VIOLATION"
    VEHICLE_COLLISION = "VEHICLE_COLLISION"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertPriority(str, Enum):
    P1 = "P1" # Immediate Life Threat
    P2 = "P2" # Critical Equipment Risk
    P3 = "P3" # Operational Risk
    P4 = "P4" # Advisory

class RootCause(BaseModel):
    description: str
    probability: float
    contributing_factors: List[str]

class RiskExplanation(BaseModel):
    why_detected: str
    contributing_factors: List[str]
    supporting_events: List[str]
    supporting_sensors: List[str]
    predicted_outcome: str
    historical_similarity: float = 0.0

class RiskConfidence(BaseModel):
    risk_confidence: float
    prediction_confidence: float
    data_quality: float
    evidence_score: float

class CompoundRiskAssessment(BaseModel):
    risk_id: str = Field(default_factory=generate_uuid)
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    risk_type: RiskType
    risk_score: float # 0 - 100
    risk_level: RiskLevel
    priority: AlertPriority
    
    explanation: RiskExplanation
    root_causes: List[RootCause]
    confidence: RiskConfidence
    
    affected_workers: List[str] # Worker IDs
    affected_zones: List[str] # Zone IDs
    recommended_actions: List[str]
    
    time_to_impact_minutes: Optional[int] = None
    hazard_spread_radius_meters: Optional[float] = None
