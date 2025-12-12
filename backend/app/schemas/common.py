"""
Common schemas used across API
Pagination, list responses, error handling
"""

from pydantic import BaseModel
from typing import List, TypeVar, Generic, Optional

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = 0
    limit: int = 10
    
    class Config:
        ge = {"skip": 0, "limit": 1}
        le = {"limit": 100}


class ListResponse(BaseModel, Generic[T]):
    """Generic list response with pagination"""
    data: List[T]
    total: int
    skip: int
    limit: int
    
    @property
    def has_more(self) -> bool:
        return self.skip + self.limit < self.total


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    status_code: int
    error_code: Optional[str] = None


class SuccessResponse(BaseModel, Generic[T]):
    """Generic success response"""
    data: T
    message: Optional[str] = None
