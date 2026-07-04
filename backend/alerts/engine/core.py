import asyncio
import structlog
from typing import List, Optional, Dict
from collections import defaultdict
from alerts.models.schemas import (
    Alert, AlertPriority, AlertStatus, AlertChannel, AlertQueue
)
from correlation.models.schemas import CompoundRiskAssessment
from agents.base import AgentSignal

logger = structlog.get_logger(__name__)

PRIORITY_ORDER = [AlertPriority.EMERGENCY, AlertPriority.CRITICAL,
                  AlertPriority.HIGH, AlertPriority.MEDIUM, AlertPriority.LOW]


class AlertEngine:
    def __init__(self):
        self._queue: Dict[str, Alert] = {}
        self._history: List[Alert] = []
        self._subscribers: List[asyncio.Queue] = []

    def evaluate_signals(self, signals: List[AgentSignal]) -> List[Alert]:
        alerts: List[Alert] = []
        for s in signals:
            priority = self._signal_severity_to_priority(s.severity)
            alert = Alert(
                title=f"{s.agent_name.replace('_', ' ').title()}: {s.signal_type.replace('_', ' ')}",
                description=s.description,
                priority=priority,
                source_agent=s.agent_name,
                source_signals=[s.signal_id],
                zone_id=s.zone_id,
                score=s.score,
                channels=self._determine_channels(priority),
                metadata=s.metadata,
            )
            self._queue[alert.alert_id] = alert
            self._history.append(alert)
            alerts.append(alert)

        if len(self._history) > 500:
            self._history = self._history[-500:]

        return alerts

    def evaluate_correlation(self, assessment: CompoundRiskAssessment) -> Optional[Alert]:
        priority = self._correlation_level_to_priority(assessment.level)
        alert = Alert(
            title=f"Compound Risk: {assessment.level.value} - {assessment.primary_zone or 'Multiple Zones'}",
            description=assessment.description,
            priority=priority,
            source_agent="correlation",
            source_signals=[c.agent_name for c in assessment.contributing_signals],
            zone_id=assessment.primary_zone,
            correlation_id=assessment.correlation_id,
            score=assessment.score,
            channels=self._determine_channels(priority),
            ttl_seconds=7200 if priority in (AlertPriority.EMERGENCY, AlertPriority.CRITICAL) else 3600,
            metadata={
                "contributing_agents": [c.agent_name for c in assessment.contributing_signals],
                "recommendations": assessment.recommendations,
                "method": assessment.method.value,
            },
        )
        self._queue[alert.alert_id] = alert
        self._history.append(alert)
        return alert

    def acknowledge(self, alert_id: str, user: str) -> bool:
        if alert_id in self._queue:
            self._queue[alert_id].status = AlertStatus.ACKNOWLEDGED
            self._queue[alert_id].acknowledged_by = user
            from utils.datetime import format_iso, utc_now
            self._queue[alert_id].acknowledged_at = format_iso(utc_now())
            return True
        for alert in self._history:
            if alert.alert_id == alert_id:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = user
                return True
        return False

    def resolve(self, alert_id: str) -> bool:
        if alert_id in self._queue:
            self._queue[alert_id].status = AlertStatus.RESOLVED
            from utils.datetime import format_iso, utc_now
            self._queue[alert_id].resolved_at = format_iso(utc_now())
            self._queue.pop(alert_id)
            return True
        return False

    def get_active_alerts(self, priority: Optional[str] = None) -> List[Alert]:
        alerts = [a for a in self._queue.values() if a.status in (AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.IN_PROGRESS)]
        if priority:
            alerts = [a for a in alerts if a.priority.value == priority.upper()]
        alerts.sort(key=lambda a: (PRIORITY_ORDER.index(a.priority) if a.priority in PRIORITY_ORDER else 999, -a.score))
        return alerts

    def get_alert_history(self, limit: int = 50) -> List[Alert]:
        return sorted(self._history, key=lambda a: a.timestamp, reverse=True)[:limit]

    def get_queue_summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = defaultdict(int)
        for a in self._queue.values():
            if a.status in (AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.IN_PROGRESS):
                counts[a.priority.value] += 1
        return dict(counts)

    def subscribe(self, q: asyncio.Queue) -> None:
        self._subscribers.append(q)

    def unsubscribe(self, q: asyncio.Queue) -> None:
        if q in self._subscribers:
            self._subscribers.remove(q)

    def _broadcast(self, alert: Alert) -> None:
        payload = {
            "event": "NEW_ALERT",
            "alert": alert.model_dump(),
        }
        for q in self._subscribers:
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                pass

    def _signal_severity_to_priority(self, severity: str) -> AlertPriority:
        mapping = {
            "CRITICAL": AlertPriority.CRITICAL,
            "HIGH": AlertPriority.HIGH,
            "MEDIUM": AlertPriority.MEDIUM,
            "LOW": AlertPriority.LOW,
        }
        return mapping.get(severity, AlertPriority.LOW)

    def _correlation_level_to_priority(self, level: str) -> AlertPriority:
        mapping = {
            "CRITICAL": AlertPriority.EMERGENCY,
            "HIGH": AlertPriority.CRITICAL,
            "MEDIUM": AlertPriority.HIGH,
            "LOW": AlertPriority.MEDIUM,
            "NONE": AlertPriority.LOW,
        }
        return mapping.get(level, AlertPriority.LOW)

    def _determine_channels(self, priority: AlertPriority) -> List[AlertChannel]:
        if priority == AlertPriority.EMERGENCY:
            return [AlertChannel.SIREN, AlertChannel.WEBSOCKET, AlertChannel.DASHBOARD, AlertChannel.SMS]
        if priority == AlertPriority.CRITICAL:
            return [AlertChannel.WEBSOCKET, AlertChannel.DASHBOARD, AlertChannel.SMS]
        if priority == AlertPriority.HIGH:
            return [AlertChannel.WEBSOCKET, AlertChannel.DASHBOARD]
        return [AlertChannel.DASHBOARD]


alert_engine = AlertEngine()
