from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from utils.datetime import format_iso, utc_now
from utils.uuid import generate_uuid
from simulator.events.enums import EventType, EventSeverity

class SimulationEvent(BaseModel):
    """Core event structure for the internal Event Bus."""
    event_id: str = Field(default_factory=generate_uuid)
    event_type: EventType
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    source: str
    severity: EventSeverity = EventSeverity.INFO
    zone_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
