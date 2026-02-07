"""Unit tests for Deck models."""

import pytest

from src.domain.models.deck import FrenchDeck, NeapolitanDeck, ProtoDeck
from src.domain.models.card import Card


class TestFrenchDeck:
    """Test suite for FrenchDeck."""
    
    def test_creates_52_cards(self) -> None:
        """Test that French deck creates exactly 52 cards."""
        deck = FrenchDeck()
        deck.crea()
        assert len(deck.cards) == 52
    
    def test_is_king_value_13(self) -> None:
        """Test French King has value 13 and is correctly identified."""
        deck = FrenchDeck()
        deck.crea()
        # Find a King (value 13)
        king = next(c for c in deck.cards if c.get_value == 13)
        assert deck.is_king(king) is True
    
    def test_is_not_king_queen(self) -> None:
        """Test that Queen is not identified as King."""
        deck = FrenchDeck()
        deck.crea()
        # Find a Queen (value 12)
        queen = next(c for c in deck.cards if c.get_value == 12)
        assert deck.is_king(queen) is False
    
    def test_is_not_king_jack(self) -> None:
        """Test that Jack is not identified as King."""
        deck = FrenchDeck()
        deck.crea()
        # Find a Jack (value 11)
        jack = next(c for c in deck.cards if c.get_value == 11)
        assert deck.is_king(jack) is False
    
    def test_get_total_cards(self) -> None:
        """Test get_total_cards returns 52."""
        deck = FrenchDeck()
        assert deck.get_total_cards() == 52
    
    def test_has_four_kings(self) -> None:
        """Test French deck has exactly 4 Kings."""
        deck = FrenchDeck()
        deck.crea()
        kings = [c for c in deck.cards if deck.is_king(c)]
        assert len(kings) == 4
    
    def test_has_all_suits(self) -> None:
        """Test French deck has all 4 suits."""
        deck = FrenchDeck()
        assert set(deck.SUITES) == {"cuori", "quadri", "fiori", "picche"}
    
    def test_has_all_values(self) -> None:
        """Test French deck has all 13 values."""
        deck = FrenchDeck()
        assert len(deck.VALUES) == 13
        assert "Asso" in deck.VALUES
        assert "Jack" in deck.VALUES
        assert "Regina" in deck.VALUES
        assert "Re" in deck.VALUES
    
    def test_is_french_deck(self) -> None:
        """Test is_french_deck returns True."""
        deck = FrenchDeck()
        assert deck.is_french_deck() is True
        assert deck.is_neapolitan_deck() is False
    
    def test_deck_type(self) -> None:
        """Test deck type is correctly set."""
        deck = FrenchDeck()
        assert deck.get_type() == "carte francesi"


