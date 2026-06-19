"""Visual effects and transitions for video generation"""

import random
from typing import Tuple

import numpy as np
from moviepy.editor import ColorClip, ImageClip
from moviepy.video.fx.all import fadein, fadeout
from PIL import Image, ImageDraw

from src.utils.logger import get_logger

logger = get_logger(__name__)


class VideoEffects:
    """Video effects and transitions"""
    
    def __init__(self):
        self.fade_duration = 1.0
    
    def apply_segment_effects(self, clip, index: int):
        """Apply effects to a segment clip"""
        # Apply fade in for first segment, fade out for last
        clip = fadein(clip, self.fade_duration)
        clip = fadeout(clip, self.fade_duration)
        return clip
    
    def create_gradient_background(self, width: int, height: int, index: int) -> ColorClip:
        """Create a gradient background"""
        # Generate random but pleasing gradient colors
        base_colors = [
            (15, 30, 60),   # Deep blue
            (40, 15, 60),   # Deep purple
            (15, 40, 30),   # Deep green
            (60, 30, 15),   # Deep orange
            (30, 15, 15),   # Deep red
            (15, 30, 45),   # Teal
            (45, 15, 30),   # Maroon
        ]
        
        # Use index to select consistent colors for the same segment
        color1 = base_colors[index % len(base_colors)]
        color2 = base_colors[(index + 1) % len(base_colors)]
        
        # Create gradient image
        gradient = self._create_gradient_image(width, height, color1, color2)
        
        # Convert to numpy array for MoviePy
        img_array = np.array(gradient)
        clip = ImageClip(img_array)
        
        return clip
    
    def _create_gradient_image(self, width: int, height: int, 
                                color1: Tuple[int, int, int], 
                                color2: Tuple[int, int, int]) -> Image.Image:
        """Create a gradient image using PIL"""
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        for y in range(height):
            # Interpolate between colors
            ratio = y / height
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return image
    
    def create_text_shadow(self, text_clip, offset: int = 3):
        """Create shadow effect for text (placeholder)"""
        # In a full implementation, this would create a shadow behind text
        # For now, we use stroke in TextClip which is simpler
        return text_clip
    
    def add_ken_burns_effect(self, image_clip, duration: float):
        """Add Ken Burns effect to image (slow zoom)"""
        # This would zoom and pan over the image
        # Implementation requires more complex MoviePy transforms
        return image_clip
