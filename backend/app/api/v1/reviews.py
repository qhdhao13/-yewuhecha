"""
合规审查API
提供文档审查的创建、查询、状态管理等功能
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.review import Review
from app.models.document import Document
from app.models.regulation import Regulation
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.review_service import ReviewService

router = APIRouter()


@router.post("/", response_model=ReviewResponse)
async def create_review(
    review_create: ReviewCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    创建审查任务
    选择员工文档和制度文件进行对比审查
    """
    # 验证文档和制度是否存在
    document = db.query(Document).filter(
        Document.id == review_create.document_id,
        Document.is_deleted == 0
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="员工文档不存在")
    
    regulation = db.query(Regulation).filter(
        Regulation.id == review_create.regulation_id,
        Regulation.is_deleted == 0
    ).first()
    
    if not regulation:
        raise HTTPException(status_code=404, detail="制度文件不存在")
    
    # 创建审查记录
    review = Review(
        document_id=review_create.document_id,
        regulation_id=review_create.regulation_id,
        status="processing",
        reviewer=review_create.reviewer
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    # 在后台执行审查任务
    # 注意：后台任务需要创建新的数据库会话，所以不传递db参数
    background_tasks.add_task(
        ReviewService.process_review,
        review_id=review.id
    )
    
    return review


@router.get("/", response_model=List[ReviewResponse])
async def list_reviews(
    skip: int = 0,
    limit: int = 100,
    document_id: Optional[int] = None,
    regulation_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取审查记录列表
    """
    try:
        query = db.query(Review)
        
        if document_id:
            query = query.filter(Review.document_id == document_id)
        if regulation_id:
            query = query.filter(Review.regulation_id == regulation_id)
        if status:
            query = query.filter(Review.status == status)
        
        # 注意：order_by() 必须在 offset() 和 limit() 之前调用
        reviews = query.order_by(Review.review_time.desc()).offset(skip).limit(limit).all()
        return reviews
    except Exception as e:
        print(f"获取审查记录列表失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取审查记录列表失败: {str(e)}")


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    """
    获取审查记录详情
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="审查记录不存在")
    
    return review

