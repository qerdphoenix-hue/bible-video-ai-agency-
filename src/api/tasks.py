"""Celery tasks for async video generation and posting"""

from celery import Celery
from typing import List, Optional

from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize Celery app
celery_app = Celery(
    "bible_video_ai",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.api.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, max_retries=3)
def generate_video_task(self, book: str, chapter: int, verses: str,
                        language: str = "en", voice_id: Optional[str] = None):
    """Celery task to generate a video"""
    try:
        from src.video_generator.generator import VideoGenerator
        from src.database import SessionLocal, GeneratedVideo, VideoStatus
        
        logger.info(f"Generating video: {book} {chapter}:{verses}")
        
        generator = VideoGenerator()
        video_path = generator.generate(
            book=book,
            chapter=chapter,
            verses=verses,
            language=language,
            voice_id=voice_id,
        )
        
        return {
            "status": "success",
            "video_path": video_path,
            "book": book,
            "chapter": chapter,
            "verses": verses,
        }
        
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        self.retry(countdown=60, exc=e)


@celery_app.task(bind=True, max_retries=3)
def post_video_to_platforms(self, video_id: int, platforms: List[str],
                            scheduled_time: Optional[str] = None):
    """Celery task to post video to multiple platforms"""
    try:
        from src.database import SessionLocal, GeneratedVideo, SocialPost, PostStatus, Platform
        from src.social_media.distributor import MediaDistributor
        from src.nlp_engine.enhancer import ContentEnhancer
        from src.social_media.base import VideoMetadata
        
        db = SessionLocal()
        
        try:
            video = db.query(GeneratedVideo).filter(GeneratedVideo.id == video_id).first()
            if not video:
                raise ValueError(f"Video {video_id} not found")
            
            # Enhance content
            enhancer = ContentEnhancer()
            from src.bible_processor.models import Passage
            passage = Passage(
                book=video.book,
                chapter=video.chapter,
                start_verse=video.start_verse,
                end_verse=video.end_verse,
            )
            enhancement = enhancer.enhance(passage)
            
            # Create metadata
            metadata = VideoMetadata(
                title=enhancement.title,
                description=enhancement.description,
                tags=enhancement.tags,
                category="22",
                privacy_status="public",
            )
            
            # Post to platforms
            distributor = MediaDistributor()
            results = distributor.post_to_multiple(
                platforms=platforms,
                video_path=video.video_path,
                metadata=metadata,
                scheduled_time=scheduled_time,
            )
            
            # Record results in database
            for platform_name, result in results.items():
                post = SocialPost(
                    video_id=video_id,
                    platform=Platform(platform_name),
                    title=enhancement.title,
                    description=enhancement.description,
                    hashtags=enhancement.hashtags,
                    status=PostStatus.POSTED if result.success else PostStatus.FAILED,
                    platform_post_id=result.post_id,
                    platform_url=result.url,
                    error_message=result.error_message,
                )
                db.add(post)
            
            db.commit()
            
            return {
                "status": "success",
                "video_id": video_id,
                "results": {k: v.success for k, v in results.items()},
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Posting failed: {e}")
        self.retry(countdown=60, exc=e)


@celery_app.task
def generate_scheduled_videos(max_videos: int = 3):
    """Generate videos on a schedule"""
    try:
        from src.video_generator.generator import VideoGenerator
        from src.database import SessionLocal, GeneratedVideo, VideoStatus
        
        logger.info(f"Running scheduled generation: max {max_videos} videos")
        
        # For now, generate from a random popular passage
        # In production, this would use a queue/rotation system
        popular_passages = [
            ("John", 3, "16"),
            ("Psalm", 23, "1-4"),
            ("Jeremiah", 29, "11"),
            ("Romans", 8, "28"),
            ("Philippians", 4, "13"),
            ("Proverbs", 3, "5-6"),
            ("Isaiah", 41, "10"),
            ("Matthew", 6, "33"),
        ]
        
        generator = VideoGenerator()
        generated = []
        
        for book, chapter, verses in popular_passages[:max_videos]:
            try:
                video_path = generator.generate(
                    book=book,
                    chapter=chapter,
                    verses=verses,
                )
                generated.append({
                    "book": book,
                    "chapter": chapter,
                    "verses": verses,
                    "path": video_path,
                })
            except Exception as e:
                logger.error(f"Failed to generate {book} {chapter}:{verses}: {e}")
                continue
        
        return {
            "status": "success",
            "generated_count": len(generated),
            "videos": generated,
        }
        
    except Exception as e:
        logger.error(f"Scheduled generation failed: {e}")
        raise


@celery_app.task
def update_analytics():
    """Update analytics from social media platforms"""
    try:
        from src.analytics.dashboard import AnalyticsDashboard
        from src.database import SessionLocal, SocialPost
        from src.social_media.youtube import YouTubePoster
        
        db = SessionLocal()
        dashboard = AnalyticsDashboard()
        
        try:
            # Get YouTube posts
            youtube_posts = db.query(SocialPost).filter(
                SocialPost.platform == "youtube",
                SocialPost.status == "posted",
            ).all()
            
            youtube = YouTubePoster()
            if youtube.authenticate():
                for post in youtube_posts:
                    if post.platform_post_id:
                        stats = youtube.get_video_analytics(post.platform_post_id)
                        post.views = stats.get("views", 0)
                        post.likes = stats.get("likes", 0)
                        post.comments = stats.get("comments", 0)
                        
                        # Record event
                        dashboard.record_event(
                            event_type="analytics_update",
                            platform="youtube",
                            video_id=post.video_id,
                            metric_name="views",
                            metric_value=stats.get("views", 0),
                        )
                
                db.commit()
            
            return {"status": "success", "updated_posts": len(youtube_posts)}
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Analytics update failed: {e}")
        raise
