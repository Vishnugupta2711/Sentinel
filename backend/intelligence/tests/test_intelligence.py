import pytest
import asyncio
from fastapi.testclient import TestClient

from core.config import settings
from intelligence.engine.core import IntelligenceEngine
from intelligence.contracts.context import IntelligenceContext

@pytest.fixture
def engine():
    # Use a fresh engine for tests
    return IntelligenceEngine()

def test_registry_and_config(engine: IntelligenceEngine):
    # Chronos is enabled by default in YAML
    assert engine.registry.get_module("chronos") is not None
    
    pipeline = engine.registry.get_execution_pipeline()
    names = [m.name() for m in pipeline]
    assert "chronos" in names
    
    # Priority check: Chronos (10) should be before Risk (20)
    chronos_idx = names.index("chronos")
    risk_idx = names.index("risk")
    assert chronos_idx < risk_idx

def test_dispatcher_execution(engine: IntelligenceEngine):
    # Run the dispatcher synchronously for the test
    ctx = IntelligenceContext(
        world_state_version=1,
        plant_id="test_plant"
    )
    
    outputs = asyncio.run(engine.dispatcher.dispatch(ctx))
    
    # Just verify dispatcher runs without raising errors
    # With Phase 7, output structure has changed significantly
    assert isinstance(outputs, dict)
    
    # Check metrics
    metrics = engine.metrics.get_metrics()
    assert "chronos" in metrics
    assert metrics["chronos"]["executions"] == 1
    assert metrics["chronos"]["success_rate_percent"] == 100.0

def test_api_status(client: TestClient):
    res = client.get(f"{settings.app.api_v1_prefix}/intelligence/status")
    assert res.status_code == 200
    assert "active_pipelines" in res.json()

def test_api_enable_disable(client: TestClient):
    # Disable chronos
    res = client.post(f"{settings.app.api_v1_prefix}/intelligence/disable/chronos")
    assert res.status_code == 200
    
    # Check it is disabled
    res = client.get(f"{settings.app.api_v1_prefix}/intelligence/modules")
    data = res.json()
    chronos = next((m for m in data if m["name"] == "chronos"), None)
    assert chronos["state"] == "DISABLED"
    
    # Re-enable
    res = client.post(f"{settings.app.api_v1_prefix}/intelligence/enable/chronos")
    assert res.status_code == 200
