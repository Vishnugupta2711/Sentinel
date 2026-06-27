from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import structlog
from prometheus_fastapi_instrumentator import Instrumentator

from api.v1.router import api_router
from core.config import settings, EnvironmentType
from core.lifespan import lifespan
from middleware.exceptions import setup_exception_handlers
from middleware.logging import StructlogMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.request_id import RequestIDMiddleware


def create_app() -> FastAPI:
    """Application factory for the FastAPI backend."""
    # Configure structlog for production
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.JSONRenderer()
        ]
    )

    is_production = settings.app.environment == EnvironmentType.PRODUCTION

    app = FastAPI(
        title=settings.app.title,
        description=settings.app.description,
        version=settings.app.version,
        openapi_url=f"{settings.app.api_v1_prefix}/openapi.json",
        # Hide Swagger/ReDoc in production to reduce attack surface
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
        debug=settings.app.debug,
        lifespan=lifespan,
    )

    # ─── Middleware (note: reverse order of execution) ──────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Real-IP"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.security.allowed_hosts
    )

    # Custom middlewares
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(StructlogMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # ─── Exception Handlers ─────────────────────────────────────────
    setup_exception_handlers(app)

    # ─── Routers ────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.app.api_v1_prefix)

    # ─── Prometheus Metrics ─────────────────────────────────────────
    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=[r".*health.*", r"/metrics"],
    ).instrument(app).expose(app, include_in_schema=False)

    # ─── Redirect root to docs (dev only) ───────────────────────────
    if not is_production:
        @app.get("/", include_in_schema=False)
        async def root():
            return RedirectResponse(url="/docs")

    return app


app = create_app()
