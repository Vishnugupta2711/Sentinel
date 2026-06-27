from typing import List
from investigation.schemas import RootCause

class RootCauseAnalyzer:
    def analyze(self) -> List[RootCause]:
        return [
            RootCause(
                category="Process",
                methodology="5 Whys",
                description="Permit system does not perform real-time sensor verification before allowing contractor entry.",
                confidence=0.98,
                evidence_ids=["EVID-003"]
            ),
            RootCause(
                category="Equipment",
                methodology="Fault Tree Analysis",
                description="Valve V-42 internal seal degradation leading to microscopic leak.",
                confidence=0.92,
                evidence_ids=["EVID-002"]
            )
        ]

analyzer = RootCauseAnalyzer()
