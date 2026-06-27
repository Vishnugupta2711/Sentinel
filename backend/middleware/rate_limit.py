"""
In-process rate limiter using a sliding window algorithm.
Acts as a defense-in-depth layer — NGINX is the primary rate limiter,
this protects the app when accessed directly (e.g., local dev, internal services).
"""
import time
from collections import defaultdict, deque
from threading import Lock

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = structlog.get_logger(__name__)


class SlidingWindowRateLimiter:
    """Thread-safe sliding window rate limiter."""

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._store: dict[str, deque] = defaultdict(deque)
        self._lock = Lock()

    def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        Returns (allowed, retry_after_seconds).
        """
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            window = self._store[key]
            # Evict expired timestamps
            while window and window[0] < cutoff:
                window.popleft()

            if len(window) >= self.max_requests:
                oldest = window[0]
                retry_after = int(oldest + self.window_seconds - now) + 1
                return False, retry_after

            window.append(now)
            return True, 0


# Rate limit zones — match nginx config values
_api_limiter = SlidingWindowRateLimiter(max_requests=100, window_seconds=10)
_ws_limiter  = SlidingWindowRateLimiter(max_requests=20,  window_seconds=10)

# Paths that skip rate limiting (health probes, metrics)
_EXEMPT_PREFIXES = ("/api/v1/health", "/metrics", "/docs", "/redoc", "/openapi.json")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Applies sliding-window rate limiting per client IP.
    WebSocket upgrade requests use a tighter limit than REST calls.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        # Skip exempt paths
        if any(path.startswith(p) for p in _EXEMPT_PREFIXES):
            return await call_next(request)

        # Determine client identifier
        client_ip = (
            request.headers.get("X-Real-IP")
            or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown")
        )

        # Choose limiter based on path
        is_ws = path.startswith("/api/v1/ws") or request.headers.get("upgrade", "").lower() == "websocket"
        limiter = _ws_limiter if is_ws else _api_limiter
        key = f"{client_ip}:{'ws' if is_ws else 'api'}"

        allowed, retry_after = limiter.is_allowed(key)
        if not allowed:
            logger.warning("Rate limit exceeded", client=client_ip, path=path)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please slow down.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
