from typing import Optional
from pydantic import BaseModel, Field
from utils.datetime import format_iso, utc_now


class TimelineEntry(BaseModel):
    version: int
    simulation_tick: int
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    world_state_version: Optional[int] = None
