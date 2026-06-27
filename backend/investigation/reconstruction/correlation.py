from typing import List
from investigation.schemas import EventCorrelation

class EventCorrelator:
    def correlate(self) -> List[EventCorrelation]:
        return [
            EventCorrelation(
                source_event="Sensor V-42 Anomaly",
                target_event="Worker W-992 Entry",
                relationship="SPATIAL_PROXIMITY (10m)",
                confidence=0.99
            ),
            EventCorrelation(
                source_event="Worker W-992 Entry",
                target_event="Hot Work Permit PTW-112",
                relationship="CAUSAL (Worker executing permit)",
                confidence=1.0
            ),
            EventCorrelation(
                source_event="Sensor V-42 Anomaly",
                target_event="Hot Work Permit PTW-112",
                relationship="COMPOUND_HAZARD (Leak + Ignition Source)",
                confidence=0.98
            )
        ]

correlator = EventCorrelator()
