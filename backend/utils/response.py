from typing import Any

from schemas.response import ErrorDetails, FailureResponse, SuccessResponse


def build_success_response(data: Any, meta: dict[str, Any] | None = None) -> SuccessResponse[Any]:
    """Builds a standardized success response."""
    # Assuming Pydantic parses dictionaries automatically to the Metadata object if passed.
    return SuccessResponse(data=data, meta=meta)


def build_error_response(code: str, message: str, request_id: str | None = None) -> FailureResponse:
    """Builds a standardized failure response."""
    return FailureResponse(
        error=ErrorDetails(code=code, message=message, request_id=request_id)
    )
