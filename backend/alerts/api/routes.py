from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from alerts.models.schemas import Alert
from alerts.engine.core import alert_engine
from pydantic import BaseModel

router = APIRouter(prefix="/alerts", tags=["Alert Engine"])


class AcknowledgeRequest(BaseModel):
    user: str


@router.get("/active", response_model=List[Alert])
async def get_active_alerts(priority: Optional[str] = Query(None)):
    return alert_engine.get_active_alerts(priority=priority)


@router.get("/history", response_model=List[Alert])
async def get_alert_history(limit: int = Query(50, ge=1, le=200)):
    return alert_engine.get_alert_history(limit=limit)


@router.get("/summary")
async def get_queue_summary():
    return alert_engine.get_queue_summary()


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, req: AcknowledgeRequest):
    success = alert_engine.acknowledge(alert_id, req.user)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "acknowledged", "alert_id": alert_id, "by": req.user}


@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    success = alert_engine.resolve(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "resolved", "alert_id": alert_id}
