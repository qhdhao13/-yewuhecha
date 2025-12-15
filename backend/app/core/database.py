"""
数据库连接和会话管理
使用SQLAlchemy进行数据库操作
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 创建数据库引擎
# SQLite数据库，连接字符串格式：sqlite:///./path/to/db.db
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """
    获取数据库会话
    用于依赖注入，在请求处理完成后自动关闭会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

