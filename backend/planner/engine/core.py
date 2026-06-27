from typing import List, Dict
import structlog
from intelligence.contracts.context import IntelligenceContext
from risk.models.schemas import CompoundRiskAssessment
from planner.models.schemas import InterventionPlan
from planner.simulation.sandbox import SimulationSandbox
from planner.optimizer.optimizer import PlanOptimizer
from planner.actions.implementations import CancelPermitAction, EvacuateZoneAction
from timeline.engine.core import timeline_engine

logger = structlog.get_logger(__name__)

class CounterfactualEngine:
    def __init__(self):
        self.sandbox = SimulationSandbox()
        self.optimizer = PlanOptimizer()
        self.active_plans: Dict[str, List[InterventionPlan]] = {} # risk_id -> ranked plans
        self.plan_history: List[InterventionPlan] = []
        
    def generate_plans(self, context: IntelligenceContext) -> Dict[str, List[InterventionPlan]]:
        logger.info("CounterfactualEngine generating intervention plans...")
        
        risks: List[CompoundRiskAssessment] = context.metadata.get("compound_risks", [])
        if not risks:
            return {}
            
        latest_entry = timeline_engine.store.latest()
        if not latest_entry:
            return {}
            
        current_state = latest_entry.get_state()
        results = {}
        
        for risk in risks:
            baseline_score = risk.risk_score
            affected_workers = len(risk.affected_workers)
            plans_for_risk = []
            
            # Scenario A: Targeted Action (Cancel Permit)
            # Find the permit related to this risk. We can cheat by looking for permits in the affected zone.
            target_permit_id = None
            for p in current_state.permits:
                w = next((w for w in current_state.workers if w.id == p.assigned_to), None)
                if w and w.zone_id in risk.affected_zones:
                    target_permit_id = p.id
                    break
                    
            if target_permit_id:
                a_action = CancelPermitAction(target_id=target_permit_id)
                cf_state, cf_risks = self.sandbox.simulate(context, current_state, [a_action])
                cf_score = max([r.risk_score for r in cf_risks]) if cf_risks else 0.0
                
                plan_a = self.optimizer.evaluate_plan(
                    scenario_name="Scenario A: Targeted Permit Cancellation",
                    actions=[a_action],
                    baseline_risk_score=baseline_score,
                    counterfactual_risk_score=cf_score,
                    affected_workers=affected_workers,
                    target_risk_id=risk.risk_id,
                    target_risk_name=risk.risk_type.value
                )
                plans_for_risk.append(plan_a)
                
            # Scenario C: Aggressive (Cancel Permit + Evacuate Zone)
            if risk.affected_zones:
                zone_id = risk.affected_zones[0]
                c_actions = [EvacuateZoneAction(target_id=zone_id)]
                if target_permit_id:
                    c_actions.append(CancelPermitAction(target_id=target_permit_id))
                    
                cf_state, cf_risks = self.sandbox.simulate(context, current_state, c_actions)
                cf_score = max([r.risk_score for r in cf_risks]) if cf_risks else 0.0
                
                plan_c = self.optimizer.evaluate_plan(
                    scenario_name="Scenario C: Aggressive Evacuation",
                    actions=c_actions,
                    baseline_risk_score=baseline_score,
                    counterfactual_risk_score=cf_score,
                    affected_workers=affected_workers,
                    target_risk_id=risk.risk_id,
                    target_risk_name=risk.risk_type.value
                )
                plans_for_risk.append(plan_c)
                
            # Baseline: No intervention
            plan_b = self.optimizer.evaluate_plan(
                scenario_name="Baseline: No Intervention",
                actions=[],
                baseline_risk_score=baseline_score,
                counterfactual_risk_score=baseline_score, # Risk stays the same
                affected_workers=0,
                target_risk_id=risk.risk_id,
                target_risk_name=risk.risk_type.value
            )
            plans_for_risk.append(plan_b)
            
            # Rank
            ranked = self.optimizer.rank_plans(plans_for_risk)
            results[risk.risk_id] = ranked
            
            self.active_plans[risk.risk_id] = ranked
            self.plan_history.extend(ranked)
            
        return results

    def get_latest_recommendations(self) -> List[InterventionPlan]:
        # Return the top plan for each active risk
        best_plans = []
        for risk_id, plans in self.active_plans.items():
            if plans:
                best_plans.append(plans[0])
        return best_plans
        
    def get_history(self) -> List[InterventionPlan]:
        return self.plan_history[-100:]

counterfactual_engine = CounterfactualEngine()
