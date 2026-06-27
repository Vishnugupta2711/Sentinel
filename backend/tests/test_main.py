from fastapi.testclient import TestClient


def test_app_startup(client: TestClient) -> None:
    """Test application startup and generic 404 response to verify global exception handler format."""
    response = client.get("/non-existent-path")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"
