"""User interface components for infrastructure layer.

Provides UI adapters like menus and displays that don't contain
business logic but interface with external systems (wxPython, etc.).

This package follows Dependency Injection pattern to keep
domain/application layers decoupled from specific UI frameworks.
"""

from src.infrastructure.ui.menu import VirtualMenu
from src.infrastructure.ui.dialog_provider import DialogProvider
from src.infrastructure.ui.basic_panel import BasicPanel
from src.infrastructure.ui.menu_panel import MenuPanel
from src.infrastructure.ui.gameplay_panel import GameplayPanel
from src.infrastructure.ui.view_manager import ViewManager

__all__ = [
    "VirtualMenu", 
    "DialogProvider",
    "BasicPanel",
    "MenuPanel",
    "GameplayPanel",
    "ViewManager"
]
