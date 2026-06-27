from typing import List
from investigation.schemas import TimelineNode
import datetime

class TimelineReconstructor:
    def reconstruct(self) -> List[TimelineNode]:
        return [
            TimelineNode(
                t_minus="T-30 min",
                timestamp=(datetime.datetime.utcnow() - datetime.timedelta(minutes=30)).isoformat() + "Z",
                event_type="Sensor Deviation",
                description="Initial microscopic pressure leak detected.",
                related_evidence_ids=["EVID-002"]
            ),
            TimelineNode(
                t_minus="T-15 min",
                timestamp=(datetime.datetime.utcnow() - datetime.timedelta(minutes=15)).isoformat() + "Z",
                event_type="Permit Active",
                description="Hot work permit activated in adjacent zone.",
                related_evidence_ids=["EVID-003"]
            ),
            TimelineNode(
                t_minus="T-5 min",
                timestamp=(datetime.datetime.utcnow() - datetime.timedelta(minutes=5)).isoformat() + "Z",
                event_type="Worker Entry",
                description="Worker W-992 entered Zone A with welding equipment.",
                related_evidence_ids=["EVID-001"]
            ),
            TimelineNode(
                t_minus="T0",
                timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                event_type="AI Intervention",
                description="Planner executed emergency shutdown and evacuation.",
                related_evidence_ids=[]
            ),
            TimelineNode(
                t_minus="T+5 min",
                timestamp=(datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).isoformat() + "Z",
                event_type="State Safe",
                description="Zone secured. Incident avoided.",
                related_evidence_ids=[]
            )
        ]

reconstructor = TimelineReconstructor()
