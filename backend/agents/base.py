from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from utils.uuid import generate_uuid
from utils.datetime import format_iso, utc_now


class AgentSignal(BaseModel):
    signal_id: str = Field(default_factory=generate_uuid)
    agent_name: str
    signal_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    zone_id: Optional[str] = None
    description: str
    score: float = 0.0
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    @abstractmethod
    async def analyze(self, world_state: Any, context: Any) -> List[AgentSignal]:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def priority(self) -> int:
        pass
