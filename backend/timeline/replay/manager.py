import asyncio
import structlog
from timeline.storage.store import TimelineStore

logger = structlog.get_logger(__name__)

class ReplayManager:
    """State machine for replaying historical states to websocket clients."""
    
    def __init__(self, store: TimelineStore):
        self.store = store
        self.is_playing = False
        self.current_index = -1
        self._queues = []
        self._task = None

    def register_queue(self, queue: asyncio.Queue):
        self._queues.append(queue)

    def unregister_queue(self, queue: asyncio.Queue):
        if queue in self._queues:
            self._queues.remove(queue)

    def get_status(self):
        return {
            "is_playing": self.is_playing,
            "current_index": self.current_index,
            "total_entries": len(self.store.get_all())
        }

    def pause(self):
        self.is_playing = False
        logger.info("Timeline replay paused.")

    def resume(self):
        if not self.is_playing:
            self.is_playing = True
            self._task = asyncio.create_task(self._playback_loop())
            logger.info("Timeline replay resumed.")

    def step_forward(self):
        entries = self.store.get_all()
        if not entries:
            return
            
        if self.current_index < len(entries) - 1:
            self.current_index += 1
            self._broadcast(entries[self.current_index].get_state().model_dump_json())

    def step_backward(self):
        entries = self.store.get_all()
        if not entries:
            return
            
        if self.current_index > 0:
            self.current_index -= 1
            self._broadcast(entries[self.current_index].get_state().model_dump_json())

    def jump_to(self, timestamp: str):
        entries = self.store.get_all()
        for i, e in enumerate(entries):
            if e.timestamp >= timestamp:
                self.current_index = i
                self._broadcast(e.get_state().model_dump_json())
                return
                
    def _broadcast(self, payload: str):
        for q in self._queues:
            q.put_nowait(payload)

    async def _playback_loop(self):
        while self.is_playing:
            entries = self.store.get_all()
            if not entries or self.current_index >= len(entries) - 1:
                self.is_playing = False
                break
                
            self.current_index += 1
            self._broadcast(entries[self.current_index].get_state().model_dump_json())
            
            await asyncio.sleep(1.0)
