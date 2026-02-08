"""Unit tests for CursorManager."""

import pytest
from src.domain.models.deck import FrenchDeck
from src.domain.models.table import GameTable
from src.domain.services.cursor_manager import CursorManager


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
def cursor(table):
    """Create cursor manager."""
    return CursorManager(table)


def test_init(cursor):
    """Test cursor initialization."""
    assert cursor.card_idx == 0
    assert cursor.pile_idx == 0
    assert cursor.last_quick_pile is None


def test_get_position(cursor):
    """Test position getter."""
    assert cursor.get_position() == (0, 0)
    
    cursor.card_idx = 2
    cursor.pile_idx = 3
    assert cursor.get_position() == (2, 3)


def test_get_current_pile(cursor):
    """Test current pile getter."""
    pile = cursor.get_current_pile()
    assert pile is not None
    assert pile == cursor.table.pile[0]


def test_get_card_at_cursor(cursor):
    """Test card getter at cursor position."""
    cursor.pile_idx = 0  # Tableau pile 1
    cursor.card_idx = 0
    
    card = cursor.get_card_at_cursor()
    assert card is not None
    
    # Move to empty pile (if exists)
    cursor.pile_idx = 12  # Stock (initially full)
    card = cursor.get_card_at_cursor()
    # Stock might have cards, so this can be either


def test_validate_position(cursor):
    """Test position validation."""
    # Set invalid pile
    cursor.pile_idx = 99
    cursor.validate_position()
    assert cursor.pile_idx == 0
    
    # Set invalid card index (too high)
    cursor.pile_idx = 0
    cursor.card_idx = 9999
    cursor.validate_position()
    assert cursor.card_idx < len(cursor.get_current_pile().cards)


def test_move_to_top_card(cursor):
    """Test moving to top card of pile."""
    cursor.pile_idx = 0
    pile = cursor.get_current_pile()
    
    if not pile.is_empty():
        idx = cursor.move_to_top_card()
        assert idx == len(pile.cards) - 1
        assert cursor.card_idx == len(pile.cards) - 1


def test_move_up_on_tableau(cursor):
    """Test moving up within tableau pile."""
    cursor.pile_idx = 0
    pile = cursor.get_current_pile()
    
    if len(pile.cards) > 1:
        cursor.card_idx = 1
        msg = cursor.move_up()
        assert cursor.card_idx == 0
        assert "1:" in msg


def test_move_down_on_tableau(cursor):
    """Test moving down within tableau pile."""
    cursor.pile_idx = 0
    pile = cursor.get_current_pile()
    
    if len(pile.cards) > 1:
        cursor.card_idx = 0
        msg = cursor.move_down()
        assert cursor.card_idx == 1
        assert "2:" in msg


def test_move_left(cursor):
    """Test moving to previous pile."""
    cursor.pile_idx = 3
    msg = cursor.move_left()
    assert cursor.pile_idx == 2
    assert "pila" in msg.lower() or "pile" in msg.lower()


def test_move_right(cursor):
    """Test moving to next pile."""
    cursor.pile_idx = 3
    msg = cursor.move_right()
    assert cursor.pile_idx == 4


def test_move_home(cursor):
    """Test jumping to first card."""
    cursor.pile_idx = 0
    pile = cursor.get_current_pile()
    
    if not pile.is_empty():
        cursor.card_idx = len(pile.cards) - 1
        msg = cursor.move_home()
        assert cursor.card_idx == 0
        assert "prima" in msg.lower()


def test_move_end(cursor):
    """Test jumping to last card."""
    cursor.pile_idx = 0
    pile = cursor.get_current_pile()
    
    if not pile.is_empty():
        cursor.card_idx = 0
        msg = cursor.move_end()
        assert cursor.card_idx == len(pile.cards) - 1
        assert "ultima" in msg.lower()


def test_jump_to_pile(cursor):
    """Test jumping to specific pile."""
    msg = cursor.jump_to_pile(5)
    assert cursor.pile_idx == 5
    assert len(msg) > 0


def test_jump_to_invalid_pile(cursor):
    """Test jumping to invalid pile index."""
    msg = cursor.jump_to_pile(99)
    assert "non valido" in msg.lower()


def test_get_position_info(cursor):
    """Test position info formatting."""
    msg = cursor.get_position_info()
    assert len(msg) > 0
    assert "pila" in msg.lower() or "pile" in msg.lower()


def test_get_card_details(cursor):
    """Test card details formatting."""
    cursor.pile_idx = 0
    pile = cursor.get_current_pile()
    
    if not pile.is_empty():
        cursor.card_idx = 0
        msg = cursor.get_card_details()
        assert "nome" in msg.lower() or "carta" in msg.lower()
