"""Configuration management"""

import os
from typing import Optional
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    app_name: str = os.getenv("APP_NAME", "Bible Video AI Agency")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # TTS
    tts_provider: str = os.getenv("TTS_PROVIDER", "elevenlabs")
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    # Video Generation
    video_provider: str = os.getenv("VIDEO_PROVIDER", "did")
    did_api_key: str = os.getenv("DID_API_KEY", "")
    
    # Social Media
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    tiktok_access_token: str = os.getenv("TIKTOK_ACCESS_TOKEN", "")
    instagram_access_token: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


def load_config(config_path: Optional[str] = None) -> dict:
    """Load YAML configuration file"""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "default.yaml"
    
    if not Path(config_path).exists():
        return {}
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}
