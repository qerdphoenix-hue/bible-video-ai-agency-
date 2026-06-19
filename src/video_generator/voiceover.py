"""Text-to-speech voiceover generation"""

import os
from pathlib import Path
from typing import Optional

try:
    from elevenlabs import generate, save, set_api_key
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VoiceoverGenerator:
    """Generate voiceovers from text using TTS"""
    
    def __init__(self):
        self.provider = settings.tts_provider
        self.api_key = settings.elevenlabs_api_key
        self.voice_id = settings.elevenlabs_voice_id
        self.temp_dir = Path(settings.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        if self.provider == "elevenlabs" and ELEVENLABS_AVAILABLE and self.api_key:
            set_api_key(self.api_key)
    
    def generate(self, text: str, voice_id: Optional[str] = None, 
                 output_path: Optional[str] = None) -> str:
        """Generate voiceover audio from text
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID (optional)
            output_path: Output file path (optional)
            
        Returns:
            Path to generated audio file
        """
        if output_path is None:
            output_path = str(self.temp_dir / "voiceover.mp3")
        
        voice_id = voice_id or self.voice_id
        
        # Try ElevenLabs first
        if self.provider == "elevenlabs" and ELEVENLABS_AVAILABLE and self.api_key:
            try:
                return self._generate_elevenlabs(text, voice_id, output_path)
            except Exception as e:
                logger.warning(f"ElevenLabs failed: {e}. Falling back to gTTS.")
        
        # Fallback to gTTS
        try:
            return self._generate_gtts(text, output_path)
        except Exception as e:
            logger.warning(f"gTTS failed: {e}. Falling back to system TTS.")
        
        # Fallback to system TTS (pyttsx3)
        try:
            return self._generate_pyttsx3(text, output_path)
        except Exception as e:
            logger.error(f"All TTS providers failed: {e}")
            raise RuntimeError(f"Could not generate voiceover: {e}")
    
    def _generate_elevenlabs(self, text: str, voice_id: str, output_path: str) -> str:
        """Generate using ElevenLabs"""
        logger.info(f"Generating ElevenLabs voiceover with voice {voice_id}")
        
        audio = generate(
            text=text,
            voice=voice_id,
            model="eleven_monolingual_v1"
        )
        
        save(audio, output_path)
        logger.info(f"ElevenLabs voiceover saved: {output_path}")
        return output_path
    
    def _generate_gtts(self, text: str, output_path: str) -> str:
        """Generate using Google TTS (gTTS)"""
        try:
            from gtts import gTTS
        except ImportError:
            logger.error("gTTS not installed. Install with: pip install gtts")
            raise
        
        logger.info("Generating gTTS voiceover")
        
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(output_path)
        
        logger.info(f"gTTS voiceover saved: {output_path}")
        return output_path
    
    def _generate_pyttsx3(self, text: str, output_path: str) -> str:
        """Generate using pyttsx3 (offline)"""
        try:
            import pyttsx3
        except ImportError:
            logger.error("pyttsx3 not installed. Install with: pip install pyttsx3")
            raise
        
        logger.info("Generating pyttsx3 voiceover")
        
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)
        
        # pyttsx3 doesn't support MP3 directly, save as WAV then convert
        wav_path = output_path.replace(".mp3", ".wav")
        engine.save_to_file(text, wav_path)
        engine.runAndWait()
        
        # Convert to MP3 using pydub
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_wav(wav_path)
            audio.export(output_path, format="mp3")
            os.remove(wav_path)
        except Exception:
            # If conversion fails, just return the WAV
            output_path = wav_path
        
        logger.info(f"pyttsx3 voiceover saved: {output_path}")
        return output_path
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        if self.provider == "elevenlabs" and ELEVENLABS_AVAILABLE:
            try:
                from elevenlabs import voices
                return [v.name for v in voices()]
            except Exception as e:
                logger.warning(f"Could not fetch ElevenLabs voices: {e}")
        
        return ["default"]
