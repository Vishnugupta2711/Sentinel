import asyncio
from typing import Callable, Dict, List, Set, Awaitable
from collections import deque
from simulator.events.models import SimulationEvent
from simulator.events.enums import EventType

# Type alias for event callbacks
EventCallback = Callable[[SimulationEvent], Awaitable[None]]

class EventBus:
    """Async In-Memory Pub/Sub Event Bus."""
    
    def __init__(self, history_limit: int = 1000):
        self._subscribers: Dict[EventType, Set[EventCallback]] = {
            event_type: set() for event_type in EventType
        }
        self._history: deque = deque(maxlen=history_limit)
        
        # A special queue or list of active websocket broadcast queues could go here
        self._broadcast_queues: List[asyncio.Queue] = []

    async def publish(self, event: SimulationEvent) -> None:
        """Publishes an event to all subscribers and records it in history."""
        self._history.append(event)
        
        # Notify specific type subscribers
        callbacks = self._subscribers.get(event.event_type, set())
        if callbacks:
            await asyncio.gather(*(callback(event) for callback in callbacks))
            
        # Broadcast to all connected websocket queues
        await self.broadcast(event)

    def subscribe(self, event_type: EventType, callback: EventCallback) -> None:
        """Subscribes a callback to a specific event type."""
        self._subscribers[event_type].add(callback)

    def unsubscribe(self, event_type: EventType, callback: EventCallback) -> None:
        """Unsubscribes a callback from a specific event type."""
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)

    async def broadcast(self, event: SimulationEvent) -> None:
        """Pushes an event to all generic broadcast queues (used by WebSockets)."""
        for q in self._broadcast_queues:
            await q.put(event)

    def register_broadcast_queue(self, queue: asyncio.Queue) -> None:
        """Registers a queue to receive all broadcasted events."""
        self._broadcast_queues.append(queue)
        
    def unregister_broadcast_queue(self, queue: asyncio.Queue) -> None:
        """Removes a broadcast queue."""
        if queue in self._broadcast_queues:
            self._broadcast_queues.remove(queue)

    def history(self) -> List[SimulationEvent]:
        """Returns the recent event history."""
        return list(self._history)

# Global singleton event bus
event_bus = EventBus()
