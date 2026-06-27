import threading
from typing import Optional
from world.models.state import PlantState
from world.registry.registry import WorldRegistry

class WorldManager:
    """Singleton Manager for the Industrial World Model."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(WorldManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._state: Optional[PlantState] = None
        self.registry: WorldRegistry = WorldRegistry()
        self._initialized = True

    def load(self, state: PlantState) -> None:
        """Loads a completely new state and indexes it."""
        with self._lock:
            self._state = state
            self.registry.index_state(state)

    def save(self) -> None:
        """Stub for future database persistence."""
        pass

    def reset(self) -> None:
        """Clears the world state."""
        with self._lock:
            self._state = None
            self.registry._index.clear()

    def get_state(self) -> Optional[PlantState]:
        """Returns the current complete PlantState."""
        return self._state

    def update_state(self, state: PlantState) -> None:
        """Thread-safe update of the state."""
        self.load(state)

# Global singleton instance
world_manager = WorldManager()
