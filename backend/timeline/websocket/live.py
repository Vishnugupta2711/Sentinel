import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from timeline.engine.core import TimelineEngine, get_timeline_engine

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/timeline/replay")
async def websocket_timeline_replay(
    websocket: WebSocket,
    engine: TimelineEngine = Depends(get_timeline_engine)
):
    await websocket.accept()
    queue = asyncio.Queue()
    engine.replay.register_queue(queue)
    
    try:
        while True:
            # Payload is a JSON string of WorldState
            payload = await queue.get()
            await websocket.send_text(payload)
    except WebSocketDisconnect:
        pass
    finally:
        engine.replay.unregister_queue(queue)
