from typing import Optional, List
import structlog
from demo.models.schemas import DemoStatus, Scenario, DemoState
from demo.scenarios.data import get_scenario
import asyncio

logger = structlog.get_logger(__name__)

class DemoDirector:
    def __init__(self):
        self.status = DemoStatus.IDLE
        self.active_scenario: Optional[Scenario] = None
        self.current_stage_num = 0
        self.playback_speed = 1.0
        self.subscribers: List[asyncio.Queue] = []
        
    def start_scenario(self, scenario_id: str) -> bool:
        scenario = get_scenario(scenario_id)
        if not scenario:
            logger.error(f"Scenario {scenario_id} not found.")
            return False
            
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
        self.status = DemoStatus.IDLE
        self.active_scenario = None
        self.current_stage_num = 0
        logger.info("Demo Reset")

    def _execute_current_stage(self):
        stage = self.active_scenario.stages[self.current_stage_num - 1]
        
        # In a real system, this interacts with the WorldState/EventBus
        # For this implementation, we broadcast the narration and actions to the UI
        payload = {
            "event": "ScenarioStageChanged",
            "scenario_id": self.active_scenario.scenario_id,
            "stage_num": stage.stage_num,
            "name": stage.name,
            "narration": stage.narration,
            "actions": [a.model_dump() for a in stage.actions]
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
