"""Tests for Bible processor module"""

import pytest

from src.bible_processor.parser import BibleParser
from src.bible_processor.validator import BibleValidator, ValidationResult
from src.bible_processor.reference import ReferenceParser, BibleReference
from src.bible_processor.segmenter import PassageSegmenter
from src.bible_processor.models import Verse, Passage, PassageSegment


class TestReferenceParser:
    """Test Bible reference parsing"""
    
    def test_parse_simple_reference(self):
        """Test parsing simple reference"""
        ref = ReferenceParser.parse("John 3:16")
        
        assert ref is not None
        assert ref.book == "John"
        assert ref.chapter == 3
        assert ref.start_verse == 16
        assert ref.end_verse is None
    
    def test_parse_verse_range(self):
        """Test parsing verse range"""
        ref = ReferenceParser.parse("John 3:16-18")
        
        assert ref is not None
        assert ref.book == "John"
        assert ref.chapter == 3
        assert ref.start_verse == 16
        assert ref.end_verse == 18
    
    def test_parse_book_abbreviation(self):
        """Test parsing book abbreviation"""
        ref = ReferenceParser.parse("1 Jn 5:7")
        
        assert ref is not None
        assert ref.book == "1 John"
    
    def test_parse_invalid_reference(self):
        """Test parsing invalid reference"""
        ref = ReferenceParser.parse("Invalid Reference")
        assert ref is None
    
    def test_normalize_book_name(self):
        """Test book name normalization"""
        assert ReferenceParser.normalize_book_name("john") == "John"
        assert ReferenceParser.normalize_book_name("JN") == "John"
        assert ReferenceParser.normalize_book_name("matthew") == "Matthew"
        assert ReferenceParser.normalize_book_name("1 cor") == "1 Corinthians"
    
    def test_parse_multiple_references(self):
        """Test parsing multiple references"""
        refs = ReferenceParser.parse_multiple("John 3:16, Psalm 23:1, Matt 5:7")
        
        assert len(refs) == 3
        assert refs[0].book == "John"
        assert refs[1].book == "Psalm"
        assert refs[2].book == "Matthew"


class TestBibleParser:
    """Test Bible text parsing"""
    
    @pytest.fixture
    def parser(self):
        return BibleParser(translation="KJV")
    
    def test_get_verse(self, parser):
        """Test getting a single verse"""
        verse = parser.get_verse("John", 3, 16)
        
        assert verse is not None
        assert verse.book == "John"
        assert verse.chapter == 3
        assert verse.verse == 16
        assert len(verse.text) > 0
    
    def test_get_verse_not_found(self, parser):
        """Test getting verse that doesn't exist"""
        verse = parser.get_verse("NonExistent", 1, 1)
        assert verse is None
    
    def test_get_passage(self, parser):
        """Test getting a passage"""
        passage = parser.get_passage("John", 3, 16, 18)
        
        assert passage is not None
        assert passage.book == "John"
        assert passage.chapter == 3
        assert passage.start_verse == 16
        assert passage.end_verse == 18
        assert len(passage.verses) == 3
        assert passage.verse_count == 3
    
    def test_get_single_verse_passage(self, parser):
        """Test getting a single verse passage"""
        passage = parser.get_passage("John", 3, 16)
        
        assert passage is not None
        assert len(passage.verses) == 1
        assert passage.verse_count == 1
    
    def test_parse_reference(self, parser):
        """Test parsing reference string"""
        passage = parser.parse_reference("John 3:16-18")
        
        assert passage is not None
        assert passage.book == "John"
        assert len(passage.verses) == 3
    
    def test_parse_multiple_references(self, parser):
        """Test parsing multiple references"""
        passages = parser.parse_multiple_references("John 3:16, Psalm 23:1")
        
        assert len(passages) == 2
        assert passages[0].book == "John"
        assert passages[1].book == "Psalm"
    
    def test_search_text(self, parser):
        """Test searching Bible text"""
        results = parser.search_text("God")
        
        assert len(results) > 0
        assert all("God" in v.text for v in results)
    
    def test_passage_word_count(self, parser):
        """Test word count calculation"""
        passage = parser.get_passage("John", 3, 16, 18)
        
        assert passage.word_count > 0
        assert passage.full_text
    
    def test_passage_properties(self, parser):
        """Test passage properties"""
        passage = parser.get_passage("John", 3, 16, 18)
        
        assert str(passage) == "John 3:16-18"
        assert passage.verse_count == 3
        assert passage.word_count > passage.verse_count
        assert len(passage.full_text) > 0


