from intelligence.config import IntelligenceConfig
from intelligence.registry.registry import ModuleRegistry
from intelligence.metrics.collector import MetricsCollector
from intelligence.state.manager import StateManager
from intelligence.events.publisher import EventPublisher
from intelligence.dispatcher.dispatcher import IntelligenceDispatcher
from intelligence.modules.core import (
    ChronosModule, RiskModule, PlannerModule,
    ComplianceModule, MemoryModule, VisionModule,
)
from intelligence.modules.phase7 import (
    GasSensorModule, WorkPermitModule, ShiftModule,
    CorrelationModule, AlertModule,
)
from rag.engine.core import rag_engine

class IntelligenceEngine:
    """The central composition root for the Sentinel Intelligence Engine."""

    def __init__(self):
        self.config = IntelligenceConfig()
        self.registry = ModuleRegistry(self.config)
        self.metrics = MetricsCollector()
        self.state = StateManager()
        self.publisher = EventPublisher()
        self.dispatcher = IntelligenceDispatcher(self.registry, self.metrics, self.state, self.publisher)

        # Register Phase 4 standard modules
        self.registry.register(ChronosModule())
        self.registry.register(RiskModule())
        self.registry.register(PlannerModule())
        self.registry.register(ComplianceModule())
        self.registry.register(MemoryModule())
        self.registry.register(VisionModule())

        # Register Phase 7 multi-agent modules
        self.registry.register(GasSensorModule())
        self.registry.register(WorkPermitModule())
        self.registry.register(ShiftModule())
        self.registry.register(CorrelationModule())
        self.registry.register(AlertModule())

        # RAG is registered from core module but wired to our Phase 7 engine
        from intelligence.modules.core import RAGModule as CoreRAGModule
        self.registry.register(CoreRAGModule())

        # Load incident corpus into RAG engine at boot
        rag_engine.reload_kb()

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
