import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# Live topology updates
ws_graph_queues = []

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/graph")
async def websocket_graph(websocket: WebSocket):
    await websocket.accept()
    queue = asyncio.Queue(maxsize=5)
    ws_graph_queues.append(queue)
    try:
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        ws_graph_queues.remove(queue)
