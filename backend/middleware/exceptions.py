import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from utils.constants import ERROR_INTERNAL, ERROR_VALIDATION
from utils.response import build_error_response

logger = structlog.get_logger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.warning("HTTP Exception", status_code=exc.status_code, detail=exc.detail)
        response_data = build_error_response(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            request_id=request_id
        )
        return JSONResponse(status_code=exc.status_code, content=response_data.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.warning("Validation Error", errors=exc.errors())
        response_data = build_error_response(
            code=ERROR_VALIDATION,
            message="Request validation failed.",
            request_id=request_id
        )
        # One could add detailed field errors here if the schema supported it, 
        # but the spec asks for the standard response schema.
        return JSONResponse(status_code=422, content=response_data.model_dump())

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.exception("Unexpected unhandled exception")
        response_data = build_error_response(
            code=ERROR_INTERNAL,
            message="An unexpected error occurred.",
            request_id=request_id
        )
        return JSONResponse(status_code=500, content=response_data.model_dump())
