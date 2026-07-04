from typing import Optional, List, Dict, Any
import structlog
from demo.models.schemas import DemoStatus, Scenario, DemoState
from demo.scenarios.data import get_scenario
from demo.scenarios.generator import synthetic_generator
from agents.gas_sensor import gas_sensor_agent
from agents.work_permit import work_permit_agent
from agents.shift import shift_agent
from correlation.engine.core import correlation_engine
from alerts.engine.core import alert_engine
from rag.engine.core import rag_engine
from agents.base import AgentSignal
import asyncio
import sys

logger = structlog.get_logger(__name__)

class DemoDirector:
    def __init__(self):
        self.status = DemoStatus.IDLE
        self.active_scenario: Optional[Scenario] = None
        self.current_stage_num = 0
        self.playback_speed = 1.0
        self.subscribers: List[asyncio.Queue] = []
        self._agent_results: Dict[str, Any] = {}

    def start_scenario(self, scenario_id: str) -> bool:
        scenario = get_scenario(scenario_id)
        if not scenario:
            logger.error(f"Scenario {scenario_id} not found.")
            return False

        synthetic_generator.reset()
        self.active_scenario = scenario
        self.current_stage_num = 1
        self.status = DemoStatus.PLAYING
        self.playback_speed = 1.0

        logger.info(f"Started Scenario: {scenario.name}")
        self._execute_current_stage()
        return True

    def next_stage(self):
        if not self.active_scenario:
            return

        if self.current_stage_num < len(self.active_scenario.stages):
            self.current_stage_num += 1
            synthetic_generator.tick()
            logger.info(f"Advanced to stage {self.current_stage_num}")
            self._execute_current_stage()
        else:
            self.status = DemoStatus.COMPLETED
            self._broadcast({"event": "DemoCompleted", "scenario_id": self.active_scenario.scenario_id})
            logger.info("Demo Completed")

    def pause(self):
        if self.status == DemoStatus.PLAYING:
            self.status = DemoStatus.PAUSED
            logger.info("Demo Paused")

    def reset(self):
        synthetic_generator.reset()
        self.status = DemoStatus.IDLE
        self.active_scenario = None
        self.current_stage_num = 0
        self._agent_results = {}
        logger.info("Demo Reset")

    def _execute_current_stage(self):
        scenario_id = self.active_scenario.scenario_id if self.active_scenario else ""
        self._run_agent_analysis(scenario_id)

    def _run_agent_analysis(self, scenario_id: str):
        world_state = synthetic_generator.build_scenario_world(scenario_id, self.current_stage_num)

        context_data = {
            "world_state_version": synthetic_generator.tick(),
            "plant_id": "PLANT_001",
            "simulation_tick": self.current_stage_num,
        }

        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                task = asyncio.ensure_future(self._analyze_with_agents(world_state, context_data))
                return
        except RuntimeError:
            pass

        asyncio.run(self._analyze_with_agents(world_state, context_data))

    async def _analyze_with_agents(self, world_state, context_data):
        all_signals: List[AgentSignal] = []
        agent_results = {}

        gas_signals = await gas_sensor_agent.analyze(world_state, context_data)
        all_signals.extend(gas_signals)
        agent_results["gas_sensor"] = [s.model_dump() for s in gas_signals]

        permit_signals = await work_permit_agent.analyze(world_state, context_data)
        all_signals.extend(permit_signals)
        agent_results["work_permit"] = [s.model_dump() for s in permit_signals]

        shift_signals = await shift_agent.analyze(world_state, context_data)
        all_signals.extend(shift_signals)
        agent_results["shift"] = [s.model_dump() for s in shift_signals]

        correlation = correlation_engine.correlate(all_signals)
        alerts = alert_engine.evaluate_signals(all_signals)
        compound_alerts = []
        for assessment in correlation.assessments:
            alert = alert_engine.evaluate_correlation(assessment)
            if alert:
                compound_alerts.append(alert)

        active_hazards = [h for h in world_state.hazards if hasattr(h, 'is_active') and h.is_active]
        if active_hazards and any(s.severity in ("HIGH", "CRITICAL") for s in all_signals):
            rag_query = " ".join([s.signal_type for s in all_signals[:3]] + [s.zone_id or "" for s in all_signals if s.zone_id])
            rag_result = rag_engine.retrieve(rag_query)
            agent_results["rag"] = rag_result.model_dump()

        self._agent_results = agent_results

        payload = {
            "event": "ScenarioStageChanged",
            "scenario_id": self.active_scenario.scenario_id if self.active_scenario else "",
            "stage_num": self.current_stage_num,
            "name": self.active_scenario.stages[self.current_stage_num - 1].name if self.active_scenario else "",
            "narration": self.active_scenario.stages[self.current_stage_num - 1].narration if self.active_scenario else "",
            "world_state": world_state.model_dump() if hasattr(world_state, 'model_dump') else {},
            "agent_signals": [s.model_dump() for s in all_signals],
            "correlation": correlation.model_dump(),
            "alerts": [a.model_dump() for a in alerts + compound_alerts],
            "rag_result": agent_results.get("rag"),
        }
        self._broadcast(payload)

    def _broadcast(self, payload: dict):
        for q in self.subscribers:
            q.put_nowait(payload)

    def get_state(self) -> DemoState:
        return DemoState(
            status=self.status,
            active_scenario_id=self.active_scenario.scenario_id if self.active_scenario else None,
            current_stage=self.current_stage_num,
            playback_speed=self.playback_speed
        )

demo_director = DemoDirector()
