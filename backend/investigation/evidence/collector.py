from typing import List
from investigation.schemas import EvidenceItem
import datetime

class EvidenceCollector:
    def collect(self) -> List[EvidenceItem]:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        return [
            EvidenceItem(
                id="EVID-001",
                source="Timeline Engine",
                timestamp=now,
                description="Worker W-992 entered Zone A",
                confidence=1.0,
                traceability_link="timeline_store://events/w992_entry"
            ),
            EvidenceItem(
                id="EVID-002",
                source="Chronos",
                timestamp=now,
                description="Pressure gradient +0.05 psi/s detected on Valve V-42",
                confidence=0.99,
                traceability_link="chronos://predictions/v42_anomaly"
            ),
            EvidenceItem(
                id="EVID-003",
                source="Compliance Engine",
                timestamp=now,
                description="Active Hot Work permit (PTW-112) in Zone A",
                confidence=1.0,
                traceability_link="compliance://permits/ptw112"
            )
        ]

collector = EvidenceCollector()
