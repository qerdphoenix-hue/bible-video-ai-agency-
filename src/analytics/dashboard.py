"""Analytics dashboard for tracking video performance"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

from sqlalchemy import func

from src.database import SessionLocal, GeneratedVideo, SocialPost, AnalyticsEvent, Platform
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsDashboard:
    """Track and analyze video performance across platforms"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def get_summary(self, period: str = "week") -> Dict:
        """Get overall analytics summary
        
        Args:
            period: 'today', 'week', 'month', 'all'
            
        Returns:
            Summary dictionary with totals and breakdowns
        """
        start_date = self._get_period_start(period)
        
        db = SessionLocal()
        try:
            # Total videos
            total_videos = db.query(GeneratedVideo).filter(
                GeneratedVideo.created_at >= start_date
            ).count()
            
            # Total posts
            total_posts = db.query(SocialPost).filter(
                SocialPost.created_at >= start_date
            ).count()
            
            # Aggregate metrics
            metrics = db.query(
                func.sum(SocialPost.views).label('total_views'),
                func.sum(SocialPost.likes).label('total_likes'),
                func.sum(SocialPost.comments).label('total_comments'),
                func.sum(SocialPost.shares).label('total_shares'),
            ).filter(
                SocialPost.created_at >= start_date
            ).first()
            
            # Platform breakdown
            platform_data = db.query(
                SocialPost.platform,
                func.count(SocialPost.id).label('post_count'),
                func.sum(SocialPost.views).label('views'),
                func.sum(SocialPost.likes).label('likes'),
                func.sum(SocialPost.comments).label('comments'),
                func.sum(SocialPost.shares).label('shares'),
            ).filter(
                SocialPost.created_at >= start_date
            ).group_by(SocialPost.platform).all()
            
            platform_breakdown = {}
            for row in platform_data:
                platform_breakdown[row.platform.value if hasattr(row.platform, 'value') else str(row.platform)] = {
                    "posts": row.post_count or 0,
                    "views": row.views or 0,
                    "likes": row.likes or 0,
                    "comments": row.comments or 0,
                    "shares": row.shares or 0,
                }
            
            return {
                "period": period,
                "total_videos": total_videos,
                "total_posts": total_posts,
                "total_views": metrics.total_views or 0,
                "total_likes": metrics.total_likes or 0,
                "total_comments": metrics.total_comments or 0,
                "total_shares": metrics.total_shares or 0,
                "platform_breakdown": platform_breakdown,
            }
            
        finally:
            db.close()
    
    def get_video_performance(self, video_id: int) -> Dict:
        """Get performance metrics for a specific video
        
        Args:
            video_id: Video ID
            
        Returns:
            Video performance metrics
        """
        db = SessionLocal()
        try:
            video = db.query(GeneratedVideo).filter(
                GeneratedVideo.id == video_id
            ).first()
            
            if not video:
                return {"error": "Video not found"}
            
            posts = db.query(SocialPost).filter(
                SocialPost.video_id == video_id
            ).all()
            
            post_data = []
            for post in posts:
                post_data.append({
                    "platform": post.platform.value if hasattr(post.platform, 'value') else str(post.platform),
                    "status": post.status.value if hasattr(post.status, 'value') else str(post.status),
                    "views": post.views,
                    "likes": post.likes,
                    "comments": post.comments,
                    "shares": post.shares,
                    "url": post.platform_url,
                })
            
            return {
                "video_id": video_id,
                "title": video.title,
                "reference": f"{video.book} {video.chapter}:{video.start_verse}",
                "status": video.status.value if hasattr(video.status, 'value') else str(video.status),
                "duration": video.duration_seconds,
                "created_at": video.created_at.isoformat() if video.created_at else None,
                "posts": post_data,
            }
            
        finally:
            db.close()
    
    def get_top_performing(self, metric: str = "views", limit: int = 10) -> List[Dict]:
        """Get top performing videos by metric
        
        Args:
            metric: Metric to sort by ('views', 'likes', 'comments')
            limit: Number of results
            
        Returns:
            List of top performing videos
        """
        db = SessionLocal()
        try:
            metric_column = getattr(SocialPost, metric, SocialPost.views)
            
            results = db.query(
                GeneratedVideo.id,
                GeneratedVideo.title,
                GeneratedVideo.book,
                GeneratedVideo.chapter,
                func.sum(metric_column).label('total_metric')
            ).join(SocialPost).group_by(
                GeneratedVideo.id
            ).order_by(
                func.sum(metric_column).desc()
            ).limit(limit).all()
            
            return [
                {
                    "id": r.id,
                    "title": r.title,
                    "reference": f"{r.book} {r.chapter}",
                    metric: r.total_metric or 0,
                }
                for r in results
            ]
            
        finally:
            db.close()
    
    def record_event(self, event_type: str, metric_name: str, metric_value: int = 0,
                     platform: Optional[str] = None, video_id: Optional[int] = None,
                     raw_data: Optional[Dict] = None) -> bool:
        """Record an analytics event
        
        Args:
            event_type: Type of event (e.g., 'post', 'view', 'engagement')
            metric_name: Name of metric (e.g., 'views', 'likes')
            metric_value: Metric value
            platform: Platform name
            video_id: Video ID
            raw_data: Raw event data
            
        Returns:
            True if recorded successfully
        """
        db = SessionLocal()
        try:
            event = AnalyticsEvent(
                event_type=event_type,
                platform=platform,
                video_id=video_id,
                metric_name=metric_name,
                metric_value=metric_value,
                raw_data=raw_data,
            )
            db.add(event)
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to record analytics event: {e}")
            return False
            
        finally:
            db.close()
    
    def _get_period_start(self, period: str) -> datetime:
        """Get start date for a period"""
        now = datetime.utcnow()
        
        if period == "today":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            return now - timedelta(days=7)
        elif period == "month":
            return now - timedelta(days=30)
        elif period == "all":
            return datetime.min
        else:
            return now - timedelta(days=7)
