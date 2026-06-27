from typing import List
from pydantic import BaseModel
from world_state.snapshot.models import WorldState

class WorldStateHistoryResponse(BaseModel):
    snapshots: List[WorldState]

class GenericResponse(BaseModel):
    success: bool
    message: str
