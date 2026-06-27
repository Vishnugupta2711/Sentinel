from abc import ABC, abstractmethod
from world_state.snapshot.models import WorldState
from planner.models.schemas import InterventionActionSchema

class BaseAction(ABC):
    """
    Interface for an atomic intervention action.
    """
    def __init__(self, target_id: str):
        self.target_id = target_id

    @abstractmethod
    def get_schema(self) -> InterventionActionSchema:
        pass

    @abstractmethod
    def apply(self, state: WorldState) -> WorldState:
        """
        Applies this action to a cloned WorldState to simulate the outcome.
        Returns the mutated WorldState.
        """
        pass
