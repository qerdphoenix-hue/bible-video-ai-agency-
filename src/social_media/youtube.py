"""YouTube video uploader using Data API v3"""

import os
import time
from pathlib import Path
from typing import Optional, Dict

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from src.social_media.base import BaseSocialMediaPoster, PostResult, VideoMetadata
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class YouTubePoster(BaseSocialMediaPoster):
    """YouTube video poster using Data API v3"""
    
    PLATFORM_NAME = "youtube"
    
    # OAuth scopes needed for YouTube upload
    SCOPES = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.readonly",
    ]
    
    # API service name and version
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"
    
    def __init__(self):
        super().__init__()
        self.credentials: Optional[Credentials] = None
        self.service = None
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """Authenticate with YouTube API using OAuth2
        
        Returns:
            True if authenticated successfully
        """
        try:
            # Check for existing token
            token_path = Path("data/tokens/youtube_token.json")
            token_path.parent.mkdir(parents=True, exist_ok=True)
            
            if token_path.exists():
                self.credentials = Credentials.from_authorized_user_file(
                    str(token_path), self.SCOPES
                )
            
            # Refresh if expired
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            
            # If no valid credentials, need to authenticate
            if not self.credentials or not self.credentials.valid:
                client_secrets = settings.youtube_client_secrets_file
                
                if not client_secrets or not Path(client_secrets).exists():
                    logger.error(
                        f"YouTube client secrets file not found: {client_secrets}\n"
                        "Please download client_secrets.json from Google Cloud Console "
                        "and set YOUTUBE_CLIENT_SECRETS_FILE in your .env"
                    )
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets, self.SCOPES
                )
                self.credentials = flow.run_local_server(port=8080)
                
                # Save token for future use
                with open(token_path, 'w') as token_file:
                    token_file.write(self.credentials.to_json())
            
            # Build the service
            self.service = build(
                self.API_SERVICE_NAME, 
                self.API_VERSION, 
                credentials=self.credentials,
                static_discovery=False
            )
            
            self.authenticated = True
            logger.info("YouTube authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return False
    
    def post_video(self, video_path: str, metadata: VideoMetadata) -> PostResult:
        """Upload a video to YouTube
        
        Args:
            video_path: Path to the video file
            metadata: Video metadata
            
        Returns:
            PostResult with upload status and video URL
        """
        # Validate video
        if not self.validate_video(video_path):
            return PostResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error_message="Video validation failed"
            )
        
        # Authenticate if not already
        if not self.authenticated:
            if not self.authenticate():
                return PostResult(
                    success=False,
                    platform=self.PLATFORM_NAME,
                    error_message="Authentication failed"
                )
        
        try:
            logger.info(f"Uploading video to YouTube: {metadata.title}")
            
            # Build video body
            body = {
                "snippet": {
                    "title": metadata.title,
                    "description": metadata.description,
                    "tags": metadata.tags,
                    "categoryId": metadata.category,
                    "defaultLanguage": metadata.language,
                },
                "status": {
                    "privacyStatus": metadata.privacy_status,
                    "selfDeclaredMadeForKids": metadata.made_for_kids,
                },
            }
            
            # Upload video file
            media = MediaFileUpload(
                video_path,
                mimetype="video/mp4",
                resumable=True
            )
            
            # Execute upload
            request = self.service.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = request.execute()
            
            video_id = response.get("id")
            video_url = f"https://youtube.com/watch?v={video_id}"
            
            logger.info(f"Video uploaded successfully: {video_url}")
            
            # Upload thumbnail if provided
            if metadata.thumbnail_path and Path(metadata.thumbnail_path).exists():
                self._upload_thumbnail(video_id, metadata.thumbnail_path)
            
            return PostResult(
                success=True,
                platform=self.PLATFORM_NAME,
                post_id=video_id,
                url=video_url,
                raw_response=response
            )
            
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            return PostResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error_message=str(e)
            )
    
    def _upload_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Upload thumbnail for a video
        
        Args:
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image
            
        Returns:
            True if successful
        """
        try:
            media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            
            self.service.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()
            
            logger.info(f"Thumbnail uploaded for video {video_id}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to upload thumbnail: {e}")
            return False
    
    def get_video_analytics(self, video_id: str) -> Dict:
        """Get video analytics
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with analytics data
        """
        try:
            # Get video statistics
            response = self.service.videos().list(
                part="statistics",
                id=video_id
            ).execute()
            
            items = response.get("items", [])
            if not items:
                return {}
            
            stats = items[0].get("statistics", {})
            
            return {
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "favorites": int(stats.get("favoriteCount", 0)),
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {}
    
    def update_video_metadata(self, video_id: str, metadata: VideoMetadata) -> bool:
        """Update video metadata after upload
        
        Args:
            video_id: YouTube video ID
            metadata: New metadata
            
        Returns:
            True if successful
        """
        try:
            body = {
                "id": video_id,
                "snippet": {
                    "title": metadata.title,
                    "description": metadata.description,
                    "tags": metadata.tags,
                    "categoryId": metadata.category,
                },
                "status": {
                    "privacyStatus": metadata.privacy_status,
                },
            }
            
            self.service.videos().update(
                part="snippet,status",
                body=body
            ).execute()
            
            logger.info(f"Video metadata updated: {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            return False
