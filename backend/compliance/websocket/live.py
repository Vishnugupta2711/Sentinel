import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
from typing import List

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ws/compliance", tags=["Compliance WebSocket"])

ws_compliance_queues: List[asyncio.Queue] = []

@router.websocket("/")
async def compliance_live_feed(websocket: WebSocket):
    await websocket.accept()
    q = asyncio.Queue()
    ws_compliance_queues.append(q)
    logger.info("Client connected to Compliance Live Feed.")
    
    try:
        while True:
            event = await q.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        logger.info("Client disconnected from Compliance Live Feed.")
    except Exception as e:
        logger.error(f"Compliance WS error: {e}")
    finally:
        if q in ws_compliance_queues:
            ws_compliance_queues.remove(q)
