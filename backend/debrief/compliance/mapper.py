from typing import List
from debrief.schemas import ComplianceMapping

class ComplianceMapper:
    def map_compliance(self) -> List[ComplianceMapping]:
        return [
            ComplianceMapping(
                regulation="OSHA 1910.252",
                section="General Requirements for Welding, Cutting, and Brazing",
                requirement="Fire watchers are required whenever welding or cutting is performed.",
                status="VIOLATION PREVENTED",
                corrective_action="Sentinel automatically revoked permit before violation occurred."
            ),
            ComplianceMapping(
                regulation="OISD-STD-105",
                section="Work Permit System",
                requirement="Hot work permit must not be issued if flammable gas is present.",
                status="VIOLATION PREVENTED",
                corrective_action="Sentinel identified pressure anomaly and counteracted permit."
            )
        ]

mapper = ComplianceMapper()
