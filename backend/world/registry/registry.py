from typing import Dict, Optional
from world.models.state import PlantState
from world.models.base import BaseWorldObject

class WorldRegistry:
    """Fast in-memory lookup index for world objects by ID."""
    
    def __init__(self):
        self._index: Dict[str, BaseWorldObject] = {}
        
    def index_state(self, state: PlantState) -> None:
        """Rebuilds the index from a given PlantState."""
        self._index.clear()
        
        if state.plant:
            self._index[state.plant.id] = state.plant
            
        for collection in [
            state.buildings, state.zones, state.workers, state.sensors,
            state.equipment, state.pipelines, state.valves, state.vehicles,
            state.hazards, state.permits, state.cameras, state.emergency_exits
        ]:
            for obj in collection:
                self._index[obj.id] = obj

    def get_by_id(self, obj_id: str) -> Optional[BaseWorldObject]:
        """Generic fast lookup by ID."""
        return self._index.get(obj_id)

    def update(self, obj: BaseWorldObject) -> None:
        """Update or insert an object in the index."""
        self._index[obj.id] = obj
