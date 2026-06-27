from debrief.schemas import DebriefReport

class ReportGenerator:
    def to_markdown(self, report: DebriefReport) -> str:
        md = f"# Incident Investigation Report: {report.incident_title}\n\n"
        md += f"**Report ID**: {report.report_id} | **Generated At**: {report.generated_at}\n\n"
        
        md += "## Executive Summary\n"
        md += f"- **Type**: {report.incident_type}\n"
        md += f"- **Severity**: {report.incident_severity}\n"
        md += f"- **Zone**: {report.affected_zone}\n"
        md += f"- **Outcome**: {report.outcome}\n"
        md += f"- **Loss Prevented**: ${report.estimated_loss_prevented:,.2f}\n\n"
        
        md += "## Incident Timeline\n"
        for t in report.timeline:
            md += f"- **{t.timestamp}**: {t.description}\n"
            
        md += "\n## Root Cause Analysis\n"
        for r in report.root_causes:
            md += f"- **[{r.category}]** (Confidence: {r.confidence}): {r.description}\n"
            
        md += "\n## AI Decision Explanation\n"
        for k, v in report.ai_explanation.items():
            md += f"**{k}**: {v}\n\n"
            
        md += "## Compliance & Regulatory Mapping\n"
        for c in report.compliance:
            md += f"- **{c.regulation} ({c.section})**: {c.requirement} -> {c.status}\n"
            
        md += "\n## Lessons Learned\n"
        md += f"- **Immediate**: {', '.join(report.lessons_learned.immediate_actions)}\n"
        md += f"- **Long-term**: {', '.join(report.lessons_learned.long_term)}\n"
        
        return md

    def to_html(self, report: DebriefReport) -> str:
        # A simple HTML renderer for the frontend to consume if needed
        md = self.to_markdown(report)
        html = md.replace("\n\n", "</p><p>").replace("\n", "<br>")
        return f"<div class='debrief-report'><p>{html}</p></div>"

generator = ReportGenerator()
