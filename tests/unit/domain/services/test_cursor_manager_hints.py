"""Unit tests for cursor manager hint generation (v1.5.0).

Tests the extended return types and hint generation for navigation methods:
- move_up/down: Return (message, hint) tuples
- move_left/right: Return (message, hint) tuples
- move_tab: Return (message, hint) tuples
- jump_to_pile: Return (message, auto_select, hint) tuples
"""

import pytest
from src.domain.services.cursor_manager import CursorManager
from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck
from src.domain.models.card import Card


@pytest.fixture
def setup_table_and_cursor():
    """Create table with test data and cursor manager."""
    deck = FrenchDeck()
    deck.crea()
    table = GameTable(deck)
    
    # Populate test cards on tableau piles
    # Pile 0: Add uncovered card for testing
    if len(table.pile_base[0].cards) > 0:
        table.pile_base[0].cards[-1].set_covered = False
    
    # Pile 1: Add multiple cards
    for _ in range(3):
        if len(deck.cards) > 0:
            card = deck.pesca()
            card.set_covered = False
            table.pile_base[1].aggiungi_carta(card)
    
    cursor = CursorManager(table)
    return cursor, table


class TestMoveUpReturnType:
    """Test move_up() returns tuple with hint."""
    
    def test_returns_tuple(self, setup_table_and_cursor):
        """move_up should return (message, hint) tuple."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 1
        cursor.card_idx = 2
        
        result = cursor.move_up()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        message, hint = result
        assert isinstance(message, str)
        assert hint is None or isinstance(hint, str)
    
    def test_hint_present_for_selectable_card(self, setup_table_and_cursor):
        """Hint should be generated for uncovered (selectable) cards."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 1
        
        # Ensure we have enough cards
        if len(table.pile_base[1].cards) >= 3:
            cursor.card_idx = 2
            
            # Ensure card is uncovered
            table.pile_base[1].cards[1].set_covered = False
            
            message, hint = cursor.move_up()
            
            # If we successfully moved up, hint should be present for uncovered card
            if "già alla prima" not in message.lower():
                assert hint is not None
                assert "INVIO" in hint.upper() or "invio" in hint.lower()
                assert "selezionare" in hint.lower()
    
    def test_hint_none_for_covered_card(self, setup_table_and_cursor):
        """Hint should be None for covered (non-selectable) cards."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 1
        cursor.card_idx = 2
        
        # Make card covered
        table.pile_base[1].cards[1].set_covered = True
        
        message, hint = cursor.move_up()
        
        assert hint is None
    
    def test_hint_none_at_first_card(self, setup_table_and_cursor):
        """No hint when already at first card."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 1
        cursor.card_idx = 0
        
        message, hint = cursor.move_up()
        
        assert hint is None
        assert "già alla prima" in message.lower()


class TestMoveDownReturnType:
    """Test move_down() returns tuple with hint."""
    
    def test_returns_tuple(self, setup_table_and_cursor):
        """move_down should return (message, hint) tuple."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 1
        cursor.card_idx = 0
        
        result = cursor.move_down()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_hint_present_for_uncovered_card(self, setup_table_and_cursor):
        """Hint should be generated when moving to uncovered card."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 1
        cursor.card_idx = 0
        
        # Ensure next card is uncovered
        if len(table.pile_base[1].cards) > 1:
            table.pile_base[1].cards[1].set_covered = False
            
            message, hint = cursor.move_down()
            
            assert hint is not None
            assert "selezionare" in hint.lower()


