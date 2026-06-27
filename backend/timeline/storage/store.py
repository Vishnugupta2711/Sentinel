import threading
from collections import deque
from typing import List, Dict, Optional
from timeline.timeline.entry import TimelineEntry

class TimelineStore:
    """
    In-memory, bounded historical storage for Timeline entries.
    Maintains O(1) indexes for entity history lookups.

    PERF: Index lists replaced with deque(maxlen=N) so eviction is O(1)
          instead of O(N) list.pop(0).
    """
    
    def __init__(self, max_capacity: int = 1000):
        self._max_capacity = max_capacity
        self._lock = threading.RLock()  # RLock: allows same thread to re-acquire
        
        # Main sequential storage — deque handles bounded capacity automatically
        self._timeline: deque = deque(maxlen=max_capacity)
        
        # Entity indexes — deque(maxlen) gives O(1) eviction
        self._worker_index: Dict[str, deque] = {}
        self._sensor_index: Dict[str, deque] = {}
        self._zone_index:   Dict[str, deque] = {}
        self._equipment_index: Dict[str, deque] = {}
        self._hazard_index: Dict[str, deque] = {}

    def _get_or_create(self, index: Dict[str, deque], key: str) -> deque:
        if key not in index:
            index[key] = deque(maxlen=self._max_capacity)
        return index[key]

    def insert(self, entry: TimelineEntry) -> None:
        """Inserts a new entry and updates indices. All appends are O(1)."""
        with self._lock:
            self._timeline.append(entry)
            state = entry.get_state()
            if not state:
                return

            for w  in state.workers:    self._get_or_create(self._worker_index,    w.id).append(entry)
            for s  in state.sensors:    self._get_or_create(self._sensor_index,    s.id).append(entry)
            for z  in state.zones:      self._get_or_create(self._zone_index,      z.id).append(entry)
            for eq in state.equipment:  self._get_or_create(self._equipment_index, eq.id).append(entry)
            for h  in state.hazards:    self._get_or_create(self._hazard_index,    h.id).append(entry)

    def latest(self) -> Optional[TimelineEntry]:
        with self._lock:
            return self._timeline[-1] if self._timeline else None

    def oldest(self) -> Optional[TimelineEntry]:
        with self._lock:
            return self._timeline[0] if self._timeline else None

    def get_all(self) -> List[TimelineEntry]:
        with self._lock:
            return list(self._timeline)

    def get_last_n(self, n: int) -> List[TimelineEntry]:
        """Return last N entries without materialising the full deque."""
        with self._lock:
            total = len(self._timeline)
            start = max(0, total - n)
            return [self._timeline[i] for i in range(start, total)]

    def get_worker_history(self, worker_id: str) -> List[TimelineEntry]:
        with self._lock:
            return list(self._worker_index.get(worker_id, []))

    def get_sensor_history(self, sensor_id: str) -> List[TimelineEntry]:
        with self._lock:
            return list(self._sensor_index.get(sensor_id, []))

    def get_zone_history(self, zone_id: str) -> List[TimelineEntry]:
        with self._lock:
            return list(self._zone_index.get(zone_id, []))

    def get_uncompressed_entries(self, keep_last: int = 100) -> List[TimelineEntry]:
        """Returns entries that need compression (older than `keep_last`)."""
        with self._lock:
            total = len(self._timeline)
            if total <= keep_last:
                return []
            target_count = total - keep_last
            return [self._timeline[i] for i in range(target_count) if not self._timeline[i].is_compressed]

    def __len__(self) -> int:
        with self._lock:
            return len(self._timeline)
