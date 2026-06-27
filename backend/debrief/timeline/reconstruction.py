from typing import List
from debrief.schemas import TimelineEvent

class TimelineReconstructor:
    def reconstruct(self) -> List[TimelineEvent]:
        # For the hackathon/demo, we will synthesize a deterministic timeline
        # representing a full T-30m scenario. In production, this would query
        # the TimelineStore for state diffs between timestamps.
        
        return [
            TimelineEvent(
                timestamp="T-30m",
                t_minus="-30m",
                event_type="Chronos Alert",
                description="Chronos detected pipeline pressure anomaly in Zone A."
            ),
            TimelineEvent(
                timestamp="T-20m",
                t_minus="-20m",
                event_type="Permit Active",
                description="Hot Work Permit approved for Contractor team in Zone A."
            ),
            TimelineEvent(
                timestamp="T-10m",
                t_minus="-10m",
                event_type="Risk Escalation",
                description="Compound Risk Engine escalated hazard: Hot Work + Pressure Anomaly."
            ),
            TimelineEvent(
                timestamp="T-5m",
                t_minus="-5m",
                event_type="Planner Triggered",
                description="Counterfactual Planner generated mitigation interventions."
            ),
            TimelineEvent(
                timestamp="T-1m",
                t_minus="-1m",
                event_type="Intervention",
                description="Automatic valve shut-off and worker evacuation order issued."
            ),
            TimelineEvent(
                timestamp="T0",
                t_minus="0",
                event_type="Safe Outcome",
                description="Explosion avoided. Pressure returned to baseline. Workers secured."
            ),
        ]

reconstructor = TimelineReconstructor()
