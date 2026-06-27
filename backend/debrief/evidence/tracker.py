from typing import List
from debrief.schemas import Evidence
import datetime

class EvidenceTracker:
    def track(self) -> List[Evidence]:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        return [
            Evidence(
                id="ev_sensor_v42",
                source="Sensor V-42",
                description="Pressure gradient +0.02 psi/min recorded over 10m window.",
                confidence=0.99,
                timestamp=now
            ),
            Evidence(
                id="ev_permit_1",
                source="Compliance Engine",
                description="Active Hot Work permit HW-892 found in Zone A.",
                confidence=1.0,
                timestamp=now
            ),
            Evidence(
                id="ev_chronos_1",
                source="Chronos Engine",
                description="Predicted explosion probability 98.4% at T+30m.",
                confidence=0.98,
                timestamp=now
            )
        ]

tracker = EvidenceTracker()
