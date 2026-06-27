from typing import List
from fastapi import APIRouter, Depends, HTTPException
from intelligence.engine.core import IntelligenceEngine, get_intelligence_engine
from intelligence.schemas.api import GenericResponse, ModuleStatus, IntelligenceStatusResponse, IntelligenceMetricsResponse

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])

@router.get("/status", response_model=IntelligenceStatusResponse)
async def get_status(engine: IntelligenceEngine = Depends(get_intelligence_engine)):
    return IntelligenceStatusResponse(
        engine_status=engine.state.get_status(),
        active_pipelines=[m.name() for m in engine.registry.get_execution_pipeline()]
    )

@router.get("/modules", response_model=List[ModuleStatus])
async def get_modules(engine: IntelligenceEngine = Depends(get_intelligence_engine)):
    return engine.registry.list_modules()

@router.get("/metrics", response_model=IntelligenceMetricsResponse)
async def get_metrics(engine: IntelligenceEngine = Depends(get_intelligence_engine)):
    return IntelligenceMetricsResponse(metrics=engine.metrics.get_metrics())

@router.post("/reload", response_model=GenericResponse)
async def reload_config(engine: IntelligenceEngine = Depends(get_intelligence_engine)):
    engine.reload_config()
    return GenericResponse(success=True, message="Intelligence configuration reloaded.")

@router.post("/enable/{module}", response_model=GenericResponse)
async def enable_module(module: str, engine: IntelligenceEngine = Depends(get_intelligence_engine)):
    if engine.registry.enable(module):
        return GenericResponse(success=True, message=f"Module '{module}' enabled.")
    raise HTTPException(status_code=404, detail="Module not found.")

@router.post("/disable/{module}", response_model=GenericResponse)
async def disable_module(module: str, engine: IntelligenceEngine = Depends(get_intelligence_engine)):
    if engine.registry.disable(module):
        return GenericResponse(success=True, message=f"Module '{module}' disabled.")
    raise HTTPException(status_code=404, detail="Module not found.")
