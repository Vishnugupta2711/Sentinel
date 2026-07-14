from fastapi import APIRouter
from typing import List
from vision.models.schemas import VisionEvent
from vision.engine.core import vision_engine

from vision.edge_manager import edge_manager, EdgeDevice

router = APIRouter(prefix="/vision", tags=["Vision Engine"])

@router.post("/cameras", response_model=EdgeDevice)
async def register_camera(device: EdgeDevice):
    return edge_manager.register_device(device)

@router.get("/streams", response_model=List[EdgeDevice])
async def get_streams():
    return edge_manager.list_devices()

@router.get("/events", response_model=List[VisionEvent])
async def get_vision_events():
    return vision_engine.get_events()

@router.post("/analyze")
async def trigger_analysis():
    return {"status": "Analysis triggered (Mock)"}

@router.get("/analytics")
async def get_analytics():
    return {"status": "Analytics placeholder"}
