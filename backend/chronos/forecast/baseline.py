from typing import Dict, Any
from chronos.forecast.interfaces import BaseForecaster
from world_state.snapshot.models import WorldState
from world.models.enums import Status

class BaselineForecaster(BaseForecaster):
    """
    A rule-based and linear-projection based forecasting engine.
    Satisfies the requirement for a hybrid/rule-based baseline before ML models.
    """
    
    def forecast(self, current_state: WorldState, horizon_minutes: int, features: Dict[str, Any]) -> WorldState:
        # Create a deep copy and update the frozen version field
        future_state = current_state.model_copy(deep=True, update={"version": current_state.version + horizon_minutes})
        
        sensor_trends = features.get("sensor_trends", {})
        
        # 1. Project Sensor Values Linearly
        for s in future_state.sensors:
            if s.id in sensor_trends:
                trend_per_minute = sensor_trends[s.id]
                s.current_value += (trend_per_minute * horizon_minutes)
                
                # Rule: if value breaches threshold, change status to WARNING or CRITICAL
                if s.current_value >= s.threshold * 1.2:
                    s.status = Status.CRITICAL
                elif s.current_value >= s.threshold:
                    s.status = Status.WARNING
                    
        # 2. Project Equipment Failures
        # If an equipment was WARNING, it might degrade to CRITICAL if horizon is large enough
        for e in future_state.equipment:
            if e.maintenance_status == Status.WARNING and horizon_minutes > 15:
                e.maintenance_status = Status.CRITICAL
                

        return future_state
