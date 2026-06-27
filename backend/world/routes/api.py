from typing import List
from fastapi import APIRouter, HTTPException

from world.models.state import PlantState
from world.models.entities import (
    Zone, Worker, Sensor, Equipment, Pipeline, Camera, Hazard
)
from world.manager.manager import world_manager

router = APIRouter(prefix="/world", tags=["World"])


@router.get(
    "",
    response_model=PlantState,
    summary="Get Entire Plant State",
    description="Returns the complete digital twin representing the industrial plant, including all assets, buildings, zones, workers, and weather."
)
async def get_world_state():
    state = world_manager.get_state()
    if not state:
        raise HTTPException(status_code=503, detail="World state is not initialized.")
    return state


@router.get(
    "/zones",
    response_model=List[Zone],
    summary="Get All Zones",
    description="Returns a list of all defined zones within the plant."
)
async def get_zones():
    state = world_manager.get_state()
    if not state:
        return []
    return state.zones


@router.get(
    "/workers",
    response_model=List[Worker],
    summary="Get All Workers",
    description="Returns a list of all workers currently tracked in the plant."
)
async def get_workers():
    state = world_manager.get_state()
    if not state:
        return []
    return state.workers


@router.get(
    "/sensors",
    response_model=List[Sensor],
    summary="Get All Sensors",
    description="Returns a list of all sensors and their current readings."
)
async def get_sensors():
    state = world_manager.get_state()
    if not state:
        return []
    return state.sensors


@router.get(
    "/equipment",
    response_model=List[Equipment],
    summary="Get All Equipment",
    description="Returns a list of all registered industrial equipment."
)
async def get_equipment():
    state = world_manager.get_state()
    if not state:
        return []
    return state.equipment


@router.get(
    "/pipelines",
    response_model=List[Pipeline],
    summary="Get All Pipelines",
    description="Returns a list of all pipelines connecting infrastructure."
)
async def get_pipelines():
    state = world_manager.get_state()
    if not state:
        return []
    return state.pipelines


@router.get(
    "/cameras",
    response_model=List[Camera],
    summary="Get All Cameras",
    description="Returns a list of all CCTV cameras and their coverage."
)
async def get_cameras():
    state = world_manager.get_state()
    if not state:
        return []
    return state.cameras


@router.get(
    "/hazards",
    response_model=List[Hazard],
    summary="Get All Hazards",
    description="Returns a list of all currently active hazards in the plant."
)
async def get_hazards():
    state = world_manager.get_state()
    if not state:
        return []
    return state.hazards
