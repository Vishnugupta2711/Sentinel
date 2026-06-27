from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from utils.uuid import generate_uuid
from utils.datetime import format_iso, utc_now

class ObjectClass(str, Enum):
    WORKER = "WORKER"
    HELMET = "HELMET"
    SAFETY_VEST = "SAFETY_VEST"
    GLOVES = "GLOVES"
    FORKLIFT = "FORKLIFT"
    TRUCK = "TRUCK"
    VALVE = "VALVE"
    EQUIPMENT = "EQUIPMENT"
    SMOKE = "SMOKE"
    FIRE = "FIRE"

class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    confidence: float

class Detection(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    object_class: ObjectClass
    bbox: BoundingBox

class TrackedObject(BaseModel):
    track_id: str
    object_class: ObjectClass
    bbox: BoundingBox
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    associated_detections: List[Detection] = Field(default_factory=list) # e.g. Helmet inside Worker bbox

class VisionEventType(str, Enum):
    WORKER_DETECTED = "WORKER_DETECTED"
    WORKER_ENTERED_ZONE = "WORKER_ENTERED_ZONE"
    WORKER_EXITED_ZONE = "WORKER_EXITED_ZONE"
    MISSING_HELMET = "MISSING_HELMET"
    MISSING_VEST = "MISSING_VEST"
    UNSAFE_BEHAVIOUR = "UNSAFE_BEHAVIOUR"
    CROWD_ALERT = "CROWD_ALERT"
    FIRE_DETECTED = "FIRE_DETECTED"
    SMOKE_DETECTED = "SMOKE_DETECTED"
    FORKLIFT_NEAR_WORKER = "FORKLIFT_NEAR_WORKER"
    WORKER_FALL_DETECTED = "WORKER_FALL_DETECTED"

class VisionEvent(BaseModel):
    event_id: str = Field(default_factory=generate_uuid)
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    event_type: VisionEventType
    camera_id: str
    description: str
    severity: str = "INFO" # INFO, WARNING, CRITICAL
    tracked_object_ids: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
