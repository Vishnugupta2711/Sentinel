from typing import List
from pydantic import BaseModel, Field
from world.models.entities import (
    Plant, Building, Zone, Sensor, Worker, Vehicle, Camera, Equipment,
    Pipeline, Valve, Permit, Hazard, EmergencyExit, WeatherState
)
from utils.datetime import format_iso, utc_now

class PlantState(BaseModel):
    """The root state object representing the entire digital twin of the industrial plant."""
    current_time: str = Field(default_factory=lambda: format_iso(utc_now()))
    weather: WeatherState
    
    plant: Plant
    buildings: List[Building] = Field(default_factory=list)
    zones: List[Zone] = Field(default_factory=list)
    workers: List[Worker] = Field(default_factory=list)
    sensors: List[Sensor] = Field(default_factory=list)
    equipment: List[Equipment] = Field(default_factory=list)
    pipelines: List[Pipeline] = Field(default_factory=list)
    valves: List[Valve] = Field(default_factory=list)
    vehicles: List[Vehicle] = Field(default_factory=list)
    hazards: List[Hazard] = Field(default_factory=list)
    permits: List[Permit] = Field(default_factory=list)
    cameras: List[Camera] = Field(default_factory=list)
    emergency_exits: List[EmergencyExit] = Field(default_factory=list)
