"""Unit tests for GameService info methods with hints (v1.5.0).

Tests the new info methods that return (message, hint) tuples:
- get_waste_info: Waste pile status with SHIFT+S navigation hint
- get_stock_info: Stock pile count with D/P draw hint
- get_game_report: Complete report (no hint)
- get_table_info: Complete table overview (no hint)
- get_timer_info: Elapsed time with options menu hint
- get_settings_info: Settings summary with options menu hint
"""

import pytest
from src.domain.services.game_service import GameService
from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck
from src.domain.rules.solitaire_rules import SolitaireRules
from src.domain.models.card import Card


@pytest.fixture
def setup_game_service():
    """Create game service with test data."""
    deck = FrenchDeck()
    deck.crea()
    table = GameTable(deck)
    rules = SolitaireRules(deck)
    service = GameService(table, rules)
    return service, table


class TestGetWasteInfo:
    """Test get_waste_info() returns tuple with hint."""
    
    def test_returns_tuple(self, setup_game_service):
        """get_waste_info should return (message, hint) tuple."""
        service, table = setup_game_service
        
        result = service.get_waste_info()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        message, hint = result
        assert isinstance(message, str)
        assert hint is None or isinstance(hint, str)
    
    def test_empty_waste_no_hint(self, setup_game_service):
        """Empty waste pile should return None hint."""
        service, table = setup_game_service
        table.pile_scarti.clear()
        
        message, hint = service.get_waste_info()
        
        assert "vuota" in message.lower()
        assert hint is None
    
    def test_waste_with_cards_has_hint(self, setup_game_service):
        """Waste with cards should include SHIFT+S hint."""
        service, table = setup_game_service
        
        # Add cards to waste
        if len(table.pile_mazzo.cards) > 0:
            for _ in range(3):
                if len(table.pile_mazzo.cards) > 0:
                    card = table.pile_mazzo.cards.pop(0)
                    table.pile_scarti.aggiungi_carta(card)
        
        message, hint = service.get_waste_info()
        
        assert "scarti" in message.lower()
        if not table.pile_scarti.is_empty():
            assert hint is not None
            assert "shift+s" in hint.lower() or "shift-s" in hint.lower()
    
    def test_waste_message_includes_count(self, setup_game_service):
        """Message should include card count."""
        service, table = setup_game_service
        
        # Add 2 cards
        for _ in range(2):
            if len(table.pile_mazzo.cards) > 0:
                card = table.pile_mazzo.cards.pop(0)
                table.pile_scarti.aggiungi_carta(card)
        
        message, hint = service.get_waste_info()
        
        if not table.pile_scarti.is_empty():
            # Should mention "carte" or count
            assert "carte" in message.lower() or "carta" in message.lower()


class TestGetStockInfo:
    """Test get_stock_info() returns tuple with hint."""
    
    def test_returns_tuple(self, setup_game_service):
        """get_stock_info should return (message, hint) tuple."""
        service, table = setup_game_service
        
        result = service.get_stock_info()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_empty_stock_no_hint(self, setup_game_service):
        """Empty stock should return None hint."""
        service, table = setup_game_service
        table.pile_mazzo.clear()
        
        message, hint = service.get_stock_info()
        
        assert "vuoto" in message.lower() or "0" in message
        assert hint is None
    
    def test_stock_with_cards_has_hint(self, setup_game_service):
        """Stock with cards should include D/P draw hint."""
        service, table = setup_game_service
        
        message, hint = service.get_stock_info()
        
        if not table.pile_mazzo.is_empty():
            assert hint is not None
            assert ("d" in hint.lower() or "p" in hint.lower())
            assert "pescare" in hint.lower() or "pesca" in hint.lower()
    
    def test_stock_message_includes_count(self, setup_game_service):
        """Message should include remaining card count."""
        service, table = setup_game_service
        
        message, hint = service.get_stock_info()
        
        # Should mention "carte" or "carta" or "mazzo"
        assert any(word in message.lower() for word in ["carte", "carta", "mazzo", "riman"])


class TestGetGameReport:
    """Test get_game_report() returns tuple without hint."""
    
    def test_returns_tuple(self, setup_game_service):
        """get_game_report should return (message, None) tuple."""
        service, table = setup_game_service
        service.start_game()
        
        result = service.get_game_report()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        message, hint = result
        assert isinstance(message, str)
        assert hint is None
    
    def test_hint_is_none(self, setup_game_service):
        """Report should not have hint (self-contained info)."""
        service, table = setup_game_service
        service.start_game()
        
        message, hint = service.get_game_report()
        
        assert hint is None
    
    def test_message_includes_statistics(self, setup_game_service):
        """Message should include game statistics."""
        service, table = setup_game_service
        service.start_game()
        service.move_count = 5
        
        message, hint = service.get_game_report()
        
        assert "report" in message.lower() or "partita" in message.lower()
        assert "mosse" in message.lower() or "5" in message
        assert "tempo" in message.lower()


