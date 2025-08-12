from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


class SearchParams(BaseModel):
    search_term: Optional[str] = Field(None, min_length=1, max_length=100)
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class FilterParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class ResponseMessage(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    message: str
    success: bool = False
    error_code: Optional[str] = None
