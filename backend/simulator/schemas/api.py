from pydantic import BaseModel

class SimulationStatusResponse(BaseModel):
    is_running: bool
    is_paused: bool
    active_generators: int

class GenericResponse(BaseModel):
    success: bool
    message: str
