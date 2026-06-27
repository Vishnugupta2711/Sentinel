import pytest
from fastapi.testclient import TestClient
from main import app
from core.config import settings

@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c

def test_get_world_state(client: TestClient):
    # The lifespan initializes the state automatically!
    response = client.get(f"{settings.app.api_v1_prefix}/world")
    assert response.status_code == 200
    data = response.json()
    assert "plant" in data
    assert "workers" in data
    assert len(data["workers"]) == 30
    assert len(data["sensors"]) == 40

def test_get_zones(client: TestClient):
    response = client.get(f"{settings.app.api_v1_prefix}/world/zones")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 8

def test_get_workers(client: TestClient):
    response = client.get(f"{settings.app.api_v1_prefix}/world/workers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 30

def test_get_sensors(client: TestClient):
    response = client.get(f"{settings.app.api_v1_prefix}/world/sensors")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 40
