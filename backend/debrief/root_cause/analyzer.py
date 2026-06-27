from typing import List
from debrief.schemas import RootCause

class RootCauseAnalyzer:
    def analyze(self) -> List[RootCause]:
        return [
            RootCause(
                category="Process",
                description="Hot work permit was approved near an active pipeline without checking latent anomalies.",
                confidence=0.98,
                evidence_ids=["ev_permit_1", "ev_chronos_1"]
            ),
            RootCause(
                category="Equipment",
                description="Valve V-42 experienced microscopic pressure fluctuations indicating seal degradation.",
                confidence=0.92,
                evidence_ids=["ev_sensor_v42"]
            ),
            RootCause(
                category="Management",
                description="Lack of dynamic risk assessment during permit approval workflow.",
                confidence=0.85,
                evidence_ids=["ev_policy_4"]
            )
        ]

analyzer = RootCauseAnalyzer()
