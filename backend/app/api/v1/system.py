"""
系统状态API
提供系统状态检查，包括Ollama服务状态和模型可用性
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import requests
from app.core.config import settings

# 添加requests到requirements.txt（如果还没有）
# requests库通常已经包含在其他依赖中

router = APIRouter()


@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """
    获取系统状态
    包括Ollama服务状态和模型可用性
    """
    status = {
        "ollama_service": False,
        "llm_model": False,
        "embedding_model": False,
        "llm_model_name": settings.OLLAMA_LLM_MODEL,
        "embedding_model_name": settings.OLLAMA_EMBEDDING_MODEL,
        "ollama_url": settings.OLLAMA_BASE_URL,
        "message": ""
    }
    
    try:
        # 检查Ollama服务是否运行
        response = requests.get(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=5
        )
        
        if response.status_code == 200:
            status["ollama_service"] = True
            models_data = response.json()
            models = [model.get("name", "") for model in models_data.get("models", [])]
            
            # 检查LLM模型是否可用
            llm_model_available = False
            for model_name in models:
                # 支持多种格式：deepseek-r1:7b, deepseek-r1:7b:latest等
                if settings.OLLAMA_LLM_MODEL in model_name or model_name.startswith(settings.OLLAMA_LLM_MODEL.split(":")[0]):
                    llm_model_available = True
                    status["llm_model"] = True
                    break
            
            # 检查嵌入模型是否可用
            embedding_model_available = False
            for model_name in models:
                if settings.OLLAMA_EMBEDDING_MODEL in model_name or model_name.startswith(settings.OLLAMA_EMBEDDING_MODEL.split(":")[0]):
                    embedding_model_available = True
                    status["embedding_model"] = True
                    break
            
            # 生成状态消息
            if status["ollama_service"] and status["llm_model"]:
                status["message"] = "系统就绪，可以正常使用"
            elif status["ollama_service"] and not status["llm_model"]:
                status["message"] = f"Ollama服务运行中，但未找到模型 {settings.OLLAMA_LLM_MODEL}"
            else:
                status["message"] = "Ollama服务未运行"
                
        else:
            status["message"] = f"Ollama服务响应异常: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        status["message"] = "无法连接到Ollama服务，请确保Ollama正在运行"
    except requests.exceptions.Timeout:
        status["message"] = "连接Ollama服务超时"
    except Exception as e:
        status["message"] = f"检查服务状态时出错: {str(e)}"
    
    return status


@router.get("/models")
async def get_available_models() -> Dict[str, Any]:
    """
    获取可用的模型列表
    """
    try:
        response = requests.get(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=5
        )
        
        if response.status_code == 200:
            models_data = response.json()
            models = models_data.get("models", [])
            
            return {
                "success": True,
                "models": [
                    {
                        "name": model.get("name", ""),
                        "size": model.get("size", 0),
                        "modified_at": model.get("modified_at", "")
                    }
                    for model in models
                ]
            }
        else:
            return {
                "success": False,
                "message": f"无法获取模型列表: {response.status_code}",
                "models": []
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"获取模型列表失败: {str(e)}",
            "models": []
        }

