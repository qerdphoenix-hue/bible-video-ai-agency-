"""Bible reference parsing and handling"""

import re
from typing import Optional, Tuple, List
from dataclasses import dataclass

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BibleReference:
    """Represents a parsed Bible reference"""
    book: str
    chapter: int
    start_verse: int
    end_verse: Optional[int] = None
    
    def __str__(self) -> str:
        """Format reference as string"""
        if self.end_verse and self.end_verse != self.start_verse:
            return f"{self.book} {self.chapter}:{self.start_verse}-{self.end_verse}"
        return f"{self.book} {self.chapter}:{self.start_verse}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "book": self.book,
            "chapter": self.chapter,
            "start_verse": self.start_verse,
            "end_verse": self.end_verse,
        }


class ReferenceParser:
    """Parse Bible references from various formats"""
    
    # Bible books with their variations
    BOOK_NAMES = {
        # Old Testament
        "genesis": "Genesis",
        "gen": "Genesis",
        "exodus": "Exodus",
        "ex": "Exodus",
        "leviticus": "Leviticus",
        "lev": "Leviticus",
        "numbers": "Numbers",
        "num": "Numbers",
        "deuteronomy": "Deuteronomy",
        "deut": "Deuteronomy",
        "joshua": "Joshua",
        "josh": "Joshua",
        "judges": "Judges",
        "judg": "Judges",
        "ruth": "Ruth",
        "1 samuel": "1 Samuel",
        "1sam": "1 Samuel",
        "2 samuel": "2 Samuel",
        "2sam": "2 Samuel",
        "1 kings": "1 Kings",
        "1kgs": "1 Kings",
        "2 kings": "2 Kings",
        "2kgs": "2 Kings",
        "1 chronicles": "1 Chronicles",
        "1chr": "1 Chronicles",
        "2 chronicles": "2 Chronicles",
        "2chr": "2 Chronicles",
        "ezra": "Ezra",
        "nehemiah": "Nehemiah",
        "neh": "Nehemiah",
        "esther": "Esther",
        "est": "Esther",
        "job": "Job",
        "psalm": "Psalm",
        "psalms": "Psalm",
        "ps": "Psalm",
        "proverbs": "Proverbs",
        "prov": "Proverbs",
        "pr": "Proverbs",
        "ecclesiastes": "Ecclesiastes",
        "eccl": "Ecclesiastes",
        "song of solomon": "Song of Solomon",
        "song": "Song of Solomon",
        "ss": "Song of Solomon",
        "isaiah": "Isaiah",
        "isa": "Isaiah",
        "jeremiah": "Jeremiah",
        "jer": "Jeremiah",
        "lamentations": "Lamentations",
        "lam": "Lamentations",
        "ezekiel": "Ezekiel",
        "ezek": "Ezekiel",
        "daniel": "Daniel",
        "dan": "Daniel",
        "hosea": "Hosea",
        "hos": "Hosea",
        "joel": "Joel",
        "amos": "Amos",
        "obadiah": "Obadiah",
        "obad": "Obadiah",
        "jonah": "Jonah",
        "jon": "Jonah",
        "micah": "Micah",
        "mic": "Micah",
        "nahum": "Nahum",
        "nah": "Nahum",
        "habakkuk": "Habakkuk",
        "hab": "Habakkuk",
        "zephaniah": "Zephaniah",
        "zeph": "Zephaniah",
        "haggai": "Haggai",
        "hag": "Haggai",
        "zechariah": "Zechariah",
        "zech": "Zechariah",
        "malachi": "Malachi",
        "mal": "Malachi",
        
        # New Testament
        "matthew": "Matthew",
        "matt": "Matthew",
        "mt": "Matthew",
        "mark": "Mark",
        "mr": "Mark",
        "luke": "Luke",
        "lk": "Luke",
        "john": "John",
        "jn": "John",
        "acts": "Acts",
        "ac": "Acts",
        "romans": "Romans",
        "rom": "Romans",
        "ro": "Romans",
        "1 corinthians": "1 Corinthians",
        "1 cor": "1 Corinthians",
        "1cor": "1 Corinthians",
        "1co": "1 Corinthians",
        "2 corinthians": "2 Corinthians",
        "2 cor": "2 Corinthians",
        "2cor": "2 Corinthians",
        "2co": "2 Corinthians",
        "galatians": "Galatians",
        "gal": "Galatians",
        "ga": "Galatians",
        "ephesians": "Ephesians",
        "eph": "Ephesians",
        "ep": "Ephesians",
        "philippians": "Philippians",
        "phil": "Philippians",
        "ph": "Philippians",
        "colossians": "Colossians",
        "col": "Colossians",
        "1 thessalonians": "1 Thessalonians",
        "1 thess": "1 Thessalonians",
        "1thess": "1 Thessalonians",
        "1th": "1 Thessalonians",
        "2 thessalonians": "2 Thessalonians",
        "2 thess": "2 Thessalonians",
        "2thess": "2 Thessalonians",
        "2th": "2 Thessalonians",
        "1 timothy": "1 Timothy",
        "1 tim": "1 Timothy",
        "1tim": "1 Timothy",
        "1ti": "1 Timothy",
        "2 timothy": "2 Timothy",
        "2 tim": "2 Timothy",
        "2tim": "2 Timothy",
        "2ti": "2 Timothy",
        "titus": "Titus",
        "tit": "Titus",
        "philemon": "Philemon",
        "phlm": "Philemon",
        "hebrews": "Hebrews",
        "heb": "Hebrews",
        "he": "Hebrews",
        "james": "James",
        "jas": "James",
        "ja": "James",
        "1 peter": "1 Peter",
        "1 pet": "1 Peter",
        "1pet": "1 Peter",
        "1pe": "1 Peter",
        "2 peter": "2 Peter",
        "2 pet": "2 Peter",
        "2pet": "2 Peter",
        "2pe": "2 Peter",
        "1 john": "1 John",
        "1 jn": "1 John",
        "1jn": "1 John",
        "1jo": "1 John",
        "2 john": "2 John",
        "2 jn": "2 John",
        "2jn": "2 John",
        "2jo": "2 John",
        "3 john": "3 John",
        "3 jn": "3 John",
        "3jn": "3 John",
        "3jo": "3 John",
        "jude": "Jude",
        "revelation": "Revelation",
        "rev": "Revelation",
        "re": "Revelation",
    }
    
    @classmethod
    def normalize_book_name(cls, book: str) -> Optional[str]:
        """Normalize book name to standard format"""
        normalized = book.strip().lower()
        return cls.BOOK_NAMES.get(normalized)
    
    @classmethod
    def parse(cls, reference: str) -> Optional[BibleReference]:
        """Parse a Bible reference string
        
        Supports formats:
        - "John 3:16"
        - "John 3:16-18"
        - "1 John 5:7-8"
        - "Gen 1:1"
        - "Psalm 23"
        
        Args:
            reference: Reference string
            
        Returns:
            BibleReference or None if parsing fails
        """
        try:
            # Remove extra whitespace
            reference = reference.strip()
            
            # Pattern: "Book Chapter:Verse" or "Book Chapter:Verse-Verse"
            # Also handles: "Book Chapter" (assumes verse 1)
            # Supports books with numbers like "1 John", "2 Corinthians"
            pattern = r"^([0-3]?\s*[a-zA-Z\s]+?)\s+(\d+)(?::(\d+))?(?:-(\d+))?$"
            match = re.match(pattern, reference, re.IGNORECASE)
            
            if not match:
                logger.warning(f"Could not parse reference: {reference}")
                return None
            
            book_str = match.group(1).strip()
            chapter = int(match.group(2))
            start_verse = int(match.group(3)) if match.group(3) else 1
            end_verse = int(match.group(4)) if match.group(4) else None
            
            # Normalize book name
            book = cls.normalize_book_name(book_str)
            if not book:
                logger.warning(f"Unknown book: {book_str}")
                return None
            
            return BibleReference(
                book=book,
                chapter=chapter,
                start_verse=start_verse,
                end_verse=end_verse,
            )
            
        except Exception as e:
            logger.error(f"Error parsing reference '{reference}': {str(e)}")
            return None
    
    @classmethod
    def parse_multiple(cls, references: str, delimiter: str = ",") -> List[BibleReference]:
        """Parse multiple references
        
        Args:
            references: String with multiple references (comma-separated by default)
            delimiter: Reference delimiter
            
        Returns:
            List of BibleReference objects
        """
        result = []
        for ref in references.split(delimiter):
            parsed = cls.parse(ref.strip())
            if parsed:
                result.append(parsed)
        return result
