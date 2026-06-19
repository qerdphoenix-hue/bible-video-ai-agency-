"""Pydantic models for API requests and responses"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


class VideoStatus(str, Enum):
    """Video generation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PostStatus(str, Enum):
    """Social media post status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    POSTING = "posting"
    POSTED = "posted"
    FAILED = "failed"


class Platform(str, Enum):
    """Supported social media platforms"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"


class VideoGenerateRequest(BaseModel):
    """Request to generate a video"""
    book: str = Field(..., description="Bible book name (e.g., John, Psalm)")
    chapter: int = Field(..., description="Chapter number")
    verses: str = Field(..., description="Verse range (e.g., '16-18' or '16')")
    language: str = Field(default="en", description="Language code")
    voice_id: Optional[str] = Field(default=None, description="Voice ID for TTS")
    template: Optional[str] = Field(default="cinematic", description="Video template")
    title: Optional[str] = Field(default=None, description="Custom video title")
    description: Optional[str] = Field(default=None, description="Custom description")
    auto_post: bool = Field(default=False, description="Auto-post after generation")
    platforms: Optional[List[Platform]] = Field(default=None, description="Platforms to post to")


class VideoGenerateResponse(BaseModel):
    """Response from video generation"""
    id: int
    title: str
    book: str
    chapter: int
    start_verse: int
    end_verse: Optional[int]
    video_path: str
    thumbnail_path: Optional[str]
    duration_seconds: Optional[int]
    status: VideoStatus
    created_at: datetime
    message: str


class PostRequest(BaseModel):
    """Request to post a video"""
    platforms: List[Platform] = Field(..., description="Platforms to post to")
    scheduled_time: Optional[datetime] = Field(default=None, description="Schedule post for later")
    title: Optional[str] = Field(default=None, description="Override title")
    description: Optional[str] = Field(default=None, description="Override description")
    hashtags: Optional[List[str]] = Field(default=None, description="Override hashtags")


class PostResponse(BaseModel):
    """Response from posting"""
    post_id: int
    platform: Platform
    status: PostStatus
    platform_url: Optional[str]
    scheduled_at: Optional[datetime]
    message: str


class VideoDetail(BaseModel):
    """Detailed video information"""
    id: int
    title: str
    description: Optional[str]
    book: str
    chapter: int
    start_verse: int
    end_verse: Optional[int]
    translation: str
    language: str
    video_path: str
    thumbnail_path: Optional[str]
    duration_seconds: Optional[int]
    resolution: Optional[str]
    file_size_mb: Optional[int]
    tags: List[str]
    hashtags: List[str]
    category: Optional[str]
    status: VideoStatus
    error_message: Optional[str]
    created_at: datetime
    generated_at: Optional[datetime]
    social_posts: List[PostResponse]


class VideoListItem(BaseModel):
    """Video list item"""
    id: int
    title: str
    book: str
    chapter: int
    status: VideoStatus
    duration_seconds: Optional[int]
    created_at: datetime
    post_count: int


class ScheduleRequest(BaseModel):
    """Request to create a schedule"""
    name: str = Field(..., description="Schedule name")
    book: Optional[str] = Field(default=None, description="Bible book (optional)")
    chapter: Optional[int] = Field(default=None, description="Chapter (optional)")
    verses: Optional[str] = Field(default=None, description="Verse range (optional)")
    auto_select: bool = Field(default=True, description="Auto-select passages")
    theme: Optional[str] = Field(default=None, description="Theme filter")
    testament: Optional[str] = Field(default=None, description="Testament filter")
    frequency: str = Field(default="daily", description="Frequency: hourly, daily, weekly")
    schedule_time: str = Field(default="09:00", description="Time in HH:MM")
    timezone: str = Field(default="UTC", description="Timezone")
    max_videos_per_run: int = Field(default=1, description="Max videos per run")
    platforms: List[Platform] = Field(default=[Platform.YOUTUBE], description="Platforms to post to")
    is_active: bool = Field(default=True, description="Whether schedule is active")


class ScheduleResponse(BaseModel):
    """Response from schedule creation"""
    id: int
    name: str
    frequency: str
    schedule_time: str
    is_active: bool
    next_run_at: Optional[datetime]
    created_at: datetime


class AnalyticsSummary(BaseModel):
    """Analytics summary"""
    total_videos: int
    total_posts: int
    total_views: int
    total_likes: int
    total_comments: int
    total_shares: int
    platform_breakdown: Dict[str, Dict[str, int]]
    period: str


class AnalyticsEventModel(BaseModel):
    """Analytics event"""
    event_type: str
    platform: Optional[str]
    metric_name: str
    metric_value: int
    recorded_at: datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
