"""NLP Engine for content enhancement"""

import re
from typing import List, Optional, Dict
from dataclasses import dataclass

from src.bible_processor.models import Passage
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ContentEnhancement:
    """Enhanced content for a Bible passage"""
    title: str
    description: str
    summary: str
    tags: List[str]
    hashtags: List[str]
    key_themes: List[str]
    reflection_question: Optional[str] = None


class ContentEnhancer:
    """Enhance Bible passage content for social media"""
    
    # Common Bible themes for auto-tagging
    THEME_KEYWORDS = {
        "love": ["love", "loved", "beloved", "charity", "affection"],
        "faith": ["faith", "believe", "believed", "believing", "trust"],
        "hope": ["hope", "hoped"],
        "peace": ["peace", "peaceful", "reconciliation"],
        "joy": ["joy", "rejoice", "glad", "happy"],
        "forgiveness": ["forgive", "forgave", "forgiven", "pardon", "mercy"],
        "salvation": ["salvation", "saved", "save", "redeem", "redemption"],
        "prayer": ["pray", "prayer", "praying", "supplication"],
        "wisdom": ["wisdom", "wise", "understanding", "knowledge"],
        "strength": ["strength", "strong", "mighty", "power"],
        "healing": ["heal", "healing", "healed", "health"],
        "fear": ["fear", "afraid", "terrified", "anxiety"],
        "courage": ["courage", "brave", "bold", "fearless"],
        "patience": ["patience", "patient", "endurance", "perseverance"],
        "guidance": ["guide", "lead", "path", "way", "direction"],
        "protection": ["protect", "shield", "refuge", "safety", "deliver"],
        "blessing": ["bless", "blessed", "blessing"],
        "grace": ["grace", "favor", "gracious"],
        "creation": ["create", "created", "creation", "heaven", "earth"],
    }
    
    def __init__(self):
        self.openai_api_key = settings.openai_api_key
        self.openai_model = settings.openai_model
    
    def enhance(self, passage: Passage) -> ContentEnhancement:
        """Generate enhanced content for a passage
        
        Args:
            passage: Bible passage
            
        Returns:
            ContentEnhancement with title, description, tags, etc.
        """
        text = passage.full_text
        reference = f"{passage.book} {passage.chapter}:{passage.start_verse}"
        if passage.end_verse and passage.end_verse != passage.start_verse:
            reference += f"-{passage.end_verse}"
        
        # Extract themes
        themes = self._extract_themes(text)
        
        # Generate title
        title = self._generate_title(passage, themes)
        
        # Generate description
        description = self._generate_description(passage, reference, themes)
        
        # Generate tags
        tags = self._generate_tags(passage, themes)
        
        # Generate hashtags
        hashtags = self._generate_hashtags(themes)
        
        # Generate reflection question
        reflection = self._generate_reflection_question(passage, themes)
        
        return ContentEnhancement(
            title=title,
            description=description,
            summary=text[:200] + "..." if len(text) > 200 else text,
            tags=tags,
            hashtags=hashtags,
            key_themes=themes,
            reflection_question=reflection
        )
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract themes from passage text using keyword matching"""
        text_lower = text.lower()
        themes = []
        
        for theme, keywords in self.THEME_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:5]  # Limit to top 5 themes
    
    def _generate_title(self, passage: Passage, themes: List[str]) -> str:
        """Generate a catchy title for the video"""
        reference = f"{passage.book} {passage.chapter}:{passage.start_verse}"
        if passage.end_verse and passage.end_verse != passage.start_verse:
            reference += f"-{passage.end_verse}"
        
        # Use themes to create contextual title
        if themes:
            theme_titles = {
                "love": f"The Power of Love - {reference}",
                "faith": f"Walk by Faith - {reference}",
                "hope": f"Hope in Hard Times - {reference}",
                "peace": f"Finding Peace - {reference}",
                "joy": f"Choose Joy - {reference}",
                "forgiveness": f"Forgiveness Changes Everything - {reference}",
                "salvation": f"The Gift of Salvation - {reference}",
                "prayer": f"The Power of Prayer - {reference}",
                "wisdom": f"God's Wisdom - {reference}",
                "strength": f"Find Your Strength - {reference}",
                "healing": f"God's Healing Promise - {reference}",
                "courage": f"Be Courageous - {reference}",
                "guidance": f"God's Guidance - {reference}",
                "protection": f"Under His Protection - {reference}",
                "blessing": f"Count Your Blessings - {reference}",
                "grace": f"Amazing Grace - {reference}",
            }
            
            for theme in themes:
                if theme in theme_titles:
                    return theme_titles[theme]
        
        # Default title
        return f"Bible Scripture: {reference}"
    
    def _generate_description(self, passage: Passage, reference: str, themes: List[str]) -> str:
        """Generate YouTube description"""
        text = passage.full_text
        
        description = f"""📖 {reference}

