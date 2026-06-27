import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from intelligence.engine.core import IntelligenceEngine, get_intelligence_engine

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/intelligence")
async def websocket_intelligence(
    websocket: WebSocket,
    engine: IntelligenceEngine = Depends(get_intelligence_engine)
):
    await websocket.accept()
    queue = asyncio.Queue()
    engine.publisher.register_queue(queue)
    
    try:
        while True:
            event = await queue.get()
            await websocket.send_json(event.model_dump())
    except WebSocketDisconnect:
        pass
    finally:
        engine.publisher.unregister_queue(queue)
