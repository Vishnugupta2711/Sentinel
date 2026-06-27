import pytest
from chronos.engine.core import ChronosEngine
from world_state.snapshot.models import WorldState
from world.models.entities import Sensor, Equipment
from world.models.enums import Status
from intelligence.contracts.context import IntelligenceContext
from timeline.engine.core import timeline_engine
from timeline.timeline.entry import TimelineEntry

@pytest.fixture
def engine():
    return ChronosEngine()
    
def test_chronos_baseline_forecasting(engine: ChronosEngine):
    # Setup some dummy timeline history
    s1_t0 = Sensor(id="s1", name="Temp", sensor_type="TEMPERATURE", unit="C", threshold=100.0, current_value=50.0, last_updated="2026-06-26T00:00:00Z", status="ONLINE", zone_id="z1")
    s1_t10 = Sensor(id="s1", name="Temp", sensor_type="TEMPERATURE", unit="C", threshold=100.0, current_value=60.0, last_updated="2026-06-26T00:10:00Z", status="ONLINE", zone_id="z1")
    
    e1 = Equipment(id="e1", name="Pump", equipment_type="PUMP", manufacturer="Test", maintenance_status="WARNING", status="ONLINE", zone_id="z1")
    
    ws0 = WorldState(version=0, sensors=[s1_t0], equipment=[e1])
    ws10 = WorldState(version=10, sensors=[s1_t10], equipment=[e1])
    
    entry0 = TimelineEntry(version=0, simulation_tick=0)
    entry0.set_state(ws0)
    timeline_engine.store.insert(entry0)
    
    entry10 = TimelineEntry(version=10, simulation_tick=10)
    entry10.set_state(ws10)
    timeline_engine.store.insert(entry10)
    
    # Run Prediction for T+30m from ws10
    ctx = IntelligenceContext(world_state_version=10, plant_id="p1")
    
    result = engine.predict(ctx, horizon_minutes=30)
    
    assert result.forecast_horizon_minutes == 30
    assert len(result.scenarios) == 3
    
    normal = next(s for s in result.scenarios if s.scenario_type == "NORMAL")
    worst = next(s for s in result.scenarios if s.scenario_type == "WORST_CASE")
    next(s for s in result.scenarios if s.scenario_type == "BEST_CASE")
    
    # S1 was increasing at +1.0 / min. So in 30 mins, normal is 60 + 30 = 90
    normal_sensor = next(s for s in normal.predicted_world_state.sensors if s.id == "s1")
    assert normal_sensor.current_value == 90.0
    
    # In worst case, trend is 1.5x -> 1.5/min -> 60 + 45 = 105. Since 105 > threshold 100, status should be WARNING
    worst_sensor = next(s for s in worst.predicted_world_state.sensors if s.id == "s1")
    assert worst_sensor.current_value == 105.0
    assert worst_sensor.status == Status.WARNING
    
    # Normal Equipment was WARNING, but after 30 mins, BaselineForecaster makes it CRITICAL
    normal_equip = next(e for e in normal.predicted_world_state.equipment if e.id == "e1")
    assert normal_equip.maintenance_status == Status.CRITICAL
    
    # Confidence metrics should be > 0
    assert normal.confidence.confidence_score > 0
    assert len(normal.reasoning.influencing_events) > 0
