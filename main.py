#!/usr/bin/env python
"""Bible Video AI Agency - CLI Entry Point"""

import sys
import logging
from pathlib import Path

import click
from dotenv import load_dotenv

# Add src to path
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Bible Video AI Agency - Generate and share Bible videos with AI"""
    pass


@cli.command()
@click.option('--book', required=True, help='Bible book name (e.g., John, Psalm)')
@click.option('--chapter', type=int, required=True, help='Chapter number')
@click.option('--verses', required=True, help='Verse range (e.g., 16-18 or 16)')
@click.option('--language', default='en', help='Language code (default: en)')
@click.option('--voice-id', default=None, help='Voice ID for narration')
@click.option('--output', default=None, help='Output directory')
@click.option('--template', default='cinematic', help='Video template style')
def generate(book, chapter, verses, language, voice_id, output, template):
    """Generate a video from a Bible passage"""
    click.echo(f"🎬 Generating video for {book} {chapter}:{verses}...")
    
    try:
        from src.video_generator.generator import VideoGenerator, VideoConfig
        
        config = VideoConfig(
            template=template,
        ) if template else None
        
        generator = VideoGenerator(config=config)
        video_path = generator.generate(
            book=book,
            chapter=chapter,
            verses=verses,
            language=language,
            voice_id=voice_id,
            output_dir=output,
        )
        
        click.echo(click.style(f"✅ Video generated: {video_path}", fg='green'))
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.option('--book', required=True, help='Bible book name')
@click.option('--chapter', type=int, required=True, help='Chapter number')
@click.option('--verses', required=True, help='Verse range')
@click.option('--platforms', default='youtube', help='Comma-separated platforms')
@click.option('--scheduled-time', help='ISO datetime for scheduling')
@click.option('--language', default='en', help='Language code')
@click.option('--title', help='Custom video title')
@click.option('--description', help='Custom description')
def generate_and_post(book, chapter, verses, platforms, scheduled_time, language, title, description):
    """Generate a video and post to social media"""
    platform_list = [p.strip().lower() for p in platforms.split(',')]
    
    click.echo(f"🎬 Generating and posting: {book} {chapter}:{verses}")
    click.echo(f"📤 Platforms: {', '.join(platform_list)}")
    
    try:
        from src.video_generator.generator import VideoGenerator
        from src.nlp_engine.enhancer import ContentEnhancer
        from src.social_media.distributor import MediaDistributor
        from src.social_media.base import VideoMetadata
        from src.bible_processor.models import Passage
        
        # Generate video
        generator = VideoGenerator()
        video_path = generator.generate(
            book=book, chapter=chapter, verses=verses, language=language
        )
        click.echo(f"✅ Video generated: {video_path}")
        
        # Enhance content
        enhancer = ContentEnhancer()
        passage = Passage(book=book, chapter=chapter, start_verse=int(verses.split('-')[0]))
        enhancement = enhancer.enhance(passage)
        
        metadata = VideoMetadata(
            title=title or enhancement.title,
            description=description or enhancement.description,
            tags=enhancement.tags,
        )
        
        # Post to platforms
        distributor = MediaDistributor()
        results = distributor.post_to_multiple(
            platforms=platform_list,
            video_path=video_path,
            metadata=metadata,
            scheduled_time=scheduled_time,
        )
        
        for platform, result in results.items():
            if result.success:
                click.echo(click.style(f"✅ {platform}: {result.url}", fg='green'))
            else:
                click.echo(click.style(f"❌ {platform}: {result.error_message}", fg='red'))
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.option('--frequency', type=click.Choice(['daily', 'weekly', 'hourly']), default='daily')
@click.option('--time', default='09:00', help='Time HH:MM')
@click.option('--max-videos', type=int, default=3, help='Max videos per run')
@click.option('--platforms', default='youtube', help='Platforms to post to')
def schedule(frequency, time, max_videos, platforms):
    """Schedule automated video generation"""
    click.echo(f"📅 Scheduling: {frequency} at {time}, max {max_videos} videos")
    
    try:
        from src.scheduler.task_scheduler import TaskScheduler
        
        scheduler = TaskScheduler()
        result = scheduler.schedule_generation(
            frequency=frequency, time=time, max_videos=max_videos
        )
        
        click.echo(click.style(f"✅ Schedule created (ID: {result['id']})", fg='green'))
        click.echo(f"Next run: {result['next_run']}")
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.option('--period', type=click.Choice(['today', 'week', 'month', 'all']), default='week')
@click.option('--platform', help='Filter by platform')
def analytics(period, platform):
    """View video performance analytics"""
    click.echo(f"📊 Analytics for period: {period}")
    
    try:
        from src.analytics.dashboard import AnalyticsDashboard
        
        dashboard = AnalyticsDashboard()
        stats = dashboard.get_summary(period=period)
        
        click.echo("\n" + "=" * 50)
        click.echo("📈 Performance Metrics")
        click.echo("=" * 50)
        click.echo(f"Total Videos: {stats['total_videos']}")
        click.echo(f"Total Posts: {stats['total_posts']}")
        click.echo(f"Total Views: {stats['total_views']:,}")
        click.echo(f"Total Likes: {stats['total_likes']:,}")
        click.echo(f"Total Comments: {stats['total_comments']:,}")
        click.echo(f"Total Shares: {stats['total_shares']:,}")
        
        if stats['platform_breakdown']:
            click.echo("\nPlatform Breakdown:")
            for platform, metrics in stats['platform_breakdown'].items():
                click.echo(f"  {platform}: {metrics['posts']} posts, {metrics['views']:,} views")
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
def serve():
    """Start the FastAPI server"""
    import uvicorn
    
    click.echo("🚀 Starting API server on http://localhost:8000")
    click.echo("📖 API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


@cli.command()
def init():
    """Initialize the database"""
    click.echo("🗄️ Initializing database...")
    
    try:
        from src.database import init_db
        init_db()
        click.echo(click.style("✅ Database initialized", fg='green'))
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.option('--translation', default='KJV', help='Bible translation to load')
def load_bible(translation):
    """Load Bible text data into the system"""
    click.echo(f"📚 Loading Bible data: {translation}")
    
    try:
        from src.bible_data_loader import load_bible_data
        
        result = load_bible_data(translation=translation)
        click.echo(click.style(f"✅ {result}", fg='green'))
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'), err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
