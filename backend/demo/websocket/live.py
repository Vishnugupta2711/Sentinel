import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
from demo.director.core import demo_director

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ws/demo", tags=["Demo WebSocket"])

@router.websocket("/")
async def demo_feed(websocket: WebSocket):
    await websocket.accept()
    q = asyncio.Queue()
    demo_director.subscribers.append(q)
    logger.info("Client connected to Demo Live Feed.")
    
    try:
        while True:
            event = await q.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        logger.info("Client disconnected from Demo Live Feed.")
    except Exception as e:
        logger.error(f"Demo WS error: {e}")
    finally:
        if q in demo_director.subscribers:
            demo_director.subscribers.remove(q)
