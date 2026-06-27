from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from world_state.snapshot.models import WorldState
from chronos.models.schemas import PredictionResult
from risk.models.schemas import CompoundRiskAssessment

class RiskEvaluationContext:
    def __init__(
        self,
        current_state: WorldState,
        historical_timeline_stats: Dict[str, Any],
        chronos_prediction: Optional[PredictionResult] = None,
        hazard_graph: Optional[Any] = None # Will type later when integrating
    ):
        self.current_state = current_state
        self.historical_timeline_stats = historical_timeline_stats
        self.chronos_prediction = chronos_prediction
        self.hazard_graph = hazard_graph

class BaseRiskRule(ABC):
    """
    Interface for a specific Compound Risk Scenario Rule.
    """
    
    @property
    @abstractmethod
    def rule_name(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, context: RiskEvaluationContext) -> Optional[CompoundRiskAssessment]:
        """
        Evaluates the context to detect a compound risk.
        Returns a CompoundRiskAssessment if the rule triggers, else None.
        """
        pass
