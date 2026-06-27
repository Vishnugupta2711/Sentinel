from investigation.schemas import InvestigationReport

class ReportCompiler:
    def compile(self, report: InvestigationReport) -> InvestigationReport:
        executive_md = f"""# Executive Incident Summary: {report.investigation_id}
**Date Generated:** {report.generated_at}
**Incident Type:** {report.incident_type}
**Status:** {report.status}

## Overview
The Sentinel AI Incident Investigation Platform (SAIIP) has completed an autonomous review of the recent incident.
The Counterfactual Planner successfully intervened, resulting in:
- **Lives Protected:** {report.impact.lives_protected}
- **Financial Loss Prevented:** ${report.impact.financial_loss_prevented:,.2f}
- **Downtime Avoided:** {report.impact.downtime_prevented_hours} hours

## Key Root Causes
"""
        for rc in report.root_causes:
            executive_md += f"- **{rc.category}**: {rc.description} (Confidence: {rc.confidence*100}%)\n"

        executive_md += """
## Immediate Actions
Sentinel has logged compliance records and generated preventative engineering controls to mitigate future occurrences.
"""
        
        technical_md = """# Technical & Compliance Appendix
## Event Correlation
"""
        for c in report.correlations:
            technical_md += f"- {c.source_event} -> {c.target_event} [{c.relationship}] (Conf: {c.confidence})\n"

        technical_md += "\n## Compliance Audit\n"
        for comp in report.compliance:
            technical_md += f"- **{comp.framework}**: {comp.section} - Status: {comp.status}\n"

        report.executive_summary = executive_md
        report.technical_appendix = technical_md
        
        return report

compiler = ReportCompiler()
