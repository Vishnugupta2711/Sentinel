import uuid
import time
from debrief.schemas import DebriefReport, LessonsLearned
from debrief.timeline.reconstruction import reconstructor
from debrief.root_cause.analyzer import analyzer
from debrief.reasoning.explainer import explainer
from debrief.evidence.tracker import tracker
from debrief.metrics.business_impact import calculator
from debrief.compliance.mapper import mapper

class DebriefEngine:
    def generate_report(self) -> DebriefReport:
        start = time.perf_counter_ns()
        
        timeline = reconstructor.reconstruct()
        root_causes = analyzer.analyze()
        ai_explanation = explainer.explain()
        evidence = tracker.track()
        impact = calculator.calculate()
        compliance = mapper.map_compliance()
        
        lessons = LessonsLearned(
            immediate_actions=["Evacuate Zone A", "Isolate Valve V-42"],
            short_term=["Inspect all valves in Zone A", "Review Hot Work permits"],
            long_term=["Install automated pressure relief systems", "Upgrade sensor fidelity"],
            training=["Retrain operators on dynamic risk assessment"],
            engineering=["Replace seals on V-42 series valves"],
            maintenance=["Increase inspection frequency for V-series valves from 12 to 6 months"],
            policy=["Mandate Sentinel clearance for all Hot Work permits"]
        )
        
        decision_time_ms = (time.perf_counter_ns() - start) / 1_000_000
        
        return DebriefReport(
            report_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
            incident_title="Near Miss: High-Pressure Explosion Avoided",
            incident_type="Compound Risk Escalation",
            incident_severity="CRITICAL (Prevented)",
            affected_zone="Zone A",
            affected_workers=12,
            estimated_probability=0.984,
            outcome="SAFE - Autonomous Intervention Successful",
            key_decisions=[
                "Detected anomaly via Chronos",
                "Escalated compound risk via Risk Engine",
                "Revoked Permit via Counterfactual Planner"
            ],
            estimated_loss_prevented=12000000.0,
            decision_time_ms=decision_time_ms,
            root_causes=root_causes,
            timeline=timeline,
            ai_explanation=ai_explanation,
            evidence=evidence,
            compliance=compliance,
            lessons_learned=lessons,
            business_impact=impact
        )

debrief_engine = DebriefEngine()
