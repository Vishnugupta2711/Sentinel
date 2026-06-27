from abc import ABC, abstractmethod
from typing import Dict, Any
from intelligence.contracts.context import IntelligenceContext

class BaseIntelligenceModule(ABC):
    """
    Core Interface for Sentinel Intelligence Modules.
    Any AI model, risk engine, or pipeline component must implement this.
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """Called once when the engine boots up."""
        pass

    @abstractmethod
    async def validate(self) -> bool:
        """Validates module configuration and dependencies."""
        pass

    @abstractmethod
    async def execute(self, context: IntelligenceContext) -> Dict[str, Any]:
        """
        Executes the core module logic against the current context.
        Returns a dictionary of structured outputs.
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Cleans up resources when the engine stops."""
        pass

    @abstractmethod
    def health(self) -> str:
        """Returns module health: 'healthy', 'degraded', or 'offline'."""
        pass

    @abstractmethod
    def version(self) -> str:
        """Returns the module version."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Returns the unique module name."""
        pass

    @abstractmethod
    def priority(self) -> int:
        """
        Returns the execution priority (lower number = executes first).
        Default implementation can be overridden.
        """
        return 100
