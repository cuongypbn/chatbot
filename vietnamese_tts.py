#!/usr/bin/env python3
"""
Vietnamese Text-to-Speech Module for Raspberry Pi 4
Supports multiple TTS engines with fallback options
Optimized for Pi 4 8GB RAM with Vietnamese pronunciation
"""

import os
import tempfile
import subprocess
import time
import requests
import pygame
from pathlib import Path
from typing import Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VietnameseTTS:
    """Vietnamese Text-to-Speech with multiple engine support"""
    
    def __init__(self, preferred_engine="gtts"):
        """
        Initialize TTS with preferred engine
        
        Args:
            preferred_engine (str): "gtts", "zalo", "edge", "espeak", "festival"
        """
        self.preferred_engine = preferred_engine
        self.available_engines = []
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
        self._check_available_engines()
    
    def _check_available_engines(self):
        """Check which TTS engines are available"""
        # Check gTTS (requires internet)
        try:
            from gtts import gTTS
            self.available_engines.append("gtts")
            logger.info("✅ gTTS available")
        except ImportError:
            logger.warning("⚠️ gTTS not available")
        
        # Check espeak-ng
        try:
            result = subprocess.run(["espeak-ng", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.available_engines.append("espeak")
                logger.info("✅ espeak-ng available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("⚠️ espeak-ng not available")
        
        # Check festival
        try:
            result = subprocess.run(["festival", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.available_engines.append("festival")
                logger.info("✅ Festival available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("⚠️ Festival not available")
        
        # Check edge-tts
        try:
            import edge_tts
            self.available_engines.append("edge")
            logger.info("✅ Edge-TTS available")
        except ImportError:
            logger.warning("⚠️ Edge-TTS not available")
        
        logger.info(f"Available TTS engines: {self.available_engines}")
    
    def _speak_gtts(self, text: str, lang: str = "vi", slow: bool = False) -> bool:
        """Use Google TTS (requires internet)"""
        try:
            from gtts import gTTS
            
            tts = gTTS(text=text, lang=lang, slow=slow)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts.save(tmp_file.name)
                
                # Play using pygame
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Clean up
                os.unlink(tmp_file.name)
                return True
                
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return False
    
    def _speak_edge_tts(self, text: str, voice: str = "vi-VN-HoaiMyNeural") -> bool:
        """Use Microsoft Edge TTS (requires internet)"""
        try:
            import asyncio
            import edge_tts
            
            async def _edge_speak():
                tts = edge_tts.Communicate(text, voice)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    async for chunk in tts.stream():
                        if chunk["type"] == "audio":
                            tmp_file.write(chunk["data"])
                    
                    # Play the file
                    pygame.mixer.music.load(tmp_file.name)
                    pygame.mixer.music.play()
                    
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)
                    
                    os.unlink(tmp_file.name)
            
            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_edge_speak())
            loop.close()
            return True
            
        except Exception as e:
            logger.error(f"Edge TTS error: {e}")
            return False
    
    def _speak_espeak(self, text: str, voice: str = "vi", speed: int = 150, pitch: int = 50) -> bool:
        """Use espeak-ng (offline, basic quality)"""
        try:
            cmd = [
                "espeak-ng", 
                "-v", voice,
                "-s", str(speed),  # Speed (words per minute)
                "-p", str(pitch),  # Pitch (0-99)
                "-a", "100",       # Amplitude (volume)
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"espeak error: {e}")
            return False
    
    def _speak_festival(self, text: str) -> bool:
        """Use Festival TTS (offline, better quality than espeak)"""
        try:
            # Create a temporary festival script
            script_content = f'''
(set! utt1 (Utterance Text "{text}"))
(utt.synth utt1)
(utt.play utt1)
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.scm', delete=False) as script_file:
                script_file.write(script_content)
                script_file.flush()
                
                cmd = ["festival", "-b", script_file.name]
                result = subprocess.run(cmd, capture_output=True, timeout=30)
                
                os.unlink(script_file.name)
                return result.returncode == 0
                
        except Exception as e:
            logger.error(f"Festival error: {e}")
            return False
    
    def _speak_zalo_api(self, text: str, voice: str = "female") -> bool:
        """Use Zalo AI TTS API (requires internet and API key)"""
        try:
            # This would require Zalo AI API credentials
            # Placeholder for future implementation
            logger.warning("Zalo TTS not implemented yet")
            return False
            
        except Exception as e:
            logger.error(f"Zalo TTS error: {e}")
            return False
    
    def speak(self, text: str, engine: Optional[str] = None, **kwargs) -> bool:
        """
        Speak text using specified or preferred engine
        
        Args:
            text (str): Text to speak
            engine (str, optional): Engine to use, falls back to preferred
            **kwargs: Engine-specific parameters
            
        Returns:
            bool: Success status
        """
        if not text.strip():
            return False
        
        # Determine which engine to use
        target_engine = engine or self.preferred_engine
        
        # Try preferred engine first
        if target_engine in self.available_engines:
            success = self._try_engine(target_engine, text, **kwargs)
            if success:
                return True
        
        # Fallback to other available engines
        for fallback_engine in self.available_engines:
            if fallback_engine != target_engine:
                logger.info(f"Falling back to {fallback_engine}")
                success = self._try_engine(fallback_engine, text, **kwargs)
                if success:
                    return True
        
        logger.error("All TTS engines failed")
        return False
    
    def _try_engine(self, engine: str, text: str, **kwargs) -> bool:
        """Try speaking with specific engine"""
        try:
            if engine == "gtts":
                return self._speak_gtts(text, 
                                      lang=kwargs.get('lang', 'vi'),
                                      slow=kwargs.get('slow', False))
            elif engine == "edge":
                return self._speak_edge_tts(text, 
                                          voice=kwargs.get('voice', 'vi-VN-HoaiMyNeural'))
            elif engine == "espeak":
                return self._speak_espeak(text,
                                        voice=kwargs.get('voice', 'vi'),
                                        speed=kwargs.get('speed', 150),
                                        pitch=kwargs.get('pitch', 50))
            elif engine == "festival":
                return self._speak_festival(text)
            elif engine == "zalo":
                return self._speak_zalo_api(text, 
                                          voice=kwargs.get('voice', 'female'))
            else:
                logger.error(f"Unknown engine: {engine}")
                return False
                
        except Exception as e:
            logger.error(f"Engine {engine} failed: {e}")
            return False
    
    def get_available_engines(self) -> list:
        """Get list of available engines"""
        return self.available_engines.copy()
    
    def set_preferred_engine(self, engine: str):
        """Set preferred TTS engine"""
        if engine in self.available_engines:
            self.preferred_engine = engine
            logger.info(f"Preferred engine set to: {engine}")
        else:
            logger.warning(f"Engine {engine} not available")


# Convenience functions for direct use
_default_tts = None

def init_vietnamese_tts(preferred_engine="gtts"):
    """Initialize the default TTS instance"""
    global _default_tts
    _default_tts = VietnameseTTS(preferred_engine)
    return _default_tts

def speak_vietnamese(text: str, engine: Optional[str] = None, **kwargs) -> bool:
    """
    Speak Vietnamese text using the default TTS instance
    
    Args:
        text (str): Text to speak in Vietnamese
        engine (str, optional): Specific engine to use
        **kwargs: Engine-specific parameters
        
    Returns:
        bool: Success status
    """
    global _default_tts
    if _default_tts is None:
        _default_tts = VietnameseTTS()
    
    return _default_tts.speak(text, engine, **kwargs)

def get_available_voices():
    """Get available Vietnamese voices for different engines"""
    return {
        "edge": [
            "vi-VN-HoaiMyNeural",   # Female voice
            "vi-VN-NamMinhNeural"   # Male voice
        ],
        "gtts": ["vi"],
        "espeak": ["vi", "vi+f3", "vi+m3"],  # Different variants
        "festival": ["vi"]
    }

# Demo function
def demo_vietnamese_tts():
    """Demo all available TTS engines"""
    tts = VietnameseTTS()
    test_text = "Xin chào, tôi là trợ lý giọng nói tiếng Việt của bạn."
    
    print("🎤 Testing Vietnamese TTS engines:")
    
    for engine in tts.get_available_engines():
        print(f"\n🔊 Testing {engine}...")
        success = tts.speak(test_text, engine=engine)
        if success:
            print(f"✅ {engine} works!")
        else:
            print(f"❌ {engine} failed")
        time.sleep(1)  # Pause between tests

if __name__ == "__main__":
    # Run demo if called directly
    demo_vietnamese_tts()