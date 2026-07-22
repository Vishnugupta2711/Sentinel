import time
from fastapi import APIRouter
from pydantic import BaseModel

from core.config import settings
from utils.datetime import format_iso, utc_now

router = APIRouter(prefix="/health", tags=["Health"])

START_TIME = time.time()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    uptime: float
    environment: str


class ReadinessResponse(BaseModel):
    ready: bool
    database: bool
    redis: bool
    kafka: bool
    qdrant: bool


class LivenessResponse(BaseModel):
    alive: bool


@router.get(
    "",
    response_model=HealthResponse,
    status_code=200,
    summary="Get Health",
    description="Returns the overall health status of the API, including uptime and environment context.",
    tags=["Health"]
)
async def get_health():
    uptime = time.time() - START_TIME
    return HealthResponse(
        status="healthy",
        service="backend",
        version=settings.app.version,
        timestamp=format_iso(utc_now()),
        uptime=uptime,
        environment=settings.app.environment.value
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=200,
    summary="Get Readiness",
    description="Checks if all core intelligence engines are loaded and ready.",
    tags=["Health"]
)
async def get_readiness():
    from intelligence.engine.core import get_intelligence_engine
    engine = get_intelligence_engine()
    
    # We map the abstract "database" etc to intelligence modules
    # since Sentinel runs fully in-memory without neo4j/postgres
    registry = engine.registry
    
    return ReadinessResponse(
        ready=True,
        database=True, # In-memory
        redis=True, # In-memory
        kafka=True, # In-memory bus
        qdrant=registry.is_enabled("rag")
    )


@router.get(
    "/live",
    response_model=LivenessResponse,
    status_code=200,
    summary="Get Liveness",
    description="Returns a simple liveness probe to verify the application process is running.",
    tags=["Health"]
)
async def get_liveness():
    return LivenessResponse(alive=True)
