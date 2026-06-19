"""Social media distributor - orchestrates posting to multiple platforms"""

from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

from src.social_media.base import BaseSocialMediaPoster, PostResult, VideoMetadata
from src.social_media.youtube import YouTubePoster
from src.social_media.tiktok import TikTokPoster
from src.social_media.instagram import InstagramPoster
from src.social_media.twitter import TwitterPoster
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MediaDistributor:
    """Distribute videos to multiple social media platforms"""
    
    PLATFORM_MAP = {
        "youtube": YouTubePoster,
        "tiktok": TikTokPoster,
        "instagram": InstagramPoster,
        "twitter": TwitterPoster,
    }
    
    def __init__(self):
        self.posters: Dict[str, BaseSocialMediaPoster] = {}
        self.logger = get_logger(self.__class__.__name__)
    
    def get_poster(self, platform: str) -> Optional[BaseSocialMediaPoster]:
        """Get or create a poster for a platform"""
        if platform not in self.posters:
            poster_class = self.PLATFORM_MAP.get(platform)
            if poster_class:
                self.posters[platform] = poster_class()
        return self.posters.get(platform)
    
    def post(self, platform: str, video_path: str, metadata: VideoMetadata,
             scheduled_time: Optional[str] = None) -> PostResult:
        """Post a video to a single platform
        
        Args:
            platform: Platform name (youtube, tiktok, etc.)
            video_path: Path to video file
            metadata: Video metadata
            scheduled_time: Optional scheduled time
            
        Returns:
            PostResult
        """
        poster = self.get_poster(platform)
        
        if not poster:
            logger.error(f"Unknown platform: {platform}")
            return PostResult(
                success=False,
                platform=platform,
                error_message=f"Unknown platform: {platform}"
            )
        
        logger.info(f"Posting to {platform}: {metadata.title}")
        
        if scheduled_time:
            return poster.schedule_post(video_path, metadata, scheduled_time)
        
        return poster.post_video(video_path, metadata)
    
    def post_to_multiple(self, platforms: List[str], video_path: str,
                         metadata: VideoMetadata,
                         scheduled_time: Optional[str] = None) -> Dict[str, PostResult]:
        """Post to multiple platforms
        
        Args:
            platforms: List of platform names
            video_path: Path to video file
            metadata: Video metadata
            scheduled_time: Optional scheduled time
            
        Returns:
            Dictionary mapping platform name to PostResult
        """
        results = {}
        
        for platform in platforms:
            result = self.post(platform, video_path, metadata, scheduled_time)
            results[platform] = result
            
            if result.success:
                logger.info(f"✅ Posted to {platform}: {result.url}")
            else:
                logger.error(f"❌ Failed to post to {platform}: {result.error_message}")
        
        return results
    
    def get_platform_status(self) -> Dict[str, bool]:
        """Get authentication status for all platforms"""
        status = {}
        
        for platform_name, poster_class in self.PLATFORM_MAP.items():
            poster = self.get_poster(platform_name)
            if poster:
                try:
                    status[platform_name] = poster.authenticate()
                except Exception as e:
                    logger.warning(f"{platform_name} auth check failed: {e}")
                    status[platform_name] = False
            else:
                status[platform_name] = False
        
        return status
