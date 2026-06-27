from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from utils.constants import REQUEST_ID_HEADER
from utils.uuid import generate_uuid


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or generate_uuid()
        
        # Add to request state for downstream use
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
