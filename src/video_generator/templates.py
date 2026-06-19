"""Video templates for Bible passages"""

import random
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ColorClip, ImageClip, TextClip, CompositeVideoClip
)

from src.bible_processor.models import PassageSegment
from src.video_generator.effects import VideoEffects
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VideoTemplate:
    """Video templates for different styles"""
    
    def __init__(self, config=None):
        self.config = config
        self.effects = VideoEffects()
        self.width = getattr(config, 'width', 1080) if config else 1080
        self.height = getattr(config, 'height', 1920) if config else 1920
        
    def create_background(self, segment: PassageSegment, index: int) -> ColorClip:
        """Create background clip for a segment"""
        # Generate gradient or solid color background
        bg_type = getattr(self.config, 'background_type', 'gradient') if self.config else 'gradient'
        
        if bg_type == "gradient":
            return self.effects.create_gradient_background(self.width, self.height, index)
        elif bg_type == "image":
            return self._create_image_background(index)
        else:
            return ColorClip(size=(self.width, self.height), color=(0, 0, 0))
    
    def create_text_overlay(self, segment: PassageSegment, size: Tuple[int, int]) -> CompositeVideoClip:
        """Create text overlay for a segment"""
        text = segment.text
        reference = segment.reference
        
        # Main text clip
        font_size = min(80, max(40, int(2000 / max(len(text) / 10, 1))))
        
        text_clip = TextClip(
            text,
            fontsize=font_size,
            color="white",
            font="Arial-Bold",
            method="caption",
            size=(self.width - 100, None),
            align="center",
            stroke_color="black",
            stroke_width=2
        )
        
        # Reference text clip
        ref_clip = TextClip(
            reference,
            fontsize=50,
            color="gold",
            font="Arial",
            align="center"
        )
        
        # Position text
        text_y = self.height // 2 - text_clip.h // 2
        ref_y = text_y - ref_clip.h - 40
        
        text_clip = text_clip.set_position(("center", text_y))
        ref_clip = ref_clip.set_position(("center", ref_y))
        
        # Create composite
        composite = CompositeVideoClip([
            ColorClip(size=(self.width, self.height), color=(0, 0, 0, 0)).set_duration(1),
            text_clip,
            ref_clip
        ], size=(self.width, self.height))
        
        return composite
    
    def create_title_card(self, title: str, duration: float = 3.0) -> CompositeVideoClip:
        """Create title card clip"""
        # Background
        bg = ColorClip(size=(self.width, self.height), color=(20, 20, 40))
        bg = bg.set_duration(duration)
        
        # Title text
        title_clip = TextClip(
            title,
            fontsize=120,
            color="gold",
            font="Arial-Bold",
            align="center",
            stroke_color="black",
            stroke_width=3
        )
        title_clip = title_clip.set_position("center").set_duration(duration)
        
        # Subtitle
        subtitle = TextClip(
            "Bible Scripture",
            fontsize=50,
            color="white",
            font="Arial",
            align="center"
        )
        subtitle = subtitle.set_position(("center", self.height // 2 + 100)).set_duration(duration)
        
        return CompositeVideoClip([bg, title_clip, subtitle])
    
    def create_outro(self, duration: float = 3.0) -> CompositeVideoClip:
        """Create outro clip"""
        bg = ColorClip(size=(self.width, self.height), color=(20, 20, 40))
        bg = bg.set_duration(duration)
        
        text = TextClip(
            "Like & Subscribe\nFor Daily Bible Verses",
            fontsize=70,
            color="white",
            font="Arial-Bold",
            align="center",
            method="caption",
            size=(self.width - 100, None)
        )
        text = text.set_position("center").set_duration(duration)
        
        return CompositeVideoClip([bg, text])
    
    def _create_image_background(self, index: int) -> ImageClip:
        """Create background from image"""
        bg_dir = Path(settings.background_images_dir)
        
        if bg_dir.exists():
            images = list(bg_dir.glob("*.jpg")) + list(bg_dir.glob("*.png"))
            if images:
                img_path = random.choice(images)
                clip = ImageClip(str(img_path))
                clip = clip.resize(height=self.height)
                return clip
        
        # Fallback to gradient
        return self.effects.create_gradient_background(self.width, self.height, index)
