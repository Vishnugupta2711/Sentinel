import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
from typing import List

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ws/risk", tags=["Risk WebSocket"])

ws_risk_queues: List[asyncio.Queue] = []

@router.websocket("/")
async def risk_live_feed(websocket: WebSocket):
    await websocket.accept()
    q = asyncio.Queue()
    ws_risk_queues.append(q)
    logger.info("Client connected to Risk Live Feed.")
    
    try:
        while True:
            event = await q.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        logger.info("Client disconnected from Risk Live Feed.")
    except Exception as e:
        logger.error(f"Risk WS error: {e}")
    finally:
        if q in ws_risk_queues:
            ws_risk_queues.remove(q)
