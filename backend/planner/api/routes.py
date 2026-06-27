from fastapi import APIRouter
from typing import List, Dict
from pydantic import BaseModel
from planner.models.schemas import InterventionPlan, PlannerResponseDTO, RecommendedPlanDTO
from planner.engine.core import counterfactual_engine

router = APIRouter(prefix="/planner", tags=["Counterfactual Planner"])

class RecommendResponse(BaseModel):
    status: str
    plans_generated: int

@router.post("/recommend", response_model=RecommendResponse)
async def trigger_recommendation():
    return RecommendResponse(status="USE_PIPELINE", plans_generated=len(counterfactual_engine.get_latest_recommendations()))

def _map_to_dto(plan: InterventionPlan) -> PlannerResponseDTO:
    cf_risk_reduction_prob = plan.evaluation.total_risk_reduction / 100.0
    predicted_prob = max(0.0, plan.target_risk_probability - cf_risk_reduction_prob)
    
    return PlannerResponseDTO(
        risk=plan.target_risk_name,
        current_probability=plan.target_risk_probability,
        recommended_plan=RecommendedPlanDTO(
            actions=[a.name for a in plan.actions],
            predicted_probability=predicted_prob,
            downtime_minutes=plan.evaluation.estimated_downtime_minutes,
            estimated_cost=plan.evaluation.total_cost,
            workers_protected=plan.evaluation.workers_protected,
            confidence=plan.evaluation.overall_confidence
        )
    )

@router.get("/latest", response_model=List[PlannerResponseDTO])
async def get_latest_plans():
    return [_map_to_dto(p) for p in counterfactual_engine.get_latest_recommendations()]

@router.get("/history", response_model=List[PlannerResponseDTO])
async def get_plan_history():
    return [_map_to_dto(p) for p in counterfactual_engine.get_history()]

@router.get("/scenarios", response_model=Dict[str, List[PlannerResponseDTO]])
async def get_scenarios_by_risk():
    return {
        risk_id: [_map_to_dto(p) for p in plans]
        for risk_id, plans in counterfactual_engine.active_plans.items()
    }
