"""TTS provider abstraction for multiple speech engines.

Supports Windows SAPI5, NVDA, and future engines like espeak.
Provides a unified interface for text-to-speech functionality with
graceful degradation when engines are unavailable.

Migrated from: src/infrastructure/audio/tts_provider.py (SHA: ad5a7045)
"""

from abc import ABC, abstractmethod
import logging
import sys
from typing import Optional, Any

_tts_logger = logging.getLogger("ui")


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


class Sapi5TtsProvider(TtsProvider):
    """Windows SAPI5 TTS provider.
    
    Uses accessible_output2 to interface with Windows Speech API (SAPI5).
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
            from accessible_output2.outputs import sapi5

            self.engine: Any = sapi5.SAPI5()
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
        self.engine.speak(text, interrupt=False)
    
    def stop(self) -> None:
        """Stop current SAPI5 speech."""
        self.engine.silence()
    
    def set_rate(self, rate: int) -> None:
        """Set SAPI5 speech rate.
        
        Args:
            rate: Speech rate from -10 to 10.
        """
        self.engine.set_rate(rate)
    
    def set_volume(self, volume: float) -> None:
        """Set SAPI5 volume.
        
        Args:
            volume: Volume from 0.0 to 1.0
        """
        self.engine.set_volume(round(max(0.0, min(1.0, volume)) * 100))


class NvdaTtsProvider(TtsProvider):
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


class EspeakTtsProvider(TtsProvider):
    """eSpeak TTS provider for Linux/cross-platform.
    
    Placeholder for future implementation.
    Uses espeak command-line tool for text-to-speech.
    
    Raises:
        NotImplementedError: Implementation pending
    """
    
    def __init__(self) -> None:
        raise NotImplementedError("eSpeak provider not yet implemented")
    
    def speak(self, text: str, interrupt: bool = False) -> None:
        raise NotImplementedError()
    
    def stop(self) -> None:
        raise NotImplementedError()
    
    def set_rate(self, rate: int) -> None:
        raise NotImplementedError()
    
    def set_volume(self, volume: float) -> None:
        raise NotImplementedError()


class DummyTtsProvider(TtsProvider):
    """No-op TTS provider — fallback when all speech engines are unavailable.

    Every method is a silent no-op so the application starts and runs
    fully even when neither NVDA nor SAPI5 is available (e.g. headless CI,
    fresh test VM, or frozen build on a machine without NVDA).

    Version
    -------
    v4.5.1: Added for frozen-runtime hardening.
    """

    def speak(self, text: str, interrupt: bool = False) -> None:
        pass

    def stop(self) -> None:
        pass

    def set_rate(self, rate: int) -> None:
        pass

    def set_volume(self, volume: float) -> None:
        pass


def create_tts_provider(engine: str = "auto") -> TtsProvider:
    """Factory function to create TTS provider.

    Attempts to create the specified TTS provider with automatic fallback
    when ``engine="auto"``.  Fallback chain: NVDA → SAPI5 → DummyTtsProvider.
    Each failed attempt is logged at WARNING level so the operator can see
    why a provider was skipped; the application never crashes even when all
    real providers are unavailable.

    Args:
        engine: Engine name.
            - ``"auto"``: Try NVDA, then SAPI5, then DummyTtsProvider.
            - ``"nvda"``: Use NVDA screen reader (raises on failure).
            - ``"sapi5"``: Use Windows SAPI5 (raises on failure).
            - ``"espeak"``: Use eSpeak (not yet implemented).
            - ``"dummy"``: Return DummyTtsProvider directly (for testing).

    Returns:
        TtsProvider instance.

    Raises:
        ValueError: If an unknown engine name is specified.
        RuntimeError: If the requested named engine fails to initialise.
    """
    if engine == "auto":
        try:
            return NvdaTtsProvider()
        except RuntimeError as nvda_err:
            _tts_logger.warning("TTS: NVDA non disponibile, fallback a SAPI5: %s", nvda_err)

        try:
            return Sapi5TtsProvider()
        except RuntimeError as sapi_err:
            _tts_logger.warning(
                "TTS: SAPI5 non disponibile, fallback a DummyTtsProvider: %s", sapi_err
            )

        _tts_logger.warning(
            "TTS: nessun motore disponibile, avvio in modalità silenziosa (DummyTtsProvider)."
        )
        return DummyTtsProvider()

    if engine == "nvda":
        return NvdaTtsProvider()

    if engine == "sapi5":
        return Sapi5TtsProvider()

    if engine == "espeak":
        return EspeakTtsProvider()

    if engine == "dummy":
        return DummyTtsProvider()

    raise ValueError(f"Unknown TTS engine: {engine}")
