"""TikTok video poster (placeholder for future integration)"""

from src.social_media.base import BaseSocialMediaPoster, PostResult, VideoMetadata
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TikTokPoster(BaseSocialMediaPoster):
    """TikTok video poster
    
    NOTE: TikTok posting requires either:
    1. TikTok for Business API ( Content Publishing API ) - requires approved developer account
    2. TikTok Login Kit + Video Upload API
    3. Web scraping approach (not recommended, against ToS)
    
    For now, this is a placeholder that logs the action.
    Full implementation will be added in a future iteration.
    """
    
    PLATFORM_NAME = "tiktok"
    
    def __init__(self):
        super().__init__()
        self.access_token = None
        self.open_id = None
    
    def authenticate(self) -> bool:
        """Authenticate with TikTok API
        
        NOTE: Full implementation requires TikTok developer approval.
        """
        logger.info("TikTok authentication not yet implemented. Placeholder only.")
        return False
    
    def post_video(self, video_path: str, metadata: VideoMetadata) -> PostResult:
        """Post video to TikTok
        
        NOTE: Placeholder implementation. Will be completed when TikTok API access is available.
        """
        logger.info(
            "TikTok posting is not yet implemented.\n"
            "To enable TikTok posting:\n"
            "1. Apply for TikTok for Business API access at developers.tiktok.com\n"
            "2. Get approved for the Content Publishing API\n"
            "3. Set TIKTOK_ACCESS_TOKEN and TIKTOK_OPEN_ID in your .env\n"
            "4. We will then implement the full upload flow."
        )
        
        return PostResult(
            success=False,
            platform=self.PLATFORM_NAME,
            error_message="TikTok posting not yet implemented. See logs for setup instructions."
        )
