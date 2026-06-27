from typing import List, Dict, Any
from pydantic import BaseModel

class GenericResponse(BaseModel):
    success: bool
    message: str

class ModuleStatus(BaseModel):
    name: str
    version: str
    health: str
    state: str
    priority: int

class IntelligenceStatusResponse(BaseModel):
    engine_status: Dict[str, Any]
    active_pipelines: List[str]
    
class IntelligenceMetricsResponse(BaseModel):
    metrics: Dict[str, Any]
