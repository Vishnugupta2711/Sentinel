from typing import List, Dict
import structlog
from utils.datetime import format_iso, utc_now
from intelligence.contracts.context import IntelligenceContext
from compliance.models.schemas import ComplianceViolation, ComplianceStatus, ViolationSeverity
from compliance.rules.base import BaseComplianceRule
from compliance.rules.implementations import MissingPPERule, OISDHotWorkGasRule
from timeline.engine.core import timeline_engine

logger = structlog.get_logger(__name__)

class ComplianceEngine:
    def __init__(self):
        self.rules: List[BaseComplianceRule] = [
            MissingPPERule(),
            OISDHotWorkGasRule()
        ]
        self.active_violations: Dict[str, ComplianceViolation] = {}
        self.violation_history: List[ComplianceViolation] = []
        self.last_audit_time = format_iso(utc_now())
        
    def evaluate(self, context: IntelligenceContext) -> List[ComplianceViolation]:
        logger.info("ComplianceEngine evaluating plant state...")
        
        latest_entry = timeline_engine.store.latest()
        if not latest_entry:
            return []
            
        current_state = latest_entry.get_state()
        
        detected_violations = []
        for rule in self.rules:
            violations = rule.evaluate(current_state)
            detected_violations.extend(violations)
            
        # Update Memory
        self.active_violations.clear() # Simplification: assume re-evaluated every tick
        for v in detected_violations:
            self.active_violations[v.violation_id] = v
            self.violation_history.append(v)
            
        self.last_audit_time = format_iso(utc_now())
            
        return detected_violations
        
    def get_status(self) -> ComplianceStatus:
        critical_count = sum(1 for v in self.active_violations.values() if v.severity == ViolationSeverity.CRITICAL)
        return ComplianceStatus(
            is_compliant=len(self.active_violations) == 0,
            active_violations=len(self.active_violations),
            critical_violations=critical_count,
            last_audit_time=self.last_audit_time
        )
        
    def get_active_violations(self) -> List[ComplianceViolation]:
        return list(self.active_violations.values())
        
    def get_history(self) -> List[ComplianceViolation]:
        return self.violation_history[-100:]

compliance_engine = ComplianceEngine()
