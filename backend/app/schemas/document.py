"""
员工文档相关的Pydantic模式
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentBase(BaseModel):
    """员工文档基础模式"""
    name: str
    type: Optional[str] = None
    author: Optional[str] = None
    department: Optional[str] = None


class DocumentCreate(DocumentBase):
    """创建员工文档的请求模式"""
    pass


class DocumentUpdate(BaseModel):
    """更新员工文档的请求模式"""
    name: Optional[str] = None
    type: Optional[str] = None
    author: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None


class DocumentResponse(DocumentBase):
    """员工文档响应模式"""
    id: int
    file_path: str
    file_type: str
    file_size: Optional[int] = None
    status: str
    upload_time: datetime
    
    class Config:
        from_attributes = True

