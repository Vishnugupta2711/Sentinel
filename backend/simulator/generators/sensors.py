import random
from world.models.state import PlantState
from world.models.enums import SensorType
from simulator.publishers.bus import EventBus
from simulator.events.models import SimulationEvent
from simulator.events.enums import EventType, EventSeverity
from utils.datetime import format_iso, utc_now

class SensorGenerator:
    """Simulates realistic drift and spikes in sensor readings."""
    
    async def tick(self, state: PlantState, bus: EventBus) -> None:
        if not state.sensors:
            return
            
        for sensor in state.sensors:
            # Random walk for sensor values
            drift = random.uniform(-1.0, 1.0)
            
            # Special logic based on sensor type to keep things realistic
            if sensor.sensor_type == SensorType.GAS:
                drift = random.uniform(-0.1, 0.2) # Gas accumulates slowly
            elif sensor.sensor_type == SensorType.TEMPERATURE:
                drift = random.uniform(-0.5, 0.5)
                
            new_value = max(0.0, sensor.current_value + drift)
            
            # Did it cross threshold?
            crossed_threshold = False
            if new_value > sensor.threshold and sensor.current_value <= sensor.threshold:
                crossed_threshold = True
                
            sensor.current_value = round(new_value, 2)
            sensor.last_updated = format_iso(utc_now())
            
            # 10% chance to emit an update event to avoid flooding, or if crossed threshold
            if random.random() < 0.1 or crossed_threshold:
                severity = EventSeverity.WARNING if new_value > sensor.threshold else EventSeverity.INFO
                event = SimulationEvent(
                    event_type=EventType.SensorUpdated,
                    source=sensor.id,
                    severity=severity,
                    zone_id=sensor.zone_id,
                    payload={
                        "sensor_id": sensor.id,
                        "sensor_type": sensor.sensor_type.value,
                        "value": sensor.current_value,
                        "unit": sensor.unit,
                        "threshold_exceeded": new_value > sensor.threshold
                    }
                )
                await bus.publish(event)
