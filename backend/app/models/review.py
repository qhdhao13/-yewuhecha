"""
审查记录数据模型
存储文档审查的元数据和统计信息
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Review(Base):
    """审查记录表"""
    __tablename__ = "reviews"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="审查记录ID")
    
    # 关联信息
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, comment="员工文档ID")
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False, comment="制度文件ID")
    
    # 审查状态
    status = Column(String(20), default="processing", comment="审查状态（processing=处理中，completed=已完成，failed=失败）")
    
    # 统计信息
    total_issues = Column(Integer, default=0, comment="不符合项总数")
    critical_count = Column(Integer, default=0, comment="严重项数量")
    general_count = Column(Integer, default=0, comment="一般项数量")
    minor_count = Column(Integer, default=0, comment="轻微项数量")
    
    # 时间信息
    review_time = Column(DateTime, server_default=func.now(), comment="审查时间")
    completed_time = Column(DateTime, nullable=True, comment="完成时间")
    
    # 审查人
    reviewer = Column(String(100), nullable=True, comment="审查人")
    
    # 关联关系
    document = relationship("Document", backref="reviews")
    regulation = relationship("Regulation", backref="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, document_id={self.document_id}, regulation_id={self.regulation_id}, status='{self.status}')>"

