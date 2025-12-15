"""
应用启动脚本
用于启动FastAPI开发服务器
"""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,  # 开发模式下自动重载
        log_level="info"
    )

