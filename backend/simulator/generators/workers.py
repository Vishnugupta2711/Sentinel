import random
from world.models.state import PlantState
from simulator.publishers.bus import EventBus
from simulator.events.models import SimulationEvent
from simulator.events.enums import EventType, EventSeverity

class WorkerGenerator:
    """Simulates worker movement and actions."""
    
    async def tick(self, state: PlantState, bus: EventBus) -> None:
        if not state.workers or not state.zones:
            return
            
        for worker in state.workers:
            # 5% chance a worker moves per tick
            if random.random() < 0.05:
                old_zone = worker.zone_id
                
                # Pick a random new zone (simulating walking)
                new_zone_obj = random.choice(state.zones)
                new_zone = new_zone_obj.id
                
                if old_zone != new_zone:
                    worker.zone_id = new_zone
                    worker.building_id = new_zone_obj.building_id
                    
                    # Publish event
                    event = SimulationEvent(
                        event_type=EventType.WorkerMoved,
                        source=worker.id,
                        severity=EventSeverity.INFO,
                        zone_id=new_zone,
                        payload={
                            "worker_id": worker.id,
                            "worker_name": worker.name,
                            "from_zone": old_zone,
                            "to_zone": new_zone
                        }
                    )
                    await bus.publish(event)
