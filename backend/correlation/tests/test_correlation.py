from agents.base import AgentSignal
from correlation.engine.core import correlation_engine
from correlation.models.schemas import CompoundRiskLevel


class TestCorrelationEngine:
    def test_no_signals_returns_empty(self):
        result = correlation_engine.correlate([])
        assert result.signal_count == 0
        assert len(result.assessments) == 0
        assert result.highest_level == CompoundRiskLevel.NONE

    def test_single_signal_no_correlation(self):
        signals = [
            AgentSignal(
                agent_name="gas_sensor", signal_type="GAS_CH4",
                severity="LOW", zone_id="ZONE_A",
                description="Low gas", score=15.0,
            ),
        ]
        result = correlation_engine.correlate(signals)
        assert len(result.assessments) == 0

    def test_multi_agent_zone_overlap(self):
        signals = [
            AgentSignal(
                agent_name="gas_sensor", signal_type="GAS_CH4",
                severity="HIGH", zone_id="ZONE_A",
                description="High gas", score=75.0,
            ),
            AgentSignal(
                agent_name="work_permit", signal_type="HOT_WORK_ACTIVE",
                severity="HIGH", zone_id="ZONE_A",
                description="Hot work", score=60.0,
            ),
        ]
        result = correlation_engine.correlate(signals)
        assert len(result.assessments) >= 1
        overlapping = [a for a in result.assessments if a.method.value == "zone_overlap"]
        assert len(overlapping) >= 1
        assert overlapping[0].primary_zone == "ZONE_A"
        assert overlapping[0].level in (CompoundRiskLevel.HIGH, CompoundRiskLevel.CRITICAL)
        assert any("gas" in r.lower() for r in overlapping[0].recommendations)

    def test_score_to_level(self):
        assert correlation_engine._score_to_level(90) == CompoundRiskLevel.CRITICAL
        assert correlation_engine._score_to_level(70) == CompoundRiskLevel.HIGH
        assert correlation_engine._score_to_level(50) == CompoundRiskLevel.MEDIUM
        assert correlation_engine._score_to_level(20) == CompoundRiskLevel.LOW
        assert correlation_engine._score_to_level(5) == CompoundRiskLevel.NONE
