from typing import Dict, Any, List
from pydantic import BaseModel, Field
from utils.datetime import format_iso, utc_now
from utils.uuid import generate_uuid
from intelligence.contracts.events import SimulationEvent

class IntelligenceContext(BaseModel):
    """
    Context passed to every Intelligence Module during execution.
    Provides immutable metadata about the current snapshot boundary.
    """
    request_id: str = Field(default_factory=generate_uuid)
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    world_state_version: int
    plant_id: str
    simulation_tick: int = 0
    current_events: List[SimulationEvent] = Field(default_factory=list)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
