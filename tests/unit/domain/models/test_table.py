"""Unit tests for GameTable model."""

import pytest

from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck, NeapolitanDeck
from src.domain.models.card import Card


class TestGameTableInitialization:
    """Test suite for GameTable initialization."""
    
    def test_creates_table_with_french_deck(self) -> None:
        """Test table creation with French deck."""
        deck = FrenchDeck()
        table = GameTable(deck)
        assert table.mazzo is deck
        assert len(table.pile_base) == 11
    
    def test_creates_table_with_neapolitan_deck(self) -> None:
        """Test table creation with Neapolitan deck."""
        deck = NeapolitanDeck()
        table = GameTable(deck)
        assert table.mazzo is deck
        assert len(table.pile_base) == 11
    
    def test_creates_11_piles(self) -> None:
        """Test that table creates exactly 11 piles (7 tableau + 4 foundation)."""
        deck = FrenchDeck()
        table = GameTable(deck)
        assert len(table.pile_base) == 11
    
    def test_deck_assigned(self) -> None:
        """Test that deck is correctly assigned to table."""
        deck = FrenchDeck()
        table = GameTable(deck)
        assert table.mazzo is deck


class TestDistribuzione:
    """Test suite for card distribution."""
    
    def test_distribuisci_carte_french_deck(self) -> None:
        """Test distribution: 28 cards distributed, 24 in stock.
        
        French deck has 52 cards total.
        After distribution: 28 in tableau, 24 remain in deck.
        """
        deck = FrenchDeck()
        table = GameTable(deck)
        
        # 28 cards distributed in tableau piles (1+2+3+4+5+6+7)
        total_distributed = sum(pile.get_size() for pile in table.pile_base[:7])
        assert total_distributed == 28
        
        # 24 cards remain in the deck
        assert deck.get_len() == 24
    
    def test_distribuisci_carte_neapolitan_deck(self) -> None:
        """CRITICAL: Test distribution with Neapolitan deck.
        
        Fixes #25, #26: Neapolitan deck has 40 cards total.
        After distribution: 28 in tableau, 12 remain in deck (not 24!).
        """
        deck = NeapolitanDeck()
        table = GameTable(deck)
        
        # 28 cards distributed
        total_distributed = sum(pile.get_size() for pile in table.pile_base[:7])
        assert total_distributed == 28
        
        # 12 cards remain in the deck (40 - 28 = 12)
        assert deck.get_len() == 12
    
    def test_last_card_each_pile_uncovered(self) -> None:
        """Test last card of each tableau pile is face-up."""
        deck = FrenchDeck()
        table = GameTable(deck)
        
        for i in range(7):
            top_card = table.pile_base[i].get_top_card()
            assert top_card is not None
            assert not top_card.get_covered
    
    def test_pile_sizes_correct(self) -> None:
        """Test piles have correct sizes (1,2,3,4,5,6,7)."""
        deck = FrenchDeck()
        table = GameTable(deck)
        
        for i in range(7):
            assert table.pile_base[i].get_size() == i + 1
    
    def test_foundation_piles_empty_after_init(self) -> None:
        """Test that foundation piles start empty."""
        deck = FrenchDeck()
        table = GameTable(deck)
        
        for i in range(7, 11):
            assert table.pile_base[i].is_empty()


