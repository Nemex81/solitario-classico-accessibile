"""User interface components for infrastructure layer.

Provides UI adapters like menus and displays that don't contain
business logic but interface with external systems (PyGame, etc.).
"""

from src.infrastructure.ui.menu import VirtualMenu

__all__ = ["VirtualMenu"]
