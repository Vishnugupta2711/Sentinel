from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from utils.datetime import format_iso, utc_now
from utils.uuid import generate_uuid
from world.models.enums import Status

class BaseWorldObject(BaseModel):
    """The foundational attributes for any object in the Industrial World Model."""
    id: str = Field(default_factory=generate_uuid)
    name: str
    description: Optional[str] = None
    status: Status = Status.ONLINE
    created_at: str = Field(default_factory=lambda: format_iso(utc_now()))
    updated_at: str = Field(default_factory=lambda: format_iso(utc_now()))
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PhysicalObject(BaseWorldObject):
    """An object that has a physical presence in the world."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    zone_id: Optional[str] = None
    building_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
