from typing import Dict, Any, List
from timeline.queries.engine import QueryEngine

class TimelineAnalytics:
    """Computes trends and statistics over the historical timeline."""
    
    def __init__(self, query_engine: QueryEngine):
        self.queries = query_engine

    def worker_movement_history(self, worker_id: str) -> List[Dict[str, Any]]:
        """Extracts the exact sequence of zone transitions for a worker."""
        history = self.queries.worker_history(worker_id)
        movements = []
        last_zone = None
        
        for entry in history:
            state = entry.get_state()
            worker = next((w for w in state.workers if w.id == worker_id), None)
            if worker and worker.zone_id != last_zone:
                movements.append({
                    "timestamp": entry.timestamp,
                    "tick": entry.simulation_tick,
                    "from_zone": last_zone,
                    "to_zone": worker.zone_id
                })
                last_zone = worker.zone_id
                
        return movements

    def sensor_trend(self, sensor_id: str) -> Dict[str, Any]:
        """Calculates basic min/max/avg for a sensor over the timeline."""
        history = self.queries.sensor_history(sensor_id)
        if not history:
            return {}
            
        values = []
        for entry in history:
            state = entry.get_state()
            sensor = next((s for s in state.sensors if s.id == sensor_id), None)
            if sensor:
                values.append(sensor.current_value)
                
        if not values:
            return {}
            
        return {
            "sensor_id": sensor_id,
            "samples": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values)
        }
        
    def plant_statistics(self) -> Dict[str, Any]:
        """High-level summary of the entire 1000-tick buffer."""
        store = self.queries.store
        entries = store.get_all()
        if not entries:
            return {"status": "No history available"}
            
        total_hazards_seen = set()
        for e in entries:
            state = e.get_state()
            for h in state.hazards:
                total_hazards_seen.add(h.id)
                
        return {
            "total_snapshots": len(entries),
            "oldest_timestamp": entries[0].timestamp,
            "newest_timestamp": entries[-1].timestamp,
            "unique_hazards_seen": len(total_hazards_seen),
            "compressed_count": sum(1 for e in entries if e.is_compressed)
        }
