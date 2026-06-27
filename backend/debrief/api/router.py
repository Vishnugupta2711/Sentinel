from fastapi import APIRouter
from debrief.engine.core import debrief_engine
from debrief.schemas import DebriefReport
from debrief.reports.generator import generator

router = APIRouter()

# Store reports in memory for the hackathon
_reports_db = {}
_latest_id = None

@router.post("/generate", response_model=DebriefReport)
async def generate_debrief():
    global _latest_id
    report = debrief_engine.generate_report()
    _reports_db[report.report_id] = report
    _latest_id = report.report_id
    return report

@router.get("/latest", response_model=DebriefReport)
async def get_latest_debrief():
    if not _latest_id:
        return debrief_engine.generate_report() # Generate one if none exist
    return _reports_db[_latest_id]

@router.get("/history")
async def get_history():
    return list(_reports_db.values())

@router.get("/report/{report_id}")
async def get_report_markdown(report_id: str):
    if report_id not in _reports_db:
        return {"error": "Report not found"}
    report = _reports_db[report_id]
    return {"markdown": generator.to_markdown(report)}
