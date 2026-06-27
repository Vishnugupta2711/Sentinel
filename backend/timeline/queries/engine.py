from typing import List, Optional
from timeline.storage.store import TimelineStore
from timeline.timeline.entry import TimelineEntry

class QueryEngine:
    """Facade for executing historical queries against the Timeline Store."""
    
    def __init__(self, store: TimelineStore):
        self.store = store

    def latest(self) -> Optional[TimelineEntry]:
        return self.store.latest()

    def oldest(self) -> Optional[TimelineEntry]:
        return self.store.oldest()

    def between(self, time1: str, time2: str) -> List[TimelineEntry]:
        """Returns entries strictly between two ISO timestamps."""
        # Simple O(N) scan for now, since N <= 1000.
        # In a real DB this would be an indexed range query.
        result = []
        entries = self.store.get_all()
        for e in entries:
            if time1 <= e.timestamp <= time2:
                result.append(e)
        return result

    def last_minutes(self, minutes: int) -> List[TimelineEntry]:
        """Returns entries from the last X minutes."""
        # In a real system, we'd parse time, but this is a simplified simulation
        # For an in-memory test environment, we might just scan the tail.
        # N=1000 is small enough for O(N)
        import dateutil.parser
        from datetime import timedelta
        from utils.datetime import utc_now
        
        cutoff = utc_now() - timedelta(minutes=minutes)
        result = []
        for e in self.store.get_all():
            try:
                dt = dateutil.parser.isoparse(e.timestamp)
                if dt >= cutoff:
                    result.append(e)
            except Exception:
                pass
        return result

    def worker_history(self, worker_id: str) -> List[TimelineEntry]:
        return self.store.get_worker_history(worker_id)

    def sensor_history(self, sensor_id: str) -> List[TimelineEntry]:
        return self.store.get_sensor_history(sensor_id)

    def zone_history(self, zone_id: str) -> List[TimelineEntry]:
        return self.store.get_zone_history(zone_id)
