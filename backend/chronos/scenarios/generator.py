from typing import List, Dict, Any
import copy
from chronos.models.schemas import ScenarioPrediction, ScenarioType
from chronos.forecast.interfaces import BaseForecaster
from chronos.confidence.engine import ConfidenceEngine
from chronos.reasoning.engine import ReasoningEngine
from world_state.snapshot.models import WorldState

class ScenarioGenerator:
    """
    Generates Best, Normal, and Worst-case scenarios using a BaseForecaster.
    """
    def __init__(self, forecaster: BaseForecaster, confidence_engine: ConfidenceEngine, reasoning_engine: ReasoningEngine):
        self.forecaster = forecaster
        self.confidence_engine = confidence_engine
        self.reasoning_engine = reasoning_engine

    def generate(self, current_state: WorldState, horizon_minutes: int, features: Dict[str, Any]) -> List[ScenarioPrediction]:
        scenarios = []
        
        # Base Confidence and Reasoning
        confidence = self.confidence_engine.calculate(features, horizon_minutes)
        reasoning = self.reasoning_engine.explain(features, horizon_minutes)
        
        # 1. NORMAL CASE
        normal_state = self.forecaster.forecast(current_state, horizon_minutes, features)
        scenarios.append(
            ScenarioPrediction(
                scenario_type=ScenarioType.NORMAL,
                probability=0.6,
                expected_risk=0.5,
                confidence=confidence,
                predicted_world_state=normal_state,
                reasoning=reasoning
            )
        )
        
        # 2. WORST CASE (Amplify trends by 1.5x)
        worst_features = copy.deepcopy(features)
        if "sensor_trends" in worst_features:
            for s_id in worst_features["sensor_trends"]:
                worst_features["sensor_trends"][s_id] *= 1.5
                
        worst_state = self.forecaster.forecast(current_state, horizon_minutes, worst_features)
        
        worst_reasoning = copy.deepcopy(reasoning)
        worst_reasoning.description += " [Worst Case: Trends amplified by 1.5x]"
        
        scenarios.append(
            ScenarioPrediction(
                scenario_type=ScenarioType.WORST_CASE,
                probability=0.15,
                expected_risk=0.9,
                confidence=confidence,
                predicted_world_state=worst_state,
                reasoning=worst_reasoning
            )
        )
        
        # 3. BEST CASE (Dampen trends by 0.5x)
        best_features = copy.deepcopy(features)
        if "sensor_trends" in best_features:
            for s_id in best_features["sensor_trends"]:
                best_features["sensor_trends"][s_id] *= 0.5
                
        best_state = self.forecaster.forecast(current_state, horizon_minutes, best_features)
        
        best_reasoning = copy.deepcopy(reasoning)
        best_reasoning.description += " [Best Case: Trends dampened by 0.5x]"
        
        scenarios.append(
            ScenarioPrediction(
                scenario_type=ScenarioType.BEST_CASE,
                probability=0.25,
                expected_risk=0.2,
                confidence=confidence,
                predicted_world_state=best_state,
                reasoning=best_reasoning
            )
        )
        
        return scenarios
