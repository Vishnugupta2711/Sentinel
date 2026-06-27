from fastapi.testclient import TestClient
from main import app
from demo.director.core import demo_director
from demo.models.schemas import DemoStatus

client = TestClient(app)

def test_get_scenarios():
    response = client.get("/api/v1/demo/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert data[0]["scenario_id"] == "DEMO_01"

def test_demo_lifecycle():
    # 1. Ensure idle state
    demo_director.reset()
    state_res = client.get("/api/v1/demo/state")
    assert state_res.json()["status"] == DemoStatus.IDLE.value
    
    # 2. Start valid scenario
    start_res = client.post("/api/v1/demo/start", json={"scenario_id": "DEMO_01"})
    assert start_res.status_code == 200
    
    state_res = client.get("/api/v1/demo/state")
    assert state_res.json()["status"] == DemoStatus.PLAYING.value
    assert state_res.json()["current_stage"] == 1
    
    # 3. Advance to next stage
    next_res = client.post("/api/v1/demo/next")
    assert next_res.status_code == 200
    
    state_res = client.get("/api/v1/demo/state")
    assert state_res.json()["current_stage"] == 2
    
    # 4. Pause
    client.post("/api/v1/demo/pause")
    state_res = client.get("/api/v1/demo/state")
    assert state_res.json()["status"] == DemoStatus.PAUSED.value
    
    # 5. Reset
    client.post("/api/v1/demo/reset")
    state_res = client.get("/api/v1/demo/state")
    assert state_res.json()["status"] == DemoStatus.IDLE.value