class TestBibleValidator:
    """Test Bible passage validation"""
    
    def test_validate_valid_reference(self):
        """Test validating valid reference"""
        result = BibleValidator.validate_reference("John 3:16-18")
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_invalid_format(self):
        """Test validating invalid reference format"""
        result = BibleValidator.validate_reference("Invalid")
        
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_validate_unknown_book(self):
        """Test validating reference with unknown book in validator"""
        # Song of Solomon parses correctly but is not in BIBLE_STRUCTURE
        result = BibleValidator.validate_reference("Song 1:1")
        
        assert not result.is_valid
        assert any("Unknown book" in e for e in result.errors)
    
    def test_validate_invalid_verse_range(self):
        """Test validating invalid verse range"""
        result = BibleValidator.validate_reference("John 3:20-10")
        
        assert not result.is_valid
        assert any("End verse" in e for e in result.errors)
    
    def test_is_valid_reference(self):
        """Test quick validation"""
        assert BibleValidator.is_valid_reference("John 3:16")
        assert not BibleValidator.is_valid_reference("Invalid")
    
    def test_validate_passage(self):
        """Test validating passage object"""
        parser = BibleParser()
        passage = parser.get_passage("John", 3, 16, 18)
        
        result = BibleValidator.validate_passage(passage)
        
        assert result.is_valid
    
    def test_validate_verse(self):
        """Test validating verse object"""
        verse = Verse(
            book="John",
            chapter=3,
            verse=16,
            text="For God so loved the world..."
        )
        
        result = BibleValidator.validate_verse(verse)
        
        assert result.is_valid


class TestPassageSegmenter:
    """Test passage segmentation"""
    
    @pytest.fixture
    def parser(self):
        return BibleParser()
    
    @pytest.fixture
    def passage(self, parser):
        return parser.get_passage("John", 3, 16, 18)
    
    @pytest.fixture
    def segmenter(self):
        return PassageSegmenter()
    
    def test_segment_by_verses(self, passage, segmenter):
        """Test segmenting by verses"""
        segments = segmenter.segment_by_verses(passage, verses_per_segment=1)
        
        assert len(segments) == 3
        assert all(len(s.verses) == 1 for s in segments)
    
    def test_segment_by_words(self, passage, segmenter):
        """Test segmenting by words"""
        segments = segmenter.segment_by_words(passage, words_per_segment=50)
        
        assert len(segments) > 0
        assert all(isinstance(s, PassageSegment) for s in segments)
    
    def test_segment_by_duration(self, passage, segmenter):
        """Test segmenting by duration"""
        segments = segmenter.segment_by_duration(passage, duration_seconds=20)
        
        assert len(segments) > 0
        assert all(s.duration_seconds <= 25 for s in segments)  # With some padding
    
    def test_segment_numbering(self, passage, segmenter):
        """Test segment numbering"""
        segments = segmenter.segment_by_verses(passage, verses_per_segment=1)
        
        for i, segment in enumerate(segments, 1):
            assert segment.segment_number == i
    
    def test_segment_duration_calculation(self, passage, segmenter):
        """Test duration calculation"""
        segments = segmenter.segment_by_verses(passage, verses_per_segment=1)
        
        assert all(s.duration_seconds > 0 for s in segments)
    
    def test_merge_segments(self, passage, segmenter):
        """Test merging segments"""
        segments = segmenter.segment_by_verses(passage, verses_per_segment=1)
        merged = segmenter.merge_segments(segments, max_duration=100)
        
        assert len(merged) <= len(segments)
        assert all(s.duration_seconds <= 100 for s in merged)
    
    def test_segment_properties(self, passage, segmenter):
        """Test segment properties"""
        segments = segmenter.segment_by_verses(passage, verses_per_segment=1)
        segment = segments[0]
        
        assert len(segment.text) > 0
        assert len(segment.reference) > 0
        assert str(segment)
