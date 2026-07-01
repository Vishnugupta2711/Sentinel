from typing import List, Optional
from datetime import datetime, timedelta
from timeline.timeline.entry import TimelineEntry


class InMemoryStore:
    def __init__(self):
        self._entries: List[TimelineEntry] = []

    def latest(self) -> Optional[TimelineEntry]:
        return self._entries[-1] if self._entries else None

    def get_last_n(self, window_minutes: int) -> List[TimelineEntry]:
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        return [e for e in self._entries if e.timestamp >= cutoff.isoformat()]

    def insert(self, entry: TimelineEntry) -> None:
        self._entries.append(entry)


class TimelineEngine:
    def __init__(self):
        self.store = InMemoryStore()


timeline_engine = TimelineEngine()
