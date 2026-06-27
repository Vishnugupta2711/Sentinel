from typing import List, Optional
from pydantic import BaseModel, Field
from world.models.base import BaseWorldObject, PhysicalObject
from world.models.enums import (
    SensorType, WorkerRole, WorkerStatus, HazardType, HazardSeverity, ValveState, Status
)

class Plant(BaseWorldObject):
    address: Optional[str] = None
    manager: Optional[str] = None
    capacity: Optional[float] = None

class Building(PhysicalObject):
    floors: int = 1
    max_occupancy: Optional[int] = None

class Zone(PhysicalObject):
    hazard_level: str = "LOW"
    max_capacity: Optional[int] = None
    current_occupancy: int = 0

class Sensor(PhysicalObject):
    sensor_type: SensorType
    current_value: float = 0.0
    unit: str
    threshold: float
    last_updated: str

class Worker(PhysicalObject):
    role: WorkerRole
    department: str
    current_ppe: List[str] = Field(default_factory=list)
    shift: str
    worker_status: WorkerStatus = WorkerStatus.ACTIVE

class Vehicle(PhysicalObject):
    vehicle_type: str
    driver_id: Optional[str] = None
    capacity: Optional[float] = None

class Camera(PhysicalObject):
    direction: float = 0.0  # angle in degrees
    coverage_radius: float = 0.0

class Equipment(PhysicalObject):
    equipment_type: str
    manufacturer: str
    criticality: str = "LOW"
    maintenance_status: Status = Status.ONLINE

class Pipeline(PhysicalObject):
    source_id: str
    destination_id: str
    material: str
    pressure_rating: float

class Valve(PhysicalObject):
    pipeline_id: str
    current_state: ValveState = ValveState.OPEN
    health: float = 100.0  # percentage

class Permit(BaseWorldObject):
    permit_type: str
    assigned_to: str
    valid_from: str
    valid_until: str
    approved_by: Optional[str] = None

class Hazard(PhysicalObject):
    hazard_type: HazardType
    severity: HazardSeverity
    radius: float
    is_active: bool = True

class EmergencyExit(PhysicalObject):
    is_blocked: bool = False
    capacity: Optional[int] = None

class WeatherState(BaseModel):
    temperature: float = 20.0
    humidity: float = 50.0
    wind_speed: float = 0.0
    wind_direction: float = 0.0
    condition: str = "CLEAR"
    last_updated: str
