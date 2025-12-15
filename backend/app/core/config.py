"""
应用配置管理
从环境变量或.env文件读取配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本信息
    APP_NAME: str = "合规审查知识库系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/compliance.db"
    
    # 文件存储配置
    UPLOAD_DIR: str = "./data/uploads"
    MAX_FILE_SIZE: int = 52428800  # 50MB
    
    # Ollama配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"  # 嵌入模型（用于文档向量化）
    OLLAMA_LLM_MODEL: str = "deepseek-r1:7b"  # 大语言模型（用于语义对比分析）
    
    # 向量数据库配置
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

