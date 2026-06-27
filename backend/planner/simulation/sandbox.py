from typing import List, Tuple
import structlog
from world_state.snapshot.models import WorldState
from planner.actions.base import BaseAction
from risk.engine.core import risk_engine
from risk.rules.base import RiskEvaluationContext
from risk.models.schemas import CompoundRiskAssessment
from intelligence.contracts.context import IntelligenceContext

logger = structlog.get_logger(__name__)

class SimulationSandbox:
    """
    Applies a list of interventions to a WorldState and runs the Risk Engine 
    to evaluate the counterfactual compound risk.
    """
    def __init__(self):
        pass

    def simulate(self, context: IntelligenceContext, base_state: WorldState, actions: List[BaseAction]) -> Tuple[WorldState, List[CompoundRiskAssessment]]:
        # 1. Clone State
        # Version must be incremented so Pydantic doesn't complain if we mutate it?
        # Actually WorldState is frozen. We use model_copy(deep=True) to allow mutations on inner lists 
        # (since inner models are not frozen unless explicitly defined).
        # We don't increment version since this is a counterfactual projection of the *current* tick.
        simulated_state = base_state.model_copy(deep=True)
        
        # 2. Apply Actions
        for action in actions:
            simulated_state = action.apply(simulated_state)
            
        # 3. Evaluate Counterfactual Risk
        # We need a dummy eval context
        eval_context = RiskEvaluationContext(
            current_state=simulated_state,
            historical_timeline_stats={},
            chronos_prediction=context.metadata.get("chronos_prediction")
        )
        
        # Run through Risk Engine rules manually (we don't want to pollute real active_risks)
        detected_risks = []
        for rule in risk_engine.rules:
            risk = rule.evaluate(eval_context)
            if risk:
                detected_risks.append(risk)
                
        return simulated_state, detected_risks
