from pydantic import BaseModel, Field
from typing import List
from enum import Enum
from world_state.snapshot.models import WorldState

class ScenarioType(str, Enum):
    BEST_CASE = "BEST_CASE"
    NORMAL = "NORMAL"
    WORST_CASE = "WORST_CASE"

class ConfidenceMetrics(BaseModel):
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    data_quality: float = Field(..., ge=0.0, le=1.0)
    historical_similarity: float = Field(..., ge=0.0, le=1.0)
    coverage_score: float = Field(..., ge=0.0, le=1.0)

class ReasoningTrace(BaseModel):
    description: str
    influencing_events: List[str] = Field(default_factory=list)
    contributing_sensors: List[str] = Field(default_factory=list)
    matched_timeline_patterns: List[str] = Field(default_factory=list)

class ScenarioPrediction(BaseModel):
    scenario_type: ScenarioType
    probability: float = Field(..., ge=0.0, le=1.0)
    expected_risk: float = Field(..., ge=0.0, le=1.0)
    confidence: ConfidenceMetrics
    predicted_world_state: WorldState
    reasoning: ReasoningTrace

class PredictionResult(BaseModel):
    prediction_id: str
    generated_at: str
    forecast_horizon_minutes: int
    scenarios: List[ScenarioPrediction]
    supporting_events: List[str] = Field(default_factory=list)
