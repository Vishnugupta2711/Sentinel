from typing import Generator

import structlog
from fastapi import Request


def get_logger(request: Request) -> Generator[structlog.stdlib.BoundLogger, None, None]:
    """
    Dependency to inject a context-bound logger.
    Automatically binds the request context if available.
    """
    request_id = getattr(request.state, "request_id", None)
    logger = structlog.get_logger("backend.api")
    if request_id:
        logger = logger.bind(request_id=request_id)
    
    yield logger
