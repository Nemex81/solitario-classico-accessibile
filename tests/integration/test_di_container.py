"""Integration tests for DI Container.

Validates dependency injection container can create and
wire all application components correctly.
"""

import pytest
from src.infrastructure.di_container import (
    DIContainer,
    get_container,
    reset_container_complete
)
from src.application.game_settings import GameSettings
from src.application.timer_manager import TimerManager
from src.application.input_handler import InputHandler
from src.domain.models.deck import FrenchDeck, NeapolitanDeck
from src.presentation.game_formatter import GameFormatter


class TestDIContainer:
    """Test dependency injection container."""
    
    def setup_method(self):
        """Reset container before each test."""
        reset_container_complete()
    
    def test_container_singleton(self):
        """Verify get_container returns same instance."""
        container1 = get_container()
        container2 = get_container()
        assert container1 is container2
    
    def test_settings_singleton(self):
        """Verify GameSettings is singleton."""
        container = DIContainer()
        settings1 = container.get_settings()
        settings2 = container.get_settings()
        assert settings1 is settings2
    
    def test_settings_persistence_across_resets(self):
        """Verify settings persist after reset()."""
        container = DIContainer()
        settings = container.get_settings()
        settings.deck_type = "neapolitan"
        
        container.reset()  # Clear instances but keep settings
        
        settings2 = container.get_settings()
        assert settings2.deck_type == "neapolitan"
        assert settings2 is settings  # Same instance
    
    def test_settings_cleared_after_reset_all(self):
        """Verify settings cleared after reset_all()."""
        container = DIContainer()
        settings = container.get_settings()
        settings.deck_type = "neapolitan"
        
        container.reset_all()  # Clear everything
        
        settings2 = container.get_settings()
        assert settings2.deck_type == "french"  # Default
        assert settings2 is not settings  # New instance
    
    def test_deck_factory_french(self):
        """Verify French deck creation."""
        container = DIContainer()
        deck = container.get_deck("french")
        
        assert isinstance(deck, FrenchDeck)
        assert deck.tipo == "french"
    
    def test_deck_factory_neapolitan(self):
        """Verify Neapolitan deck creation."""
        container = DIContainer()
        deck = container.get_deck("neapolitan")
        
        assert isinstance(deck, NeapolitanDeck)
        assert deck.tipo == "neapolitan"
    
    def test_deck_factory_uses_settings(self):
        """Verify deck type from settings when not specified."""
        container = DIContainer()
        settings = container.get_settings()
        settings.deck_type = "neapolitan"
        
        deck = container.get_deck()  # No type specified
        assert isinstance(deck, NeapolitanDeck)
    
    def test_deck_factory_invalid_type(self):
        """Verify error on invalid deck type."""
        container = DIContainer()
        
        with pytest.raises(ValueError, match="Unknown deck type"):
            container.get_deck("invalid")
    
    def test_timer_manager_factory(self):
        """Verify TimerManager creation with settings."""
        container = DIContainer()
        settings = container.get_settings()
        settings.timer_minutes = 15
        
        timer = container.get_timer_manager()
        assert isinstance(timer, TimerManager)
        assert timer.duration_seconds == 15 * 60
    
    def test_timer_manager_new_instance_each_call(self):
        """Verify TimerManager is factory (not singleton)."""
        container = DIContainer()
        timer1 = container.get_timer_manager()
        timer2 = container.get_timer_manager()
        
        assert timer1 is not timer2  # Different instances
    
    def test_input_handler_singleton(self):
        """Verify InputHandler is singleton."""
        container = DIContainer()
        handler1 = container.get_input_handler()
        handler2 = container.get_input_handler()
        
        assert isinstance(handler1, InputHandler)
        assert handler1 is handler2
    
    def test_formatter_singleton(self):
        """Verify GameFormatter is singleton."""
        container = DIContainer()
        formatter1 = container.get_formatter()
        formatter2 = container.get_formatter()
        
        assert isinstance(formatter1, GameFormatter)
        assert formatter1 is formatter2
    
    def test_formatter_language_variants(self):
        """Verify different formatters for different languages."""
        container = DIContainer()
        formatter_it = container.get_formatter("it")
        formatter_en = container.get_formatter("en")
        
        assert formatter_it is not formatter_en  # Different instances
    
    def test_screen_reader_singleton(self):
        """Verify ScreenReader is singleton."""
        container = DIContainer()
        sr1 = container.get_screen_reader()
        sr2 = container.get_screen_reader()
        
        assert sr1 is sr2
