"""Video generation using MoviePy and AI voiceovers"""

import os
import random
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass

import numpy as np
from moviepy.editor import (
    CompositeVideoClip, AudioFileClip, TextClip, ColorClip,
    concatenate_videoclips, ImageClip
)
from moviepy.video.fx.all import fadein, fadeout
from PIL import Image, ImageDraw, ImageFont

from src.bible_processor.models import Passage, PassageSegment
from src.video_generator.voiceover import VoiceoverGenerator
from src.video_generator.templates import VideoTemplate
from src.video_generator.effects import VideoEffects
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class VideoConfig:
    """Video generation configuration"""
    width: int = 1080
    height: int = 1920
    fps: int = 30
    template: str = "cinematic"
    font_size: int = 60
    font_color: str = "white"
    bg_color: str = "black"
    duration_per_segment: float = 5.0
    fade_duration: float = 1.0
    text_shadow: bool = True
    background_type: str = "gradient"  # gradient, solid, image, video


class VideoGenerator:
    """Main video generator for Bible passages"""
    
    def __init__(self, config: Optional[VideoConfig] = None):
        """Initialize video generator"""
        self.config = config or VideoConfig(
            width=settings.video_width,
            height=settings.video_height,
            fps=settings.video_fps,
            template=settings.video_template
        )
        self.voiceover = VoiceoverGenerator()
        self.template = VideoTemplate(self.config)
        self.effects = VideoEffects()
        self.output_dir = Path(settings.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate(self,
                 book: str,
                 chapter: int,
                 verses: str,
                 language: str = "en",
                 voice_id: Optional[str] = None,
                 output_dir: Optional[str] = None) -> str:
        """Generate a video from a Bible passage
        
        Args:
            book: Bible book name
            chapter: Chapter number
            verses: Verse range (e.g., "16-18" or "16")
            language: Language code
            voice_id: Voice ID for TTS
            output_dir: Output directory
            
        Returns:
            Path to generated video
        """
        from src.bible_processor.parser import BibleParser
        from src.bible_processor.segmenter import PassageSegmenter
        
        logger.info(f"Starting video generation for {book} {chapter}:{verses}")
        
        # Parse verses range
        start_verse, end_verse = self._parse_verse_range(verses)
        
        # Get passage
        parser = BibleParser()
        passage = parser.get_passage(book, chapter, start_verse, end_verse)
        
        if not passage or not passage.verses:
            raise ValueError(f"Could not find passage: {book} {chapter}:{verses}")
        
        # Segment passage
        segmenter = PassageSegmenter(words_per_segment=40)
        segments = segmenter.segment_by_words(passage)
        
        if not segments:
            raise ValueError("No segments generated from passage")
        
        # Generate voiceover
        audio_path = self._generate_audio(passage, segments, voice_id)
        
        # Generate video clips
        video_clips = self._generate_video_clips(segments, audio_path)
        
        # Combine clips
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # Add audio
        if audio_path and Path(audio_path).exists():
            audio = AudioFileClip(audio_path)
            final_video = final_video.set_audio(audio)
        
        # Add intro/outro
        final_video = self._add_intro_outro(final_video, passage)
        
        # Export
        output_path = self._get_output_path(book, chapter, verses, output_dir)
        
        logger.info(f"Exporting video to {output_path}")
        final_video.write_videofile(
            str(output_path),
            fps=self.config.fps,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=str(Path(settings.temp_dir) / f"temp_audio_{book}_{chapter}.mp3"),
            remove_temp=True
        )
        
        # Cleanup
        final_video.close()
        for clip in video_clips:
            clip.close()
        
        logger.info(f"Video generated successfully: {output_path}")
        return str(output_path)
    
    def _parse_verse_range(self, verses: str) -> Tuple[int, int]:
        """Parse verse range string"""
        if "-" in verses:
            parts = verses.split("-")
            return int(parts[0]), int(parts[1])
        return int(verses), int(verses)
    
    def _generate_audio(self, passage: Passage, segments: List[PassageSegment], 
                        voice_id: Optional[str]) -> Optional[str]:
        """Generate voiceover audio"""
        try:
            full_text = passage.full_text
            audio_path = self.voiceover.generate(
                text=full_text,
                voice_id=voice_id,
                output_path=str(Path(settings.temp_dir) / f"voice_{passage.book}_{passage.chapter}.mp3")
            )
            return audio_path
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return None
    
    def _generate_video_clips(self, segments: List[PassageSegment], 
                               audio_path: Optional[str]) -> List:
        """Generate video clips for each segment"""
        clips = []
        
        for i, segment in enumerate(segments):
            # Create background
            bg_clip = self.template.create_background(segment, i)
            
            # Add text overlay
            text_clip = self.template.create_text_overlay(segment, bg_clip.size)
            
            # Composite
            segment_clip = CompositeVideoClip([bg_clip, text_clip])
            
            # Add effects
            segment_clip = self.effects.apply_segment_effects(segment_clip, i)
            
            # Set duration based on segment
            segment_clip = segment_clip.set_duration(segment.duration_seconds)
            
            clips.append(segment_clip)
        
        return clips
    
    def _add_intro_outro(self, video, passage: Passage):
        """Add intro and outro to video"""
        # Intro
        intro_text = f"{passage.book} {passage.chapter}"
        intro_clip = self.template.create_title_card(intro_text, duration=3.0)
        
        # Outro
        outro_text = "Thanks for watching!"
        outro_clip = self.template.create_outro(duration=3.0)
        
        # Combine
        final = concatenate_videoclips([intro_clip, video, outro_clip], method="compose")
        return final
    
    def _get_output_path(self, book: str, chapter: int, verses: str, 
                         output_dir: Optional[str] = None) -> Path:
        """Get output path for video"""
        out_dir = Path(output_dir) if output_dir else self.output_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        
        safe_name = f"{book.replace(' ', '_')}_{chapter}_{verses.replace('-', '_')}"
        return out_dir / f"{safe_name}.mp4"
