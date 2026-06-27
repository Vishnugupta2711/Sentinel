from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from investigation.engine.pipeline import pipeline
from investigation.api.websocket import manager
from investigation.schemas import InvestigationReport

router = APIRouter()

@router.post("/start", response_model=Dict[str, str])
async def start_investigation(background_tasks: BackgroundTasks, client_id: str = "default"):
    # Run the investigation asynchronously in the background
    background_tasks.add_task(pipeline.run_investigation, manager, client_id)
    return {"status": "started", "message": "Investigation pipeline triggered."}

@router.get("/latest", response_model=InvestigationReport)
async def get_latest_investigation():
    report = pipeline.get_latest()
    if not report:
        raise HTTPException(status_code=404, detail="No investigations found.")
    return report

@router.get("/history", response_model=List[InvestigationReport])
async def get_history():
    return list(pipeline.reports.values())

@router.get("/{inv_id}", response_model=InvestigationReport)
async def get_investigation(inv_id: str):
    report = pipeline.get_by_id(inv_id)
    if not report:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    return report

@router.post("/export/{inv_id}", response_model=Dict[str, Any])
async def export_investigation(inv_id: str, format: str = "markdown"):
    report = pipeline.get_by_id(inv_id)
    if not report:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    
    if format == "markdown":
        return {
            "executive_summary": report.executive_summary,
            "technical_appendix": report.technical_appendix
        }
    elif format == "json":
        return report.dict()
    else:
        raise HTTPException(status_code=400, detail="Unsupported format.")
