import asyncio
import structlog
from world.manager.manager import world_manager
from simulator.publishers.bus import event_bus
from simulator.generators.workers import WorkerGenerator
from simulator.generators.sensors import SensorGenerator
from simulator.generators.weather import WeatherGenerator
from world_state.builder.builder import world_state_builder
from world_state.websocket.live import ws_queues
from intelligence.engine.core import intelligence_engine
from intelligence.contracts.context import IntelligenceContext
from timeline.engine.core import timeline_engine
from timeline.timeline.entry import TimelineEntry
from hazard_graph.engine.core import hazard_graph_engine
from hazard_graph.websocket.live import ws_graph_queues

logger = structlog.get_logger(__name__)

def _push_latest(q: asyncio.Queue, item):
    try:
        q.put_nowait(item)
    except asyncio.QueueFull:
        try:
            q.get_nowait()
            q.put_nowait(item)
        except (asyncio.QueueEmpty, asyncio.QueueFull):
            pass

class SimulationEngine:
    """Core simulator engine that ticks every second and drives generators."""
    
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self._task: asyncio.Task | None = None
        self._generators = [
            WorkerGenerator(),
            SensorGenerator(),
            WeatherGenerator()
        ]
        
    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.is_paused = False
        self._task = asyncio.create_task(self._loop())
        logger.info("Simulation engine started.")
        
    def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
        logger.info("Simulation engine stopped.")
        
    def pause(self):
        self.is_paused = True
        logger.info("Simulation engine paused.")
        
    def resume(self):
        self.is_paused = False
        logger.info("Simulation engine resumed.")
        
    def reset(self):
        self.stop()
        world_manager.reset()
        logger.info("Simulation engine and world state reset.")

    async def _loop(self):
        while self.is_running:
            if not self.is_paused:
                state = world_manager.get_state()
                if state:
                    for gen in self._generators:
                        try:
                            await gen.tick(state, event_bus)
                        except Exception as e:
                            logger.error(f"Generator {gen.__class__.__name__} failed: {e}")
                            
                    # After all generators run, build the immutable snapshot
                    try:
                        snapshot = world_state_builder.build_snapshot()
                        # Broadcast snapshot to websocket clients
                        for q in ws_queues:
                            _push_latest(q, snapshot)
                            
                        # Insert into Historical Timeline Engine
                        entry = TimelineEntry(version=snapshot.version, simulation_tick=snapshot.version)
                        entry.set_state(snapshot)
                        timeline_engine.store.insert(entry)
                        
                        # Sync Dynamic Hazard Graph
                        hazard_graph_engine.updates.sync(snapshot)
                        
                        # Broadcast graph update
                        # In reality we'd send just the deltas, but for now we signal an update
                        for q in ws_graph_queues:
                            _push_latest(q, {"event": "GRAPH_UPDATED", "version": snapshot.version})
                            
                        # Trigger Intelligence Engine Pipeline
                        context = IntelligenceContext(
                            world_state_version=snapshot.version,
                            plant_id=snapshot.plant.id if snapshot.plant else "unknown",
                            simulation_tick=snapshot.version
                        )
                        asyncio.create_task(intelligence_engine.dispatcher.dispatch(context))
                        
                    except Exception as e:
                        logger.error(f"Failed to build WorldState snapshot or dispatch intelligence: {e}")
                            
            await asyncio.sleep(1.0)

# Global singleton engine
simulation_engine = SimulationEngine()
