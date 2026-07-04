from typing import List, Dict, Optional, Any
from collections import defaultdict
import structlog
from correlation.models.schemas import (
    CorrelationMethod, CompoundRiskLevel, AgentContribution,
    TemporalWindow, CompoundRiskAssessment, CorrelationResult
)
from agents.base import AgentSignal

logger = structlog.get_logger(__name__)

TEMPORAL_WINDOW_MINUTES = 15
ZONE_WEIGHT = 1.5
CROSS_AGENT_WEIGHT = 2.0


class CorrelationEngine:
    def __init__(self):
        self._history: List[AgentSignal] = []

    def correlate(self, signals: List[AgentSignal]) -> CorrelationResult:
        self._history.extend(signals)
        if len(self._history) > 1000:
            self._history = self._history[-1000:]

        assessments: List[CompoundRiskAssessment] = []

        zone_assessments = self._correlate_by_zone(signals)
        assessments.extend(zone_assessments)

        temporal_assessments = self._correlate_temporal(signals)
        assessments.extend(temporal_assessments)

        severity_assessments = self._correlate_severity_escalation(signals)
        assessments.extend(severity_assessments)

        unique_zones = set(s.zone_id for s in signals if s.zone_id)
        highest = self._highest_level([a.level for a in assessments]) if assessments else CompoundRiskLevel.NONE

        return CorrelationResult(
            assessments=assessments,
            signal_count=len(signals),
            agent_count=len(set(s.agent_name for s in signals)),
            highest_level=highest,
        )

    def _correlate_by_zone(self, signals: List[AgentSignal]) -> List[CompoundRiskAssessment]:
        assessments: List[CompoundRiskAssessment] = []
        by_zone: Dict[str, List[AgentSignal]] = defaultdict(list)

        for s in signals:
            if s.zone_id:
                by_zone[s.zone_id].append(s)

        for zone_id, zone_signals in by_zone.items():
            if len(zone_signals) < 2:
                continue

            agent_names = set(s.agent_name for s in zone_signals)
            if len(agent_names) < 2:
                continue

            total_score = sum(s.score for s in zone_signals)
            avg_score = total_score / len(zone_signals)
            cross_agent_bonus = (len(agent_names) - 1) * CROSS_AGENT_WEIGHT * 10
            zone_bonus = ZONE_WEIGHT * 5
            compound_score = min(avg_score + cross_agent_bonus + zone_bonus, 100.0)

            level = self._score_to_level(compound_score)

            agents_involved = []
            for agent_name in sorted(agent_names):
                agent_signals = [s for s in zone_signals if s.agent_name == agent_name]
                if agent_signals:
                    top = max(agent_signals, key=lambda x: x.score)
                    agents_involved.append(AgentContribution(
                        agent_name=agent_name,
                        signal_type=top.signal_type,
                        current_severity=top.severity,
                        current_score=top.score,
                    ))

            signal_types = [s.signal_type for s in zone_signals]
            gas_related = any("GAS" in s for s in signal_types)
            hot_work_related = any("HOT_WORK" in s or "CONFINED" in s for s in signal_types)
            shift_related = any("SHIFT" in s or "HANDOVER" in s for s in signal_types)

            recommendations = []
            if gas_related and hot_work_related:
                recommendations.append("IMMEDIATE: Suspend all hot work in zone - gas hazard detected")
            if gas_related and shift_related:
                recommendations.append("URGENT: Verify shift handover completed near gas hazard zone")
            if hot_work_related:
                recommendations.append("Ensure fire watch is present and extinguishers are accessible")
            if level in (CompoundRiskLevel.HIGH, CompoundRiskLevel.CRITICAL):
                recommendations.append("Consider evacuating zone until risk is mitigated")

            descriptions = []
            agent_count = len(agent_names)
            desc = f"Compound risk in {zone_id}: {agent_count} agents reporting ({', '.join(sorted(agent_names))}). "
            if gas_related and hot_work_related:
                desc += "Gas hazard overlapping with hot work - IMMEDIATE ACTION REQUIRED. "
            desc += f"Compound score: {compound_score:.1f}/100 ({level.value})."
            descriptions.append(desc)

            if level != CompoundRiskLevel.NONE:
                assessments.append(CompoundRiskAssessment(
                    correlation_id=f"zone-{zone_id}-{len(assessments)}",
                    level=level,
                    score=round(compound_score, 1),
                    primary_zone=zone_id,
                    description=descriptions[0],
                    method=CorrelationMethod.ZONE_OVERLAP,
                    contributing_signals=agents_involved,
                    recommendations=recommendations,
                    metadata={
                        "zone_id": zone_id,
                        "agents_involved": list(agent_names),
                        "signal_count": len(zone_signals),
                        "gas_hazard": gas_related,
                        "hot_work_active": hot_work_related,
                        "shift_issue": shift_related,
                    }
                ))

        return assessments

    def _correlate_temporal(self, signals: List[AgentSignal]) -> List[CompoundRiskAssessment]:
        assessments: List[CompoundRiskAssessment] = []
        if len(self._history) < 3:
            return assessments

        recent = self._history[-50:]
        escalating = defaultdict(list)
        for s in recent:
            if s.score >= 30:
                escalating[s.zone_id or "unknown"].append(s)

        for zone_id, zone_signals in escalating.items():
            if len(zone_signals) >= 3:
                score_trend = [s.score for s in zone_signals[-5:]]
                if len(score_trend) >= 3 and score_trend[-1] > score_trend[0] * 1.5:
                    avg = sum(score_trend) / len(score_trend)
                    compound_score = min(avg * 1.3, 100.0)
                    level = self._score_to_level(compound_score)
                    if level != CompoundRiskLevel.NONE:
                        assessments.append(CompoundRiskAssessment(
                            correlation_id=f"temporal-{zone_id}-{len(assessments)}",
                            level=level,
                            score=round(compound_score, 1),
                            primary_zone=zone_id,
                            description=f"Escalating risk in {zone_id}: signal scores rising {score_trend[0]:.0f}→{score_trend[-1]:.0f} over recent observations",
                            method=CorrelationMethod.TEMPORAL_WINDOW,
                            contributing_signals=[AgentContribution(
                                agent_name=s.agent_name,
                                signal_type=s.signal_type,
                                current_severity=s.severity,
                                current_score=s.score,
                            ) for s in zone_signals[-3:]],
                            recommendations=["Monitor zone closely - risk trending upward",
                                             "Prepare intervention plan if trend continues"],
                        ))
        return assessments

    def _correlate_severity_escalation(self, signals: List[AgentSignal]) -> List[CompoundRiskAssessment]:
        assessments: List[CompoundRiskAssessment] = []
        critical_signals = [s for s in signals if s.severity == "CRITICAL"]

        for cs in critical_signals:
            zone_signals = [s for s in self._history[-20:] if s.zone_id == cs.zone_id and s.signal_id != cs.signal_id]
            non_critical = [s for s in zone_signals if s.severity != "CRITICAL"]

            if len(non_critical) >= 2:
                agent_names = set(s.agent_name for s in non_critical)
                if len(agent_names) >= 2:
                    total = sum(s.score for s in non_critical) + cs.score
                    avg = total / (len(non_critical) + 1)
                    compound_score = min(avg * 1.5, 100.0)
                    level = self._score_to_level(compound_score)
                    if level not in (CompoundRiskLevel.NONE, CompoundRiskLevel.LOW):
                        zone_label = cs.zone_id or "unknown"
                        assessments.append(CompoundRiskAssessment(
                            correlation_id=f"severity-{cs.zone_id or 'unknown'}-{len(assessments)}",
                            level=level,
                            score=round(compound_score, 1),
                            primary_zone=cs.zone_id,
                            description=f"Severity escalation in {zone_label}: {cs.agent_name} reports CRITICAL while {len(non_critical)} other signals present",
                            method=CorrelationMethod.SEVERITY_ESCALATION,
                            contributing_signals=[
                                AgentContribution(
                                    agent_name=cs.agent_name,
                                    signal_type=cs.signal_type,
                                    current_severity=cs.severity,
                                    current_score=cs.score,
                                )
                            ] + [
                                AgentContribution(
                                    agent_name=s.agent_name,
                                    signal_type=s.signal_type,
                                    current_severity=s.severity,
                                    current_score=s.score,
                                ) for s in non_critical[:3]
                            ],
                            recommendations=["CRITICAL: Immediate evacuation may be required",
                                             "Dispatch safety officer to zone immediately"],
                        ))

        return assessments

    def get_latest_assessments(self, top_k: int = 5) -> List[CompoundRiskAssessment]:
        all_assessments = []
        for sig in self._history:
            pass
        return []

    def _score_to_level(self, score: float) -> CompoundRiskLevel:
        if score >= 85:
            return CompoundRiskLevel.CRITICAL
        if score >= 65:
            return CompoundRiskLevel.HIGH
        if score >= 35:
            return CompoundRiskLevel.MEDIUM
        if score >= 10:
            return CompoundRiskLevel.LOW
        return CompoundRiskLevel.NONE

    def _highest_level(self, levels: List[CompoundRiskLevel]) -> CompoundRiskLevel:
        order = [CompoundRiskLevel.NONE, CompoundRiskLevel.LOW, CompoundRiskLevel.MEDIUM,
                 CompoundRiskLevel.HIGH, CompoundRiskLevel.CRITICAL]
        max_idx = max(order.index(l) for l in levels)
        return order[max_idx]


correlation_engine = CorrelationEngine()
