"""Twitter/X video poster (placeholder for future integration)"""

from src.social_media.base import BaseSocialMediaPoster, PostResult, VideoMetadata
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TwitterPoster(BaseSocialMediaPoster):
    """Twitter/X video poster
    
    NOTE: Twitter posting requires Twitter API v2 with media upload access.
    For now, this is a placeholder.
    """
    
    PLATFORM_NAME = "twitter"
    
    def authenticate(self) -> bool:
        logger.info("Twitter authentication not yet implemented. Placeholder only.")
        return False
    
    def post_video(self, video_path: str, metadata: VideoMetadata) -> PostResult:
        logger.info(
            "Twitter posting is not yet implemented.\n"
            "To enable Twitter posting:\n"
            "1. Apply for Twitter API v2 Elevated access\n"
            "2. Set TWITTER_API_KEY, TWITTER_API_SECRET, etc. in your .env\n"
        )
        return PostResult(
            success=False,
            platform=self.PLATFORM_NAME,
            error_message="Twitter posting not yet implemented."
        )
