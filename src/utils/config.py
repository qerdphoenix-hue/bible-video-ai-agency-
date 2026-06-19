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
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # TTS
    tts_provider: str = os.getenv("TTS_PROVIDER", "elevenlabs")
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    elevenlabs_voice_id: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    
    # Video Generation
    video_width: int = int(os.getenv("VIDEO_WIDTH", "1080"))
    video_height: int = int(os.getenv("VIDEO_HEIGHT", "1920"))
    video_fps: int = int(os.getenv("VIDEO_FPS", "30"))
    video_template: str = os.getenv("VIDEO_TEMPLATE", "cinematic")
    
    # Background Assets
    background_images_dir: str = os.getenv("BACKGROUND_IMAGES_DIR", "data/backgrounds")
    background_videos_dir: str = os.getenv("BACKGROUND_VIDEOS_DIR", "data/backgrounds/videos")
    
    # Social Media
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    youtube_client_secrets_file: str = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "")
    tiktok_access_token: str = os.getenv("TIKTOK_ACCESS_TOKEN", "")
    tiktok_open_id: str = os.getenv("TIKTOK_OPEN_ID", "")
    instagram_access_token: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    instagram_account_id: str = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
    twitter_api_key: str = os.getenv("TWITTER_API_KEY", "")
    twitter_api_secret: str = os.getenv("TWITTER_API_SECRET", "")
    twitter_access_token: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    twitter_access_token_secret: str = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./bible_ai.db")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    
    # Scheduling
    scheduler_interval_hours: int = int(os.getenv("SCHEDULER_INTERVAL_HOURS", "24"))
    max_videos_per_day: int = int(os.getenv("MAX_VIDEOS_PER_DAY", "3"))
    
    # Output
    output_dir: str = os.getenv("OUTPUT_DIR", "data/generated_videos")
    temp_dir: str = os.getenv("TEMP_DIR", "data/temp")
    
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
