
from typing import (  # Import Generic, List, TypeVar
    Any,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
)
from pydantic import BaseModel, ConfigDict




class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: Optional[str] = None
    resolution: Optional[str] = None
    data: Optional[Any] = None
    role: Optional[str] = None


class SuccessResponse(BaseModel):
    role: Optional[str] = None
    message: str = "SUCCESS"
    data: Optional[Any] = None
    status_code: int
    headers: Optional[Dict[str, str]] = None
    
    
# Generic Pydantic model for paginated responses
ItemType = TypeVar("ItemType")


class PaginatedResponse(BaseModel, Generic[ItemType]):
    items: List[ItemType]
    total: int
    page: int
    per_page: int
    total_pages: int
