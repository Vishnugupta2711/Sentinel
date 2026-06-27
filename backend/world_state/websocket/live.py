import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["WebSocket"])

# Since we want to broadcast every new snapshot, we need a queue for this router.
# We'll expose a global list of queues that the builder can push to.
ws_queues = []

@router.websocket("/ws/world-state")
async def websocket_world_state(websocket: WebSocket):
    """
    WebSocket endpoint that streams the full WorldState JSON every time a new one is built.
    """
    await websocket.accept()
    queue = asyncio.Queue(maxsize=5)
    ws_queues.append(queue)
    
    try:
        while True:
            snapshot = await queue.get()
            # Use pre-serialized JSON string cached by the builder
            cached = getattr(snapshot, '_cached_json', None)
            if cached:
                await websocket.send_text(cached)
            else:
                await websocket.send_text(snapshot.model_dump_json())
    except WebSocketDisconnect:
        pass
    finally:
        if queue in ws_queues:
            ws_queues.remove(queue)