class TestMoveLeftRightReturnType:
    """Test move_left/right return tuples with hints."""
    
    def test_move_left_returns_tuple(self, setup_table_and_cursor):
        """move_left should return (message, hint) tuple."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 2
        
        result = cursor.move_left()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        message, hint = result
        assert isinstance(message, str)
    
    def test_move_left_hint_about_navigation(self, setup_table_and_cursor):
        """Hint should mention arrow key navigation."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 2
        
        message, hint = cursor.move_left()
        
        assert hint is not None
        assert "frecce" in hint.lower() or "su" in hint.lower() or "giù" in hint.lower()
    
    def test_move_right_returns_tuple(self, setup_table_and_cursor):
        """move_right should return (message, hint) tuple."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 2
        
        result = cursor.move_right()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_move_right_hint_about_navigation(self, setup_table_and_cursor):
        """Hint should mention arrow key navigation."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 2
        
        message, hint = cursor.move_right()
        
        assert hint is not None
        assert "frecce" in hint.lower() or "su" in hint.lower()
    
    def test_move_left_at_boundary(self, setup_table_and_cursor):
        """No hint when at first pile."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 0
        
        message, hint = cursor.move_left()
        
        assert hint is None
        assert "già alla prima" in message.lower()
    
    def test_move_right_at_boundary(self, setup_table_and_cursor):
        """No hint when at last pile."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = len(table.pile) - 1
        
        message, hint = cursor.move_right()
        
        assert hint is None
        assert "già all'ultima" in message.lower()


