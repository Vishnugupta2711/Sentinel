from typing import List
from world.models.state import PlantState
from world.models.entities import (
    Plant, Building, Zone, Sensor, Worker, Vehicle, Camera, Equipment,
    Pipeline, Valve, Permit, Hazard, EmergencyExit, WeatherState
)
from utils.datetime import format_iso, utc_now

class WorldBuilder:
    """Builder pattern for constructing a full PlantState digital twin."""
    
    def __init__(self):
        self._plant: Plant = None
        self._buildings: List[Building] = []
        self._zones: List[Zone] = []
        self._workers: List[Worker] = []
        self._sensors: List[Sensor] = []
        self._equipment: List[Equipment] = []
        self._pipelines: List[Pipeline] = []
        self._valves: List[Valve] = []
        self._vehicles: List[Vehicle] = []
        self._hazards: List[Hazard] = []
        self._permits: List[Permit] = []
        self._cameras: List[Camera] = []
        self._emergency_exits: List[EmergencyExit] = []
        self._weather: WeatherState = WeatherState(last_updated=format_iso(utc_now()))

    def create_plant(self, name: str, description: str, address: str) -> 'WorldBuilder':
        self._plant = Plant(name=name, description=description, address=address)
        return self

    def set_weather(self, weather: WeatherState) -> 'WorldBuilder':
        self._weather = weather
        return self

    def add_building(self, building: Building) -> 'WorldBuilder':
        self._buildings.append(building)
        return self

    def add_zone(self, zone: Zone) -> 'WorldBuilder':
        self._zones.append(zone)
        return self

    def attach_sensor(self, sensor: Sensor) -> 'WorldBuilder':
        self._sensors.append(sensor)
        return self

    def attach_worker(self, worker: Worker) -> 'WorldBuilder':
        self._workers.append(worker)
        return self

    def attach_camera(self, camera: Camera) -> 'WorldBuilder':
        self._cameras.append(camera)
        return self

    def attach_equipment(self, equipment: Equipment) -> 'WorldBuilder':
        self._equipment.append(equipment)
        return self

    def attach_pipeline(self, pipeline: Pipeline) -> 'WorldBuilder':
        self._pipelines.append(pipeline)
        return self

    def attach_valve(self, valve: Valve) -> 'WorldBuilder':
        self._valves.append(valve)
        return self

    def attach_vehicle(self, vehicle: Vehicle) -> 'WorldBuilder':
        self._vehicles.append(vehicle)
        return self

    def attach_hazard(self, hazard: Hazard) -> 'WorldBuilder':
        self._hazards.append(hazard)
        return self

    def attach_permit(self, permit: Permit) -> 'WorldBuilder':
        self._permits.append(permit)
        return self

    def attach_emergency_exit(self, exit: EmergencyExit) -> 'WorldBuilder':
        self._emergency_exits.append(exit)
        return self

    def build(self) -> PlantState:
        """Assembles and returns the final PlantState."""
        if not self._plant:
            raise ValueError("Plant must be created before building the World.")
            
        return PlantState(
            plant=self._plant,
            weather=self._weather,
            buildings=self._buildings,
            zones=self._zones,
            workers=self._workers,
            sensors=self._sensors,
            equipment=self._equipment,
            pipelines=self._pipelines,
            valves=self._valves,
            vehicles=self._vehicles,
            hazards=self._hazards,
            permits=self._permits,
            cameras=self._cameras,
            emergency_exits=self._emergency_exits,
            current_time=format_iso(utc_now())
        )
