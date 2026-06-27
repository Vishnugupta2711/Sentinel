import pytest
from risk.engine.core import CompoundRiskEngine
from risk.models.schemas import RiskType, RiskLevel, AlertPriority
from world_state.snapshot.models import WorldState
from world.models.entities import Sensor, Permit, Worker
from world.models.enums import Status
from intelligence.contracts.context import IntelligenceContext
from timeline.engine.core import timeline_engine
from timeline.timeline.entry import TimelineEntry

@pytest.fixture
def engine():
    return CompoundRiskEngine()

def test_explosion_risk_rule(engine: CompoundRiskEngine):
    # Setup state
    s1 = Sensor(id="s1", name="Gas Sensor", sensor_type="GAS", unit="PPM", threshold=100.0, current_value=120.0, last_updated="2026-06-26T00:00:00Z", status=Status.CRITICAL, zone_id="z1")
    p1 = Permit(id="p1", name="hot_work_permit", permit_type="HOT_WORK", assigned_to="w1", valid_from="2026-06-26T00:00:00Z", valid_until="2026-06-26T23:59:59Z", status=Status.ONLINE)
    w1 = Worker(id="w1", name="John", department="Maint", shift="Day", role="MAINTENANCE", status=Status.ONLINE, zone_id="z1")
    w2 = Worker(id="w2", name="Jane", department="Eng", shift="Day", role="SUPERVISOR", status=Status.ONLINE, zone_id="z2")
    
    ws = WorldState(version=1, sensors=[s1], permits=[p1], workers=[w1, w2])
    
    # Needs to be in timeline for the engine to pick it up
    entry = TimelineEntry(version=1, simulation_tick=1)
    entry.set_state(ws)
    timeline_engine.store.insert(entry)
    
    ctx = IntelligenceContext(world_state_version=1, plant_id="p1")
    
    risks = engine.analyze(ctx)
    
    assert len(risks) == 1
    r = risks[0]
    
    assert r.risk_type == RiskType.EXPLOSION
    assert r.priority == AlertPriority.P1
    assert r.risk_level == RiskLevel.CRITICAL
    assert r.affected_zones == ["z1"]
    assert r.affected_workers == ["w1"]
    
def test_worker_fatality_rule(engine: CompoundRiskEngine):
    s1 = Sensor(id="s1", name="Smoke Sensor", sensor_type="SMOKE", unit="PPM", threshold=100.0, current_value=150.0, last_updated="2026-06-26T00:00:00Z", status=Status.CRITICAL, zone_id="z3")
    p1 = Permit(id="p1", name="confined_space", permit_type="CONFINED_SPACE", assigned_to="w1", valid_from="2026-06-26T00:00:00Z", valid_until="2026-06-26T23:59:59Z", status=Status.ONLINE)
    w1 = Worker(id="w1", name="Mike", department="Maint", shift="Day", role="SAFETY_OFFICER", status=Status.ONLINE, zone_id="z3")
    
    ws = WorldState(version=2, sensors=[s1], permits=[p1], workers=[w1])
    
    entry = TimelineEntry(version=2, simulation_tick=2)
    entry.set_state(ws)
    timeline_engine.store.insert(entry)
    
    ctx = IntelligenceContext(world_state_version=2, plant_id="p1")
    
    risks = engine.analyze(ctx)
    
    assert len(risks) == 1
    r = risks[0]
    
    assert r.risk_type == RiskType.CHEMICAL_EXPOSURE
    assert r.priority == AlertPriority.P1
    assert r.affected_zones == ["z3"]
    assert r.affected_workers == ["w1"]
