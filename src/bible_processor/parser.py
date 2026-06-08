"""Bible text parser"""

import json
from pathlib import Path
from typing import Optional, Dict, List

from src.bible_processor.models import Verse, Passage, Testament, BibleBook
from src.bible_processor.reference import ReferenceParser, BibleReference
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BibleParser:
    """Parse Bible passages from various sources"""
    
    # Default Bible data location
    DATA_DIR = Path(__file__).parent.parent.parent / "data" / "bible_texts"
    
    def __init__(self, translation: str = "KJV"):
        """Initialize parser
        
        Args:
            translation: Bible translation (KJV, ESV, NRSV, etc.)
        """
        self.translation = translation
        self.bible_data: Dict = {}
        self._load_bible_data()
    
    def _load_bible_data(self):
        """Load Bible text data from JSON files"""
        try:
            # Try to load from data directory
            bible_file = self.DATA_DIR / f"{self.translation.lower()}.json"
            
            if bible_file.exists():
                with open(bible_file, 'r', encoding='utf-8') as f:
                    self.bible_data = json.load(f)
                logger.info(f"Loaded Bible data: {bible_file}")
            else:
                logger.warning(f"Bible data file not found: {bible_file}")
                self._load_sample_data()
        except Exception as e:
            logger.error(f"Error loading Bible data: {str(e)}")
            self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample Bible data for testing"""
        self.bible_data = {
            "John": {
                "3": {
                    "16": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
                    "17": "For God sent not his Son into the world to condemn the world; but that the world through him might be saved.",
                    "18": "He that believeth on him is not condemned: but he that believeth not is condemned already, because he hath not believed in the name of the only begotten Son of God.",
                }
            },
            "Psalm": {
                "23": {
                    "1": "The Lord is my shepherd; I shall not want.",
                    "2": "He maketh me to lie down in green pastures: he leadeth me beside the still waters.",
                    "3": "He restoreth my soul: he leadeth me in the paths of righteousness for his name's sake.",
                    "4": "Yea, though I walk through the valley of the shadow of death, I will fear no evil: for thou art with me; thy rod and thy staff they comfort me.",
                }
            }
        }
    
    def get_verse(self, book: str, chapter: int, verse: int) -> Optional[Verse]:
        """Get a single verse
        
        Args:
            book: Book name
            chapter: Chapter number
            verse: Verse number
            
        Returns:
            Verse object or None
        """
        try:
            if book not in self.bible_data:
                logger.warning(f"Book not found: {book}")
                return None
            
            chapter_data = self.bible_data[book].get(str(chapter))
            if not chapter_data:
                logger.warning(f"Chapter not found: {book} {chapter}")
                return None
            
            verse_text = chapter_data.get(str(verse))
            if not verse_text:
                logger.warning(f"Verse not found: {book} {chapter}:{verse}")
                return None
            
            return Verse(
                book=book,
                chapter=chapter,
                verse=verse,
                text=verse_text,
                translation=self.translation
            )
            
        except Exception as e:
            logger.error(f"Error getting verse {book} {chapter}:{verse}: {str(e)}")
            return None
    
    def get_passage(self, 
                   book: str, 
                   chapter: int, 
                   start_verse: int = 1,
                   end_verse: Optional[int] = None) -> Optional[Passage]:
        """Get a Bible passage
        
        Args:
            book: Book name
            chapter: Chapter number
            start_verse: Starting verse
            end_verse: Ending verse (defaults to start_verse)
            
        Returns:
            Passage object or None
        """
        try:
            if end_verse is None:
                end_verse = start_verse
            
            verses = []
            for v in range(start_verse, end_verse + 1):
                verse = self.get_verse(book, chapter, v)
                if verse:
                    verses.append(verse)
            
            if not verses:
                logger.warning(f"No verses found for {book} {chapter}:{start_verse}-{end_verse}")
                return None
            
            passage = Passage(
                book=book,
                chapter=chapter,
                start_verse=start_verse,
                end_verse=end_verse if end_verse != start_verse else None,
                verses=verses,
                translation=self.translation
            )
            
            logger.info(f"Retrieved passage: {passage}")
            return passage
            
        except Exception as e:
            logger.error(f"Error getting passage: {str(e)}")
            return None
    
    def parse_reference(self, reference: str) -> Optional[Passage]:
        """Parse a reference string and get the passage
        
        Args:
            reference: Reference string (e.g., "John 3:16-18")
            
        Returns:
            Passage object or None
        """
        try:
            parsed_ref = ReferenceParser.parse(reference)
            if not parsed_ref:
                return None
            
            return self.get_passage(
                book=parsed_ref.book,
                chapter=parsed_ref.chapter,
                start_verse=parsed_ref.start_verse,
                end_verse=parsed_ref.end_verse
            )
            
        except Exception as e:
            logger.error(f"Error parsing reference: {str(e)}")
            return None
    
    def parse_multiple_references(self, references: str) -> List[Passage]:
        """Parse multiple references
        
        Args:
            references: Multiple references separated by commas
            
        Returns:
            List of Passage objects
        """
        passages = []
        parsed_refs = ReferenceParser.parse_multiple(references)
        
        for ref in parsed_refs:
            passage = self.get_passage(
                book=ref.book,
                chapter=ref.chapter,
                start_verse=ref.start_verse,
                end_verse=ref.end_verse
            )
            if passage:
                passages.append(passage)
        
        return passages
    
    def search_text(self, query: str) -> List[Verse]:
        """Search for verses containing specific text
        
        Args:
            query: Search query
            
        Returns:
            List of matching verses
        """
        results = []
        query_lower = query.lower()
        
        try:
            for book, chapters in self.bible_data.items():
                for chapter_num, verses in chapters.items():
                    for verse_num, verse_text in verses.items():
                        if query_lower in verse_text.lower():
                            results.append(Verse(
                                book=book,
                                chapter=int(chapter_num),
                                verse=int(verse_num),
                                text=verse_text,
                                translation=self.translation
                            ))
        except Exception as e:
            logger.error(f"Error searching text: {str(e)}")
        
        return results
