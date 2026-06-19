"""API routes for video generation and social media"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from src.database import get_db, init_db, GeneratedVideo, SocialPost, GenerationSchedule
from src.api.models import (
    VideoGenerateRequest, VideoGenerateResponse, VideoDetail, VideoListItem,
    PostRequest, PostResponse, ScheduleRequest, ScheduleResponse,
    AnalyticsSummary, HealthResponse, ErrorResponse
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1")


@router.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()


@router.post("/videos/generate", response_model=VideoGenerateResponse)
async def generate_video(
    request: VideoGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate a video from a Bible passage"""
    try:
        from src.video_generator.generator import VideoGenerator
        from src.nlp_engine.enhancer import ContentEnhancer
        from src.database import VideoStatus
        
        # Create video record
        video = GeneratedVideo(
            title=request.title or f"{request.book} {request.chapter}:{request.verses}",
            book=request.book,
            chapter=request.chapter,
            start_verse=int(request.verses.split("-")[0]) if "-" in request.verses else int(request.verses),
            end_verse=int(request.verses.split("-")[1]) if "-" in request.verses else None,
            language=request.language,
            status=VideoStatus.PROCESSING,
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Generate video
        generator = VideoGenerator()
        video_path = generator.generate(
            book=request.book,
            chapter=request.chapter,
            verses=request.verses,
            language=request.language,
            voice_id=request.voice_id,
        )
        
        # Update video record
        video.video_path = video_path
        video.status = VideoStatus.COMPLETED
        db.commit()
        
        # Auto-post if requested
        if request.auto_post and request.platforms:
            background_tasks.add_task(
                _post_video_task,
                video.id,
                request.platforms,
                None
            )
        
        return VideoGenerateResponse(
            id=video.id,
            title=video.title,
            book=video.book,
            chapter=video.chapter,
            start_verse=video.start_verse,
            end_verse=video.end_verse,
            video_path=video.video_path,
            thumbnail_path=video.thumbnail_path,
            duration_seconds=video.duration_seconds,
            status=video.status,
            created_at=video.created_at,
            message="Video generated successfully",
        )
        
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/videos/{video_id}/post")
async def post_video(
    video_id: int,
    request: PostRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Post a video to social media platforms"""
    video = db.query(GeneratedVideo).filter(GeneratedVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if video.status.value != "completed":
        raise HTTPException(status_code=400, detail="Video not ready for posting")
    
    # Queue posting task
    background_tasks.add_task(
        _post_video_task,
        video_id,
        request.platforms,
        request.scheduled_time.isoformat() if request.scheduled_time else None
    )
    
    return {
        "message": f"Posting scheduled to {len(request.platforms)} platforms",
        "video_id": video_id,
        "platforms": [p.value for p in request.platforms],
    }


@router.get("/videos", response_model=List[VideoListItem])
async def list_videos(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List generated videos"""
    query = db.query(GeneratedVideo)
    
    if status:
        query = query.filter(GeneratedVideo.status == status)
    
    videos = query.order_by(GeneratedVideo.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        VideoListItem(
            id=v.id,
            title=v.title,
            book=v.book,
            chapter=v.chapter,
            status=v.status,
            duration_seconds=v.duration_seconds,
            created_at=v.created_at,
            post_count=len(v.social_posts),
        )
        for v in videos
    ]


@router.get("/videos/{video_id}", response_model=VideoDetail)
async def get_video(video_id: int, db: Session = Depends(get_db)):
    """Get video details"""
    video = db.query(GeneratedVideo).filter(GeneratedVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return VideoDetail(
        id=video.id,
        title=video.title,
        description=video.description,
        book=video.book,
        chapter=video.chapter,
        start_verse=video.start_verse,
        end_verse=video.end_verse,
        translation=video.translation,
        language=video.language,
        video_path=video.video_path,
        thumbnail_path=video.thumbnail_path,
        duration_seconds=video.duration_seconds,
        resolution=video.resolution,
        file_size_mb=video.file_size_mb,
        tags=video.tags or [],
        hashtags=video.hashtags or [],
        category=video.category,
        status=video.status,
        error_message=video.error_message,
        created_at=video.created_at,
        generated_at=video.generated_at,
        social_posts=[
            PostResponse(
                post_id=p.id,
                platform=p.platform,
                status=p.status,
                platform_url=p.platform_url,
                scheduled_at=p.scheduled_at,
                message="Posted" if p.status.value == "posted" else "Pending",
            )
            for p in video.social_posts
        ],
    )


@router.post("/schedules", response_model=ScheduleResponse)
async def create_schedule(
    request: ScheduleRequest,
    db: Session = Depends(get_db)
):
    """Create a generation schedule"""
    try:
        from src.scheduler.task_scheduler import TaskScheduler
        
        scheduler = TaskScheduler()
        result = scheduler.schedule_generation(
            frequency=request.frequency,
            time=request.schedule_time,
            max_videos=request.max_videos_per_run,
            name=request.name,
        )
        
        return ScheduleResponse(
            id=result["id"],
            name=result["name"],
            frequency=result["frequency"],
            schedule_time=result["time"],
            is_active=True,
            next_run_at=result["next_run"],
            created_at=result.get("created_at", __import__("datetime").datetime.utcnow()),
        )
        
    except Exception as e:
        logger.error(f"Schedule creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules")
async def list_schedules(db: Session = Depends(get_db)):
    """List all schedules"""
    from src.scheduler.task_scheduler import TaskScheduler
    
    scheduler = TaskScheduler()
    return scheduler.get_schedules()


@router.get("/analytics/summary")
async def get_analytics_summary(
    period: str = "week",
    db: Session = Depends(get_db)
):
    """Get analytics summary"""
    from src.analytics.dashboard import AnalyticsDashboard
    
    dashboard = AnalyticsDashboard()
    return dashboard.get_summary(period)


@router.get("/analytics/videos/{video_id}")
async def get_video_analytics(video_id: int, db: Session = Depends(get_db)):
    """Get analytics for a specific video"""
    from src.analytics.dashboard import AnalyticsDashboard
    
    dashboard = AnalyticsDashboard()
    return dashboard.get_video_performance(video_id)


def _post_video_task(video_id: int, platforms: List, scheduled_time: Optional[str]):
    """Background task to post video"""
    try:
        from src.api.tasks import post_video_to_platforms
        post_video_to_platforms.delay(
            video_id=video_id,
            platforms=[p.value for p in platforms],
            scheduled_time=scheduled_time,
        )
    except Exception as e:
        logger.error(f"Failed to queue post task: {e}")
