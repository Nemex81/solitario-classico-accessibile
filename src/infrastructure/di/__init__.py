"""Dependency injection module for IoC container pattern.

Port from hs_deckmanager with simplifications for solitario.

Provides:
- DependencyContainer: IoC container for dependency injection
"""

from .dependency_container import DependencyContainer

__all__ = ["DependencyContainer"]