class TestNeapolitanDeck:
    """Test suite for NeapolitanDeck."""
    
    def test_creates_40_cards(self) -> None:
        """Test that Neapolitan deck creates exactly 40 cards."""
        deck = NeapolitanDeck()
        deck.crea()
        assert len(deck.cards) == 40
    
    def test_is_king_value_10(self) -> None:
        """CRITICAL: Neapolitan King has value 10 (fixes #28, #29)."""
        deck = NeapolitanDeck()
        deck.crea()
        # Find a King (value 10)
        king = next(c for c in deck.cards if c.get_value == 10)
        assert deck.is_king(king) is True
    
    def test_is_not_king_cavallo(self) -> None:
        """Test that Cavallo (9) is not identified as King."""
        deck = NeapolitanDeck()
        deck.crea()
        # Find a Cavallo (value 9)
        cavallo = next(c for c in deck.cards if c.get_value == 9)
        assert deck.is_king(cavallo) is False
    
    def test_is_not_king_regina(self) -> None:
        """Test that Regina (8) is not identified as King."""
        deck = NeapolitanDeck()
        deck.crea()
        # Find a Regina (value 8)
        regina = next(c for c in deck.cards if c.get_value == 8)
        assert deck.is_king(regina) is False
    
    def test_no_8_9_10_numeric_cards(self) -> None:
        """Test Neapolitan deck has only 1-7, Regina(8), Cavallo(9), Re(10)."""
        deck = NeapolitanDeck()
        # Check VALUES list doesn't have string "8", "9", "10"
        assert "8" not in deck.VALUES
        assert "9" not in deck.VALUES
        assert "10" not in deck.VALUES
        # But it has the figure cards with those values
        assert "Regina" in deck.VALUES  # value 8
        assert "Cavallo" in deck.VALUES  # value 9
        assert "Re" in deck.VALUES  # value 10
    
    def test_get_total_cards(self) -> None:
        """Test get_total_cards returns 40."""
        deck = NeapolitanDeck()
        assert deck.get_total_cards() == 40
    
    def test_has_four_kings(self) -> None:
        """Test Neapolitan deck has exactly 4 Kings."""
        deck = NeapolitanDeck()
        deck.crea()
        kings = [c for c in deck.cards if deck.is_king(c)]
        assert len(kings) == 4
    
    def test_has_all_suits(self) -> None:
        """Test Neapolitan deck has all 4 Italian suits."""
        deck = NeapolitanDeck()
        assert set(deck.SUITES) == {"bastoni", "coppe", "denari", "spade"}
    
    def test_has_all_values(self) -> None:
        """Test Neapolitan deck has all 10 values."""
        deck = NeapolitanDeck()
        assert len(deck.VALUES) == 10
        assert "Asso" in deck.VALUES
        assert "Regina" in deck.VALUES
        assert "Cavallo" in deck.VALUES
        assert "Re" in deck.VALUES
    
    def test_is_neapolitan_deck(self) -> None:
        """Test is_neapolitan_deck returns True."""
        deck = NeapolitanDeck()
        assert deck.is_neapolitan_deck() is True
        assert deck.is_french_deck() is False
    
    def test_deck_type(self) -> None:
        """Test deck type is correctly set."""
        deck = NeapolitanDeck()
        assert deck.get_type() == "carte napoletane"


class TestDeckInterface:
    """Test common ProtoDeck API for both deck types."""
    
    @pytest.mark.parametrize("deck_class", [FrenchDeck, NeapolitanDeck])
    def test_get_total_cards(self, deck_class) -> None:
        """Test get_total_cards returns correct value for each deck."""
        deck = deck_class()
        total = deck.get_total_cards()
        assert total in [52, 40]
    
    @pytest.mark.parametrize("deck_class", [FrenchDeck, NeapolitanDeck])
    def test_mischia_randomizes(self, deck_class) -> None:
        """Test shuffle randomizes card order."""
        deck = deck_class()
        deck.crea()
        # Get IDs of first 10 cards
        original_ids = [c.get_id for c in deck.cards[:10]]
        deck.mischia()
        # Get IDs of first 10 cards after shuffle
        shuffled_ids = [c.get_id for c in deck.cards[:10]]
        # Very unlikely to have same order after shuffle
        assert original_ids != shuffled_ids
    
    @pytest.mark.parametrize("deck_class", [FrenchDeck, NeapolitanDeck])
    def test_pesca_draws_card(self, deck_class) -> None:
        """Test pesca draws a card from the deck."""
        deck = deck_class()
        deck.crea()
        initial_len = deck.get_len()
        carta = deck.pesca()
        assert carta is not None
        assert deck.get_len() == initial_len - 1
    
    @pytest.mark.parametrize("deck_class", [FrenchDeck, NeapolitanDeck])
    def test_reset_recreates_and_shuffles(self, deck_class) -> None:
        """Test reset recreates full deck and shuffles."""
        deck = deck_class()
        # Draw some cards
        for _ in range(10):
            deck.pesca()
        assert deck.get_len() < deck.get_total_cards()
        
        # Reset
        deck.reset()
        assert deck.get_len() == deck.get_total_cards()
    
    @pytest.mark.parametrize("deck_class", [FrenchDeck, NeapolitanDeck])
    def test_get_carta_valid_index(self, deck_class) -> None:
        """Test get_carta returns card at valid index."""
        deck = deck_class()
        deck.crea()
        carta = deck.get_carta(0)
        assert carta is not None
        carta = deck.get_carta(deck.get_len() - 1)
        assert carta is not None
    
    @pytest.mark.parametrize("deck_class", [FrenchDeck, NeapolitanDeck])
    def test_get_carta_invalid_index(self, deck_class) -> None:
        """Test get_carta returns None for invalid index."""
        deck = deck_class()
        deck.crea()
        carta = deck.get_carta(999)
        assert carta is None
    
    @pytest.mark.parametrize("deck_class", [FrenchDeck, NeapolitanDeck])
    def test_rimuovi_carte(self, deck_class) -> None:
        """Test rimuovi_carte removes and returns cards."""
        deck = deck_class()
        deck.crea()
        initial_len = deck.get_len()
        n = 5
        
        removed = deck.rimuovi_carte(n)
        assert len(removed) == n
        assert deck.get_len() == initial_len - n
    
    @pytest.mark.parametrize("deck_class", [FrenchDeck, NeapolitanDeck])
    def test_inserisci_carte(self, deck_class) -> None:
        """Test inserisci_carte adds cards to deck."""
        deck = deck_class()
        deck.crea()
        initial_len = deck.get_len()
        
        # Create some additional cards
        additional_cards = [Card("Asso", "cuori"), Card("2", "quadri")]
        deck.inserisci_carte(additional_cards)
        
        assert deck.get_len() == initial_len + len(additional_cards)
    
    @pytest.mark.parametrize("deck_class", [FrenchDeck, NeapolitanDeck])
    def test_is_empty_dek(self, deck_class) -> None:
        """Test is_empty_dek correctly detects empty deck."""
        deck = deck_class()
        # Initially has cards (auto-created by __init__)
        assert deck.is_empty_dek() is False
        
        # Remove all cards
        while deck.get_len() > 0:
            deck.pesca()
        
        assert deck.is_empty_dek() is True
    
    @pytest.mark.parametrize("deck_class", [FrenchDeck, NeapolitanDeck])
    def test_get_suits(self, deck_class) -> None:
        """Test get_suits returns suit list."""
        deck = deck_class()
        suits = deck.get_suits()
        assert len(suits) == 4
        assert isinstance(suits, list)


