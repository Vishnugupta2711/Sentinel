import pytest
import asyncio
from fastapi.testclient import TestClient

from main import app
from core.config import settings
from simulator.publishers.bus import event_bus
from simulator.events.models import SimulationEvent
from simulator.events.enums import EventType, EventSeverity

@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c

def test_event_bus():
    received = []
    
    async def dummy_callback(event: SimulationEvent):
        received.append(event)
        
    event_bus.subscribe(EventType.WorkerMoved, dummy_callback)
    
    evt = SimulationEvent(
        event_type=EventType.WorkerMoved,
        source="w1",
        severity=EventSeverity.INFO,
        payload={"msg": "test"}
    )
    
    # Run async publish synchronously for the test
    asyncio.run(event_bus.publish(evt))
    
    assert len(received) == 1
    assert received[0].source == "w1"
    
    event_bus.unsubscribe(EventType.WorkerMoved, dummy_callback)
    asyncio.run(event_bus.publish(evt))
    assert len(received) == 1

def test_simulator_api(client: TestClient):
    # Status
    res = client.get(f"{settings.app.api_v1_prefix}/simulation/status")
    assert res.status_code == 200
    assert "is_running" in res.json()
    
    # Pause
    res = client.post(f"{settings.app.api_v1_prefix}/simulation/pause")
    assert res.status_code == 200
    
    # Resume / Start
    res = client.post(f"{settings.app.api_v1_prefix}/simulation/start")
    assert res.status_code == 200

def test_websocket(client: TestClient):
    # Just verify connection works and we can close it
    with client.websocket_connect(f"{settings.app.api_v1_prefix}/ws/live") as websocket:
        assert websocket is not None