class TestPutToBase:
    """Test suite for placing cards on tableau piles."""
    
    def test_king_on_empty_pile_french(self) -> None:
        """Test French King (value 13) can be placed on empty pile."""
        deck = FrenchDeck()
        deck.crea()
        
        # Create table without auto-distribution
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Find a King (value 13)
        king = next(c for c in deck.cards if c.get_value == 13)
        king.set_uncover()
        
        result = table.put_to_base(king, 0)
        assert result is True
        assert table.pile_base[0].get_size() == 1
    
    def test_king_on_empty_pile_neapolitan(self) -> None:
        """CRITICAL: Test Neapolitan King (value 10) on empty pile.
        
        Fixes #28, #29: Uses is_king() from Commit #1.
        Neapolitan King has value 10, not 13.
        """
        deck = NeapolitanDeck()
        deck.crea()
        
        # Create table without auto-distribution
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Find a King (value 10 in Neapolitan deck)
        king = next(c for c in deck.cards if c.get_value == 10)
        king.set_uncover()
        
        result = table.put_to_base(king, 0)
        assert result is True
        assert table.pile_base[0].get_size() == 1
    
    def test_non_king_rejected_on_empty_pile(self) -> None:
        """Test non-King cards are rejected on empty pile."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Try to place a Queen (value 12)
        queen = next(c for c in deck.cards if c.get_value == 12)
        queen.set_uncover()
        
        result = table.put_to_base(queen, 0)
        assert result is False
        assert table.pile_base[0].is_empty()
    
    def test_alternating_colors_accepted(self) -> None:
        """Test cards with alternating colors are accepted."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Uncover all cards first
        for card in deck.cards:
            card.set_uncover()
        
        # Place a King first (red)
        king = next(c for c in deck.cards if c.get_value == 13 and c.get_color == "rosso")
        table.pile_base[0].aggiungi_carta(king)
        
        # Try to place a Queen of opposite color (blue)
        queen = next(c for c in deck.cards if c.get_value == 12 and c.get_color == "blu")
        
        result = table.put_to_base(queen, 0)
        assert result is True
        assert table.pile_base[0].get_size() == 2
    
    def test_same_color_rejected(self) -> None:
        """Test cards with same color are rejected."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Uncover all cards first
        for card in deck.cards:
            card.set_uncover()
        
        # Place a King first (red)
        king = next(c for c in deck.cards if c.get_value == 13 and c.get_color == "rosso")
        table.pile_base[0].aggiungi_carta(king)
        
        # Try to place a Queen of same color (red)
        queen = next((c for c in deck.cards if c.get_value == 12 and c.get_color == "rosso" and c != king), None)
        assert queen is not None
        
        result = table.put_to_base(queen, 0)
        assert result is False
    
    def test_descending_values_accepted(self) -> None:
        """Test cards with descending values are accepted."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Uncover all cards first
        for card in deck.cards:
            card.set_uncover()
        
        # Place a 5 (red)
        five = next(c for c in deck.cards if c.get_value == 5 and c.get_color == "rosso")
        table.pile_base[0].aggiungi_carta(five)
        
        # Place a 4 (descending, opposite color - blue)
        four = next(c for c in deck.cards if c.get_value == 4 and c.get_color == "blu")
        
        result = table.put_to_base(four, 0)
        assert result is True
    
    def test_invalid_pile_index_rejected(self) -> None:
        """Test invalid pile index is rejected."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        king = next(c for c in deck.cards if c.get_value == 13)
        king.set_uncover()
        
        result = table.put_to_base(king, 7)  # Foundation pile
        assert result is False
        
        result = table.put_to_base(king, -1)  # Negative index
        assert result is False


class TestVerificaVittoria:
    """Test suite for victory condition."""
    
    def test_vittoria_french_deck(self) -> None:
        """CRITICAL: Test victory with French deck (4 piles at value 13)."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Simulate 4 complete foundation piles with Kings on top (value 13)
        kings = [c for c in deck.cards if c.get_value == 13]
        for i, king in enumerate(kings[:4]):
            table.pile_base[7 + i].aggiungi_carta(king)
        
        assert table.verifica_vittoria() is True
    
    def test_vittoria_neapolitan_deck(self) -> None:
        """CRITICAL: Test victory with Neapolitan deck (4 piles at value 10)."""
        deck = NeapolitanDeck()
        deck.crea()
        
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Simulate 4 complete foundation piles with Kings on top (value 10)
        kings = [c for c in deck.cards if c.get_value == 10]
        for i, king in enumerate(kings[:4]):
            table.pile_base[7 + i].aggiungi_carta(king)
        
        assert table.verifica_vittoria() is True
    
    def test_not_vittoria_incomplete(self) -> None:
        """Test no victory if foundations incomplete."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Only 3 piles complete
        kings = [c for c in deck.cards if c.get_value == 13]
        for i in range(3):
            table.pile_base[7 + i].aggiungi_carta(kings[i])
        
        assert table.verifica_vittoria() is False
    
    def test_not_vittoria_empty_foundation(self) -> None:
        """Test no victory if a foundation is empty."""
        deck = FrenchDeck()
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        assert table.verifica_vittoria() is False
    
    def test_not_vittoria_wrong_top_card(self) -> None:
        """Test no victory if top card is not King."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Place Queens (value 12) instead of Kings
        queens = [c for c in deck.cards if c.get_value == 12]
        for i in range(4):
            table.pile_base[7 + i].aggiungi_carta(queens[i])
        
        assert table.verifica_vittoria() is False


class TestGameTableAPI:
    """Test suite for GameTable API methods."""
    
    def test_get_pile_valid_index(self) -> None:
        """Test getting a pile with valid index."""
        deck = FrenchDeck()
        table = GameTable(deck)
        
        pile = table.get_pile(0)
        assert pile is not None
        assert pile is table.pile_base[0]
    
    def test_get_pile_invalid_index(self) -> None:
        """Test getting a pile with invalid index."""
        deck = FrenchDeck()
        table = GameTable(deck)
        
        pile = table.get_pile(-1)
        assert pile is None
        
        pile = table.get_pile(11)
        assert pile is None
    
    def test_reset(self) -> None:
        """Test resetting the table."""
        deck = FrenchDeck()
        table = GameTable(deck)
        
        # Modify a pile
        original_size = table.pile_base[0].get_size()
        table.pile_base[0].rimuovi_carta()
        
        # Reset should redistribute
        table.reset()
        
        # Check distribution is correct again
        total_distributed = sum(pile.get_size() for pile in table.pile_base[:7])
        assert total_distributed == 28
        assert deck.get_len() == 24


class TestPutToFoundation:
    """Test suite for placing cards on foundation piles."""
    
    def test_ace_on_empty_foundation(self) -> None:
        """Test Ace can be placed on empty foundation."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Find an Ace
        ace = next(c for c in deck.cards if c.get_value == 1)
        
        result = table.put_to_foundation(ace, 7)
        assert result is True
        assert table.pile_base[7].get_size() == 1
    
    def test_non_ace_rejected_on_empty_foundation(self) -> None:
        """Test non-Ace cards are rejected on empty foundation."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Try to place a 2
        two = next(c for c in deck.cards if c.get_value == 2)
        
        result = table.put_to_foundation(two, 7)
        assert result is False
    
    def test_ascending_same_suit_accepted(self) -> None:
        """Test ascending value with same suit is accepted."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable.__new__(GameTable)
        table.mazzo = deck
        from src.domain.models.pile import Pile
        table.pile_base = [Pile() for _ in range(11)]
        
        # Uncover all cards first
        for card in deck.cards:
            card.set_uncover()
        
        # Place Ace of hearts
        ace = next(c for c in deck.cards if c.get_value == 1 and c.get_suit == "cuori")
        table.pile_base[7].aggiungi_carta(ace)
        
        # Place 2 of hearts
        two = next(c for c in deck.cards if c.get_value == 2 and c.get_suit == "cuori")
        
        result = table.put_to_foundation(two, 7)
        assert result is True
