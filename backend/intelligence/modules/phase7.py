from typing import Dict, Any
import structlog
from intelligence.interfaces.module import BaseIntelligenceModule
from intelligence.contracts.context import IntelligenceContext
from world_state.snapshot.models import WorldState

from agents.gas_sensor import gas_sensor_agent
from agents.work_permit import work_permit_agent
from agents.shift import shift_agent
from correlation.engine.core import correlation_engine, correlation_engine as corr_engine
from correlation.websocket.live import ws_correlation_queues
from rag.engine.core import rag_engine
from alerts.engine.core import alert_engine
from alerts.websocket.live import router as alerts_ws_router

logger = structlog.get_logger(__name__)


def _get_world_state(context: IntelligenceContext) -> WorldState:
    ws = context.metadata.get("world_state")
    if ws is not None:
        return ws
    from timeline.engine.core import timeline_engine
    latest_entry = timeline_engine.store.latest()
    if latest_entry and hasattr(latest_entry, 'snapshot'):
        return latest_entry.snapshot
    return WorldState(version=0, plant_id=context.plant_id)


class GasSensorModule(BaseIntelligenceModule):
    async def initialize(self) -> None:
        pass

    async def validate(self) -> bool:
        return True

    async def execute(self, context: IntelligenceContext) -> Dict[str, Any]:
        world_state = _get_world_state(context)
        signals = await gas_sensor_agent.analyze(world_state, context)
        context.metadata["gas_sensor_signals"] = signals

        for s in signals:
            alert_engine.evaluate_signals([s])

        logger.info(f"GasSensorModule: {len(signals)} signals generated")
        return {"status": "gas_sensor_executed", "signals": len(signals)}

    async def shutdown(self) -> None:
        pass

    def health(self) -> str:
        return "healthy"

    def version(self) -> str:
        return "1.0.0"

    def name(self) -> str:
        return "gas_sensor"

    def priority(self) -> int:
        return 5


class WorkPermitModule(BaseIntelligenceModule):
    async def initialize(self) -> None:
        pass

    async def validate(self) -> bool:
        return True

    async def execute(self, context: IntelligenceContext) -> Dict[str, Any]:
        world_state = _get_world_state(context)
        signals = await work_permit_agent.analyze(world_state, context)
        context.metadata["work_permit_signals"] = signals

        for s in signals:
            alert_engine.evaluate_signals([s])

        logger.info(f"WorkPermitModule: {len(signals)} signals generated")
        return {"status": "work_permit_executed", "signals": len(signals)}

    async def shutdown(self) -> None:
        pass

    def health(self) -> str:
        return "healthy"

    def version(self) -> str:
        return "1.0.0"

    def name(self) -> str:
        return "work_permit"

    def priority(self) -> int:
        return 6


class ShiftModule(BaseIntelligenceModule):
    async def initialize(self) -> None:
        pass

    async def validate(self) -> bool:
        return True

    async def execute(self, context: IntelligenceContext) -> Dict[str, Any]:
        world_state = _get_world_state(context)
        signals = await shift_agent.analyze(world_state, context)
        context.metadata["shift_signals"] = signals

        for s in signals:
            alert_engine.evaluate_signals([s])

        logger.info(f"ShiftModule: {len(signals)} signals generated")
        return {"status": "shift_executed", "signals": len(signals)}

    async def shutdown(self) -> None:
        pass

    def health(self) -> str:
        return "healthy"

    def version(self) -> str:
        return "1.0.0"

    def name(self) -> str:
        return "shift"

    def priority(self) -> int:
        return 7


class CorrelationModule(BaseIntelligenceModule):
    async def initialize(self) -> None:
        pass

    async def validate(self) -> bool:
        return True

    async def execute(self, context: IntelligenceContext) -> Dict[str, Any]:
        all_signals = []
        for key in ("gas_sensor_signals", "work_permit_signals", "shift_signals"):
            signals = context.metadata.get(key, [])
            all_signals.extend(signals)

        result = correlation_engine.correlate(all_signals)
        context.metadata["correlation_result"] = result

        for assessment in result.assessments:
            alert_engine.evaluate_correlation(assessment)

        for q in ws_correlation_queues:
            q.put_nowait({
                "event": "CORRELATION_UPDATED",
                "result": result.model_dump(),
            })

        logger.info(f"CorrelationModule: {len(result.assessments)} compound risks, level={result.highest_level.value}")
        return {
            "status": "correlation_executed",
            "assessments": len(result.assessments),
            "highest_level": result.highest_level.value,
        }

    async def shutdown(self) -> None:
        pass

    def health(self) -> str:
        return "healthy"

    def version(self) -> str:
        return "1.0.0"

    def name(self) -> str:
        return "correlation"

    def priority(self) -> int:
        return 15


class RAGModule(BaseIntelligenceModule):
    async def initialize(self) -> None:
        rag_engine.reload_kb()

    async def validate(self) -> bool:
        return bool(rag_engine.documents)

    async def execute(self, context: IntelligenceContext) -> Dict[str, Any]:
        correlation = context.metadata.get("correlation_result")
        if correlation and correlation.assessments:
            top = correlation.assessments[0]
            signal_types = [c.signal_type for c in top.contributing_signals]
            result = rag_engine.retrieve_by_signal_context(signal_types, top.primary_zone)
            context.metadata["rag_result"] = result
            logger.info(f"RAGModule: {len(result.documents)} docs, {len(result.incidents)} incidents retrieved")
            return {
                "status": "rag_executed",
                "documents": len(result.documents),
                "incidents": len(result.incidents),
            }

        logger.info("RAGModule: no correlation context, skipping")
        return {"status": "rag_executed", "documents": 0, "incidents": 0}

    async def shutdown(self) -> None:
        pass

    def health(self) -> str:
        return "healthy"

    def version(self) -> str:
        return "1.0.0"

    def name(self) -> str:
        return "rag"

    def priority(self) -> int:
        return 70


class AlertModule(BaseIntelligenceModule):
    async def initialize(self) -> None:
        pass

    async def validate(self) -> bool:
        return True

    async def execute(self, context: IntelligenceContext) -> Dict[str, Any]:
        active = alert_engine.get_active_alerts()
        summary = alert_engine.get_queue_summary()
        context.metadata["alert_summary"] = summary
        logger.info(f"AlertModule: {len(active)} active alerts: {summary}")
        return {
            "status": "alert_executed",
            "active_alerts": len(active),
            "summary": summary,
        }

    async def shutdown(self) -> None:
        pass

    def health(self) -> str:
        return "healthy"

    def version(self) -> str:
        return "1.0.0"

    def name(self) -> str:
        return "alerts"

    def priority(self) -> int:
        return 80
