"""Task scheduler for automated video generation"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
from dataclasses import dataclass

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.database import SessionLocal, GenerationSchedule
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TaskScheduler:
    """Schedule and manage automated video generation tasks"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.logger = get_logger(self.__class__.__name__)
    
    def schedule_generation(self, frequency: str, time: str, max_videos: int = 3,
                           name: str = "Auto Generation") -> Dict:
        """Schedule automated video generation
        
        Args:
            frequency: 'hourly', 'daily', 'weekly'
            time: Time in HH:MM format (for daily/weekly)
            max_videos: Max videos per run
            name: Schedule name
            
        Returns:
            Schedule configuration dict
        """
        try:
            hour, minute = map(int, time.split(':'))
        except ValueError:
            hour, minute = 9, 0
        
        # Create trigger based on frequency
        if frequency == "hourly":
            trigger = IntervalTrigger(hours=1)
            next_run = datetime.now() + timedelta(hours=1)
        elif frequency == "daily":
            trigger = CronTrigger(hour=hour, minute=minute)
            next_run = datetime.now().replace(hour=hour, minute=minute, second=0)
            if next_run < datetime.now():
                next_run += timedelta(days=1)
        elif frequency == "weekly":
            trigger = CronTrigger(day_of_week="mon", hour=hour, minute=minute)
            next_run = datetime.now() + timedelta(days=7)
        else:
            trigger = IntervalTrigger(hours=24)
            next_run = datetime.now() + timedelta(hours=24)
        
        # Add job to scheduler
        job_id = f"generation_{name.lower().replace(' ', '_')}"
        self.scheduler.add_job(
            func=self._run_generation,
            trigger=trigger,
            id=job_id,
            name=name,
            kwargs={"max_videos": max_videos},
            replace_existing=True
        )
        
        # Save to database
        db = SessionLocal()
        try:
            schedule = GenerationSchedule(
                name=name,
                frequency=frequency,
                schedule_time=time,
                max_videos_per_run=max_videos,
                is_active=True,
                next_run_at=next_run
            )
            db.add(schedule)
            db.commit()
            db.refresh(schedule)
            
            self.logger.info(f"Scheduled '{name}': {frequency} at {time}, max {max_videos} videos")
            
            return {
                "id": schedule.id,
                "name": name,
                "frequency": frequency,
                "time": time,
                "max_videos": max_videos,
                "next_run": next_run.isoformat(),
                "job_id": job_id,
            }
        finally:
            db.close()
    
    def _run_generation(self, max_videos: int = 3):
        """Run generation task (called by scheduler)"""
        self.logger.info(f"Running scheduled generation: max {max_videos} videos")
        
        # This will be called by Celery in production
        # For now, log the event
        try:
            from src.api.tasks import generate_scheduled_videos
            generate_scheduled_videos.delay(max_videos=max_videos)
        except Exception as e:
            self.logger.error(f"Failed to trigger generation: {e}")
    
    def get_schedules(self) -> List[Dict]:
        """Get all active schedules"""
        db = SessionLocal()
        try:
            schedules = db.query(GenerationSchedule).filter(
                GenerationSchedule.is_active == True
            ).all()
            
            return [
                {
                    "id": s.id,
                    "name": s.name,
                    "frequency": s.frequency,
                    "time": s.schedule_time,
                    "max_videos": s.max_videos_per_run,
                    "next_run": s.next_run_at.isoformat() if s.next_run_at else None,
                    "last_run": s.last_run_at.isoformat() if s.last_run_at else None,
                }
                for s in schedules
            ]
        finally:
            db.close()
    
    def remove_schedule(self, schedule_id: int) -> bool:
        """Remove a schedule"""
        db = SessionLocal()
        try:
            schedule = db.query(GenerationSchedule).filter(
                GenerationSchedule.id == schedule_id
            ).first()
            
            if not schedule:
                return False
            
            # Remove from scheduler
            job_id = f"generation_{schedule.name.lower().replace(' ', '_')}"
            try:
                self.scheduler.remove_job(job_id)
            except Exception:
                pass
            
            # Deactivate in database
            schedule.is_active = False
            db.commit()
            
            self.logger.info(f"Removed schedule: {schedule.name}")
            return True
            
        finally:
            db.close()
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        self.logger.info("Scheduler shutdown")
