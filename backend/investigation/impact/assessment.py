from investigation.schemas import ImpactAssessment

class ImpactAssessor:
    def assess(self) -> ImpactAssessment:
        return ImpactAssessment(
            lives_protected=1,
            downtime_prevented_hours=72,
            financial_loss_prevented=1250000.00,
            environmental_impact_avoided="Prevented toxic cloud release of 150kg",
            insurance_savings=45000.00,
            regulatory_penalties_avoided=500000.00,
            equipment_protected=["V-42", "T-99", "Surrounding Sensors"]
        )

assessor = ImpactAssessor()
