from fastapi import APIRouter
from typing import List
from vision.models.schemas import VisionEvent
from vision.engine.core import vision_engine

router = APIRouter(prefix="/vision", tags=["Vision Engine"])

@router.post("/analyze")
async def trigger_analysis():
    # In a real system, this takes a frame or clip.
    # For MVP, we will inject a mock detection through the pipeline and generate an event.
    return {"status": "Analysis triggered (Mock)"}

@router.get("/events", response_model=List[VisionEvent])
async def get_vision_events():
    return vision_engine.get_events()

@router.get("/streams")
async def get_streams():
    return [{"camera_id": "cam_01", "status": "ONLINE", "fps": 30}]

@router.get("/analytics")
async def get_analytics():
    return {"status": "Analytics placeholder"}
