from typing import Dict

class ReasoningExplainer:
    def explain(self) -> Dict[str, str]:
        return {
            "chronos_prediction": "Chronos detected a consistent +0.02 psi/min pressure gradient over 10 minutes on Valve V-42, projecting a critical threshold breach within 30 minutes.",
            "risk_escalation": "The Compound Risk Engine identified an intersection between the projected pressure breach and an active Hot Work permit located in Zone A (10m proximity).",
            "planner_intervention": "The Counterfactual Planner rejected 'Evacuate Whole Plant' due to high downtime cost ($2M), and selected 'Revoke Permit & Isolate Valve' as it offered 99.9% risk reduction with minimal downtime ($50k)."
        }

explainer = ReasoningExplainer()
