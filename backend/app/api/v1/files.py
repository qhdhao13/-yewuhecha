"""
文件访问API
提供文件下载和查看功能
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.core.config import settings
from app.models.regulation import Regulation
from app.models.document import Document

router = APIRouter()


@router.get("/regulations/{regulation_id}/download")
async def download_regulation(
    regulation_id: int,
    db: Session = Depends(get_db)
):
    """
    下载制度文件
    """
    regulation = db.query(Regulation).filter(
        Regulation.id == regulation_id,
        Regulation.is_deleted == 0
    ).first()
    
    if not regulation:
        raise HTTPException(status_code=404, detail="制度文件不存在")
    
    # 构建文件完整路径
    file_path = os.path.join(settings.UPLOAD_DIR, regulation.file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=regulation.name + os.path.splitext(regulation.file_path)[1],
        media_type='application/octet-stream'
    )


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    下载员工文档
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.is_deleted == 0
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 构建文件完整路径
    file_path = os.path.join(settings.UPLOAD_DIR, document.file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=document.name + os.path.splitext(document.file_path)[1],
        media_type='application/octet-stream'
    )

