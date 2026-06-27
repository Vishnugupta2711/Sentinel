from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # We can't await inside a list comprehension if we want to ignore errors elegantly, but this is simple enough
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/ws/debrief")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # If client requests a generation via WS
            if data == "START_REPORT":
                await manager.broadcast({"event": "ReportStarted", "progress": 10})
                await asyncio.sleep(1)
                await manager.broadcast({"event": "AnalysisProgress", "progress": 50, "stage": "Root Cause Analysis"})
                await asyncio.sleep(1)
                await manager.broadcast({"event": "AnalysisProgress", "progress": 80, "stage": "Compliance Mapping"})
                await asyncio.sleep(1)
                await manager.broadcast({"event": "ReportCompleted", "progress": 100})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
