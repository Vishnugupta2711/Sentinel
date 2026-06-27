from risk.models.schemas import RiskLevel, AlertPriority

class ScoringEngine:
    @staticmethod
    def calculate_level(score: float) -> RiskLevel:
        if score >= 85:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 30:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    @staticmethod
    def determine_priority(level: RiskLevel, has_life_threat: bool) -> AlertPriority:
        if has_life_threat and level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            return AlertPriority.P1
        if level == RiskLevel.CRITICAL:
            return AlertPriority.P2
        if level == RiskLevel.HIGH:
            return AlertPriority.P3
        return AlertPriority.P4
