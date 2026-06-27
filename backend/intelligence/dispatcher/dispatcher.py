import asyncio
import time
import structlog
from typing import Dict, Any, List

from intelligence.registry.registry import ModuleRegistry
from intelligence.contracts.context import IntelligenceContext
from intelligence.metrics.collector import MetricsCollector
from intelligence.state.manager import StateManager
from intelligence.events.publisher import EventPublisher

logger = structlog.get_logger(__name__)

# Modules that MUST run sequentially because downstream modules depend on their output
# (Chronos → Risk → Planner all share context.metadata)
SEQUENTIAL_MODULES = {"chronos", "risk", "planner", "compliance"}
# Independent modules that have no data dependencies and can run in parallel
PARALLEL_MODULES   = {"memory", "vision", "rag"}


class IntelligenceDispatcher:
    """Orchestrates the execution pipeline of AI modules.

    PERF: Independent modules (memory, vision, rag) now run via asyncio.gather()
          in parallel. The core analytical chain (chronos → risk → planner →
          compliance) still runs sequentially because each stage consumes the
          previous stage's output from context.metadata.
    """

    def __init__(self, registry: ModuleRegistry, metrics: MetricsCollector,
                 state: StateManager, publisher: EventPublisher):
        self.registry  = registry
        self.metrics   = metrics
        self.state     = state
        self.publisher = publisher

    async def _run_module(self, module, context: IntelligenceContext) -> tuple[str, Any]:
        name = module.name()
        await self.publisher.publish("ModuleStarted", context.request_id, module_name=name)
        start = time.perf_counter()
        try:
            output = await module.execute(context)
            latency = (time.perf_counter() - start) * 1000
            self.metrics.record_execution(name, latency, success=True)
            await self.publisher.publish("ModuleCompleted", context.request_id, module_name=name,
                                         payload={"latency_ms": round(latency, 2)})
            return name, output
        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            logger.error(f"Intelligence module '{name}' failed", error=str(e))
            self.metrics.record_execution(name, latency, success=False)
            await self.publisher.publish("ModuleFailed", context.request_id, module_name=name,
                                         payload={"error": str(e)})
            return name, None

    async def dispatch(self, context: IntelligenceContext) -> Dict[str, Any]:
        pipeline = self.registry.get_execution_pipeline()

        self.state.start_execution(context.request_id)
        await self.publisher.publish("PipelineStarted", context.request_id,
                                     payload={"modules": [m.name() for m in pipeline]})

        sequential: List = [m for m in pipeline if m.name() in SEQUENTIAL_MODULES]
        parallel:   List = [m for m in pipeline if m.name() in PARALLEL_MODULES]

        final_outputs: Dict[str, Any] = {}
        success = True

        # Phase 1: run core analytical chain sequentially (data dependencies)
        for module in sequential:
            name, output = await self._run_module(module, context)
            if output is None:
                success = False
            else:
                final_outputs[name] = output

        # Phase 2: run independent modules concurrently
        if parallel:
            results = await asyncio.gather(
                *[self._run_module(m, context) for m in parallel],
                return_exceptions=False
            )
            for name, output in results:
                if output is None:
                    success = False
                else:
                    final_outputs[name] = output

        self.state.finish_execution(success, details={"outputs_collected": list(final_outputs.keys())})
        await self.publisher.publish("PipelineCompleted", context.request_id, payload={"success": success})
        return final_outputs
