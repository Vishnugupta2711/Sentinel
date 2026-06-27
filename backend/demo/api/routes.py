from fastapi import APIRouter, HTTPException
from typing import List
from demo.scenarios.data import SCENARIOS
from demo.director.core import demo_director
from demo.models.schemas import DemoState, Scenario
from pydantic import BaseModel

router = APIRouter(prefix="/demo", tags=["Demo Engine"])

class StartRequest(BaseModel):
    scenario_id: str

@router.get("/scenarios", response_model=List[Scenario])
async def get_scenarios():
    return SCENARIOS

@router.get("/state", response_model=DemoState)
async def get_state():
    return demo_director.get_state()

@router.post("/start")
async def start_demo(req: StartRequest):
    success = demo_director.start_scenario(req.scenario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"status": "started", "scenario_id": req.scenario_id}

@router.post("/next")
async def next_stage():
    demo_director.next_stage()
    return {"status": "advanced", "current_stage": demo_director.current_stage_num}

@router.post("/pause")
async def pause_demo():
    demo_director.pause()
    return {"status": "paused"}

@router.post("/reset")
async def reset_demo():
    demo_director.reset()
    return {"status": "reset"}
