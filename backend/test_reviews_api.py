"""
测试审查API
"""
from app.core.database import SessionLocal
from app.models.review import Review
from sqlalchemy import inspect

# 创建数据库会话
db = SessionLocal()

try:
    # 检查表是否存在
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    print("数据库表:", tables)
    
    if 'reviews' in tables:
        # 检查表结构
        columns = inspector.get_columns('reviews')
        print("\nreviews表字段:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        # 尝试查询数据
        try:
            reviews = db.query(Review).all()
            print(f"\n审查记录数量: {len(reviews)}")
            if reviews:
                print("第一条记录:")
                review = reviews[0]
                print(f"  ID: {review.id}")
                print(f"  document_id: {review.document_id}")
                print(f"  regulation_id: {review.regulation_id}")
                print(f"  status: {review.status}")
                print(f"  review_time: {review.review_time}")
                print(f"  total_issues: {review.total_issues}")
        except Exception as e:
            print(f"\n查询错误: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n错误: reviews表不存在，需要运行 init_db.py")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
