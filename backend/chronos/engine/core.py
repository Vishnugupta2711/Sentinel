import uuid
from datetime import datetime, timezone
from typing import List, Optional
from chronos.models.schemas import PredictionResult
from chronos.features.extractor import FeatureExtractor
from chronos.forecast.baseline import BaselineForecaster
from chronos.confidence.engine import ConfidenceEngine
from chronos.reasoning.engine import ReasoningEngine
from chronos.scenarios.generator import ScenarioGenerator
from intelligence.contracts.context import IntelligenceContext
from timeline.engine.core import timeline_engine
import structlog

logger = structlog.get_logger(__name__)

class ChronosEngine:
    """
    Composition Root for Chronos Predictive Engine.
    Coordinates feature extraction, forecasting, and scenario generation.
    """
    
    def __init__(self):
        self.extractor = FeatureExtractor()
        self.forecaster = BaselineForecaster()
        self.confidence_engine = ConfidenceEngine()
        self.reasoning_engine = ReasoningEngine()
        self.scenario_generator = ScenarioGenerator(
            forecaster=self.forecaster,
            confidence_engine=self.confidence_engine,
            reasoning_engine=self.reasoning_engine
        )
        
        # Store predictions in memory for APIs
        self.history: List[PredictionResult] = []
        
    def predict(self, context: IntelligenceContext, horizon_minutes: int) -> PredictionResult:
        logger.info(f"Chronos running prediction for T+{horizon_minutes}m")
        
        # Get Current State
        latest_entry = timeline_engine.store.latest()
        if not latest_entry:
            raise ValueError("No timeline entry found. Cannot predict.")
        current_state = latest_entry.get_state()
        
        # 1. Feature Extraction
        trends = self.extractor.extract_sensor_trends(context, window_minutes=10)
        features = {"sensor_trends": trends}
        
        # 2. Scenario Generation
        scenarios = self.scenario_generator.generate(current_state, horizon_minutes, features)
        
        # 3. Build Result
        result = PredictionResult(
            prediction_id=str(uuid.uuid4()),
            generated_at=datetime.now(timezone.utc).isoformat(),
            forecast_horizon_minutes=horizon_minutes,
            scenarios=scenarios,
            supporting_events=["WorldState Updated"]
        )
        
        self.history.append(result)
        # Keep last 100
        if len(self.history) > 100:
            self.history.pop(0)
            
        return result
        
    def get_latest(self) -> Optional[PredictionResult]:
        if not self.history:
            return None
        return self.history[-1]
        
    def get_history(self, limit: int = 10) -> List[PredictionResult]:
        return self.history[-limit:]

chronos_engine = ChronosEngine()
