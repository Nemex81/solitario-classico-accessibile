"""Infrastructure layer for external adapters.

Provides adapters for external systems (TTS, UI, etc.) and
dependency injection container for application wiring.

Components:
- accessibility/: Screen reader and TTS providers
- ui/: PyGame UI components (menus)
- di_container: Dependency injection container
"""

from src.infrastructure.di_container import (
    DIContainer,
    get_container,
    reset_container,
    reset_container_complete
)

__all__ = [
    "DIContainer",
    "get_container",
    "reset_container",
    "reset_container_complete"
]
