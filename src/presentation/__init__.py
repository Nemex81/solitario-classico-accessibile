"""Presentation layer for output formatting.

Transforms domain models and application state into
human-readable text for screen reader output.

Components:
- GameFormatter: Text formatting for TTS output
"""

from src.presentation.game_formatter import GameFormatter

__all__ = ["GameFormatter"]
