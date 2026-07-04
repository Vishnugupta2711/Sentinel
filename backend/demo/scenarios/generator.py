import random
import math
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from demo.models.schemas import Scenario, ScenarioStage, DemoAction, DemoActionType
from world.models.entities import Sensor, Worker, Permit, Zone, Hazard
from world.models.enums import SensorType, WorkerRole, WorkerStatus, HazardType, HazardSeverity, Status
from world_state.snapshot.models import WorldState
from utils.uuid import generate_uuid
from utils.datetime import format_iso, utc_now


class SyntheticDataGenerator:
    def __init__(self):
        self._tick = 0

    def generate_sensor_readings(self, base_value: float, variance: float, trend: float = 0) -> float:
        noise = random.gauss(0, variance)
        drift = trend * self._tick * 0.01
        return round(base_value + noise + drift, 2)

    def tick(self) -> int:
        self._tick += 1
        return self._tick

    def reset(self) -> None:
        self._tick = 0

    def build_scenario_world(self, scenario_id: str, stage_num: int) -> WorldState:
        if scenario_id == "DEMO_01":
            return self._build_gas_leak_scenario(stage_num)
        elif scenario_id == "DEMO_02":
            return self._build_confined_space_scenario(stage_num)
        elif scenario_id == "DEMO_03":
            return self._build_forklift_scenario(stage_num)
        return self._build_default_world()

    def _build_gas_leak_scenario(self, stage_num: int) -> WorldState:
        gas_levels = {1: 5.0, 2: 5.0, 3: 45.0, 4: 85.0}
        gas_level = gas_levels.get(stage_num, 5.0)

        has_permit = stage_num >= 2
        has_hazard = stage_num >= 3

        return WorldState(
            version=self._tick,
            plant_id="PLANT_001",
            zones=[
                Zone(
                    id="ZONE_COKE", name="Coke Oven Battery", hazard_level="HIGH",
                    x=0, y=0, z=0, max_capacity=20, current_occupancy=3,
                ),
                Zone(
                    id="ZONE_SAFE", name="Control Room", hazard_level="LOW",
                    x=100, y=0, z=0, max_capacity=10, current_occupancy=5,
                ),
            ],
            sensors=[
                Sensor(
                    id="SENSOR_GAS_01", name="Methane Detector - Coke Oven",
                    sensor_type=SensorType.GAS, current_value=gas_level,
                    unit="CH4", threshold=30.0, x=10, y=20, z=5,
                    zone_id="ZONE_COKE", last_updated=format_iso(utc_now()),
                ),
                Sensor(
                    id="SENSOR_GAS_02", name="H2S Monitor - Coke Oven",
                    sensor_type=SensorType.GAS, current_value=gas_level * 0.3,
                    unit="H2S", threshold=10.0, x=15, y=25, z=5,
                    zone_id="ZONE_COKE", last_updated=format_iso(utc_now()),
                ),
                Sensor(
                    id="SENSOR_TEMP_01", name="Temperature - Coke Oven",
                    sensor_type=SensorType.TEMPERATURE, current_value=85.0,
                    unit="C", threshold=100.0, x=10, y=20, z=5,
                    zone_id="ZONE_COKE", last_updated=format_iso(utc_now()),
                ),
            ],
            workers=[
                Worker(
                    id="WORKER_001", name="John Doe", role=WorkerRole.OPERATOR,
                    x=15, y=22, z=0, zone_id="ZONE_COKE", department="Operations",
                    current_ppe=["hard_hat", "safety_glasses", "steel_toed_boots"],
                    shift="DAY",
                ),
                Worker(
                    id="WORKER_002", name="Jane Smith", role=WorkerRole.SUPERVISOR,
                    x=105, y=5, z=0, zone_id="ZONE_SAFE", department="Operations",
                    current_ppe=["hard_hat", "safety_glasses"],
                    shift="DAY",
                ),
            ],
            permits=[
                Permit(
                    id="PERMIT_HW_001", name="Hot Work - Coke Oven",
                    permit_type="HOT_WORK" if has_permit else "NONE",
                    assigned_to="John Doe",
                    valid_from=format_iso(utc_now()),
                    valid_until=format_iso(datetime.now(timezone.utc) + timedelta(hours=4)),
                    approved_by="Jane Smith",
                ),
            ] if has_permit else [],
            hazards=[
                Hazard(
                    id="HAZARD_GAS_01", hazard_type=HazardType.GAS_LEAK,
                    severity=HazardSeverity.CRITICAL if has_hazard else HazardSeverity.LOW,
                    x=10, y=20, z=5, zone_id="ZONE_COKE",
                    radius=30.0, is_active=has_hazard,
                ),
            ] if has_hazard else [],
            weather=None,
            zone_occupancy={"ZONE_COKE": 1, "ZONE_SAFE": 5},
            plant_status="WARNING" if stage_num >= 3 else "NORMAL",
        )

    def _build_confined_space_scenario(self, stage_num: int) -> WorldState:
        h2s_level = 2.0 if stage_num == 1 else 45.0
        has_hazard = stage_num >= 2

        return WorldState(
            version=self._tick,
            plant_id="PLANT_001",
            zones=[
                Zone(
                    id="ZONE_TANK", name="Storage Tank T-101", hazard_level="HIGH",
                    x=50, y=50, z=0, max_capacity=2, current_occupancy=1,
                ),
            ],
            sensors=[
                Sensor(
                    id="SENSOR_H2S_01", name="H2S Monitor - Tank T-101",
                    sensor_type=SensorType.GAS, current_value=h2s_level,
                    unit="H2S", threshold=10.0, x=50, y=50, z=2,
                    zone_id="ZONE_TANK", last_updated=format_iso(utc_now()),
                ),
            ],
            workers=[
                Worker(
                    id="WORKER_003", name="John Doe", role=WorkerRole.MAINTENANCE,
                    x=50, y=50, z=1, zone_id="ZONE_TANK", department="Maintenance",
                    current_ppe=["hard_hat", "safety_glasses", "steel_toed_boots", "harness"],
                    shift="DAY",
                ),
            ],
            permits=[
                Permit(
                    id="PERMIT_CS_001", name="Confined Space - Tank T-101",
                    permit_type="CONFINED_SPACE",
                    assigned_to="John Doe",
                    valid_from=format_iso(utc_now()),
                    valid_until=format_iso(datetime.now(timezone.utc) + timedelta(hours=2)),
                    approved_by="Jane Smith",
                ),
            ],
            hazards=[
                Hazard(
                    id="HAZARD_H2S_01", hazard_type=HazardType.GAS_LEAK,
                    severity=HazardSeverity.CRITICAL if has_hazard else HazardSeverity.LOW,
                    x=50, y=50, z=2, zone_id="ZONE_TANK",
                    radius=5.0, is_active=has_hazard,
                ),
            ] if has_hazard else [],
            zone_occupancy={"ZONE_TANK": 1},
            plant_status="WARNING" if has_hazard else "NORMAL",
        )

    def _build_forklift_scenario(self, stage_num: int) -> WorldState:
        return WorldState(
            version=self._tick,
            plant_id="PLANT_001",
            zones=[
                Zone(
                    id="ZONE_WAREHOUSE", name="Warehouse B", hazard_level="MEDIUM",
                    x=200, y=100, z=0, max_capacity=30, current_occupancy=5,
                ),
            ],
            sensors=[
                Sensor(
                    id="SENSOR_MOTION_01", name="Motion Sensor - Corner B4",
                    sensor_type=SensorType.GAS, current_value=0,
                    unit="NONE", threshold=0, x=220, y=115, z=3,
                    zone_id="ZONE_WAREHOUSE", last_updated=format_iso(utc_now()),
                ),
            ],
            workers=[
                Worker(
                    id="WORKER_004", name="Alice Brown", role=WorkerRole.OPERATOR,
                    x=225, y=110, z=0, zone_id="ZONE_WAREHOUSE", department="Logistics",
                    current_ppe=["hard_hat", "safety_glasses", "steel_toed_boots", "high_vis"],
                    shift="DAY",
                ),
            ],
            permits=[],
            hazards=[],
            zone_occupancy={"ZONE_WAREHOUSE": 1},
            plant_status="NORMAL",
        )

    def _build_default_world(self) -> WorldState:
        return WorldState(
            version=self._tick,
            plant_id="PLANT_001",
            zones=[
                Zone(id="ZONE_DEFAULT", name="Default Zone", hazard_level="LOW",
                     x=0, y=0, z=0, max_capacity=50, current_occupancy=1),
            ],
            sensors=[
                Sensor(id="SENSOR_DEF_01", name="Default Sensor",
                       sensor_type=SensorType.GAS, current_value=2.0,
                       unit="CH4", threshold=30.0, x=0, y=0, z=0,
                       zone_id="ZONE_DEFAULT", last_updated=format_iso(utc_now())),
            ],
            workers=[
                Worker(id="WORKER_DEF_01", name="Default Worker",
                       role=WorkerRole.OPERATOR, x=0, y=0, z=0,
                       zone_id="ZONE_DEFAULT", department="Operations",
                       current_ppe=["hard_hat"], shift="DAY"),
            ],
            permits=[],
            hazards=[],
            zone_occupancy={"ZONE_DEFAULT": 1},
            plant_status="NORMAL",
        )


synthetic_generator = SyntheticDataGenerator()
