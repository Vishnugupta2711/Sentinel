from enum import Enum

class Status(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    MAINTENANCE = "MAINTENANCE"

class SensorType(str, Enum):
    GAS = "GAS"
    TEMPERATURE = "TEMPERATURE"
    PRESSURE = "PRESSURE"
    HUMIDITY = "HUMIDITY"
    FLOW = "FLOW"
    VIBRATION = "VIBRATION"
    SMOKE = "SMOKE"

class WorkerRole(str, Enum):
    OPERATOR = "OPERATOR"
    SUPERVISOR = "SUPERVISOR"
    MAINTENANCE = "MAINTENANCE"
    SAFETY_OFFICER = "SAFETY_OFFICER"
    CONTRACTOR = "CONTRACTOR"

class WorkerStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ON_BREAK = "ON_BREAK"
    OFF_SHIFT = "OFF_SHIFT"
    EMERGENCY = "EMERGENCY"

class HazardType(str, Enum):
    GAS_LEAK = "GAS_LEAK"
    FIRE = "FIRE"
    SPILL = "SPILL"
    STRUCTURAL = "STRUCTURAL"
    ELECTRICAL = "ELECTRICAL"

class HazardSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ValveState(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PARTIAL = "PARTIAL"
    FAULT = "FAULT"
