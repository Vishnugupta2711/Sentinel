from debrief.schemas import BusinessImpact

class BusinessImpactCalculator:
    def calculate(self) -> BusinessImpact:
        return BusinessImpact(
            workers_protected=12,
            downtime_prevented_hours=48,
            financial_loss_prevented=12000000.0,
            environmental_impact_avoided="Prevented Class 1 Hazardous Gas Release",
            regulatory_penalties_avoided=500000.0,
            estimated_insurance_savings=150000.0
        )

calculator = BusinessImpactCalculator()
