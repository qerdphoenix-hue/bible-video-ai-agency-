"""Instagram video poster (placeholder for future integration)"""

from src.social_media.base import BaseSocialMediaPoster, PostResult, VideoMetadata
from src.utils.logger import get_logger

logger = get_logger(__name__)


class InstagramPoster(BaseSocialMediaPoster):
    """Instagram video poster
    
    NOTE: Instagram posting requires:
    1. Instagram Graph API (for Business/Creator accounts) - requires Facebook app
    2. Meta Business Suite API
    
    For now, this is a placeholder that logs the action.
    """
    
    PLATFORM_NAME = "instagram"
    
    def __init__(self):
        super().__init__()
        self.access_token = None
        self.account_id = None
    
    def authenticate(self) -> bool:
        """Authenticate with Instagram Graph API"""
        logger.info("Instagram authentication not yet implemented. Placeholder only.")
        return False
    
    def post_video(self, video_path: str, metadata: VideoMetadata) -> PostResult:
        """Post video to Instagram"""
        logger.info(
            "Instagram posting is not yet implemented.\n"
            "To enable Instagram posting:\n"
            "1. Create a Facebook app with Instagram Graph API product\n"
            "2. Get a Business/Creator Instagram account\n"
            "3. Set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID in your .env\n"
            "4. We will then implement the full upload flow."
        )
        
        return PostResult(
            success=False,
            platform=self.PLATFORM_NAME,
            error_message="Instagram posting not yet implemented. See logs for setup instructions."
        )
