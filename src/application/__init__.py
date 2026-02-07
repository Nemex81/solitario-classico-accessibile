"""Application layer for game engine facade.

This layer provides the high-level GameEngine facade that orchestrates
all domain and infrastructure components for a clean game API.
"""

from src.application.game_engine import GameEngine

__all__ = ["GameEngine"]
