from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI

from core.config import settings
from core.logging import setup_logging
from core.security_validation import validate_secrets
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

    yield
    
    logger.info("Application shutting down")
    
    # Close DB, Redis, Kafka connections here in the future
