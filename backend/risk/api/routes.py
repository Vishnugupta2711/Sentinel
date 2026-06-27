from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from risk.models.schemas import CompoundRiskAssessment
from risk.engine.core import risk_engine

router = APIRouter(prefix="/risk", tags=["Compound Risk Engine"])

class AnalyzeResponse(BaseModel):
    status: str
    risks_detected: int

@router.post("/analyze", response_model=AnalyzeResponse)
async def trigger_analysis():
    # Typically driven by Intelligence Pipeline. 
    return AnalyzeResponse(status="USE_PIPELINE", risks_detected=len(risk_engine.get_current_risks()))

@router.get("/current", response_model=List[CompoundRiskAssessment])
async def get_current_risks():
    return risk_engine.get_current_risks()

@router.get("/history", response_model=List[CompoundRiskAssessment])
async def get_risk_history():
    return risk_engine.get_history()

@router.get("/zones", response_model=List[str])
async def get_affected_zones():
    zones = set()
    for r in risk_engine.get_current_risks():
        zones.update(r.affected_zones)
    return list(zones)

@router.get("/workers", response_model=List[str])
async def get_affected_workers():
    workers = set()
    for r in risk_engine.get_current_risks():
        workers.update(r.affected_workers)
    return list(workers)
