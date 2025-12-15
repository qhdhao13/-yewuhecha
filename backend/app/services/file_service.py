"""
文件上传服务
处理文件的上传、存储、验证等功能
"""
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from datetime import datetime
from app.core.config import settings


class FileService:
    """文件上传服务类"""
    
    # 支持的文件类型
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.md'}
    # 文件类型映射
    FILE_TYPE_MAP = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'docx',  # 旧版Word格式，需要特殊处理
        '.txt': 'txt',
        '.md': 'md'
    }
    
    @staticmethod
    def validate_file(file: UploadFile) -> Tuple[str, str]:
        """
        验证上传的文件
        返回: (文件扩展名, 文件类型)
        """
        # 获取文件扩展名
        filename = file.filename or ""
        file_ext = Path(filename).suffix.lower()
        
        # 验证文件扩展名
        if file_ext not in FileService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}。支持格式: {', '.join(FileService.ALLOWED_EXTENSIONS)}"
            )
        
        # 获取文件类型
        file_type = FileService.FILE_TYPE_MAP.get(file_ext, 'unknown')
        
        return file_ext, file_type
    
    @staticmethod
    def validate_file_size(file: UploadFile) -> int:
        """
        验证文件大小
        返回: 文件大小（字节）
        """
        # 读取文件内容以获取大小
        content = file.file.read()
        file_size = len(content)
        
        # 重置文件指针，以便后续读取
        file.file.seek(0)
        
        # 检查文件大小限制
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制: {file_size / 1024 / 1024:.2f}MB，最大允许: {settings.MAX_FILE_SIZE / 1024 / 1024:.2f}MB"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="文件为空")
        
        return file_size
    
    @staticmethod
    def generate_file_path(file_type: str, category: str = "general") -> Tuple[str, str]:
        """
        生成文件存储路径
        category: 文件类别（regulations=制度文件, documents=员工文档）
        返回: (相对路径, 完整路径)
        """
        # 创建按日期组织的目录结构
        date_str = datetime.now().strftime("%Y%m%d")
        
        # 生成唯一文件名
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}_{int(datetime.now().timestamp())}.{file_type}"
        
        # 构建路径
        relative_path = f"{category}/{date_str}/{filename}"
        full_path = os.path.join(settings.UPLOAD_DIR, relative_path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        return relative_path, full_path
    
    @staticmethod
    async def save_file(file: UploadFile, file_path: str) -> None:
        """
        保存文件到指定路径
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 写入文件
            with open(file_path, "wb") as f:
                # 分块读取和写入，避免内存问题
                while True:
                    chunk = await file.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    f.write(chunk)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"文件保存失败: {str(e)}"
            )
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        删除文件
        返回: 是否删除成功
        """
        try:
            # 如果是相对路径，转换为绝对路径
            if not os.path.isabs(file_path):
                full_path = os.path.join(settings.UPLOAD_DIR, file_path)
            else:
                full_path = file_path
            
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
            return False
    
    @staticmethod
    def get_file_url(file_path: str) -> str:
        """
        获取文件的访问URL
        """
        # 如果是绝对路径，提取相对路径
        if os.path.isabs(file_path):
            # 从完整路径中提取相对路径
            if file_path.startswith(settings.UPLOAD_DIR):
                relative_path = file_path[len(settings.UPLOAD_DIR):].lstrip('/')
            else:
                relative_path = os.path.basename(file_path)
        else:
            relative_path = file_path
        
        # 返回相对于uploads目录的URL
        return f"/uploads/{relative_path}"

