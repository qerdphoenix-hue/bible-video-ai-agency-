#!/usr/bin/env python
"""
Bible Video AI Agency - CLI Entry Point

Provides command-line interface for:
- Generating videos from Bible passages
- Posting videos to social media
- Scheduling video generation
- Viewing analytics
"""

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
@click.option('--verses', required=True, help='Verse range (e.g., 3:16-18 or 16)')
@click.option('--language', default='en', help='Language code (default: en)')
@click.option('--voice-id', default='default', help='Voice ID for narration')
@click.option('--output', default='data/generated_videos', help='Output directory')
def generate(book, chapter, verses, language, voice_id, output):
    """Generate a video from a Bible passage"""
    click.echo(f"🎬 Generating video for {book} {chapter}:{verses}...")
    click.echo(f"Language: {language}")
    click.echo(f"Voice: {voice_id}")
    click.echo(f"Output: {output}")
    
    try:
        # Import video generator
        from video_generator.generator import VideoGenerator
        
        generator = VideoGenerator()
        video_path = generator.generate(
            book=book,
            chapter=chapter,
            verses=verses,
            language=language,
            voice_id=voice_id,
            output_dir=output
        )
        
        click.echo(click.style(f"✅ Video generated successfully: {video_path}", fg='green'))
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.option('--book', required=True, help='Bible book name')
@click.option('--chapter', type=int, required=True, help='Chapter number')
@click.option('--verses', required=True, help='Verse range')
@click.option('--platforms', default='youtube,tiktok,instagram', 
              help='Comma-separated list of platforms')
@click.option('--scheduled-time', help='ISO format datetime for scheduling')
@click.option('--language', default='en', help='Language code')
def generate_and_post(book, chapter, verses, platforms, scheduled_time, language):
    """Generate a video and post it to social media platforms"""
    platform_list = [p.strip() for p in platforms.split(',')]
    
    click.echo(f"🎬 Generating and posting video for {book} {chapter}:{verses}...")
    click.echo(f"Platforms: {', '.join(platform_list)}")
    if scheduled_time:
        click.echo(f"Scheduled for: {scheduled_time}")
    
    try:
        # Import generators
        from video_generator.generator import VideoGenerator
        from social_media.distributor import MediaDistributor
        
        # Generate video
        generator = VideoGenerator()
        video_path = generator.generate(
            book=book,
            chapter=chapter,
            verses=verses,
            language=language
        )
        
        click.echo(f"✅ Video generated: {video_path}")
        
        # Post to platforms
        distributor = MediaDistributor()
        for platform in platform_list:
            click.echo(f"📤 Posting to {platform}...")
            distributor.post(
                platform=platform,
                video_path=video_path,
                scheduled_time=scheduled_time
            )
            click.echo(click.style(f"✅ Posted to {platform}", fg='green'))
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.option('--frequency', type=click.Choice(['daily', 'weekly', 'hourly']), 
              default='daily', help='Scheduling frequency')
@click.option('--time', default='09:00', help='Time in HH:MM format')
@click.option('--max-videos', type=int, default=3, help='Max videos per period')
def schedule(frequency, time, max_videos):
    """Schedule automated video generation"""
    click.echo(f"📅 Scheduling video generation...")
    click.echo(f"Frequency: {frequency}")
    click.echo(f"Time: {time}")
    click.echo(f"Max videos: {max_videos}")
    
    try:
        from scheduler.task_scheduler import TaskScheduler
        
        scheduler = TaskScheduler()
        scheduler.schedule_generation(
            frequency=frequency,
            time=time,
            max_videos=max_videos
        )
        
        click.echo(click.style("✅ Scheduler configured successfully", fg='green'))
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.option('--period', type=click.Choice(['today', 'week', 'month', 'all']), 
              default='week', help='Time period')
@click.option('--platform', help='Specific platform to analyze')
def analytics(period, platform):
    """View video performance analytics"""
    click.echo(f"📊 Fetching analytics...")
    click.echo(f"Period: {period}")
    if platform:
        click.echo(f"Platform: {platform}")
    
    try:
        from analytics.dashboard import Analytics
        
        analytics_engine = Analytics()
        stats = analytics_engine.get_stats(period=period, platform=platform)
        
        click.echo("\n" + "="*50)
        click.echo("📈 Performance Metrics")
        click.echo("="*50)
        
        for key, value in stats.items():
            click.echo(f"{key}: {value}")
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
def serve():
    """Start the FastAPI server"""
    import uvicorn
    
    click.echo("🚀 Starting Bible Video AI Agency API server...")
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == '__main__':
    cli()