"""User interface components for infrastructure layer.

Provides UI adapters like menus and displays that don't contain
business logic but interface with external systems (PyGame, etc.).

This package follows Dependency Injection pattern to keep
domain/application layers decoupled from specific UI frameworks.
"""

from src.infrastructure.ui.menu import VirtualMenu
from src.infrastructure.ui.dialog_provider import DialogProvider

__all__ = ["VirtualMenu", "DialogProvider"]
