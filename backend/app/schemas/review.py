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
    total_issues: int = 0
    critical_count: int = 0
    general_count: int = 0
    minor_count: int = 0
    review_time: datetime
    completed_time: Optional[datetime] = None
    reviewer: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }

