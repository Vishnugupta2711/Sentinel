from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from utils.uuid import generate_uuid
from utils.datetime import format_iso, utc_now

class ActionType(str, Enum):
    DELAY_PERMIT = "DELAY_PERMIT"
    CANCEL_PERMIT = "CANCEL_PERMIT"
    INCREASE_VENTILATION = "INCREASE_VENTILATION"
    DECREASE_PRESSURE = "DECREASE_PRESSURE"
    CLOSE_VALVE = "CLOSE_VALVE"
    OPEN_VALVE = "OPEN_VALVE"
    EMERGENCY_SHUTDOWN = "EMERGENCY_SHUTDOWN"
    EVACUATE_ZONE = "EVACUATE_ZONE"
    REDUCE_WORKER_COUNT = "REDUCE_WORKER_COUNT"
    DISPATCH_MAINTENANCE = "DISPATCH_MAINTENANCE"
    INCREASE_INSPECTION = "INCREASE_INSPECTION"
    PAUSE_EQUIPMENT = "PAUSE_EQUIPMENT"
    REDUCE_TEMPERATURE = "REDUCE_TEMPERATURE"
    ACTIVATE_BACKUP_SYSTEM = "ACTIVATE_BACKUP_SYSTEM"

class InterventionActionSchema(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    description: str
    action_type: ActionType
    target_id: str # ID of the Permit, Zone, Valve, etc.
    estimated_duration_minutes: int
    estimated_cost_usd: float
    expected_risk_reduction_percentage: float
    production_impact_percentage: float
    confidence: float

class ReasoningTrace(BaseModel):
    why_this_plan: str
    why_alternatives_rejected: List[str]
    expected_outcome: str

class PlanEvaluation(BaseModel):
    total_risk_reduction: float
    total_cost: float
    estimated_downtime_minutes: int
    workers_protected: int
    overall_confidence: float

class InterventionPlan(BaseModel):
    plan_id: str = Field(default_factory=generate_uuid)
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    scenario_name: str
    target_risk_id: str
    target_risk_name: str
    target_risk_probability: float
    actions: List[InterventionActionSchema]
    evaluation: PlanEvaluation
    reasoning: ReasoningTrace
    score: float # Optimizer score used for ranking

class RecommendedPlanDTO(BaseModel):
    actions: List[str]
    predicted_probability: float
    downtime_minutes: int
    estimated_cost: float
    workers_protected: int
    confidence: float

class PlannerResponseDTO(BaseModel):
    risk: str
    current_probability: float
    recommended_plan: RecommendedPlanDTO
