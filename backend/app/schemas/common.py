from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


class ResponseBase(BaseModel):
    """Base response schema"""
    success: bool = True
    message: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    page_size: int = 20
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20
            }
        }


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True
