import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class StructlogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        
        request_id = getattr(request.state, "request_id", None)
        
        structlog.contextvars.clear_contextvars()
        if request_id:
            structlog.contextvars.bind_contextvars(request_id=request_id)
            
        structlog.contextvars.bind_contextvars(
            method=request.method,
            path=request.url.path
        )
        
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            structlog.contextvars.bind_contextvars(
                status_code=response.status_code,
                response_time=process_time
            )
            
            if response.status_code >= 500:
                logger.error("Server error")
            elif response.status_code >= 400:
                logger.warning("Client error")
            else:
                logger.info("Request processed")
                
            return response
        except Exception as e:
            process_time = time.perf_counter() - start_time
            structlog.contextvars.bind_contextvars(
                status_code=500,
                response_time=process_time
            )
            logger.exception("Unhandled exception during request processing")
            raise e
