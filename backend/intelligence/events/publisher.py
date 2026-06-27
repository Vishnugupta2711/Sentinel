import asyncio
from typing import Any, Dict
from pydantic import BaseModel, Field
from utils.datetime import format_iso, utc_now
from utils.uuid import generate_uuid

class IntelligenceEvent(BaseModel):
    event_id: str = Field(default_factory=generate_uuid)
    event_type: str
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    request_id: str
    module_name: str | None = None
    payload: Dict[str, Any] = Field(default_factory=dict)

class EventPublisher:
    """Publishes intelligence lifecycle events."""
    
    def __init__(self):
        self._queues = []

    def register_queue(self, queue: asyncio.Queue):
        self._queues.append(queue)

    def unregister_queue(self, queue: asyncio.Queue):
        if queue in self._queues:
            self._queues.remove(queue)

    async def publish(self, event_type: str, request_id: str, module_name: str | None = None, payload: Dict[str, Any] = None):
        evt = IntelligenceEvent(
            event_type=event_type,
            request_id=request_id,
            module_name=module_name,
            payload=payload or {}
        )
        for q in self._queues:
            await q.put(evt)
