import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
from typing import List

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ws/rag", tags=["RAG WebSocket"])

ws_rag_queues: List[asyncio.Queue] = []


@router.websocket("/")
async def rag_feed(websocket: WebSocket):
    await websocket.accept()
    q = asyncio.Queue()
    ws_rag_queues.append(q)
    logger.info("Client connected to RAG Live Feed.")

    try:
        while True:
            event = await q.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        logger.info("Client disconnected from RAG Live Feed.")
    except Exception as e:
        logger.error(f"RAG WS error: {e}")
    finally:
        if q in ws_rag_queues:
            ws_rag_queues.remove(q)
