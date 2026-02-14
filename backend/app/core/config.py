from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/openstock"
    
    # Tushare API Token
    TUSHARE_TOKEN: str = ""
    
    # 应用配置
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
