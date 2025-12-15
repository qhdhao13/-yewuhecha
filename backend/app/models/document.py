"""
员工文档数据模型
存储员工上传的文档信息
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Document(Base):
    """员工文档表"""
    __tablename__ = "documents"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="文档ID")
    
    # 基本信息
    name = Column(String(200), nullable=False, comment="文档名称")
    type = Column(String(50), nullable=True, comment="文档类型（如：报告、方案、申请等）")
    author = Column(String(100), nullable=True, comment="撰写人")
    department = Column(String(100), nullable=True, comment="撰写部门")
    
    # 文件信息
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_type = Column(String(20), nullable=False, comment="文件类型（pdf/docx/txt/md）")
    file_size = Column(Integer, nullable=True, comment="文件大小（字节）")
    
    # 内容信息
    content = Column(Text, nullable=True, comment="文档文本内容")
    vector_id = Column(String(100), nullable=True, comment="向量数据库中的ID")
    
    # 状态信息
    status = Column(String(20), default="pending", comment="审查状态（pending=待审查，reviewing=审查中，completed=已完成）")
    
    # 元数据
    upload_time = Column(DateTime, server_default=func.now(), comment="上传时间")
    
    # 软删除标记
    is_deleted = Column(Integer, default=0, comment="是否已删除（0=未删除，1=已删除）")
    
    def __repr__(self):
        return f"<Document(id={self.id}, name='{self.name}', author='{self.author}', status='{self.status}')>"

