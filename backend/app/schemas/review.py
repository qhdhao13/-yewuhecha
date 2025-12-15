"""
审查记录相关的Pydantic模式
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    """创建审查记录的请求模式"""
    document_id: int
    regulation_id: int
    reviewer: Optional[str] = None


class ReviewResponse(BaseModel):
    """审查记录响应模式"""
    id: int
    document_id: int
    regulation_id: int
    status: str
    total_issues: int
    critical_count: int
    general_count: int
    minor_count: int
    review_time: datetime
    completed_time: Optional[datetime] = None
    reviewer: Optional[str] = None
    
    class Config:
        from_attributes = True

