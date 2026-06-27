from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class DemoStatus(str, Enum):
    IDLE = "IDLE"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"

class DemoActionType(str, Enum):
    UPDATE_STATE = "UPDATE_STATE"
    EMIT_VISION = "EMIT_VISION"
    TRIGGER_PLAN = "TRIGGER_PLAN"

class DemoAction(BaseModel):
    type: DemoActionType
    payload: Dict[str, Any]

class ScenarioStage(BaseModel):
    stage_num: int
    name: str
    narration: str
    actions: List[DemoAction]

class Scenario(BaseModel):
    scenario_id: str
    name: str
    description: str
    stages: List[ScenarioStage]

class DemoState(BaseModel):
    status: DemoStatus
    active_scenario_id: Optional[str]
    current_stage: int
    playback_speed: float
