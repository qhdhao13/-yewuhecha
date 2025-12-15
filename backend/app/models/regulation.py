"""
制度文件数据模型
存储制度文件的基本信息和元数据
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Regulation(Base):
    """制度文件表"""
    __tablename__ = "regulations"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="制度ID")
    
    # 基本信息
    name = Column(String(200), nullable=False, comment="制度名称")
    code = Column(String(100), unique=True, nullable=True, comment="制度编号")
    type = Column(String(50), nullable=True, comment="制度类型（如：财务制度、人事制度等）")
    effective_date = Column(DateTime, nullable=True, comment="生效日期")
    
    # 文件信息
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_type = Column(String(20), nullable=False, comment="文件类型（pdf/docx/txt/md）")
    file_size = Column(Integer, nullable=True, comment="文件大小（字节）")
    
    # 内容信息
    content = Column(Text, nullable=True, comment="文档文本内容")
    vector_id = Column(String(100), nullable=True, comment="向量数据库中的ID")
    
    # 元数据
    upload_time = Column(DateTime, server_default=func.now(), comment="上传时间")
    uploader = Column(String(100), nullable=True, comment="上传人")
    
    # 软删除标记
    is_deleted = Column(Integer, default=0, comment="是否已删除（0=未删除，1=已删除）")
    
    def __repr__(self):
        return f"<Regulation(id={self.id}, name='{self.name}', code='{self.code}')>"

