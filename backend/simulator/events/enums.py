from enum import Enum

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
