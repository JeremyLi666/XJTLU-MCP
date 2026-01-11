from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 应用配置
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # AI 服务配置
    USE_MOCK_AI: bool = True
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # 安全配置
    API_SECRET_KEY: str = "xjtlu_academic_navigator_secret_key"
    
    # 路径配置
    MOCK_DATA_PATH: str = "mock"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()