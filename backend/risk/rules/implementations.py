from typing import Optional
from risk.rules.base import BaseRiskRule, RiskEvaluationContext
from risk.models.schemas import (
    CompoundRiskAssessment, RiskType, RiskExplanation, RootCause, RiskConfidence
)
from risk.scoring.calculator import ScoringEngine
from world.models.enums import Status

class ExplosionRiskRule(BaseRiskRule):
    """
    Detects Compound Risk: High Gas + Hot Work Permit + Maintenance Active
    """
    @property
    def rule_name(self) -> str:
        return "ExplosionRisk_Gas_HotWork"

    def evaluate(self, context: RiskEvaluationContext) -> Optional[CompoundRiskAssessment]:
        state = context.current_state
        
        high_gas_sensors = [s for s in state.sensors if s.sensor_type == "GAS" and s.status in [Status.WARNING, Status.CRITICAL]]
        hot_work_permits = [p for p in state.permits if p.permit_type == "HOT_WORK" and p.status == Status.ONLINE]
        
        if not high_gas_sensors or not hot_work_permits:
            return None
            
        # Match zones via worker
        affected_zones = set()
        for p in hot_work_permits:
            worker = next((w for w in state.workers if w.id == p.assigned_to), None)
            if worker and worker.zone_id:
                for s in high_gas_sensors:
                    if s.zone_id == worker.zone_id:
                        affected_zones.add(s.zone_id)
                    
        if not affected_zones:
            return None
            
        # We have a match!
        affected_zones_list = list(affected_zones)
        affected_workers = [w.id for w in state.workers if w.zone_id in affected_zones]
        
        score = 95.0
        level = ScoringEngine.calculate_level(score)
        priority = ScoringEngine.determine_priority(level, has_life_threat=True)
        
        explanation = RiskExplanation(
            why_detected="Detected dangerous combination of high combustible gas levels and active Hot Work permits in the same zone.",
            contributing_factors=["Combustible Gas detected", "Hot Work Permit Active", "Ignition Source Present"],
            supporting_events=[],
            supporting_sensors=[s.id for s in high_gas_sensors],
            predicted_outcome="Potential atmospheric ignition and explosion",
            historical_similarity=0.85
        )
        
        root_causes = [
            RootCause(
                description="Gas leak from pressurized pipeline near maintenance area",
                probability=0.8,
                contributing_factors=["Pipeline degradation", "Valve failure"]
            )
        ]
        
        confidence = RiskConfidence(
            risk_confidence=0.95,
            prediction_confidence=0.90,
            data_quality=0.99,
            evidence_score=0.95
        )
        
        return CompoundRiskAssessment(
            risk_type=RiskType.EXPLOSION,
            risk_score=score,
            risk_level=level,
            priority=priority,
            explanation=explanation,
            root_causes=root_causes,
            confidence=confidence,
            affected_workers=affected_workers,
            affected_zones=affected_zones_list,
            recommended_actions=["IMMEDIATELY STOP HOT WORK", "EVACUATE ZONE", "INCREASE VENTILATION"],
            time_to_impact_minutes=5,
            hazard_spread_radius_meters=50.0
        )

class WorkerFatalityRule(BaseRiskRule):
    """
    Detects Compound Risk: Gas Leak + Worker Inside Zone + Confined Space
    """
    @property
    def rule_name(self) -> str:
        return "WorkerFatality_ConfinedSpace_Gas"
        
    def evaluate(self, context: RiskEvaluationContext) -> Optional[CompoundRiskAssessment]:
        state = context.current_state
        
        toxic_gas = [s for s in state.sensors if s.sensor_type in ["GAS", "SMOKE"] and s.status == Status.CRITICAL]
        confined_spaces = [p for p in state.permits if p.permit_type == "CONFINED_SPACE" and p.status == Status.ONLINE]
        
        if not toxic_gas or not confined_spaces:
            return None
            
        affected_zones = set()
        for p in confined_spaces:
            worker = next((w for w in state.workers if w.id == p.assigned_to), None)
            if worker and worker.zone_id:
                for s in toxic_gas:
                    if s.zone_id == worker.zone_id:
                        affected_zones.add(s.zone_id)
                    
        if not affected_zones:
            return None
            
        affected_workers = [w.id for w in state.workers if w.zone_id in affected_zones]
        
        if not affected_workers:
            return None # No workers to be fatal for
            
        score = 99.0
        level = ScoringEngine.calculate_level(score)
        priority = ScoringEngine.determine_priority(level, has_life_threat=True)
        
        explanation = RiskExplanation(
            why_detected="Workers detected inside a confined space with critical toxic gas levels.",
            contributing_factors=["Toxic Gas detected", "Confined Space Active", "Workers Present"],
            supporting_events=[],
            supporting_sensors=[s.id for s in toxic_gas],
            predicted_outcome="Worker asphyxiation or fatality",
            historical_similarity=0.9
        )
        
        return CompoundRiskAssessment(
            risk_type=RiskType.CHEMICAL_EXPOSURE,
            risk_score=score,
            risk_level=level,
            priority=priority,
            explanation=explanation,
            root_causes=[RootCause(description="Ventilation failure in confined space", probability=0.9, contributing_factors=["Fan failure"])],
            confidence=RiskConfidence(risk_confidence=0.99, prediction_confidence=0.95, data_quality=0.99, evidence_score=0.99),
            affected_workers=affected_workers,
            affected_zones=list(affected_zones),
            recommended_actions=["IMMEDIATE RESCUE OPERATION", "DEPLOY EMERGENCY VENTILATION"],
            time_to_impact_minutes=1,
            hazard_spread_radius_meters=10.0
        )
