import random
from world.models.state import PlantState
from simulator.publishers.bus import EventBus
from simulator.events.models import SimulationEvent
from simulator.events.enums import EventType, EventSeverity
from utils.datetime import format_iso, utc_now

class WeatherGenerator:
    """Simulates weather changes."""
    
    async def tick(self, state: PlantState, bus: EventBus) -> None:
        weather = state.weather
        if not weather:
            return
            
        # Weather changes very slowly. 1% chance per tick to adjust
        if random.random() < 0.01:
            weather.temperature += random.uniform(-0.5, 0.5)
            weather.wind_speed = max(0.0, weather.wind_speed + random.uniform(-1.0, 1.0))
            weather.humidity = min(100.0, max(0.0, weather.humidity + random.uniform(-2.0, 2.0)))
            weather.last_updated = format_iso(utc_now())
            
            event = SimulationEvent(
                event_type=EventType.WeatherChanged,
                source="WEATHER_STATION",
                severity=EventSeverity.INFO,
                payload={
                    "temperature": round(weather.temperature, 2),
                    "wind_speed": round(weather.wind_speed, 2),
                    "humidity": round(weather.humidity, 2)
                }
            )
            await bus.publish(event)
