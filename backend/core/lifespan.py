from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI

from core.config import settings
from core.logging import setup_logging
from core.security_validation import validate_secrets
from world.manager.manager import world_manager
from world.sample_data.factory import generate_sample_world
from simulator.engine.core import simulation_engine
from timeline.engine.core import timeline_engine

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI.
    Executes startup and shutdown events.
    """
    # Startup
    setup_logging()
    logger.info("Application starting up", version=app.version)

    # Validate secrets before doing anything else
    validate_secrets(settings)

    # Initialize DB, Redis, Kafka connections here in the future

    logger.info("Initializing Industrial World Model (Digital Twin)")
    state = generate_sample_world()
    world_manager.load(state)
    logger.info("Industrial World Model generated and loaded successfully")
    
    logger.info("Starting Simulation Engine")
    simulation_engine.start()

    logger.info("Starting Timeline Compression Manager")
    timeline_engine.startup()
    
    yield
    
    # Shutdown
    logger.info("Application shutting down")
    timeline_engine.shutdown()
    simulation_engine.stop()
    
    # Close DB, Redis, Kafka connections here in the future
