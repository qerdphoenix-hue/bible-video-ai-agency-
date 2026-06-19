"""Base social media poster interface"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)


class PostStatus(str, Enum):
    """Post status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    POSTING = "posting"
    POSTED = "posted"
    FAILED = "failed"


@dataclass
class PostResult:
    """Result of a social media post"""
    success: bool
    platform: str
    post_id: Optional[str] = None
    url: Optional[str] = None
    scheduled_time: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict] = None


@dataclass
class VideoMetadata:
    """Metadata for video posting"""
    title: str
    description: str
    tags: List[str]
    category: str = "22"  # YouTube default: People & Blogs
    privacy_status: str = "public"  # public, unlisted, private
    made_for_kids: bool = False
    language: str = "en"
    thumbnail_path: Optional[str] = None


class BaseSocialMediaPoster(ABC):
    """Abstract base class for social media posting"""
    
    PLATFORM_NAME: str = "base"
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform API
        
        Returns:
            True if authenticated successfully
        """
        pass
    
    @abstractmethod
    def post_video(self, video_path: str, metadata: VideoMetadata) -> PostResult:
        """Post a video to the platform
        
        Args:
            video_path: Path to the video file
            metadata: Video metadata (title, description, tags, etc.)
            
        Returns:
            PostResult with success status and platform-specific info
        """
        pass
    
    def validate_video(self, video_path: str) -> bool:
        """Validate video file before posting
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if video is valid for posting
        """
        path = Path(video_path)
        
        if not path.exists():
            self.logger.error(f"Video file not found: {video_path}")
            return False
        
        # Check file size (most platforms have limits)
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 2048:  # 2GB limit for most platforms
            self.logger.error(f"Video too large: {size_mb:.1f} MB")
            return False
        
        # Check file extension
        valid_extensions = {'.mp4', '.mov', '.avi', '.wmv', '.flv', '.webm'}
        if path.suffix.lower() not in valid_extensions:
            self.logger.error(f"Invalid video format: {path.suffix}")
            return False
        
        self.logger.info(f"Video validated: {path.name} ({size_mb:.1f} MB)")
        return True
    
    def schedule_post(self, video_path: str, metadata: VideoMetadata, 
                      scheduled_time: str) -> PostResult:
        """Schedule a video post for later
        
        Args:
            video_path: Path to video file
            metadata: Video metadata
            scheduled_time: ISO format datetime string
            
        Returns:
            PostResult
        """
        # Default implementation: just log and return scheduled status
        self.logger.info(f"Scheduling post for {scheduled_time}")
        return PostResult(
            success=True,
            platform=self.PLATFORM_NAME,
            scheduled_time=scheduled_time,
            raw_response={"scheduled": True}
        )
