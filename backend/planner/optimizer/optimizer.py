from typing import List
from planner.models.schemas import InterventionPlan, PlanEvaluation, ReasoningTrace
from planner.actions.base import BaseAction

class PlanOptimizer:
    def evaluate_plan(
        self, 
        scenario_name: str, 
        actions: List[BaseAction], 
        baseline_risk_score: float, 
        counterfactual_risk_score: float,
        affected_workers: int,
        target_risk_id: str,
        target_risk_name: str
    ) -> InterventionPlan:
        # Sum up costs
        total_cost = sum(a.get_schema().estimated_cost_usd for a in actions)
        total_downtime = sum(a.get_schema().estimated_duration_minutes for a in actions)
        
        # Risk Reduction
        risk_reduction = max(0.0, baseline_risk_score - counterfactual_risk_score)
        
        eval = PlanEvaluation(
            total_risk_reduction=risk_reduction,
            total_cost=total_cost,
            estimated_downtime_minutes=total_downtime,
            workers_protected=affected_workers if risk_reduction > 50 else 0,
            overall_confidence=0.9
        )
        
        # Optimizer Score: Heavily weight risk reduction, penalize cost
        # score = Risk Reduction (max 100) * 10 - Cost Penalty
        cost_penalty = total_cost * 0.01 + total_downtime * 0.5
        score = (risk_reduction * 10) - cost_penalty
        
        reasoning = ReasoningTrace(
            why_this_plan=f"Reduces compound risk by {risk_reduction:.1f} points with a cost of ${total_cost:.2f}.",
            why_alternatives_rejected=[], # Populated later
            expected_outcome="Risk levels return to NORMAL." if counterfactual_risk_score < 30 else "Risk levels mitigated but require monitoring."
        )
        
        return InterventionPlan(
            scenario_name=scenario_name,
            target_risk_id=target_risk_id,
            target_risk_name=target_risk_name,
            target_risk_probability=baseline_risk_score / 100.0,
            actions=[a.get_schema() for a in actions],
            evaluation=eval,
            reasoning=reasoning,
            score=score
        )
        
    def rank_plans(self, plans: List[InterventionPlan]) -> List[InterventionPlan]:
        # Sort descending by score
        ranked = sorted(plans, key=lambda p: p.score, reverse=True)
        
        # Populate why alternatives rejected
        if len(ranked) > 1:
            best_plan = ranked[0]
            for plan in ranked[1:]:
                plan.reasoning.why_alternatives_rejected.append(f"Outperformed by {best_plan.scenario_name} which has score {best_plan.score:.1f}.")
                
        return ranked
