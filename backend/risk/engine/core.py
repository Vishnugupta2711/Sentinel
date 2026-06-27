from typing import List, Dict
from collections import deque
import structlog
from risk.rules.base import BaseRiskRule, RiskEvaluationContext
from risk.models.schemas import CompoundRiskAssessment
from risk.rules.implementations import ExplosionRiskRule, WorkerFatalityRule
from intelligence.contracts.context import IntelligenceContext
from timeline.engine.core import timeline_engine

logger = structlog.get_logger(__name__)

class CompoundRiskEngine:
    """
    Composition root for Phase 9. Evaluates all compound risk rules.
    """
    def __init__(self):
        self.rules: List[BaseRiskRule] = [
            ExplosionRiskRule(),
            WorkerFatalityRule()
        ]
        
        # PERF: deque(maxlen) provides O(1) eviction — no list copy needed
        self.active_risks: Dict[str, CompoundRiskAssessment] = {}
        self.risk_history: deque = deque(maxlen=1000)
        
    def analyze(self, context: IntelligenceContext) -> List[CompoundRiskAssessment]:
        logger.info("CompoundRiskEngine analyzing state...")
        
        # We need the current state. Since IntelligenceContext only has world_state_version,
        # we pull it from timeline like Chronos did, but we can also just expect the pipeline to pass it
        # Actually, let's fetch it from the timeline store
        latest_entry = timeline_engine.store.latest()
        if not latest_entry:
            return []
            
        current_state = latest_entry.get_state()
        
        # Build Evaluation Context
        eval_context = RiskEvaluationContext(
            current_state=current_state,
            historical_timeline_stats={},
            chronos_prediction=context.metadata.get("chronos_prediction")
        )
        
        detected_risks = []
        for rule in self.rules:
            risk = rule.evaluate(eval_context)
            if risk:
                detected_risks.append(risk)
                
        # Update Memory — deque auto-evicts at maxlen
        for r in detected_risks:
            self.active_risks[r.risk_id] = r
            self.risk_history.append(r)
            
        return detected_risks
        
    def get_current_risks(self) -> List[CompoundRiskAssessment]:
        return list(self.active_risks.values())
        
    def get_history(self) -> List[CompoundRiskAssessment]:
        return self.risk_history

risk_engine = CompoundRiskEngine()
