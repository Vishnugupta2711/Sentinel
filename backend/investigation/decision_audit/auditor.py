from typing import List
from investigation.schemas import DecisionAudit

class DecisionAuditor:
    def audit(self) -> List[DecisionAudit]:
        return [
            DecisionAudit(
                engine_name="Chronos Forecaster",
                decision_made="Predicted threshold breach for V-42 at T+30m",
                latency_ms=0.15,
                accuracy_score=0.99,
                alternative_actions_considered=[]
            ),
            DecisionAudit(
                engine_name="Counterfactual Planner",
                decision_made="Revoked PTW-112 and triggered evacuation of Zone A",
                latency_ms=0.22,
                accuracy_score=1.0,
                alternative_actions_considered=[
                    "Shut down entire plant (Rejected: Unnecessary downtime)",
                    "Deploy fire suppression (Rejected: Premature)"
                ]
            )
        ]

auditor = DecisionAuditor()
