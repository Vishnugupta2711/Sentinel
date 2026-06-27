from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from world.models.entities import (
    Worker, Sensor, Equipment, Pipeline, Valve, Permit,
    WeatherState, Hazard, Camera, Vehicle, Plant, Building, Zone, EmergencyExit
)
from utils.datetime import format_iso, utc_now
from utils.uuid import generate_uuid

class WorldState(BaseModel):
    """
    Immutable snapshot of the entire plant at a specific tick in time.
    """
    snapshot_id: str = Field(default_factory=generate_uuid)
    version: int
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    
    # Core Infrastructure
    plant: Optional[Plant] = None
    buildings: List[Building] = Field(default_factory=list)
    zones: List[Zone] = Field(default_factory=list)
    
    # Active Assets
    workers: List[Worker] = Field(default_factory=list)
    sensors: List[Sensor] = Field(default_factory=list)
    equipment: List[Equipment] = Field(default_factory=list)
    pipelines: List[Pipeline] = Field(default_factory=list)
    valves: List[Valve] = Field(default_factory=list)
    cameras: List[Camera] = Field(default_factory=list)
    vehicles: List[Vehicle] = Field(default_factory=list)
    emergency_exits: List[EmergencyExit] = Field(default_factory=list)
    
    # Conditions & Operations
    weather: Optional[WeatherState] = None
    permits: List[Permit] = Field(default_factory=list)
    hazards: List[Hazard] = Field(default_factory=list)
    
    # Computed metrics
    zone_occupancy: Dict[str, int] = Field(default_factory=dict)
    plant_status: str = "NORMAL"

    model_config = ConfigDict(frozen=True)
