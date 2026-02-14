"""
UI Factories Module - Factory Pattern for Window and Widget Creation

This module provides factory classes for creating UI components following
the Factory Pattern from hs_deckmanager.

Factories:
    - ViewFactory: Creates windows and panels with dependency injection
    - WidgetFactory: Creates wxPython widgets with accessibility support

Version:
    v2.2.0: Created as part of Window Management Migration
"""

from src.infrastructure.ui.factories.view_factory import ViewFactory, WindowKey, ALL_WINDOWS
from src.infrastructure.ui.factories.widget_factory import WidgetFactory

__all__ = [
    'ViewFactory',
    'WindowKey',
    'ALL_WINDOWS',
    'WidgetFactory',
]
