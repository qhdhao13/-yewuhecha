"""
数据库初始化脚本
创建数据库表和初始数据
"""
from app.core.database import engine, Base
from app.models import Regulation, Document, Review, Annotation

def init_db():
    """初始化数据库，创建所有表"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功！")

if __name__ == "__main__":
    init_db()

