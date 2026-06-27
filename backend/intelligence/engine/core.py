from intelligence.config import IntelligenceConfig
from intelligence.registry.registry import ModuleRegistry
from intelligence.metrics.collector import MetricsCollector
from intelligence.state.manager import StateManager
from intelligence.events.publisher import EventPublisher
from intelligence.dispatcher.dispatcher import IntelligenceDispatcher
from intelligence.modules.core import (
    ChronosModule, RiskModule, PlannerModule, 
    ComplianceModule, MemoryModule, VisionModule, RAGModule
)

class IntelligenceEngine:
    """The central composition root for the Sentinel Intelligence Engine."""
    
    def __init__(self):
        self.config = IntelligenceConfig()
        self.registry = ModuleRegistry(self.config)
        self.metrics = MetricsCollector()
        self.state = StateManager()
        self.publisher = EventPublisher()
        self.dispatcher = IntelligenceDispatcher(self.registry, self.metrics, self.state, self.publisher)
        
        # Register standard modules
        self.registry.register(ChronosModule())
        self.registry.register(RiskModule())
        self.registry.register(PlannerModule())
        self.registry.register(ComplianceModule())
        self.registry.register(MemoryModule())
        self.registry.register(VisionModule())
        self.registry.register(RAGModule())
        
    def reload_config(self):
        self.config.reload()
        # Re-evaluate enablement based on new config
        for mod in self.registry._modules.values():
            if self.config.is_enabled(mod.name()):
                self.registry.enable(mod.name())
            else:
                self.registry.disable(mod.name())

# Global Instance (Used for Dependency Injection in Routers and Hooks)
intelligence_engine = IntelligenceEngine()

def get_intelligence_engine() -> IntelligenceEngine:
    """Dependency Injection provider for FastAPI routes."""
    return intelligence_engine
