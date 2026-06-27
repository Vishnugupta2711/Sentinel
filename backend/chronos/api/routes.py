from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel
from chronos.models.schemas import PredictionResult, ScenarioPrediction
from chronos.engine.core import chronos_engine

router = APIRouter(prefix="/chronos", tags=["Chronos Predictive Engine"])

class PredictRequest(BaseModel):
    horizon_minutes: int = 30
    
class PredictResponse(BaseModel):
    prediction_id: str
    status: str = "SUCCESS"

@router.post("/predict", response_model=PredictResponse)
async def trigger_prediction(req: PredictRequest):
    # This is normally triggered by the internal Intelligence Engine pipeline.
    # Exposing for manual trigger testing. We need a dummy context since we don't have the live loop here.
    # In reality, this endpoint might just queue a job. For MVP, we'll return a mock if context is missing,
    # or just return status since live predictions are broadcasted.
    return PredictResponse(prediction_id="manual-trigger-not-fully-supported", status="USE_PIPELINE")

@router.get("/latest", response_model=Optional[PredictionResult])
async def get_latest_prediction():
    return chronos_engine.get_latest()

@router.get("/history", response_model=List[PredictionResult])
async def get_prediction_history(limit: int = 10):
    return chronos_engine.get_history(limit)
    
@router.get("/scenarios", response_model=List[ScenarioPrediction])
async def get_latest_scenarios():
    latest = chronos_engine.get_latest()
    if not latest:
        return []
    return latest.scenarios