class TestGetTableInfo:
    """Test get_table_info() returns tuple without hint."""
    
    def test_returns_tuple(self, setup_game_service):
        """get_table_info should return (message, None) tuple."""
        service, table = setup_game_service
        
        result = service.get_table_info()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        message, hint = result
        assert isinstance(message, str)
        assert hint is None
    
    def test_hint_is_none(self, setup_game_service):
        """Table info should not have hint (comprehensive info)."""
        service, table = setup_game_service
        
        message, hint = service.get_table_info()
        
        assert hint is None
    
    def test_message_includes_table_overview(self, setup_game_service):
        """Message should include all pile types."""
        service, table = setup_game_service
        
        message, hint = service.get_table_info()
        
        assert "pile" in message.lower()
        # Should mention different pile types
        assert any(word in message.lower() for word in ["base", "semi", "mazzo", "scarti"])


class TestGetTimerInfo:
    """Test get_timer_info() returns tuple with options hint."""
    
    def test_returns_tuple(self, setup_game_service):
        """get_timer_info should return (message, hint) tuple."""
        service, table = setup_game_service
        service.start_game()
        
        result = service.get_timer_info()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        message, hint = result
        assert isinstance(message, str)
        assert isinstance(hint, str)
    
    def test_hint_mentions_options(self, setup_game_service):
        """Hint should mention options menu (O key)."""
        service, table = setup_game_service
        service.start_game()
        
        message, hint = service.get_timer_info()
        
        assert hint is not None
        assert "o" in hint.lower()
        assert "opzioni" in hint.lower() or "timer" in hint.lower()
    
    def test_message_includes_time(self, setup_game_service):
        """Message should include elapsed time."""
        service, table = setup_game_service
        service.start_game()
        
        message, hint = service.get_timer_info()
        
        assert "tempo" in message.lower()
        assert "minuti" in message.lower() or "secondi" in message.lower()


class TestGetSettingsInfo:
    """Test get_settings_info() returns tuple with options hint."""
    
    def test_returns_tuple(self, setup_game_service):
        """get_settings_info should return (message, hint) tuple."""
        service, table = setup_game_service
        
        result = service.get_settings_info()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        message, hint = result
        assert isinstance(message, str)
        assert isinstance(hint, str)
    
    def test_hint_mentions_options_menu(self, setup_game_service):
        """Hint should mention opening options menu."""
        service, table = setup_game_service
        
        message, hint = service.get_settings_info()
        
        assert hint is not None
        assert "o" in hint.lower()
        assert "opzioni" in hint.lower() or "menu" in hint.lower()
    
    def test_message_includes_settings(self, setup_game_service):
        """Message should include settings summary."""
        service, table = setup_game_service
        
        message, hint = service.get_settings_info()
        
        assert "impostazioni" in message.lower() or "settings" in message.lower()
        # Should mention some setting categories
        assert any(word in message.lower() for word in ["mazzo", "difficoltà", "timer"])


class TestHintConsistency:
    """Test consistency across all info methods."""
    
    def test_all_hints_are_italian(self, setup_game_service):
        """All hints should be in Italian."""
        service, table = setup_game_service
        service.start_game()
        
        # Add some cards to waste
        if len(table.pile_mazzo.cards) > 0:
            card = table.pile_mazzo.cards.pop(0)
            table.pile_scarti.aggiungi_carta(card)
        
        # Collect all hints
        hints = []
        _, hint = service.get_waste_info()
        if hint:
            hints.append(hint)
        
        _, hint = service.get_stock_info()
        if hint:
            hints.append(hint)
        
        _, hint = service.get_timer_info()
        if hint:
            hints.append(hint)
        
        _, hint = service.get_settings_info()
        if hint:
            hints.append(hint)
        
        # Check Italian keywords (not English)
        for hint in hints:
            assert not any(word in hint.lower() for word in ["press", "use", "open", "modify"])
    
    def test_hints_are_actionable(self, setup_game_service):
        """All hints should suggest specific actions."""
        service, table = setup_game_service
        service.start_game()
        
        # Add card to waste
        if len(table.pile_mazzo.cards) > 0:
            card = table.pile_mazzo.cards.pop(0)
            table.pile_scarti.aggiungi_carta(card)
        
        # Collect hints
        hints = []
        for method in [service.get_waste_info, service.get_stock_info, 
                       service.get_timer_info, service.get_settings_info]:
            _, hint = method()
            if hint:
                hints.append(hint)
        
        # Each hint should mention an action or key
        for hint in hints:
            has_action = any(word in hint.lower() for word in 
                           ["premi", "usa", "shift", "o", "d", "p", "s"])
            assert has_action
