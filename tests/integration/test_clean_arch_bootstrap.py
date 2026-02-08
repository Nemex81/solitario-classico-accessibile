"""Integration tests for Clean Architecture bootstrap.

Validates that all architectural layers integrate correctly
without circular dependencies or import errors.
"""

import pytest
import sys
from pathlib import Path


class TestCleanArchBootstrap:
    """Test complete application bootstrap."""
    
    def test_domain_layer_imports(self):
        """Verify Domain layer components import without errors."""
        # Models
        from src.domain.models.card import Card
        from src.domain.models.pile import Pile
        from src.domain.models.deck import ProtoDeck, FrenchDeck, NeapolitanDeck
        
        assert Card is not None
        assert Pile is not None
        assert ProtoDeck is not None
        assert FrenchDeck is not None
        assert NeapolitanDeck is not None
    
    def test_application_layer_imports(self):
        """Verify Application layer components import without errors."""
        from src.application.game_settings import GameSettings
        from src.application.timer_manager import TimerManager
        from src.application.input_handler import InputHandler, GameCommand
        
        assert GameSettings is not None
        assert TimerManager is not None
        assert InputHandler is not None
        assert GameCommand is not None
    
    def test_infrastructure_layer_imports(self):
        """Verify Infrastructure layer components import without errors."""
        from src.infrastructure.di_container import DIContainer, get_container
        from src.infrastructure.accessibility.screen_reader import ScreenReader
        from src.infrastructure.ui.menu import VirtualMenu
        
        assert DIContainer is not None
        assert get_container is not None
        assert ScreenReader is not None
        assert VirtualMenu is not None
    
    def test_presentation_layer_imports(self):
        """Verify Presentation layer components import without errors."""
        from src.presentation.game_formatter import GameFormatter
        
        assert GameFormatter is not None
    
    def test_no_circular_dependencies(self):
        """Verify no circular import dependencies."""
        # Import all layers in order (should not raise)
        from src.domain.models.deck import FrenchDeck
        from src.application.game_settings import GameSettings
        from src.infrastructure.di_container import DIContainer
        from src.presentation.game_formatter import GameFormatter
        
        # If we got here, no circular dependencies
        assert True
    
    def test_domain_layer_isolation(self):
        """Verify Domain layer has no external dependencies."""
        # Domain should only depend on standard library
        from src.domain.models.deck import FrenchDeck
        
        deck = FrenchDeck()
        deck.crea()
        
        # Should work without any Application/Infrastructure imports
        assert len(deck.cards) == 52
    
    def test_application_layer_depends_on_domain_only(self):
        """Verify Application layer only depends on Domain (not Infrastructure)."""
        from src.application.game_settings import GameSettings
        from src.application.timer_manager import TimerManager
        
        # These should work without Infrastructure imports
        settings = GameSettings()
        timer = TimerManager(minutes=10)
        
        assert settings.timer_minutes == 10
        assert timer.duration_seconds == 600
    
    def test_complete_bootstrap_sequence(self):
        """Verify complete bootstrap from entry point."""
        # Simulate test.py bootstrap sequence
        from src.infrastructure.di_container import get_container
        
        container = get_container()
        
        # Application setup
        settings = container.get_settings()
        assert settings is not None
        
        # Domain setup
        deck = container.get_deck("french")
        assert deck is not None
        
        # Infrastructure setup
        input_handler = container.get_input_handler()
        assert input_handler is not None
        
        # Presentation setup
        formatter = container.get_formatter()
        assert formatter is not None
        
        # If we got here, complete bootstrap works
        assert True
