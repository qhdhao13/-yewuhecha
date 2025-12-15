"""
制度文件相关的Pydantic模式
用于API请求和响应的数据验证
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RegulationBase(BaseModel):
    """制度文件基础模式"""
    name: str
    code: Optional[str] = None
    type: Optional[str] = None
    effective_date: Optional[datetime] = None
    uploader: Optional[str] = None


class RegulationCreate(RegulationBase):
    """创建制度文件的请求模式"""
    pass


class RegulationUpdate(BaseModel):
    """更新制度文件的请求模式"""
    name: Optional[str] = None
    code: Optional[str] = None
    type: Optional[str] = None
    effective_date: Optional[datetime] = None


class RegulationResponse(RegulationBase):
    """制度文件响应模式"""
    id: int
    file_path: str
    file_type: str
    file_size: Optional[int] = None
    upload_time: datetime
    
    class Config:
        from_attributes = True

