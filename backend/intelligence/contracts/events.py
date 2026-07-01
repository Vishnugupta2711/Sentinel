from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from utils.datetime import format_iso, utc_now
from utils.uuid import generate_uuid


class EventType(str, Enum):
    WorkerMoved = "WorkerMoved"
    WorkerEnteredZone = "WorkerEnteredZone"
    WorkerExitedZone = "WorkerExitedZone"
    SensorUpdated = "SensorUpdated"
    WeatherChanged = "WeatherChanged"
    ValveStateChanged = "ValveStateChanged"
    EquipmentFailure = "EquipmentFailure"
    PermitIssued = "PermitIssued"
    PermitExpired = "PermitExpired"
    MaintenanceStarted = "MaintenanceStarted"
    MaintenanceCompleted = "MaintenanceCompleted"
    CameraStatusChanged = "CameraStatusChanged"
    HazardDetected = "HazardDetected"
    EmergencyRaised = "EmergencyRaised"


class EventSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class SimulationEvent(BaseModel):
    event_id: str = Field(default_factory=generate_uuid)
    event_type: EventType
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    source: str
    severity: EventSeverity = EventSeverity.INFO
    zone_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
