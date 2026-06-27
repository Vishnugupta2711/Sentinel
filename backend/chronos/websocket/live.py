import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
from typing import List

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ws/chronos", tags=["Chronos WebSocket"])

# Used by the engine to broadcast new predictions
ws_chronos_queues: List[asyncio.Queue] = []

@router.websocket("/")
async def chronos_live_feed(websocket: WebSocket):
    """
    Live stream of Chronos prediction updates.
    """
    await websocket.accept()
    q = asyncio.Queue()
    ws_chronos_queues.append(q)
    logger.info("Client connected to Chronos Live Feed.")
    
    try:
        while True:
            # Wait for prediction events
            event = await q.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        logger.info("Client disconnected from Chronos Live Feed.")
    except Exception as e:
        logger.error(f"Chronos WS error: {e}")
    finally:
        if q in ws_chronos_queues:
            ws_chronos_queues.remove(q)
