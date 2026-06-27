from typing import List
from investigation.schemas import Recommendation

class RecommendationGenerator:
    def generate(self) -> List[Recommendation]:
        return [
            Recommendation(
                category="Engineering",
                priority="CRITICAL",
                owner="Maintenance Dept",
                description="Replace Valve V-42 internal seals with high-pressure rated graphite components.",
                expected_risk_reduction="Eliminates microscopic leak vulnerability (99% reduction)"
            ),
            Recommendation(
                category="Administrative",
                priority="HIGH",
                owner="HSE Team",
                description="Update PTW system to require positive Chronos risk check before issuing Hot Work permits.",
                expected_risk_reduction="Prevents compounding risks of leaks and ignition sources (85% reduction)"
            )
        ]

generator = RecommendationGenerator()
