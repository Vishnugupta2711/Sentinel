from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel

class NodeType(str, Enum):
    PLANT = "Plant"
    BUILDING = "Building"
    ZONE = "Zone"
    WORKER = "Worker"
    SENSOR = "Sensor"
    EQUIPMENT = "Equipment"
    PIPELINE = "Pipeline"
    VALVE = "Valve"
    PERMIT = "Permit"
    HAZARD = "Hazard"
    VEHICLE = "Vehicle"
    CAMERA = "Camera"
    EMERGENCY_EXIT = "EmergencyExit"
    WEATHER = "Weather"

class Node(BaseModel):
    id: str
    type: NodeType
    label: str
    attributes: Dict[str, Any] = {}
