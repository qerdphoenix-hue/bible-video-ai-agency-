"""Bible data loader - downloads and loads full Bible text"""

import json
import urllib.request
from pathlib import Path
from typing import Dict, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Public domain Bible JSON endpoints
BIBLE_SOURCES = {
    "KJV": "https://raw.githubusercontent.com/aruljohn/Bible-kjv/master/Bible-kjv.json",
    "WEB": "https://raw.githubusercontent.com/aruljohn/Bible-web/master/Bible-web.json",
}


def load_bible_data(translation: str = "KJV", data_dir: Optional[str] = None) -> str:
    """Download and load Bible text data
    
    Args:
        translation: Bible translation (KJV, WEB, etc.)
        data_dir: Directory to save data (default: data/bible_texts)
        
    Returns:
        Status message
    """
    data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data" / "bible_texts"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    bible_file = data_dir / f"{translation.lower()}.json"
    
    # Check if already exists
    if bible_file.exists():
        logger.info(f"Bible data already exists: {bible_file}")
        return f"Bible data already loaded: {bible_file}"
    
    # Download from source
    source_url = BIBLE_SOURCES.get(translation)
    if not source_url:
        return f"No download source for translation: {translation}. Available: {', '.join(BIBLE_SOURCES.keys())}"
    
    try:
        logger.info(f"Downloading Bible data from {source_url}")
        urllib.request.urlretrieve(source_url, bible_file)
        logger.info(f"Bible data downloaded: {bible_file}")
        return f"Bible data downloaded successfully: {bible_file}"
        
    except Exception as e:
        logger.error(f"Failed to download Bible data: {e}")
        
        # Create a larger sample data as fallback
        _create_extended_sample_data(bible_file)
        return f"Download failed. Created extended sample data: {bible_file}"


def _create_extended_sample_data(output_path: Path):
    """Create extended sample Bible data for testing"""
    sample_data = {
        "Genesis": {
            "1": {str(i): f"Genesis 1 verse {i} sample text." for i in range(1, 32)},
            "2": {str(i): f"Genesis 2 verse {i} sample text." for i in range(1, 26)},
        },
        "Exodus": {
            "1": {str(i): f"Exodus 1 verse {i} sample text." for i in range(1, 23)},
            "14": {str(i): f"Exodus 14 verse {i} - The Red Sea parted." for i in range(1, 32)},
        },
        "Psalm": {
            "1": {str(i): f"Psalm 1 verse {i} sample text." for i in range(1, 7)},
            "23": {
                "1": "The Lord is my shepherd; I shall not want.",
                "2": "He maketh me to lie down in green pastures: he leadeth me beside the still waters.",
                "3": "He restoreth my soul: he leadeth me in the paths of righteousness for his name's sake.",
                "4": "Yea, though I walk through the valley of the shadow of death, I will fear no evil: for thou art with me; thy rod and thy staff they comfort me.",
                "5": "Thou preparest a table before me in the presence of mine enemies: thou anointest my head with oil; my cup runneth over.",
                "6": "Surely goodness and mercy shall follow me all the days of my life: and I will dwell in the house of the Lord for ever.",
            },
            "91": {str(i): f"Psalm 91 verse {i} - He who dwells in the secret place of the Most High." for i in range(1, 17)},
        },
        "Proverbs": {
            "3": {
                "5": "Trust in the Lord with all thine heart; and lean not unto thine own understanding.",
                "6": "In all thy ways acknowledge him, and he shall direct thy paths.",
            },
        },
        "Isaiah": {
            "40": {
                "31": "But they that wait upon the Lord shall renew their strength; they shall mount up with wings as eagles; they shall run, and not be weary; and they shall walk, and not faint.",
            },
            "41": {
                "10": "Fear thou not; for I am with thee: be not dismayed; for I am thy God: I will strengthen thee; yea, I will help thee; yea, I will uphold thee with the right hand of my righteousness.",
            },
        },
        "Jeremiah": {
            "29": {
                "11": "For I know the thoughts that I think toward you, saith the Lord, thoughts of peace, and not of evil, to give you an expected end.",
            },
        },
        "Matthew": {
            "5": {str(i): f"Matthew 5 verse {i} - Beatitudes and teachings." for i in range(1, 49)},
            "6": {
                "33": "But seek ye first the kingdom of God, and his righteousness; and all these things shall be added unto you.",
            },
            "7": {str(i): f"Matthew 7 verse {i} - Judge not, that ye be not judged." for i in range(1, 30)},
            "11": {
                "28": "Come unto me, all ye that labour and are heavy laden, and I will give you rest.",
            },
        },
        "John": {
            "1": {str(i): f"John 1 verse {i} - In the beginning was the Word." for i in range(1, 52)},
            "3": {
                "16": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
                "17": "For God sent not his Son into the world to condemn the world; but that the world through him might be saved.",
            },
            "14": {
                "6": "Jesus saith unto him, I am the way, the truth, and the life: no man cometh unto the Father, but by me.",
            },
            "15": {
                "13": "Greater love hath no man than this, that a man lay down his life for his friends.",
            },
        },
        "Romans": {
            "8": {
                "28": "And we know that all things work together for good to them that love God, to them who are the called according to his purpose.",
            },
            "12": {
                "2": "And be not conformed to this world: but be ye transformed by the renewing of your mind, that ye may prove what is that good, and acceptable, and perfect, will of God.",
            },
        },
        "Philippians": {
            "4": {
                "13": "I can do all things through Christ which strengtheneth me.",
            },
        },
        "Hebrews": {
            "11": {
                "1": "Now faith is the substance of things hoped for, the evidence of things not seen.",
            },
        },
        "1 John": {
            "4": {
                "18": "There is no fear in love; but perfect love casteth out fear: because fear hath torment. He that feareth is not made perfect in love.",
            },
        },
        "Revelation": {
            "21": {
                "4": "And God shall wipe away all tears from their eyes; and there shall be no more death, neither sorrow, nor crying, neither shall there be any more pain: for the former things are passed away.",
            },
        },
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Extended sample data created: {output_path}")
