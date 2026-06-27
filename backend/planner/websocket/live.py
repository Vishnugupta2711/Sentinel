import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
from typing import List

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ws/planner", tags=["Planner WebSocket"])

ws_planner_queues: List[asyncio.Queue] = []

@router.websocket("/")
async def planner_live_feed(websocket: WebSocket):
    await websocket.accept()
    q = asyncio.Queue()
    ws_planner_queues.append(q)
    logger.info("Client connected to Planner Live Feed.")
    
    try:
        while True:
            event = await q.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        logger.info("Client disconnected from Planner Live Feed.")
    except Exception as e:
        logger.error(f"Planner WS error: {e}")
    finally:
        if q in ws_planner_queues:
            ws_planner_queues.remove(q)
