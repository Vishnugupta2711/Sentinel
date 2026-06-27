from fastapi import APIRouter
from pydantic import BaseModel
import psutil
import time

router = APIRouter(prefix="/system", tags=["System & Infrastructure"])

# Store startup time when module is imported
START_TIME = time.time()

class SystemStatus(BaseModel):
    status: str
    uptime_seconds: float
    cpu_usage_percent: float
    memory_usage_percent: float
    environment: str

class SystemVersion(BaseModel):
    version: str
    build: str
    tier: str

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    uptime = time.time() - START_TIME
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory().percent
    
    return SystemStatus(
        status="HEALTHY",
        uptime_seconds=round(uptime, 2),
        cpu_usage_percent=cpu,
        memory_usage_percent=mem,
        environment="production"
    )

@router.get("/version", response_model=SystemVersion)
async def get_system_version():
    return SystemVersion(
        version="1.0.0",
        build="2026-06-26",
        tier="Enterprise Mission Control"
    )

@router.get("/metrics")
async def get_system_metrics():
    # In a full deployment, this is typically handled by starlette-prometheus
    # We provide a mock fallback if exporter is not mounted
    return {"metrics_endpoint": "/metrics", "status": "Refer to Prometheus Exporter"}
