"""Accessibility infrastructure for screen reader support.

Provides text-to-speech functionality and screen reader integration
for blind users. Supports multiple TTS engines through TtsProvider.

Migrated from src/infrastructure/audio/ to better reflect purpose.
"""

from src.infrastructure.accessibility.screen_reader import ScreenReader
from src.infrastructure.accessibility.tts_provider import (
    TtsProvider,
    create_tts_provider,
    Sapi5TtsProvider,
    EspeakTtsProvider
)

__all__ = [
    "ScreenReader",
    "TtsProvider",
    "create_tts_provider",
    "Sapi5TtsProvider",
    "EspeakTtsProvider"
]
