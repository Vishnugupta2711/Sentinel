from abc import ABC, abstractmethod
from typing import Dict, Any
from world_state.snapshot.models import WorldState

class BaseForecaster(ABC):
    
    @abstractmethod
    def forecast(self, current_state: WorldState, horizon_minutes: int, features: Dict[str, Any]) -> WorldState:
        """
        Takes the current state, extracted features (like trends), and projects 
        a new WorldState into the future by horizon_minutes.
        """
        pass
