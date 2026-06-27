import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Provides a TestClient for testing the FastAPI application."""
    with TestClient(app) as client:
        yield client
