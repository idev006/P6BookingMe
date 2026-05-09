from pydantic import BaseModel
from typing import Any, Generic, TypeVar, Optional

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    message: Optional[str] = None
    status: str = "success"

class PaginatedResponse(StandardResponse, Generic[T]):
    total: int
    page: int
    per_page: int
    pages: int
