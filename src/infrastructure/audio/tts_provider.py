"""TTS provider abstraction for multiple speech engines.

Supports Windows SAPI5, NVDA, and future engines like espeak.
Provides a unified interface for text-to-speech functionality with
graceful degradation when engines are unavailable.
"""

from abc import ABC, abstractmethod
import sys
from typing import Optional, Any


class TtsProvider(ABC):
    """Abstract TTS provider interface.
    
    Defines the contract for text-to-speech engines. All TTS providers
    must implement these methods to ensure consistent behavior across
    different speech engines.
    """
    
    @abstractmethod
    def speak(self, text: str, interrupt: bool = False) -> None:
        """Speak text using TTS engine.
        
        Args:
            text: Text to speak
            interrupt: Stop current speech before speaking
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop current speech immediately."""
        pass
    
    @abstractmethod
    def set_rate(self, rate: int) -> None:
        """Set speech rate.
        
        Args:
            rate: Speech rate from -10 (slowest) to 10 (fastest)
        """
        pass
    
    @abstractmethod
    def set_volume(self, volume: float) -> None:
        """Set volume level.
        
        Args:
            volume: Volume level from 0.0 (silent) to 1.0 (maximum)
        """
        pass


class Sapi5Provider(TtsProvider):
    """Windows SAPI5 TTS provider.
    
    Uses pyttsx3 library to interface with Windows Speech API (SAPI5).
    Only available on Windows platforms.
    
    Raises:
        RuntimeError: If not running on Windows or if SAPI5 initialization fails
    """
    
    def __init__(self) -> None:
        """Initialize SAPI5 TTS engine.
        
        Raises:
            RuntimeError: If SAPI5 is not available or initialization fails
        """
        if sys.platform != "win32":
            raise RuntimeError("SAPI5 only available on Windows")
        
        try:
            import pyttsx3  # type: ignore[import-not-found]
            self.engine: Any = pyttsx3.init(driverName="sapi5")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize SAPI5: {e}")
    
    def speak(self, text: str, interrupt: bool = False) -> None:
        """Speak text using SAPI5.
        
        Args:
            text: Text to speak
            interrupt: If True, stops current speech before speaking
        """
        if interrupt:
            self.stop()
        self.engine.say(text)
        self.engine.runAndWait()
    
    def stop(self) -> None:
        """Stop current SAPI5 speech."""
        self.engine.stop()
    
    def set_rate(self, rate: int) -> None:
        """Set SAPI5 speech rate.
        
        Args:
            rate: Speech rate from -10 to 10. Mapped to SAPI5 range 125-250
                 (default 200)
        """
        # SAPI5 rate: 125-250 (default 200)
        sapi5_rate = 200 + (rate * 5)
        self.engine.setProperty('rate', sapi5_rate)
    
    def set_volume(self, volume: float) -> None:
        """Set SAPI5 volume.
        
        Args:
            volume: Volume from 0.0 to 1.0
        """
        self.engine.setProperty('volume', volume)


class NvdaProvider(TtsProvider):
    """NVDA screen reader provider.
    
    Uses accessible_output2 library to interface with NVDA screen reader.
    Requires NVDA to be running on the system.
    
    Raises:
        RuntimeError: If NVDA is not running or initialization fails
    """
    
    def __init__(self) -> None:
        """Initialize NVDA screen reader interface.
        
        Raises:
            RuntimeError: If NVDA is not available or not running
        """
        try:
            from accessible_output2.outputs import nvda
            self.nvda: Any = nvda.NVDA()
            if not self.nvda.is_active():
                raise RuntimeError("NVDA not running")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize NVDA: {e}")
    
    def speak(self, text: str, interrupt: bool = False) -> None:
        """Speak text using NVDA.
        
        Args:
            text: Text to speak
            interrupt: If True, silences current speech before speaking
        """
        self.nvda.speak(text, interrupt=interrupt)
    
    def stop(self) -> None:
        """Stop current NVDA speech."""
        self.nvda.silence()
    
    def set_rate(self, rate: int) -> None:
        """Set NVDA speech rate.
        
        Note: NVDA rate control is not exposed via accessible_output2.
        This method is a no-op but required by the interface.
        
        Args:
            rate: Speech rate from -10 to 10 (ignored)
        """
        # NVDA rate control not exposed via accessible_output2
        pass
    
    def set_volume(self, volume: float) -> None:
        """Set NVDA volume.
        
        Note: NVDA volume control is not exposed via accessible_output2.
        This method is a no-op but required by the interface.
        
        Args:
            volume: Volume from 0.0 to 1.0 (ignored)
        """
        # NVDA volume control not exposed via accessible_output2
        pass


def create_tts_provider(engine: str = "auto") -> TtsProvider:
    """Factory function to create TTS provider.
    
    Attempts to create the specified TTS provider, with automatic
    fallback when engine="auto". The auto mode tries NVDA first
    (preferred for blind users), then falls back to SAPI5.
    
    Args:
        engine: Engine name. Options:
            - "auto": Try NVDA first, then SAPI5
            - "nvda": Use NVDA screen reader
            - "sapi5": Use Windows SAPI5
            
    Returns:
        TTS provider instance
        
    Raises:
        RuntimeError: If no compatible engine available (auto mode)
        ValueError: If unknown engine name specified
    """
    if engine == "auto":
        # Try NVDA first (preferred for blind users)
        try:
            return NvdaProvider()
        except RuntimeError:
            pass
        
        # Fallback to SAPI5
        try:
            return Sapi5Provider()
        except RuntimeError:
            pass
        
        raise RuntimeError("No TTS engine available")
    
    if engine == "nvda":
        return NvdaProvider()
    
    if engine == "sapi5":
        return Sapi5Provider()
    
    raise ValueError(f"Unknown TTS engine: {engine}")
