import asyncio
import structlog
from typing import Optional
from investigation.schemas import InvestigationReport
from investigation.evidence.collector import collector
from investigation.timeline.reconstruction import reconstructor
from investigation.reconstruction.correlation import correlator
from investigation.root_cause.analyzer import analyzer
from investigation.decision_audit.auditor import auditor
from investigation.compliance.audit import auditor as compliance_auditor
from investigation.impact.assessment import assessor
from investigation.recommendations.generator import generator
from investigation.reports.compiler import compiler

logger = structlog.get_logger(__name__)

class InvestigationPipeline:
    def __init__(self):
        self.reports = {}

    async def run_investigation(self, ws_manager=None, client_id=None) -> InvestigationReport:
        
        async def notify(stage: str):
            if ws_manager and client_id:
                await ws_manager.send_personal_message(
                    {"type": "progress", "stage": stage}, client_id
                )
            await asyncio.sleep(0.5)

        await notify("STAGE 1: Evidence Collection")
        evidence = collector.collect()
        
        await notify("STAGE 2: Timeline Reconstruction")
        timeline = reconstructor.reconstruct()
        
        await notify("STAGE 3: Event Correlation")
        correlations = correlator.correlate()
        
        await notify("STAGE 4: Root Cause Analysis")
        root_causes = analyzer.analyze()
        
        await notify("STAGE 5: Decision Audit")
        decisions = auditor.audit()
        
        await notify("STAGE 6: Compliance Audit")
        compliance = compliance_auditor.audit()
        
        await notify("STAGE 7: Business Impact Assessment")
        impact = assessor.assess()
        
        await notify("STAGE 8: Preventive Recommendations")
        recommendations = generator.generate()
        
        await notify("STAGE 9: Finalizing Report")
        report = InvestigationReport(
            incident_type="Compound Hazard (Leak + Ignition)",
            status="COMPLETED",
            evidence=evidence,
            timeline=timeline,
            correlations=correlations,
            root_causes=root_causes,
            decisions=decisions,
            compliance=compliance,
            impact=impact,
            recommendations=recommendations
        )
        
        report = compiler.compile(report)
        self.reports[report.investigation_id] = report
        
        if ws_manager and client_id:
            await ws_manager.send_personal_message(
                {"type": "completed", "report_id": report.investigation_id}, client_id
            )
            
        return report

    def get_latest(self) -> Optional[InvestigationReport]:
        if not self.reports:
            return None
        return list(self.reports.values())[-1]
        
    def get_by_id(self, inv_id: str) -> Optional[InvestigationReport]:
        return self.reports.get(inv_id)

pipeline = InvestigationPipeline()
