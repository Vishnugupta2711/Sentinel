import pytest
from planner.engine.core import CounterfactualEngine
from risk.models.schemas import RiskType, RiskLevel, AlertPriority, CompoundRiskAssessment, RiskExplanation, RiskConfidence
from world_state.snapshot.models import WorldState
from world.models.entities import Sensor, Permit, Worker
from world.models.enums import Status
from intelligence.contracts.context import IntelligenceContext
from timeline.engine.core import timeline_engine
from timeline.timeline.entry import TimelineEntry

@pytest.fixture
def engine():
    return CounterfactualEngine()
    
def test_counterfactual_engine(engine: CounterfactualEngine):
    # Setup state
    s1 = Sensor(id="s1", name="Gas Sensor", sensor_type="GAS", unit="PPM", threshold=100.0, current_value=120.0, last_updated="2026-06-26T00:00:00Z", status=Status.CRITICAL, zone_id="z1")
    p1 = Permit(id="p1", name="hot_work_permit", permit_type="HOT_WORK", assigned_to="w1", valid_from="2026-06-26T00:00:00Z", valid_until="2026-06-26T23:59:59Z", status=Status.ONLINE)
    w1 = Worker(id="w1", name="John", department="Maint", shift="Day", role="MAINTENANCE", status=Status.ONLINE, zone_id="z1")
    
    ws = WorldState(version=1, sensors=[s1], permits=[p1], workers=[w1])
    
    entry = TimelineEntry(version=1, simulation_tick=1)
    entry.set_state(ws)
    timeline_engine.store.insert(entry)
    
    # We need a risk to evaluate
    risk = CompoundRiskAssessment(
        risk_type=RiskType.EXPLOSION,
        risk_score=95.0,
        risk_level=RiskLevel.CRITICAL,
        priority=AlertPriority.P1,
        explanation=RiskExplanation(why_detected="", contributing_factors=[], supporting_events=[], supporting_sensors=[], predicted_outcome=""),
        root_causes=[],
        confidence=RiskConfidence(risk_confidence=1.0, prediction_confidence=1.0, data_quality=1.0, evidence_score=1.0),
        affected_workers=["w1"],
        affected_zones=["z1"],
        recommended_actions=[]
    )
    
    ctx = IntelligenceContext(world_state_version=1, plant_id="p1", metadata={"compound_risks": [risk]})
    
    results = engine.generate_plans(ctx)
    
    assert risk.risk_id in results
    plans = results[risk.risk_id]
    
    # We expect 3 scenarios (A, C, Baseline)
    assert len(plans) == 3
    
    # Check that Scenario A (Targeted) is better than Baseline
    scenario_a = next(p for p in plans if "Scenario A" in p.scenario_name)
    baseline = next(p for p in plans if "Baseline" in p.scenario_name)
    
    assert scenario_a.score > baseline.score
    
    # Check actions for Scenario A
    assert len(scenario_a.actions) == 1
    assert scenario_a.actions[0].action_type == "CANCEL_PERMIT"
    assert scenario_a.actions[0].target_id == "p1"
