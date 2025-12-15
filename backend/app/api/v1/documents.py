"""
员工文档管理API
提供员工文档的上传、查询、更新、删除等功能
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.services.file_service import FileService
from app.services.document_parser import DocumentParser

router = APIRouter()


@router.post("/", response_model=DocumentResponse)
async def create_document(
    name: str = Form(...),
    type: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传员工文档
    接收文件上传，解析内容，存储到数据库和文件系统
    """
    try:
        # 1. 验证文件
        file_ext, file_type = FileService.validate_file(file)
        file_size = FileService.validate_file_size(file)
        
        # 2. 生成文件存储路径
        relative_path, full_path = FileService.generate_file_path(
            file_type=file_type,
            category="documents"
        )
        
        # 3. 保存文件
        await FileService.save_file(file, full_path)
        
        # 4. 解析文档内容
        content = ""
        try:
            content = DocumentParser.parse_file(full_path)
        except Exception as e:
            # 解析失败不影响文件上传，只记录错误
            print(f"文档解析失败: {str(e)}")
        
        # 5. 创建数据库记录
        document = Document(
            name=name,
            type=type,
            author=author,
            department=department,
            file_path=relative_path,  # 存储相对路径
            file_type=file_type,
            file_size=file_size,
            content=content,
            status="pending"  # 初始状态为待审查
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 如果数据库操作失败，尝试删除已上传的文件
        if 'full_path' in locals():
            FileService.delete_file(full_path)
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )


@router.get("/")
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    author: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取员工文档列表
    支持分页、状态筛选、作者筛选和搜索
    返回格式：{"items": [...], "total": 总数}
    """
    query = db.query(Document).filter(Document.is_deleted == 0)
    
    if status:
        query = query.filter(Document.status == status)
    if author:
        query = query.filter(Document.author == author)
    if department:
        query = query.filter(Document.department == department)
    if search:
        query = query.filter(Document.name.contains(search))
    
    # 获取总数
    total = query.count()
    
    # 获取分页数据
    documents = query.offset(skip).limit(limit).all()
    
    return {
        "items": documents,
        "total": total
    }


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    获取员工文档详情
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.is_deleted == 0
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """
    更新员工文档信息
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.is_deleted == 0
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    update_data = document_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    删除员工文档（软删除）
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.is_deleted == 0
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    document.is_deleted = 1
    db.commit()
    
    return {"message": "删除成功"}

