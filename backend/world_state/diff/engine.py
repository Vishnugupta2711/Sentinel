from typing import Dict, List, Any
from pydantic import BaseModel
from world_state.snapshot.models import WorldState

class StateDelta(BaseModel):
    """Structured differences between two WorldState snapshots."""
    version_a: int
    version_b: int
    worker_movement: List[Dict[str, Any]] = []
    sensor_changes: List[Dict[str, Any]] = []
    weather_changes: Dict[str, Any] = {}
    hazard_changes: List[Dict[str, Any]] = []

class StateDiffEngine:
    """Compares two immutable WorldState snapshots and extracts deltas."""
    
    @staticmethod
    def compare(state_a: WorldState, state_b: WorldState) -> StateDelta:
        delta = StateDelta(version_a=state_a.version, version_b=state_b.version)
        
        # 1. Compare Workers (movement)
        workers_a = {w.id: w for w in state_a.workers}
        for w_b in state_b.workers:
            w_a = workers_a.get(w_b.id)
            if w_a and w_a.zone_id != w_b.zone_id:
                delta.worker_movement.append({
                    "worker_id": w_b.id,
                    "from_zone": w_a.zone_id,
                    "to_zone": w_b.zone_id
                })
                
        # 2. Compare Sensors (thresholds or value shifts)
        sensors_a = {s.id: s for s in state_a.sensors}
        for s_b in state_b.sensors:
            s_a = sensors_a.get(s_b.id)
            if s_a and s_a.current_value != s_b.current_value:
                delta.sensor_changes.append({
                    "sensor_id": s_b.id,
                    "old_value": s_a.current_value,
                    "new_value": s_b.current_value
                })
                
        # 3. Compare Weather
        wa = state_a.weather
        wb = state_b.weather
        if wa and wb:
            if wa.temperature != wb.temperature or wa.wind_speed != wb.wind_speed or wa.humidity != wb.humidity:
                delta.weather_changes = {
                    "temp_diff": round(wb.temperature - wa.temperature, 2),
                    "wind_diff": round(wb.wind_speed - wa.wind_speed, 2),
                    "humidity_diff": round(wb.humidity - wa.humidity, 2)
                }

        # 4. Compare Hazards
        haz_a = {h.id: h for h in state_a.hazards}
        for h_b in state_b.hazards:
            if h_b.id not in haz_a:
                delta.hazard_changes.append({
                    "action": "ADDED",
                    "hazard_id": h_b.id,
                    "type": h_b.hazard_type.value
                })
        for h_a in state_a.hazards:
            if h_a.id not in {h.id for h in state_b.hazards}:
                delta.hazard_changes.append({
                    "action": "REMOVED",
                    "hazard_id": h_a.id
                })

        return delta
