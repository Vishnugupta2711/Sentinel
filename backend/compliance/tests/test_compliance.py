import pytest
from compliance.engine.core import ComplianceEngine
from compliance.models.schemas import RegulationBody, ViolationSeverity
from world_state.snapshot.models import WorldState
from world.models.entities import Sensor, Permit, Worker, Zone
from world.models.enums import Status
from intelligence.contracts.context import IntelligenceContext
from timeline.engine.core import timeline_engine
from timeline.timeline.entry import TimelineEntry

@pytest.fixture
def engine():
    return ComplianceEngine()

def test_missing_ppe_rule(engine: ComplianceEngine):
    z1 = Zone(id="z1", name="Reactor Zone", hazard_level="CRITICAL")
    w1 = Worker(id="w1", name="John", department="Maint", shift="Day", role="MAINTENANCE", status=Status.ONLINE, zone_id="z1", current_ppe=["Hard Hat"]) # Missing Goggles
    w2 = Worker(id="w2", name="Jane", department="Eng", shift="Day", role="SUPERVISOR", status=Status.ONLINE, zone_id="z1", current_ppe=["Hard Hat", "Safety Goggles"]) # Compliant
    
    ws = WorldState(version=1, zones=[z1], workers=[w1, w2])
    
    entry = TimelineEntry(version=1, simulation_tick=1)
    entry.set_state(ws)
    timeline_engine.store.insert(entry)
    
    ctx = IntelligenceContext(world_state_version=1, plant_id="p1")
    
    violations = engine.evaluate(ctx)
    
    assert len(violations) == 1
    v = violations[0]
    
    assert v.severity == ViolationSeverity.MAJOR
    assert v.regulation_reference.body == RegulationBody.INTERNAL_SOP
    assert "Safety Goggles" in v.description
    assert "w1" in v.evidence.supporting_workers
    assert "w2" not in v.evidence.supporting_workers

def test_oisd_hot_work_rule(engine: ComplianceEngine):
    s1 = Sensor(id="s1", name="Gas Sensor", sensor_type="GAS", unit="PPM", threshold=100.0, current_value=120.0, last_updated="2026-06-26T00:00:00Z", status=Status.CRITICAL, zone_id="z1")
    p1 = Permit(id="p1", name="hot_work", permit_type="HOT_WORK", assigned_to="w1", valid_from="2026-06-26T00:00:00Z", valid_until="2026-06-26T23:59:59Z", status=Status.ONLINE)
    w1 = Worker(id="w1", name="Mike", department="Maint", shift="Day", role="MAINTENANCE", status=Status.ONLINE, zone_id="z1", current_ppe=[])
    
    ws = WorldState(version=2, sensors=[s1], permits=[p1], workers=[w1])
    
    entry = TimelineEntry(version=2, simulation_tick=2)
    entry.set_state(ws)
    timeline_engine.store.insert(entry)
    
    ctx = IntelligenceContext(world_state_version=2, plant_id="p1")
    
    violations = engine.evaluate(ctx)
    
    # We should get both PPE (Mike has no PPE in a high hazard zone? Wait, zone_id=z1 doesn't have hazard_level in this state since we didn't add it to ws.zones. So missing PPE rule won't fire)
    assert len(violations) == 1
    v = violations[0]
    
    assert v.severity == ViolationSeverity.CRITICAL
    assert v.regulation_reference.body == RegulationBody.OISD
    assert "w1" in v.evidence.supporting_workers
    assert "p1" in v.evidence.supporting_permits
    assert "s1" in v.evidence.supporting_sensors
