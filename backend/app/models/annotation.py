"""
标注数据模型
存储审查过程中识别出的不符合项标注信息
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Annotation(Base):
    """标注表"""
    __tablename__ = "annotations"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="标注ID")
    
    # 关联信息
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, comment="审查记录ID")
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, comment="员工文档ID")
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False, comment="制度文件ID")
    
    # 位置信息
    position = Column(String(100), nullable=True, comment="标注位置（段落号/行号/字符位置）")
    start_pos = Column(Integer, nullable=True, comment="起始位置（字符索引）")
    end_pos = Column(Integer, nullable=True, comment="结束位置（字符索引）")
    
    # 内容信息
    content = Column(Text, nullable=True, comment="不符合的内容文本")
    regulation_clause = Column(Text, nullable=True, comment="对应的制度条款内容")
    
    # 问题分类
    issue_type = Column(String(50), nullable=False, comment="问题类型（content_mismatch=内容不符，missing=缺失，extra=多余，format=格式不符）")
    severity = Column(String(20), nullable=False, comment="严重程度（critical=严重，general=一般，minor=轻微）")
    
    # 说明信息
    reason = Column(Text, nullable=True, comment="不符合原因说明")
    suggestion = Column(Text, nullable=True, comment="修改建议")
    
    # 状态信息
    status = Column(String(20), default="pending", comment="标注状态（pending=待确认，confirmed=已确认，ignored=已忽略）")
    
    # 时间信息
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 审查人
    reviewer = Column(String(100), nullable=True, comment="审查人")
    
    # 关联关系
    review = relationship("Review", backref="annotations")
    document = relationship("Document", backref="annotations")
    regulation = relationship("Regulation", backref="annotations")
    
    def __repr__(self):
        return f"<Annotation(id={self.id}, issue_type='{self.issue_type}', severity='{self.severity}', status='{self.status}')>"