"{text}"

✨ Today's Bible verse reminds us of God's word and promises.

🙏 Take a moment to reflect on this scripture and let it guide your day.

💬 What does this verse mean to you? Share your thoughts in the comments!

🔔 Subscribe for daily Bible verses and inspiration.

#Bible #Scripture #DailyVerse #Christian #Faith
"""
        return description.strip()
    
    def _generate_tags(self, passage: Passage, themes: List[str]) -> List[str]:
        """Generate YouTube tags"""
        base_tags = [
            "Bible",
            "Scripture",
            "Daily Verse",
            "Christian",
            "Faith",
            "Bible Study",
            "God's Word",
            "Inspiration",
            passage.book,
            f"{passage.book} {passage.chapter}",
        ]
        
        # Add theme-based tags
        theme_tags = [theme.title() for theme in themes]
        
        tags = base_tags + theme_tags
        return tags[:15]  # YouTube allows up to 500 chars, ~15 tags is safe
    
    def _generate_hashtags(self, themes: List[str]) -> List[str]:
        """Generate social media hashtags"""
        base_hashtags = [
            "#Bible",
            "#Scripture",
            "#DailyVerse",
            "#Christian",
            "#Faith",
            "#GodsWord",
            "#BibleVerse",
            "#Inspiration",
            "#Jesus",
            "#Prayer",
        ]
        
        theme_hashtags = [f"#{theme.title()}" for theme in themes[:3]]
        
        hashtags = base_hashtags + theme_hashtags
        return hashtags[:15]
    
    def _generate_reflection_question(self, passage: Passage, themes: List[str]) -> Optional[str]:
        """Generate a reflection question for engagement"""
        questions = {
            "love": "How can you show more love to others today?",
            "faith": "What step of faith is God calling you to take?",
            "hope": "Where do you need hope in your life right now?",
            "peace": "What do you need to surrender to find peace?",
            "joy": "What are you grateful for today?",
            "forgiveness": "Who do you need to forgive or ask forgiveness from?",
            "salvation": "How has God's grace changed your life?",
            "prayer": "What would you like to pray about today?",
            "wisdom": "What decision are you seeking wisdom for?",
            "strength": "Where do you need God's strength today?",
            "healing": "What area of your life needs healing?",
            "courage": "What challenge requires courage today?",
            "guidance": "Where do you need God's guidance right now?",
            "protection": "What are you trusting God to protect?",
            "blessing": "How has God blessed you recently?",
            "grace": "How has God's grace impacted your life?",
        }
        
        for theme in themes:
            if theme in questions:
                return questions[theme]
        
        return "How does this verse speak to you today?"
    
    def enhance_with_ai(self, passage: Passage) -> ContentEnhancement:
        """Enhance content using OpenAI (if API key available)"""
        if not self.openai_api_key:
            logger.info("No OpenAI API key, using rule-based enhancement")
            return self.enhance(passage)
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            reference = f"{passage.book} {passage.chapter}:{passage.start_verse}"
            if passage.end_verse and passage.end_verse != passage.start_verse:
                reference += f"-{passage.end_verse}"
            
            prompt = f"""Generate engaging social media content for this Bible passage:

Reference: {reference}
Text: {passage.full_text}

Create:
1. A catchy title (under 60 chars)
2. A compelling YouTube description (include emojis, call to action, hashtags)
3. 10 relevant tags
4. 10 relevant hashtags
5. 3 key themes
6. 1 reflection question for engagement

Format as JSON."""
            
            response = client.chat.completions.create(
                model=self.openai_model or "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Christian content creator."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            import json
            content = json.loads(response.choices[0].message.content)
            
            return ContentEnhancement(
                title=content.get("title", "Bible Scripture"),
                description=content.get("description", ""),
                summary=passage.full_text[:200] + "...",
                tags=content.get("tags", []),
                hashtags=content.get("hashtags", []),
                key_themes=content.get("themes", []),
                reflection_question=content.get("reflection_question")
            )
            
        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}, falling back to rule-based")
            return self.enhance(passage)
