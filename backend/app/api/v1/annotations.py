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
    try:
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
        
        # 先排序，再分页
        annotations = query.order_by(Annotation.create_time.desc()).offset(skip).limit(limit).all()
        return annotations
    except Exception as e:
        print(f"获取标注列表失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取标注列表失败: {str(e)}")


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
    
    update_data = annotation_update.model_dump(exclude_unset=True)
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


@router.post("/{annotation_id}/generate-suggestion")
async def generate_ai_suggestion(
    annotation_id: int,
    db: Session = Depends(get_db)
):
    """
    为标注生成AI改进建议
    使用Ollama生成更详细和实用的改进建议
    """
    from app.services.ollama_service import OllamaService
    
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    
    if not annotation:
        raise HTTPException(status_code=404, detail="标注不存在")
    
    try:
        ollama_service = OllamaService()
        
        # 构建问题描述
        issue_description = f"""
问题类型：{annotation.issue_type}
不符合内容：{annotation.content or '未指定'}
对应的制度条款：{annotation.regulation_clause or '未指定'}
当前原因说明：{annotation.reason or '无'}
当前修改建议：{annotation.suggestion or '无'}
        """.strip()
        
        # 生成改进建议
        result = ollama_service.generate_enhanced_suggestion(
            issue_description=issue_description,
            regulation_clause=annotation.regulation_clause or "",
            issue_type=annotation.issue_type,
            severity=annotation.severity
        )
        
        # 更新标注的建议（可选，也可以只返回不保存）
        if result.get("suggestion"):
            annotation.suggestion = result["suggestion"]
            if result.get("reason") and not annotation.reason:
                annotation.reason = result["reason"]
            db.commit()
            db.refresh(annotation)
        
        return {
            "success": True,
            "suggestion": result.get("suggestion", ""),
            "reason": result.get("reason", ""),
            "detailed_analysis": result.get("detailed_analysis", ""),
            "improved_content": result.get("improved_content", "")
        }
    except Exception as e:
        print(f"生成AI建议失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成AI建议失败: {str(e)}")

