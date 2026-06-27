import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
from typing import List

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ws/vision", tags=["Vision WebSocket"])

ws_vision_queues: List[asyncio.Queue] = []

@router.websocket("/")
async def vision_live_feed(websocket: WebSocket):
    await websocket.accept()
    q = asyncio.Queue()
    ws_vision_queues.append(q)
    logger.info("Client connected to Vision Live Feed.")
    
    try:
        while True:
            event = await q.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        logger.info("Client disconnected from Vision Live Feed.")
    except Exception as e:
        logger.error(f"Vision WS error: {e}")
    finally:
        if q in ws_vision_queues:
            ws_vision_queues.remove(q)
