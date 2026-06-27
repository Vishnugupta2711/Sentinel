from typing import List, Dict, Any
from pydantic import BaseModel
from world_state.snapshot.models import WorldState

class GenericResponse(BaseModel):
    success: bool
    message: str

class TimelineEntryResponse(BaseModel):
    entry_id: str
    timestamp: str
    version: int
    simulation_tick: int
    metadata: Dict[str, Any]
    state: WorldState

class TimelineHistoryResponse(BaseModel):
    entries: List[TimelineEntryResponse]

class ReplayStatusResponse(BaseModel):
    is_playing: bool
    current_index: int
    total_entries: int
