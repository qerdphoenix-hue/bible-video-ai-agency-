"""Data models for Bible processor"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum


class Testament(str, Enum):
    """Bible Testament"""
    OLD = "old"
    NEW = "new"


class Language(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    PORTUGUESE = "pt"
    ITALIAN = "it"
    CHINESE = "zh"
    KOREAN = "ko"


@dataclass
class Verse:
    """Single Bible verse"""
    book: str
    chapter: int
    verse: int
    text: str
    translation: str = "KJV"
    
    def __str__(self) -> str:
        return f"{self.book} {self.chapter}:{self.verse}"


@dataclass
class Passage:
    """Bible passage containing multiple verses"""
    book: str
    chapter: int
    start_verse: int
    end_verse: Optional[int] = None
    verses: List[Verse] = None
    translation: str = "KJV"
    language: Language = Language.ENGLISH
    title: Optional[str] = None
    summary: Optional[str] = None
    themes: List[str] = None
    
    def __post_init__(self):
        if self.verses is None:
            self.verses = []
        if self.themes is None:
            self.themes = []
    
    def __str__(self) -> str:
        if self.end_verse and self.end_verse != self.start_verse:
            return f"{self.book} {self.chapter}:{self.start_verse}-{self.end_verse}"
        return f"{self.book} {self.chapter}:{self.start_verse}"
    
    @property
    def full_text(self) -> str:
        """Get complete passage text"""
        return " ".join([verse.text for verse in self.verses])
    
    @property
    def verse_count(self) -> int:
        """Get number of verses in passage"""
        return len(self.verses)
    
    @property
    def word_count(self) -> int:
        """Get word count of passage"""
        return len(self.full_text.split())


@dataclass
class PassageSegment:
    """Segment of a passage for video content"""
    passage: Passage
    segment_number: int
    verses: List[Verse]
    duration_seconds: float = 30.0
    narration_text: Optional[str] = None
    background_theme: Optional[str] = None
    
    def __str__(self) -> str:
        return f"Segment {self.segment_number}: {len(self.verses)} verses (~{self.duration_seconds}s)"
    
    @property
    def text(self) -> str:
        """Get segment text"""
        return " ".join([verse.text for verse in self.verses])
    
    @property
    def reference(self) -> str:
        """Get segment reference"""
        if len(self.verses) == 1:
            v = self.verses[0]
            return f"{v.book} {v.chapter}:{v.verse}"
        
        first_v = self.verses[0]
        last_v = self.verses[-1]
        
        if first_v.chapter == last_v.chapter:
            return f"{first_v.book} {first_v.chapter}:{first_v.verse}-{last_v.verse}"
        else:
            return f"{first_v.book} {first_v.chapter}:{first_v.verse} - {last_v.chapter}:{last_v.verse}"


@dataclass
class BibleBook:
    """Bible book metadata"""
    name: str
    abbreviation: str
    testament: Testament
    chapter_count: int
    verses_per_chapter: Dict[int, int]  # {chapter: verse_count}
    
    def get_verse_count(self, chapter: int) -> int:
        """Get verse count for a chapter"""
        return self.verses_per_chapter.get(chapter, 0)
