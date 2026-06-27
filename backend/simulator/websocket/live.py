import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from simulator.publishers.bus import event_bus

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/live")
async def websocket_live_events(websocket: WebSocket):
    """
    WebSocket endpoint that streams all simulation events in real-time.
    """
    await websocket.accept()
    queue = asyncio.Queue()
    event_bus.register_broadcast_queue(queue)
    
    try:
        while True:
            event = await queue.get()
            await websocket.send_json(event.model_dump())
    except WebSocketDisconnect:
        pass
    finally:
        event_bus.unregister_broadcast_queue(queue)
