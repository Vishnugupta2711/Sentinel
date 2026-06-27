import random
from world.builder.builder import WorldBuilder
from world.models.state import PlantState
from world.models.entities import (
    Building, Zone, Sensor, Worker, Camera, Equipment, Pipeline, Valve, EmergencyExit, WeatherState
)
from world.models.enums import SensorType, WorkerRole, WorkerStatus, ValveState, Status
from utils.datetime import format_iso, utc_now
from utils.uuid import generate_uuid

def generate_sample_world() -> PlantState:
    """Generates a realistic mock digital twin of an industrial plant."""
    builder = WorldBuilder()
    
    # 1. Plant
    builder.create_plant(
        name="Sentinel Alpha Plant",
        description="Main production and refinement facility.",
        address="100 Industrial Parkway, Sector 7"
    )
    builder.set_weather(WeatherState(
        temperature=random.uniform(15.0, 35.0),
        humidity=random.uniform(30.0, 80.0),
        wind_speed=random.uniform(0.0, 25.0),
        condition="CLEAR",
        last_updated=format_iso(utc_now())
    ))

    # 2. Buildings (2)
    b1 = Building(name="Processing Facility", floors=3, max_occupancy=200)
    b2 = Building(name="Control Center", floors=1, max_occupancy=50)
    builder.add_building(b1).add_building(b2)

    # 3. Zones (8)
    zones = []
    for i in range(8):
        building_id = b1.id if i < 6 else b2.id
        z = Zone(
            name=f"Zone {i+1}", 
            building_id=building_id,
            hazard_level=random.choice(["LOW", "MEDIUM", "HIGH"]),
            max_capacity=50,
            current_occupancy=random.randint(0, 20)
        )
        zones.append(z)
        builder.add_zone(z)

    # 4. Sensors (40)
    for i in range(40):
        z = random.choice(zones)
        stype = random.choice(list(SensorType))
        builder.attach_sensor(Sensor(
            name=f"Sensor-{stype.value}-{i}",
            zone_id=z.id,
            building_id=z.building_id,
            sensor_type=stype,
            unit="unit",
            threshold=100.0,
            current_value=random.uniform(0.0, 90.0),
            last_updated=format_iso(utc_now())
        ))

    # 5. Workers (30)
    for i in range(30):
        z = random.choice(zones)
        builder.attach_worker(Worker(
            name=f"Worker {i}",
            role=random.choice(list(WorkerRole)),
            department="Operations",
            shift="DAY",
            worker_status=WorkerStatus.ACTIVE,
            zone_id=z.id,
            building_id=z.building_id
        ))

    # 6. Cameras (25)
    for i in range(25):
        z = random.choice(zones)
        builder.attach_camera(Camera(
            name=f"CCTV-{i}",
            zone_id=z.id,
            building_id=z.building_id,
            direction=random.uniform(0, 360),
            coverage_radius=random.uniform(10, 50)
        ))

    # 7. Equipment (50)
    for i in range(50):
        z = random.choice(zones)
        builder.attach_equipment(Equipment(
            name=f"Equipment-{i}",
            equipment_type=random.choice(["Pump", "Compressor", "Generator", "Motor"]),
            manufacturer="IndustrialCorp",
            zone_id=z.id,
            building_id=z.building_id,
            criticality=random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
            maintenance_status=Status.ONLINE
        ))

    # 8. Pipelines (15)
    pipelines = []
    for i in range(15):
        p = Pipeline(
            name=f"Pipeline-{i}",
            source_id=generate_uuid(),
            destination_id=generate_uuid(),
            material="Steel",
            pressure_rating=random.uniform(100.0, 1000.0)
        )
        pipelines.append(p)
        builder.attach_pipeline(p)

    # 9. Valves (20)
    for i in range(20):
        p = random.choice(pipelines)
        builder.attach_valve(Valve(
            name=f"Valve-{i}",
            pipeline_id=p.id,
            current_state=random.choice(list(ValveState)),
            health=random.uniform(50.0, 100.0)
        ))

    # 10. Emergency Exits (5)
    for i in range(5):
        b = random.choice([b1, b2])
        builder.attach_emergency_exit(EmergencyExit(
            name=f"Exit-{i}",
            building_id=b.id,
            is_blocked=False,
            capacity=100
        ))

    return builder.build()
