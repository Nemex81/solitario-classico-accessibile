"""Audio infrastructure for screen reader and TTS support.

This package provides accessible audio feedback for the solitaire game
through text-to-speech engines and screen reader integration.
"""

from src.infrastructure.audio.screen_reader import ScreenReader
from src.infrastructure.audio.tts_provider import (
    TtsProvider,
    Sapi5Provider,
    NvdaProvider,
    create_tts_provider,
)

__all__ = [
    "ScreenReader",
    "TtsProvider",
    "Sapi5Provider",
    "NvdaProvider",
    "create_tts_provider",
]
