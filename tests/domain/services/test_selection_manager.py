"""Unit tests for SelectionManager."""

import pytest
from src.domain.models.deck import FrenchDeck
from src.domain.models.table import GameTable
from src.domain.models.pile import Pile, PileType
from src.domain.services.selection_manager import SelectionManager


@pytest.fixture
def table():
    """Create game table with dealt cards."""
    deck = FrenchDeck()
    deck.crea()
    deck.mischia()
    table = GameTable(deck)
    table.distribuisci_carte()
    return table


@pytest.fixture
def manager():
    """Create selection manager."""
    return SelectionManager()


def test_init(manager):
    """Test manager initialization."""
    assert len(manager.selected_cards) == 0
    assert manager.origin_pile is None
    assert manager.target_card is None
    assert not manager.has_selection()


def test_clear_empty_selection(manager):
    """Test clearing when nothing selected."""
    msg = manager.clear_selection()
    assert "nessuna" in msg.lower()


def test_select_card_sequence(manager, table):
    """Test selecting card sequence from pile."""
    pile = table.pile_base[0]
    
    if not pile.is_empty():
        # Uncover all cards for testing
        for card in pile.cards:
            card.scopri()
        
        msg = manager.select_card_sequence(pile, 0)
        
        assert manager.has_selection()
        assert len(manager.selected_cards) > 0
        assert manager.origin_pile == pile
        assert "selezionate" in msg.lower()


def test_select_covered_card(manager, table):
    """Test selecting covered card (should fail)."""
    pile = table.pile_base[0]
    
    if not pile.is_empty():
        # Ensure first card is covered
        pile.cards[0].copri()
        
        msg = manager.select_card_sequence(pile, 0)
        assert "coperta" in msg.lower()
        assert not manager.has_selection()


def test_select_from_empty_pile(manager, table):
    """Test selecting from empty pile."""
    # Create empty pile
    empty_pile = Pile("test", PileType.TABLEAU)
    
    msg = manager.select_card_sequence(empty_pile, 0)
    assert "vuota" in msg.lower()
    assert not manager.has_selection()


def test_select_twice(manager, table):
    """Test selecting when already have selection."""
    pile = table.pile_base[0]
    
    if not pile.is_empty():
        # Uncover cards
        for card in pile.cards:
            card.scopri()
        
        # First selection
        manager.select_card_sequence(pile, 0)
        
        # Try second selection
        msg = manager.select_card_sequence(pile, 0)
        assert "già selezionato" in msg.lower()


def test_select_top_card_from_waste(manager, table):
    """Test selecting from waste pile."""
    waste = table.pile_scarti
    
    # Add a card to waste for testing
    if not waste.is_empty():
        msg = manager.select_top_card_from_waste(waste)
        
        assert manager.has_selection()
        assert len(manager.selected_cards) == 1
        assert manager.origin_pile == waste


def test_select_from_empty_waste(manager, table):
    """Test selecting from empty waste pile."""
    waste = table.pile_scarti
    waste.clear()  # Ensure empty
    
    msg = manager.select_top_card_from_waste(waste)
    assert "vuota" in msg.lower()
    assert not manager.has_selection()


def test_get_selection_info(manager, table):
    """Test selection info formatting."""
    pile = table.pile_base[0]
    
    if not pile.is_empty():
        # Uncover cards
        for card in pile.cards:
            card.scopri()
        
        manager.select_card_sequence(pile, 0)
        msg = manager.get_selection_info()
        
        assert "carte selezionate" in msg.lower() or "selezionate" in msg.lower()
        assert "target" in msg.lower() or "carta" in msg.lower()


def test_get_info_no_selection(manager):
    """Test info when nothing selected."""
    msg = manager.get_selection_info()
    assert "nessuna" in msg.lower()


def test_can_move_to(manager, table):
    """Test preliminary move validation."""
    source = table.pile_base[0]
    dest = table.pile_base[1]
    
    # No selection: can't move
    assert not manager.can_move_to(dest)
    
    if not source.is_empty():
        # Uncover cards
        for card in source.cards:
            card.scopri()
        
        # Make selection
        manager.select_card_sequence(source, 0)
        
        # Can't move to same pile
        assert not manager.can_move_to(source)
        
        # Can potentially move to different pile
        assert manager.can_move_to(dest)


def test_clear_selection_after_select(manager, table):
    """Test clearing after selection."""
    pile = table.pile_base[0]
    
    if not pile.is_empty():
        # Uncover and select
        for card in pile.cards:
            card.scopri()
        
        manager.select_card_sequence(pile, 0)
        assert manager.has_selection()
        
        # Clear
        msg = manager.clear_selection()
        assert "annullo" in msg.lower()
        assert not manager.has_selection()
        assert manager.origin_pile is None
        assert manager.target_card is None
