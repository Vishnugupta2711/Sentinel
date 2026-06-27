from abc import ABC, abstractmethod
from typing import List
from world_state.snapshot.models import WorldState
from compliance.models.schemas import ComplianceViolation

class BaseComplianceRule(ABC):
    @property
    @abstractmethod
    def rule_id(self) -> str:
        pass
        
    @abstractmethod
    def evaluate(self, state: WorldState) -> List[ComplianceViolation]:
        pass