class TestKingValidationBugFix:
    """Tests specifically for the is_king() bug fix (#28, #29).
    
    These tests ensure that Kings are correctly identified regardless
    of deck type, which was a critical bug in the legacy code.
    """
    
    def test_french_king_on_empty_pile(self) -> None:
        """Test French King (value 13) can be identified for empty pile placement."""
        deck = FrenchDeck()
        deck.crea()
        
        # Find all Kings
        kings = [c for c in deck.cards if c.get_value == 13]
        
        # All should be identified as Kings
        for king in kings:
            assert deck.is_king(king), f"Card {king.get_name} should be King"
    
    def test_neapolitan_king_on_empty_pile(self) -> None:
        """Test Neapolitan King (value 10) can be identified for empty pile placement.
        
        This was the critical bug #28: Neapolitan Kings were blocked on empty piles.
        """
        deck = NeapolitanDeck()
        deck.crea()
        
        # Find all Kings (value 10 in Neapolitan)
        kings = [c for c in deck.cards if c.get_value == 10]
        
        # All should be identified as Kings
        for king in kings:
            assert deck.is_king(king), f"Card {king.get_name} should be King"
    
    def test_french_non_kings_not_identified(self) -> None:
        """Test that non-King cards are not falsely identified as Kings."""
        deck = FrenchDeck()
        deck.crea()
        
        # Check all non-King cards
        non_kings = [c for c in deck.cards if c.get_value != 13]
        
        for card in non_kings:
            assert not deck.is_king(card), f"Card {card.get_name} should not be King"
    
    def test_neapolitan_non_kings_not_identified(self) -> None:
        """Test that non-King Neapolitan cards are not falsely identified as Kings."""
        deck = NeapolitanDeck()
        deck.crea()
        
        # Check all non-King cards (especially Cavallo with value 9)
        non_kings = [c for c in deck.cards if c.get_value != 10]
        
        for card in non_kings:
            assert not deck.is_king(card), f"Card {card.get_name} should not be King"
    
    def test_king_value_differs_by_deck_type(self) -> None:
        """Test that King values are different for French vs Neapolitan decks."""
        french = FrenchDeck()
        neapolitan = NeapolitanDeck()
        
        # French King is 13
        assert french.FIGURE_VALUES["Re"] == 13
        
        # Neapolitan King is 10
        assert neapolitan.FIGURE_VALUES["Re"] == 10
        
        # They should be different
        assert french.FIGURE_VALUES["Re"] != neapolitan.FIGURE_VALUES["Re"]
