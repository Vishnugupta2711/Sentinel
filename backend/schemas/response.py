from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Metadata(BaseModel):
    request_id: str | None = None
    timestamp: str | None = None


class Pagination(BaseModel):
    total: int
    page: int
    size: int
    pages: int


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: Metadata | None = None
    pagination: Pagination | None = None


class ErrorDetails(BaseModel):
    code: str
    message: str
    request_id: str | None = None


class FailureResponse(BaseModel):
    success: bool = False
    error: ErrorDetails
