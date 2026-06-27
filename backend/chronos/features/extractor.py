from typing import Dict
from intelligence.contracts.context import IntelligenceContext
from timeline.engine.core import timeline_engine


class FeatureExtractor:
    """
    Extracts time-series features from the Historical Timeline Engine
    to be used by Chronos Forecasters.

    PERF: Uses store.get_last_n() to slice directly from the deque
          without materialising the full 1000-entry list.
    """

    def extract_sensor_trends(self, context: IntelligenceContext, window_minutes: int = 10) -> Dict[str, float]:
        """
        Calculates the linear trend (gradient) of sensor values over the
        specified time window. Returns a dict mapping sensor_id → trend/min.
        """
        snapshots = timeline_engine.store.get_last_n(window_minutes)

        if len(snapshots) < 2:
            return {}

        # Group sensor values by extracting only first and last state
        # instead of accumulating large arrays in memory (O(S) vs O(T*S))
        first_state = snapshots[0].get_state()
        last_state = snapshots[-1].get_state()
        
        if not first_state or not last_state:
            return {}
            
        first_vals = {s.id: s.current_value for s in first_state.sensors}
        last_vals = {s.id: s.current_value for s in last_state.sensors}

        window_f = float(window_minutes)
        return {
            s_id: (last_vals[s_id] - first_vals[s_id]) / window_f
            for s_id in first_vals.keys() & last_vals.keys()
        }
