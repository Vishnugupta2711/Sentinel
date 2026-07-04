from agents.base import AgentSignal
from alerts.engine.core import alert_engine
from alerts.models.schemas import AlertPriority, AlertStatus
from correlation.models.schemas import CompoundRiskAssessment, CompoundRiskLevel, AgentContribution


class TestAlertEngine:
    def test_evaluate_signals(self):
        signals = [
            AgentSignal(
                agent_name="gas_sensor", signal_type="GAS_CH4",
                severity="CRITICAL", zone_id="ZONE_A",
                description="Critical gas level", score=95.0,
            ),
        ]
        alerts = alert_engine.evaluate_signals(signals)
        assert len(alerts) == 1
        assert alerts[0].priority == AlertPriority.CRITICAL
        assert alerts[0].source_agent == "gas_sensor"

    def test_evaluate_correlation_assessment(self):
        assessment = CompoundRiskAssessment(
            correlation_id="test-001",
            level=CompoundRiskLevel.CRITICAL,
            score=94.0,
            primary_zone="ZONE_A",
            description="Test compound risk",
            method="zone_overlap",
            contributing_signals=[
                AgentContribution(agent_name="gas_sensor", signal_type="GAS_CH4",
                                  current_severity="CRITICAL", current_score=95.0),
            ],
            recommendations=["Evacuate zone"],
        )
        alert = alert_engine.evaluate_correlation(assessment)
        assert alert is not None
        assert alert.priority == AlertPriority.EMERGENCY
        assert alert.correlation_id == "test-001"

    def test_acknowledge_alert(self):
        signals = [
            AgentSignal(
                agent_name="test", signal_type="TEST",
                severity="HIGH", zone_id="Z1",
                description="Test", score=50.0,
            ),
        ]
        alerts = alert_engine.evaluate_signals(signals)
        assert len(alerts) > 0
        alert_id = alerts[0].alert_id
        result = alert_engine.acknowledge(alert_id, "test_user")
        assert result is True
        active = alert_engine.get_active_alerts()
        assert any(a.alert_id == alert_id and a.status == AlertStatus.ACKNOWLEDGED for a in active)

    def test_resolve_alert(self):
        signals = [
            AgentSignal(
                agent_name="test", signal_type="TEST",
                severity="LOW", zone_id="Z1",
                description="Test", score=10.0,
            ),
        ]
        alerts = alert_engine.evaluate_signals(signals)
        alert_id = alerts[0].alert_id
        result = alert_engine.resolve(alert_id)
        assert result is True
        active = alert_engine.get_active_alerts()
        assert all(a.alert_id != alert_id for a in active)

    def test_get_active_alerts_sorted(self):
        alert_engine.evaluate_signals([
            AgentSignal(agent_name="a", signal_type="T1", severity="LOW", zone_id="Z1", description="Low", score=10.0),
            AgentSignal(agent_name="b", signal_type="T2", severity="CRITICAL", zone_id="Z2", description="Critical", score=95.0),
            AgentSignal(agent_name="c", signal_type="T3", severity="HIGH", zone_id="Z3", description="High", score=70.0),
        ])
        active = alert_engine.get_active_alerts()
        order = [AlertPriority.EMERGENCY, AlertPriority.CRITICAL, AlertPriority.HIGH, AlertPriority.MEDIUM, AlertPriority.LOW]
        indices = []
        for a in active:
            try:
                indices.append(order.index(a.priority))
            except ValueError:
                indices.append(999)
        for i in range(len(indices) - 1):
            assert indices[i] <= indices[i + 1], f"Alert order wrong at {i}: {[a.priority.value for a in active]}"

    def test_queue_summary(self):
        summary = alert_engine.get_queue_summary()
        assert isinstance(summary, dict)
