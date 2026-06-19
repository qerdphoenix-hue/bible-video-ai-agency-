"""Database models and session management"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Enum, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Create engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()


class VideoStatus(str, PyEnum):
    """Video generation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PostStatus(str, PyEnum):
    """Social media post status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    POSTING = "posting"
    POSTED = "posted"
    FAILED = "failed"


class Platform(str, PyEnum):
    """Supported social media platforms"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"


class GeneratedVideo(Base):
    """Generated video metadata"""
    __tablename__ = "generated_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    book = Column(String(100), nullable=False)
    chapter = Column(Integer, nullable=False)
    start_verse = Column(Integer, nullable=False)
    end_verse = Column(Integer, nullable=True)
    translation = Column(String(50), default="KJV")
    language = Column(String(10), default="en")
    
    # File paths
    video_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=True)
    audio_path = Column(String(500), nullable=True)
    
    # Video specs
    duration_seconds = Column(Integer, nullable=True)
    resolution = Column(String(50), nullable=True)
    file_size_mb = Column(Integer, nullable=True)
    
    # Metadata
    tags = Column(JSON, default=list)
    hashtags = Column(JSON, default=list)
    category = Column(String(100), nullable=True)
    
    # Status
    status = Column(Enum(VideoStatus), default=VideoStatus.PENDING)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    generated_at = Column(DateTime, nullable=True)
    
    # Relationships
    social_posts = relationship("SocialPost", back_populates="video", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<GeneratedVideo(id={self.id}, title='{self.title}', status='{self.status}')>"


class SocialPost(Base):
    """Social media post tracking"""
    __tablename__ = "social_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("generated_videos.id"), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    
    # Platform-specific IDs
    platform_post_id = Column(String(255), nullable=True)
    platform_url = Column(String(500), nullable=True)
    
    # Post content
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    hashtags = Column(JSON, default=list)
    
    # Status
    status = Column(Enum(PostStatus), default=PostStatus.PENDING)
    error_message = Column(Text, nullable=True)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    
    # Analytics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    analytics_updated_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    video = relationship("GeneratedVideo", back_populates="social_posts")
    
    def __repr__(self):
        return f"<SocialPost(id={self.id}, platform='{self.platform}', status='{self.status}')>"


class GenerationSchedule(Base):
    """Scheduled generation jobs"""
    __tablename__ = "generation_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    
    # Bible selection
    book = Column(String(100), nullable=True)
    chapter = Column(Integer, nullable=True)
    start_verse = Column(Integer, nullable=True)
    end_verse = Column(Integer, nullable=True)
    
    # Or auto-select
    auto_select = Column(Boolean, default=True)
    theme = Column(String(100), nullable=True)
    testament = Column(String(50), nullable=True)
    
    # Schedule
    frequency = Column(String(50), default="daily")  # hourly, daily, weekly
    schedule_time = Column(String(10), default="09:00")  # HH:MM
    timezone = Column(String(50), default="UTC")
    max_videos_per_run = Column(Integer, default=1)
    
    # Platforms
    platforms = Column(JSON, default=list)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<GenerationSchedule(id={self.id}, name='{self.name}', active={self.is_active})>"


class AnalyticsEvent(Base):
    """Analytics events tracking"""
    __tablename__ = "analytics_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)
    platform = Column(String(100), nullable=True)
    video_id = Column(Integer, ForeignKey("generated_videos.id"), nullable=True)
    
    # Metrics
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Integer, default=0)
    
    # Raw data
    raw_data = Column(JSON, nullable=True)
    
    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AnalyticsEvent(id={self.id}, type='{self.event_type}', metric='{self.metric_name}')>"


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
