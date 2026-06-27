from typing import List
from fastapi import APIRouter
from simulator.engine.core import simulation_engine
from simulator.schemas.api import SimulationStatusResponse, GenericResponse
from simulator.events.models import SimulationEvent
from simulator.publishers.bus import event_bus

router = APIRouter(prefix="/simulation", tags=["Simulation"])

@router.get("/status", response_model=SimulationStatusResponse)
async def get_status():
    """Get the current running status of the simulation engine."""
    return SimulationStatusResponse(
        is_running=simulation_engine.is_running,
        is_paused=simulation_engine.is_paused,
        active_generators=len(simulation_engine._generators)
    )

@router.get("/events", response_model=List[SimulationEvent])
async def get_recent_events():
    """Get the history of recent simulation events."""
    return event_bus.history()

@router.post("/start", response_model=GenericResponse)
async def start_simulation():
    """Start the simulation engine."""
    simulation_engine.start()
    return GenericResponse(success=True, message="Simulation started.")

@router.post("/stop", response_model=GenericResponse)
async def stop_simulation():
    """Stop the simulation engine."""
    simulation_engine.stop()
    return GenericResponse(success=True, message="Simulation stopped.")

@router.post("/pause", response_model=GenericResponse)
async def pause_simulation():
    """Pause the simulation engine."""
    simulation_engine.pause()
    return GenericResponse(success=True, message="Simulation paused.")

@router.post("/reset", response_model=GenericResponse)
async def reset_simulation():
    """Reset the simulation engine and the digital twin state."""
    simulation_engine.reset()
    return GenericResponse(success=True, message="Simulation reset.")
