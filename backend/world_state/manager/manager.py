import threading
from collections import deque
from typing import Optional, List
from world_state.snapshot.models import WorldState

class SnapshotManager:
    """Singleton Manager for WorldState history and versioning."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SnapshotManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._history: deque = deque(maxlen=1000)
        self._current_snapshot: Optional[WorldState] = None
        self._previous_snapshot: Optional[WorldState] = None
        self._version_counter: int = 0
        self._initialized = True

    def push_snapshot(self, snapshot: WorldState) -> None:
        """Stores a new snapshot, rolling history forward."""
        with self._lock:
            self._previous_snapshot = self._current_snapshot
            self._current_snapshot = snapshot
            self._history.append(snapshot)
            # Update counter to reflect latest pushed (just in case they differ)
            self._version_counter = snapshot.version

    def get_next_version(self) -> int:
        """Atomically gets the next version number."""
        with self._lock:
            self._version_counter += 1
            return self._version_counter

    def latest(self) -> Optional[WorldState]:
        """Returns the most recent snapshot."""
        return self._current_snapshot

    def previous(self) -> Optional[WorldState]:
        """Returns the previous snapshot."""
        return self._previous_snapshot

    def get_by_version(self, version: int) -> Optional[WorldState]:
        """Looks up a snapshot in history by version number."""
        # Simple linear scan since it's only 1000 items and in-memory
        for snap in reversed(self._history):
            if snap.version == version:
                return snap
        return None

    def history(self, limit: int = 100) -> List[WorldState]:
        """Returns the N most recent snapshots (latest first)."""
        history_list = list(self._history)
        history_list.reverse()
        return history_list[:limit]

    def rollback(self, version: int) -> Optional[WorldState]:
        """
        Reverts the current state to a specific version.
        Note: This only resets the manager's active pointer. 
        The underlying WorldManager/PlantState will need to be reloaded if we truly rollback.
        """
        with self._lock:
            snap = self.get_by_version(version)
            if snap:
                self._current_snapshot = snap
                # Truncate history to discard newer snapshots
                while self._history and self._history[-1].version > version:
                    self._history.pop()
                self._version_counter = version
                return snap
            return None

# Global singleton
snapshot_manager = SnapshotManager()
