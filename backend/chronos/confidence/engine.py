from chronos.models.schemas import ConfidenceMetrics
from typing import Dict, Any

class ConfidenceEngine:
    """
    Calculates the confidence metrics for a prediction based on available features
    and data quality.
    """
    
    def calculate(self, features: Dict[str, Any], horizon_minutes: int) -> ConfidenceMetrics:
        # Simplistic baseline logic:
        # Confidence drops as horizon increases.
        base_confidence = max(0.1, 1.0 - (horizon_minutes * 0.01))
        
        sensor_trends = features.get("sensor_trends", {})
        
        # If we have very little historical data (no trends), data quality is low.
        data_quality = 1.0 if len(sensor_trends) > 0 else 0.5
        
        # Historical similarity could rely on a vector search, for now baseline is 0.8
        historical_similarity = 0.8
        
        coverage = min(1.0, len(sensor_trends) / 10.0) if sensor_trends else 0.0
        
        # Overall confidence is a weighted sum
        overall = (base_confidence * 0.5) + (data_quality * 0.2) + (historical_similarity * 0.3)
        
        return ConfidenceMetrics(
            confidence_score=round(overall, 2),
            data_quality=data_quality,
            historical_similarity=historical_similarity,
            coverage_score=coverage
        )
