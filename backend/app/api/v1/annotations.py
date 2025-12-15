"""
标注管理API
提供标注的查询、更新、删除等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.annotation import Annotation
from app.schemas.annotation import AnnotationUpdate, AnnotationResponse

router = APIRouter()


@router.get("/", response_model=List[AnnotationResponse])
async def list_annotations(
    review_id: Optional[int] = None,
    document_id: Optional[int] = None,
    regulation_id: Optional[int] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    issue_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取标注列表
    支持多种筛选条件
    """
    query = db.query(Annotation)
    
    if review_id:
        query = query.filter(Annotation.review_id == review_id)
    if document_id:
        query = query.filter(Annotation.document_id == document_id)
    if regulation_id:
        query = query.filter(Annotation.regulation_id == regulation_id)
    if status:
        query = query.filter(Annotation.status == status)
    if severity:
        query = query.filter(Annotation.severity == severity)
    if issue_type:
        query = query.filter(Annotation.issue_type == issue_type)
    
    annotations = query.offset(skip).limit(limit).order_by(Annotation.create_time.desc()).all()
    return annotations


@router.get("/{annotation_id}", response_model=AnnotationResponse)
async def get_annotation(
    annotation_id: int,
    db: Session = Depends(get_db)
):
    """
    获取标注详情
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    
    if not annotation:
        raise HTTPException(status_code=404, detail="标注不存在")
    
    return annotation


@router.put("/{annotation_id}", response_model=AnnotationResponse)
async def update_annotation(
    annotation_id: int,
    annotation_update: AnnotationUpdate,
    db: Session = Depends(get_db)
):
    """
    更新标注信息
    用于人工审核和编辑标注
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    
    if not annotation:
        raise HTTPException(status_code=404, detail="标注不存在")
    
    update_data = annotation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(annotation, field, value)
    
    db.commit()
    db.refresh(annotation)
    return annotation


@router.delete("/{annotation_id}")
async def delete_annotation(
    annotation_id: int,
    db: Session = Depends(get_db)
):
    """
    删除标注
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    
    if not annotation:
        raise HTTPException(status_code=404, detail="标注不存在")
    
    db.delete(annotation)
    db.commit()
    
    return {"message": "删除成功"}

