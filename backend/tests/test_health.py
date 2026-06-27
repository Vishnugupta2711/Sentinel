from fastapi.testclient import TestClient

from core.config import settings


def test_health_endpoint(client: TestClient) -> None:
    """Test the /health endpoint."""
    response = client.get(f"{settings.app.api_v1_prefix}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "backend"
    assert data["version"] == settings.app.version
    assert "timestamp" in data
    assert "uptime" in data
    assert "environment" in data
    
    # Check if request ID middleware is working
    assert "x-request-id" in response.headers


def test_readiness_endpoint(client: TestClient) -> None:
    """Test the /ready endpoint."""
    response = client.get(f"{settings.app.api_v1_prefix}/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    assert data["database"] is True
    assert data["redis"] is True
    assert data["kafka"] is True
    assert data["neo4j"] is True
    assert data["qdrant"] is False


def test_liveness_endpoint(client: TestClient) -> None:
    """Test the /live endpoint."""
    response = client.get(f"{settings.app.api_v1_prefix}/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["alive"] is True
