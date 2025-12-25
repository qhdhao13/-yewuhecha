"""
制度文件管理API
提供制度文件的上传、查询、更新、删除等功能
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.regulation import Regulation
from app.schemas.regulation import RegulationCreate, RegulationUpdate, RegulationResponse
from app.services.file_service import FileService
from app.services.document_parser import DocumentParser

router = APIRouter()


@router.post("/", response_model=RegulationResponse)
async def create_regulation(
    name: str = Form(...),
    code: Optional[str] = Form(None),
    type: Optional[str] = Form(None),
    effective_date: Optional[str] = Form(None),
    uploader: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传制度文件
    接收文件上传，解析内容，存储到数据库和文件系统
    """
    try:
        # 1. 验证文件
        file_ext, file_type = FileService.validate_file(file)
        file_size = FileService.validate_file_size(file)
        
        # 2. 生成文件存储路径
        relative_path, full_path = FileService.generate_file_path(
            file_type=file_type,
            category="regulations"
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
        
        # 5. 处理生效日期
        effective_date_obj = None
        if effective_date:
            try:
                effective_date_obj = datetime.fromisoformat(effective_date.replace('Z', '+00:00'))
            except:
                try:
                    effective_date_obj = datetime.strptime(effective_date, "%Y-%m-%d")
                except:
                    pass  # 如果日期格式不正确，设为None
        
        # 6. 创建数据库记录
        regulation = Regulation(
            name=name,
            code=code,
            type=type,
            effective_date=effective_date_obj,
            file_path=relative_path,  # 存储相对路径
            file_type=file_type,
            file_size=file_size,
            content=content,
            uploader=uploader
        )
        
        db.add(regulation)
        db.commit()
        db.refresh(regulation)
        
        return regulation
        
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
async def list_regulations(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取制度文件列表
    支持分页、类型筛选和搜索
    返回格式：{"items": [...], "total": 总数}
    """
    try:
        query = db.query(Regulation).filter(Regulation.is_deleted == 0)
        
        if type:
            query = query.filter(Regulation.type == type)
        if search:
            query = query.filter(Regulation.name.contains(search))
        
        # 获取总数
        total = query.count()
        
        # 获取分页数据
        regulations = query.offset(skip).limit(limit).all()
        
        return {
            "items": regulations,
            "total": total
        }
    except Exception as e:
        print(f"获取制度文件列表失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取制度文件列表失败: {str(e)}")


@router.get("/{regulation_id}", response_model=RegulationResponse)
async def get_regulation(
    regulation_id: int,
    db: Session = Depends(get_db)
):
    """
    获取制度文件详情
    """
    regulation = db.query(Regulation).filter(
        Regulation.id == regulation_id,
        Regulation.is_deleted == 0
    ).first()
    
    if not regulation:
        raise HTTPException(status_code=404, detail="制度文件不存在")
    
    return regulation


@router.put("/{regulation_id}", response_model=RegulationResponse)
async def update_regulation(
    regulation_id: int,
    regulation_update: RegulationUpdate,
    db: Session = Depends(get_db)
):
    """
    更新制度文件信息
    只能更新元数据，不能更新文件内容
    """
    regulation = db.query(Regulation).filter(
        Regulation.id == regulation_id,
        Regulation.is_deleted == 0
    ).first()
    
    if not regulation:
        raise HTTPException(status_code=404, detail="制度文件不存在")
    
    # 更新字段
    update_data = regulation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(regulation, field, value)
    
    db.commit()
    db.refresh(regulation)
    return regulation


@router.delete("/{regulation_id}")
async def delete_regulation(
    regulation_id: int,
    db: Session = Depends(get_db)
):
    """
    删除制度文件（软删除）
    """
    regulation = db.query(Regulation).filter(
        Regulation.id == regulation_id,
        Regulation.is_deleted == 0
    ).first()
    
    if not regulation:
        raise HTTPException(status_code=404, detail="制度文件不存在")
    
    regulation.is_deleted = 1
    db.commit()
    
    return {"message": "删除成功"}

