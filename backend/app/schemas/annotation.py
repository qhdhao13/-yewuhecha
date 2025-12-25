"""
标注相关的Pydantic模式
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnnotationResponse(BaseModel):
    """标注响应模式"""
    id: int
    review_id: int
    document_id: int
    regulation_id: int
    position: Optional[str] = None
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    content: Optional[str] = None
    regulation_clause: Optional[str] = None
    issue_type: str
    severity: str
    reason: Optional[str] = None
    suggestion: Optional[str] = None
    status: str
    create_time: datetime
    update_time: datetime
    reviewer: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }


class AnnotationUpdate(BaseModel):
    """更新标注的请求模式"""
    status: Optional[str] = None
    reason: Optional[str] = None
    suggestion: Optional[str] = None
    severity: Optional[str] = None