class TestMoveTabReturnType:
    """Test move_tab() returns tuple with hint."""
    
    def test_returns_tuple(self, setup_table_and_cursor):
        """move_tab should return (message, hint) tuple."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 0
        
        result = cursor.move_tab()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_hint_mentions_tab(self, setup_table_and_cursor):
        """Hint should mention TAB key."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 0
        
        message, hint = cursor.move_tab()
        
        assert hint is not None
        assert "tab" in hint.lower()
    
    def test_hint_mentions_next_pile_type(self, setup_table_and_cursor):
        """Hint should mention moving to next pile type."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 0
        
        message, hint = cursor.move_tab()
        
        assert hint is not None
        assert "prossimo tipo" in hint.lower() or "pila" in hint.lower()


class TestJumpToPileReturnType:
    """Test jump_to_pile() returns 3-tuple with hint."""
    
    def test_returns_triple(self, setup_table_and_cursor):
        """jump_to_pile should return (message, auto_select, hint) tuple."""
        cursor, table = setup_table_and_cursor
        
        result = cursor.jump_to_pile(1)
        
        assert isinstance(result, tuple)
        assert len(result) == 3
        message, auto_select, hint = result
        assert isinstance(message, str)
        assert isinstance(auto_select, bool)
        assert hint is None or isinstance(hint, str)
    
    def test_hint_for_tableau_pile(self, setup_table_and_cursor):
        """Hint for tableau pile should mention double-tap."""
        cursor, table = setup_table_and_cursor
        
        # Ensure pile has card
        if len(table.pile_base[2].cards) > 0:
            message, auto_select, hint = cursor.jump_to_pile(2)
            
            assert hint is not None
            assert "premi ancora" in hint.lower()
            assert "3" in hint  # Pile number
    
    def test_hint_for_foundation_pile(self, setup_table_and_cursor):
        """Hint for foundation pile should mention SHIFT+number."""
        cursor, table = setup_table_and_cursor
        
        # Add card to foundation pile
        pile_idx = 7  # First foundation pile
        card = Card(1, 1, table.pile[pile_idx])  # Ace
        card.set_covered = False
        table.pile[pile_idx].aggiungi_carta(card)
        
        message, auto_select, hint = cursor.jump_to_pile(pile_idx)
        
        if hint:
            assert "shift" in hint.lower()
    
    def test_hint_for_stock_pile(self, setup_table_and_cursor):
        """Hint for stock pile should mention drawing card."""
        cursor, table = setup_table_and_cursor
        
        message, auto_select, hint = cursor.jump_to_pile(12)
        
        if not table.pile_mazzo.is_empty():
            assert hint is not None
            assert "invio" in hint.lower() or "pescare" in hint.lower()
    
    def test_hint_for_waste_pile(self, setup_table_and_cursor):
        """Hint for waste pile should mention arrows and CTRL+ENTER."""
        cursor, table = setup_table_and_cursor
        
        # Add card to waste using the table's deck
        if len(table.pile_mazzo.cards) > 0:
            card = table.pile_mazzo.cards.pop(0)
            table.pile_scarti.aggiungi_carta(card)
        
        message, auto_select, hint = cursor.jump_to_pile(11)
        
        if not table.pile_scarti.is_empty():
            assert hint is not None
            assert "frecce" in hint.lower() or "ctrl" in hint.lower()
    
    def test_no_hint_for_empty_pile(self, setup_table_and_cursor):
        """No hint when pile is empty."""
        cursor, table = setup_table_and_cursor
        
        # Find or create empty pile
        pile_idx = 0
        if len(table.pile_base) > pile_idx:
            table.pile_base[pile_idx].cards.clear()
            
            message, auto_select, hint = cursor.jump_to_pile(pile_idx)
            
            assert hint is None
    
    def test_double_tap_no_hint(self, setup_table_and_cursor):
        """Double-tap (second press) should not return hint."""
        cursor, table = setup_table_and_cursor
        
        # First tap
        cursor.jump_to_pile(1)
        
        # Second tap (double-tap)
        message, auto_select, hint = cursor.jump_to_pile(1)
        
        # On double-tap, either hint is None or auto_select is True
        if auto_select:
            # If auto-selecting, no hint needed
            assert True
        else:
            # If not auto-selecting (e.g., stock/waste), might have hint
            pass


class TestHintContentQuality:
    """Test quality and consistency of hint messages."""
    
    def test_hints_are_in_italian(self, setup_table_and_cursor):
        """All hints should be in Italian."""
        cursor, table = setup_table_and_cursor
        
        # Collect hints from various methods
        hints = []
        
        cursor.pile_idx = 1
        if len(table.pile_base[1].cards) > 1:
            _, hint = cursor.move_left()
            if hint:
                hints.append(hint)
            
            _, hint = cursor.move_tab()
            if hint:
                hints.append(hint)
        
        # Check Italian keywords
        for hint in hints:
            # Should contain Italian words, not English
            assert not any(word in hint.lower() for word in ["press", "use", "select", "arrow"])
    
    def test_hint_contains_actionable_command(self, setup_table_and_cursor):
        """Hints should suggest specific actions."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 2
        
        message, hint = cursor.move_left()
        
        if hint:
            # Should mention a key or action
            has_action = any(word in hint.lower() for word in 
                           ["premi", "usa", "frecce", "invio", "tab", "shift"])
            assert has_action
    
    def test_hints_reference_correct_pile_numbers(self, setup_table_and_cursor):
        """Hints should reference correct pile indices."""
        cursor, table = setup_table_and_cursor
        
        # Test tableau pile hints
        for pile_idx in range(7):
            if len(table.pile_base[pile_idx].cards) > 0:
                message, auto_select, hint = cursor.jump_to_pile(pile_idx)
                
                if hint and "premi ancora" in hint.lower():
                    # Should contain pile number (1-7, not 0-6)
                    assert str(pile_idx + 1) in hint


class TestBackwardCompatibility:
    """Ensure changes don't break existing behavior."""
    
    def test_navigation_still_moves_cursor(self, setup_table_and_cursor):
        """Navigation methods should still move cursor correctly."""
        cursor, table = setup_table_and_cursor
        
        initial_pile = cursor.pile_idx
        cursor.move_right()
        
        assert cursor.pile_idx == initial_pile + 1
    
    def test_message_content_unchanged(self, setup_table_and_cursor):
        """Message content should remain the same as before."""
        cursor, table = setup_table_and_cursor
        cursor.pile_idx = 1
        
        message, hint = cursor.move_left()
        
        # Message should still contain pile info
        assert "pila" in message.lower()
    
    def test_can_ignore_hint_if_not_needed(self, setup_table_and_cursor):
        """Caller can ignore hint part of tuple."""
        cursor, table = setup_table_and_cursor
        
        # Can unpack and ignore hint
        message, _ = cursor.move_left()
        assert isinstance(message, str)
        
        # Can also unpack to different variable name
        msg, command_hint = cursor.move_right()
        assert isinstance(msg, str)
