from agents.gas_sensor import gas_sensor_agent, _classify_gas_level
from agents.work_permit import work_permit_agent
from agents.shift import shift_agent
from world_state.snapshot.models import WorldState
from world.models.entities import Sensor, Worker, Zone, Permit, Hazard
from world.models.enums import SensorType, WorkerRole, WorkerStatus, HazardType, HazardSeverity


def _make_context():
    class FakeContext:
        world_state_version = 1
        plant_id = "PLANT_001"
        simulation_tick = 1
        current_events = []
        configuration = {}
        metadata = {}
    return FakeContext()


class TestGasSensorAgent:
    def test_no_gas_sensors_no_signals(self):
        ws = WorldState(version=1, plant_id="P1", sensors=[])
        signals = []
        async def run():
            nonlocal signals
            signals = await gas_sensor_agent.analyze(ws, _make_context())
        import asyncio
        asyncio.run(run())
        assert len(signals) == 0

    def test_gas_sensor_high_value_generates_signal(self):
        ws = WorldState(
            version=1, plant_id="P1",
            sensors=[
                Sensor(
                    id="S1", name="Gas Detector 1",
                    sensor_type=SensorType.GAS, current_value=45.0,
                    unit="CH4", threshold=30.0, x=0, y=0, z=0,
                    zone_id="ZONE_A", last_updated="2024-01-01T00:00:00Z",
                ),
            ],
            zones=[Zone(id="ZONE_A", name="Zone A", hazard_level="HIGH", x=0, y=0, z=0)],
        )
        signals = []
        async def run():
            nonlocal signals
            signals = await gas_sensor_agent.analyze(ws, _make_context())
        import asyncio
        asyncio.run(run())
        assert len(signals) == 1
        assert signals[0].severity in ("HIGH", "MEDIUM")
        assert signals[0].zone_id == "ZONE_A"
        assert signals[0].score > 0
        assert "GAS_CH4" in signals[0].signal_type

    def test_gas_classification(self):
        sev, score = _classify_gas_level("CH4", 75.0)
        assert sev == "CRITICAL"
        assert score >= 90

        sev, score = _classify_gas_level("CH4", 5.0)
        assert sev == "LOW"
        assert score == 0.0

        sev, score = _classify_gas_level("H2S", 15.0)
        assert sev == "MEDIUM"
        assert 40 <= score <= 70


class TestWorkPermitAgent:
    def test_no_permits_no_signals(self):
        ws = WorldState(version=1, plant_id="P1", permits=[])
        signals = []
        async def run():
            nonlocal signals
            signals = await work_permit_agent.analyze(ws, _make_context())
        import asyncio
        asyncio.run(run())
        assert len(signals) == 0

    def test_hot_work_permit_signal(self):
        ws = WorldState(
            version=1, plant_id="P1",
            zones=[Zone(id="ZONE_A", name="Zone A", hazard_level="LOW", x=0, y=0, z=0)],
            workers=[Worker(
                id="W1", name="Test", role=WorkerRole.OPERATOR,
                x=0, y=0, z=0, zone_id="ZONE_A", department="Ops",
                current_ppe=["hard_hat"], shift="DAY",
            )],
            permits=[Permit(
                id="P1", name="Hot Work Permit - Test", permit_type="HOT_WORK", assigned_to="Test",
                valid_from="2024-01-01T00:00:00Z", valid_until="2024-01-01T04:00:00Z",
                approved_by="Supervisor",
            )],
        )
        signals = []
        async def run():
            nonlocal signals
            signals = await work_permit_agent.analyze(ws, _make_context())
        import asyncio
        asyncio.run(run())
        assert len(signals) >= 1
        assert any(s.signal_type == "HOT_WORK_ACTIVE" for s in signals)


class TestShiftAgent:
    def test_no_workers_no_signals(self):
        ws = WorldState(version=1, plant_id="P1", workers=[])
        signals = []
        async def run():
            nonlocal signals
            signals = await shift_agent.analyze(ws, _make_context())
        import asyncio
        asyncio.run(run())
        assert len(signals) == 0
