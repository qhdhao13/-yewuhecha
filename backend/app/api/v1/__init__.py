"""
API v1 路由汇总
将所有API路由集中管理
"""
from fastapi import APIRouter
from app.api.v1 import regulations, documents, reviews, annotations, files, system

# 创建API路由器
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(regulations.router, prefix="/regulations", tags=["制度文件管理"])
api_router.include_router(documents.router, prefix="/documents", tags=["员工文档管理"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["合规审查"])
api_router.include_router(annotations.router, prefix="/annotations", tags=["标注管理"])
api_router.include_router(files.router, prefix="/files", tags=["文件访问"])
api_router.include_router(system.router, prefix="/system", tags=["系统状态"])

