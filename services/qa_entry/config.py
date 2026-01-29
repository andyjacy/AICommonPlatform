from pydantic_settings import BaseSettings
from typing import Optional
import logging

class Settings(BaseSettings):
    """全局配置"""
    
    # 服务信息
    service_name: str = "qa_entry"
    service_version: str = "1.0.0"
    debug: bool = False
    
    # Redis配置
    redis_url: str = "redis://:ai_redis_2024@localhost:6379/0"
    
    # 数据库配置
    database_url: str = "postgresql://admin:ai_platform_2024@localhost:5432/ai_platform"
    
    # 外部服务配置
    prompt_service_url: str = "http://localhost:8002"
    rag_service_url: str = "http://localhost:8003"
    agent_service_url: str = "http://localhost:8004"
    llm_service_url: str = "http://localhost:8006"
    integration_service_url: str = "http://localhost:8005"
    
    # LLM配置
    llm_provider: str = "openai"  # openai, aliyun, baidu
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "json"  # json 或 text
    
    # 超时配置
    request_timeout: int = 30
    rag_timeout: int = 20
    llm_timeout: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 全局设置实例
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """获取全局设置"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
