"""Text summarization utilities"""

from src.bible_processor.models import Passage
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PassageSummarizer:
    """Summarize Bible passages"""
    
    def summarize(self, passage: Passage, max_words: int = 50) -> str:
        """Create a brief summary of a passage
        
        Args:
            passage: Bible passage
            max_words: Maximum words in summary
            
        Returns:
            Summary string
        """
        text = passage.full_text
        words = text.split()
        
        if len(words) <= max_words:
            return text
        
        # Simple truncation with ellipsis
        summary = " ".join(words[:max_words]) + "..."
        return summary
