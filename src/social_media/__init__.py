"""Social media module"""

from src.social_media.base import BaseSocialMediaPoster, PostResult, VideoMetadata
from src.social_media.distributor import MediaDistributor
from src.social_media.youtube import YouTubePoster
from src.social_media.tiktok import TikTokPoster
from src.social_media.instagram import InstagramPoster
from src.social_media.twitter import TwitterPoster

__all__ = [
    "BaseSocialMediaPoster",
    "PostResult",
    "VideoMetadata",
    "MediaDistributor",
    "YouTubePoster",
    "TikTokPoster",
    "InstagramPoster",
    "TwitterPoster",
]