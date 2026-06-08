"""Bible passage segmentation for video content"""

from typing import List, Optional
from dataclasses import dataclass

from src.bible_processor.models import Passage, PassageSegment, Verse
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PassageSegmenter:
    """Segment Bible passages for video generation"""
    
    # Default segment configuration
    DEFAULT_WORDS_PER_SEGMENT = 50  # ~30 seconds of narration
    DEFAULT_SEGMENT_DURATION = 30.0  # seconds
    WORDS_PER_MINUTE = 150  # Average speaking rate
    
    def __init__(self, 
                 words_per_segment: int = DEFAULT_WORDS_PER_SEGMENT,
                 duration_seconds: float = DEFAULT_SEGMENT_DURATION):
        """Initialize segmenter
        
        Args:
            words_per_segment: Target words per segment
            duration_seconds: Duration for each segment in seconds
        """
        self.words_per_segment = words_per_segment
        self.duration_seconds = duration_seconds
    
    def segment_by_verses(self, passage: Passage, verses_per_segment: int = 1) -> List[PassageSegment]:
        """Segment passage by number of verses
        
        Args:
            passage: Passage to segment
            verses_per_segment: Number of verses per segment
            
        Returns:
            List of PassageSegment objects
        """
        segments = []
        
        if not passage.verses or verses_per_segment < 1:
            logger.warning("Cannot segment: no verses or invalid verses_per_segment")
            return segments
        
        for i in range(0, len(passage.verses), verses_per_segment):
            segment_verses = passage.verses[i:i + verses_per_segment]
            
            # Calculate segment duration based on word count
            word_count = len(" ".join([v.text for v in segment_verses]).split())
            duration = self._calculate_duration(word_count)
            
            segment = PassageSegment(
                passage=passage,
                segment_number=len(segments) + 1,
                verses=segment_verses,
                duration_seconds=duration
            )
            segments.append(segment)
            
            logger.debug(f"Created segment {segment}")
        
        return segments
    
    def segment_by_words(self, passage: Passage, 
                        words_per_segment: Optional[int] = None) -> List[PassageSegment]:
        """Segment passage by approximate word count
        
        Args:
            passage: Passage to segment
            words_per_segment: Target words per segment
            
        Returns:
            List of PassageSegment objects
        """
        if words_per_segment is None:
            words_per_segment = self.words_per_segment
        
        segments = []
        current_verses = []
        current_words = 0
        
        if not passage.verses:
            logger.warning("Cannot segment: passage has no verses")
            return segments
        
        for verse in passage.verses:
            verse_words = len(verse.text.split())
            
            # Add verse to current segment or start new one
            if current_words + verse_words <= words_per_segment:
                current_verses.append(verse)
                current_words += verse_words
            else:
                # Save current segment if it has verses
                if current_verses:
                    segment = PassageSegment(
                        passage=passage,
                        segment_number=len(segments) + 1,
                        verses=current_verses,
                        duration_seconds=self._calculate_duration(current_words)
                    )
                    segments.append(segment)
                    logger.debug(f"Created segment {segment}")
                
                # Start new segment
                current_verses = [verse]
                current_words = verse_words
        
        # Add final segment
        if current_verses:
            segment = PassageSegment(
                passage=passage,
                segment_number=len(segments) + 1,
                verses=current_verses,
                duration_seconds=self._calculate_duration(current_words)
            )
            segments.append(segment)
            logger.debug(f"Created segment {segment}")
        
        return segments
    
    def segment_by_duration(self, passage: Passage, 
                           duration_seconds: Optional[float] = None) -> List[PassageSegment]:
        """Segment passage by target duration
        
        Args:
            passage: Passage to segment
            duration_seconds: Target duration per segment
            
        Returns:
            List of PassageSegment objects
        """
        if duration_seconds is None:
            duration_seconds = self.duration_seconds
        
        # Convert duration to approximate word count
        words_per_segment = int((duration_seconds / 60) * self.WORDS_PER_MINUTE)
        return self.segment_by_words(passage, words_per_segment)
    
    def segment_by_themes(self, passage: Passage, themes: List[str]) -> List[PassageSegment]:
        """Segment passage by content themes (if available)
        
        Args:
            passage: Passage to segment
            themes: List of themes to identify
            
        Returns:
            List of PassageSegment objects
        """
        segments = []
        
        # Simple implementation: segment by verses and assign themes
        # In production, this would use NLP to identify theme boundaries
        verse_segments = self.segment_by_verses(passage, verses_per_segment=1)
        
        for i, segment in enumerate(verse_segments):
            # Assign theme based on position (simplified)
            theme_index = min(i, len(themes) - 1) if themes else None
            segment.background_theme = themes[theme_index] if theme_index is not None else None
            segments.append(segment)
        
        return segments
    
    def _calculate_duration(self, word_count: int) -> float:
        """Calculate segment duration based on word count
        
        Args:
            word_count: Number of words
            
        Returns:
            Duration in seconds
        """
        # Average speaking rate is ~150 words per minute
        minutes = word_count / self.WORDS_PER_MINUTE
        seconds = minutes * 60
        
        # Add padding for visual effects
        return max(10.0, min(60.0, seconds + 2.0))
    
    def merge_segments(self, segments: List[PassageSegment], 
                      max_duration: float = 60.0) -> List[PassageSegment]:
        """Merge adjacent segments if they're too short
        
        Args:
            segments: List of segments to merge
            max_duration: Maximum duration to merge to
            
        Returns:
            List of merged PassageSegment objects
        """
        if not segments:
            return []
        
        merged = []
        current_segment = None
        
        for segment in segments:
            if current_segment is None:
                current_segment = PassageSegment(
                    passage=segment.passage,
                    segment_number=1,
                    verses=segment.verses.copy(),
                    duration_seconds=segment.duration_seconds
                )
            else:
                # Check if we can merge
                new_duration = current_segment.duration_seconds + segment.duration_seconds
                
                if new_duration <= max_duration:
                    # Merge
                    current_segment.verses.extend(segment.verses)
                    current_segment.duration_seconds = new_duration
                else:
                    # Save current and start new
                    current_segment.segment_number = len(merged) + 1
                    merged.append(current_segment)
                    
                    current_segment = PassageSegment(
                        passage=segment.passage,
                        segment_number=len(merged) + 1,
                        verses=segment.verses.copy(),
                        duration_seconds=segment.duration_seconds
                    )
        
        # Add final segment
        if current_segment:
            current_segment.segment_number = len(merged) + 1
            merged.append(current_segment)
        
        return merged
