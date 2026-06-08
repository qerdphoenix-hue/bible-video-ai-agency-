"""Bible passage validation"""

from typing import Optional, Tuple
from dataclasses import dataclass

from src.bible_processor.reference import ReferenceParser, BibleReference
from src.bible_processor.models import Passage, Verse
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of validation"""
    is_valid: bool
    errors: list
    warnings: list
    
    def __str__(self) -> str:
        msg = f"Valid: {self.is_valid}\n"
        if self.errors:
            msg += f"Errors: {', '.join(self.errors)}\n"
        if self.warnings:
            msg += f"Warnings: {', '.join(self.warnings)}\n"
        return msg


class BibleValidator:
    """Validate Bible references and passages"""
    
    # Valid books with verse counts per chapter
    BIBLE_STRUCTURE = {
        # Old Testament
        "Genesis": {1: 31, 2: 25, 3: 24},  # Simplified for example
        "Exodus": {1: 22, 2: 25},
        "Psalm": {23: 6},
        
        # New Testament
        "Matthew": {1: 25, 2: 23, 3: 17, 4: 25, 5: 48},
        "Mark": {1: 45, 2: 28, 3: 35},
        "Luke": {1: 80, 2: 52, 3: 38},
        "John": {1: 51, 2: 25, 3: 36, 4: 54, 5: 47},
        "Acts": {1: 26, 2: 47, 3: 26},
        "Romans": {1: 32, 2: 29},
        "1 Corinthians": {1: 31, 2: 16},
        "2 Corinthians": {1: 24, 2: 17},
        "Galatians": {1: 24, 2: 21},
        "Ephesians": {1: 23, 2: 22},
        "Philippians": {1: 30, 2: 30},
        "Colossians": {1: 29, 2: 23},
        "1 Thessalonians": {1: 10, 2: 20},
        "2 Thessalonians": {1: 12, 2: 17},
        "1 Timothy": {1: 20, 2: 15},
        "2 Timothy": {1: 18, 2: 26},
        "Titus": {1: 16, 2: 15},
        "Philemon": {1: 25},
        "Hebrews": {1: 14, 2: 18},
        "James": {1: 27, 2: 26},
        "1 Peter": {1: 25, 2: 25},
        "2 Peter": {1: 21, 2: 22},
        "1 John": {1: 10, 2: 29},
        "2 John": {1: 14},
        "3 John": {1: 14},
        "Jude": {1: 25},
        "Revelation": {1: 20, 2: 29},
    }
    
    @classmethod
    def validate_reference(cls, reference: str) -> ValidationResult:
        """Validate a Bible reference string
        
        Args:
            reference: Reference string to validate
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Parse reference
        parsed = ReferenceParser.parse(reference)
        if not parsed:
            errors.append(f"Invalid reference format: {reference}")
            return ValidationResult(False, errors, warnings)
        
        # Validate book exists
        if parsed.book not in cls.BIBLE_STRUCTURE:
            errors.append(f"Unknown book: {parsed.book}")
            return ValidationResult(False, errors, warnings)
        
        book_data = cls.BIBLE_STRUCTURE[parsed.book]
        
        # Validate chapter exists
        if parsed.chapter not in book_data:
            errors.append(f"Chapter {parsed.chapter} not found in {parsed.book}")
            return ValidationResult(False, errors, warnings)
        
        max_verse = book_data[parsed.chapter]
        
        # Validate start verse
        if parsed.start_verse < 1:
            errors.append(f"Start verse must be >= 1, got {parsed.start_verse}")
        elif parsed.start_verse > max_verse:
            errors.append(f"Start verse {parsed.start_verse} exceeds max verse {max_verse}")
        
        # Validate end verse
        if parsed.end_verse:
            if parsed.end_verse < parsed.start_verse:
                errors.append(f"End verse {parsed.end_verse} cannot be less than start verse {parsed.start_verse}")
            elif parsed.end_verse > max_verse:
                warnings.append(f"End verse {parsed.end_verse} may exceed max verse {max_verse}")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    @classmethod
    def validate_passage(cls, passage: Passage) -> ValidationResult:
        """Validate a Passage object
        
        Args:
            passage: Passage to validate
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Validate passage has verses
        if not passage.verses:
            errors.append("Passage has no verses")
        elif len(passage.verses) == 0:
            errors.append("Passage verses list is empty")
        
        # Validate verse count matches reference
        expected_count = 1
        if passage.end_verse:
            expected_count = passage.end_verse - passage.start_verse + 1
        
        if len(passage.verses) != expected_count:
            warnings.append(
                f"Expected {expected_count} verses, got {len(passage.verses)}"
            )
        
        # Validate all verses have text
        empty_verses = [v for v in passage.verses if not v.text or not v.text.strip()]
        if empty_verses:
            errors.append(f"Found {len(empty_verses)} verses with empty text")
        
        # Validate verses are sequential
        if len(passage.verses) > 1:
            for i in range(1, len(passage.verses)):
                prev_verse = passage.verses[i-1]
                curr_verse = passage.verses[i]
                
                if curr_verse.verse != prev_verse.verse + 1:
                    if curr_verse.chapter == prev_verse.chapter:
                        warnings.append(
                            f"Non-sequential verses: {prev_verse.verse} -> {curr_verse.verse}"
                        )
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    @classmethod
    def validate_verse(cls, verse: Verse) -> ValidationResult:
        """Validate a single Verse
        
        Args:
            verse: Verse to validate
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Validate book
        if verse.book not in cls.BIBLE_STRUCTURE:
            errors.append(f"Unknown book: {verse.book}")
            return ValidationResult(False, errors, warnings)
        
        book_data = cls.BIBLE_STRUCTURE[verse.book]
        
        # Validate chapter
        if verse.chapter not in book_data:
            errors.append(f"Chapter {verse.chapter} not found in {verse.book}")
            return ValidationResult(False, errors, warnings)
        
        # Validate verse number
        max_verse = book_data[verse.chapter]
        if verse.verse < 1 or verse.verse > max_verse:
            errors.append(
                f"Verse {verse.verse} out of range [1-{max_verse}] "
                f"for {verse.book} {verse.chapter}"
            )
        
        # Validate text
        if not verse.text or not verse.text.strip():
            errors.append("Verse has no text")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    @classmethod
    def is_valid_reference(cls, reference: str) -> bool:
        """Quick check if reference is valid
        
        Args:
            reference: Reference string
            
        Returns:
            True if valid, False otherwise
        """
        result = cls.validate_reference(reference)
        return result.is_valid
