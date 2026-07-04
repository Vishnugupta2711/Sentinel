from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from correlation.models.schemas import CorrelationResult, CompoundRiskAssessment
from correlation.engine.core import correlation_engine

router = APIRouter(prefix="/correlation", tags=["Correlation Layer"])


@router.get("/latest", response_model=CorrelationResult)
async def get_latest():
    assessments = correlation_engine.get_latest_assessments()
    return CorrelationResult(assessments=assessments)


@router.get("/assessments", response_model=List[CompoundRiskAssessment])
async def get_assessments(
    zone_id: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
):
    assessments = correlation_engine.get_latest_assessments(top_k=limit)
    if zone_id:
        assessments = [a for a in assessments if a.primary_zone == zone_id]
    if level:
        assessments = [a for a in assessments if a.level.value == level.upper()]
    return assessments[:limit]
