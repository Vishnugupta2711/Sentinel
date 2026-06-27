from chronos.models.schemas import ReasoningTrace
from typing import Dict, Any

class ReasoningEngine:
    """
    Generates human-readable explanations and traces for predictions.
    """
    
    def explain(self, features: Dict[str, Any], horizon_minutes: int) -> ReasoningTrace:
        sensor_trends = features.get("sensor_trends", {})
        
        influencing = []
        sensors = []
        desc = f"Projected future state for {horizon_minutes} minutes ahead based on linear baselines."
        
        if sensor_trends:
            desc += " Sensor trends were extracted and applied."
            for s_id, trend in sensor_trends.items():
                if abs(trend) > 0.1: # Significant trend
                    influencing.append(f"Strong trend detected on {s_id}: {trend:.2f}/min")
                    sensors.append(s_id)
        else:
            desc += " Insufficient historical timeline data to extract dynamic trends."
            
        return ReasoningTrace(
            description=desc,
            influencing_events=influencing,
            contributing_sensors=sensors,
            matched_timeline_patterns=["Linear Extension"]
        )
