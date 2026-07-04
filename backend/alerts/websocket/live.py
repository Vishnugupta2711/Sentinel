import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
from alerts.engine.core import alert_engine

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ws/alerts", tags=["Alert WebSocket"])


@router.websocket("/")
async def alert_feed(websocket: WebSocket):
    await websocket.accept()
    q = asyncio.Queue()
    alert_engine.subscribe(q)
    logger.info("Client connected to Alert Live Feed.")

    try:
        while True:
            event = await q.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        logger.info("Client disconnected from Alert Live Feed.")
    except Exception as e:
        logger.error(f"Alert WS error: {e}")
    finally:
        alert_engine.unsubscribe(q)
