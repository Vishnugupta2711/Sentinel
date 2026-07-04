import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
from typing import List

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ws/correlation", tags=["Correlation WebSocket"])

ws_correlation_queues: List[asyncio.Queue] = []


@router.websocket("/")
async def correlation_feed(websocket: WebSocket):
    await websocket.accept()
    q = asyncio.Queue()
    ws_correlation_queues.append(q)
    logger.info("Client connected to Correlation Live Feed.")

    try:
        while True:
            event = await q.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        logger.info("Client disconnected from Correlation Live Feed.")
    except Exception as e:
        logger.error(f"Correlation WS error: {e}")
    finally:
        if q in ws_correlation_queues:
            ws_correlation_queues.remove(q)
