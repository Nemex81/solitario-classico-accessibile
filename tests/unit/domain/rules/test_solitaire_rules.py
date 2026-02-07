"""Unit tests for SolitaireRules."""

import pytest

from src.domain.rules.solitaire_rules import SolitaireRules
from src.domain.models.deck import FrenchDeck, NeapolitanDeck, ProtoDeck
from src.domain.models.card import Card
from src.domain.models.pile import Pile


class TestTableauRules:
    """Test tableau placement rules."""
    
    def test_king_on_empty_tableau_french(self) -> None:
        """Test French King (value 13) can be placed on empty tableau."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        king = Card("Re", "cuori")
        king.set_int_value(13)
        king.set_uncover()
        
        assert rules.can_place_on_tableau(king, pile) is True
    
    def test_king_on_empty_tableau_neapolitan(self) -> None:
        """CRITICAL: Neapolitan King (value 10) on empty tableau."""
        deck = NeapolitanDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        king = Card("Re", "coppe")
        king.set_int_value(10)
        king.set_uncover()
        
        assert rules.can_place_on_tableau(king, pile) is True
    
    def test_non_king_rejected_on_empty_tableau(self) -> None:
        """Test non-King cards rejected on empty tableau."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        queen = Card("Regina", "cuori")
        queen.set_int_value(12)
        queen.set_uncover()
        
        assert rules.can_place_on_tableau(queen, pile) is False
    
    def test_alternating_colors_accepted_on_tableau(self) -> None:
        """Test alternating colors accepted on tableau."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Place red 7
        red_seven = Card("7", "cuori")
        red_seven.set_int_value(7)
        red_seven.set_uncover()
        red_seven.set_color("rosso")
        pile.aggiungi_carta(red_seven)
        
        # Try black 6
        black_six = Card("6", "picche")
        black_six.set_int_value(6)
        black_six.set_uncover()
        black_six.set_color("blu")
        
        assert rules.can_place_on_tableau(black_six, pile) is True
    
    def test_same_color_rejected_on_tableau(self) -> None:
        """Test same color rejected on tableau."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Place red 7
        red_seven = Card("7", "cuori")
        red_seven.set_int_value(7)
        red_seven.set_uncover()
        red_seven.set_color("rosso")
        pile.aggiungi_carta(red_seven)
        
        # Try red 6 (same color)
        red_six = Card("6", "cuori")
        red_six.set_int_value(6)
        red_six.set_uncover()
        red_six.set_color("rosso")
        
        assert rules.can_place_on_tableau(red_six, pile) is False
    
    def test_descending_value_required_on_tableau(self) -> None:
        """Test descending value by 1 is required."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Place 7
        seven = Card("7", "cuori")
        seven.set_int_value(7)
        seven.set_uncover()
        seven.set_color("rosso")
        pile.aggiungi_carta(seven)
        
        # Try 5 (skips 6)
        five = Card("5", "picche")
        five.set_int_value(5)
        five.set_uncover()
        five.set_color("blu")
        
        assert rules.can_place_on_tableau(five, pile) is False
    
    def test_ascending_value_rejected_on_tableau(self) -> None:
        """Test ascending value rejected on tableau."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Place 7
        seven = Card("7", "cuori")
        seven.set_int_value(7)
        seven.set_uncover()
        seven.set_color("rosso")
        pile.aggiungi_carta(seven)
        
        # Try 8 (ascending)
        eight = Card("8", "picche")
        eight.set_int_value(8)
        eight.set_uncover()
        eight.set_color("blu")
        
        assert rules.can_place_on_tableau(eight, pile) is False


class TestFoundationRules:
    """Test foundation placement rules."""
    
    def test_ace_on_empty_foundation(self) -> None:
        """Test Ace can be placed on empty foundation."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        ace = Card("Asso", "cuori")
        ace.set_int_value(1)
        ace.set_uncover()
        
        assert rules.can_place_on_foundation(ace, pile) is True
    
    def test_non_ace_rejected_on_empty_foundation(self) -> None:
        """Test non-Ace rejected on empty foundation."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        two = Card("2", "cuori")
        two.set_int_value(2)
        two.set_uncover()
        
        assert rules.can_place_on_foundation(two, pile) is False
    
    def test_same_suit_ascending_accepted_on_foundation(self) -> None:
        """Test same suit ascending value accepted on foundation."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Place Ace of hearts
        ace = Card("Asso", "cuori")
        ace.set_int_value(1)
        ace.set_uncover()
        ace.set_suit("cuori")
        pile.aggiungi_carta(ace)
        
        # Try 2 of hearts
        two = Card("2", "cuori")
        two.set_int_value(2)
        two.set_uncover()
        two.set_suit("cuori")
        
        assert rules.can_place_on_foundation(two, pile) is True
    
    def test_different_suit_rejected_on_foundation(self) -> None:
        """Test different suit rejected on foundation."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Place Ace of hearts
        ace = Card("Asso", "cuori")
        ace.set_int_value(1)
        ace.set_uncover()
        ace.set_suit("cuori")
        pile.aggiungi_carta(ace)
        
        # Try 2 of spades (different suit)
        two = Card("2", "picche")
        two.set_int_value(2)
        two.set_uncover()
        two.set_suit("picche")
        
        assert rules.can_place_on_foundation(two, pile) is False
    
    def test_skip_value_rejected_on_foundation(self) -> None:
        """Test skipping value rejected on foundation."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Place Ace
        ace = Card("Asso", "cuori")
        ace.set_int_value(1)
        ace.set_uncover()
        ace.set_suit("cuori")
        pile.aggiungi_carta(ace)
        
        # Try 3 (skips 2)
        three = Card("3", "cuori")
        three.set_int_value(3)
        three.set_uncover()
        three.set_suit("cuori")
        
        assert rules.can_place_on_foundation(three, pile) is False
    
    def test_foundation_complete_french_deck(self) -> None:
        """Test foundation complete with French King (13)."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Place King on top
        king = Card("Re", "cuori")
        king.set_int_value(13)
        king.set_uncover()
        pile.aggiungi_carta(king)
        
        assert rules.is_foundation_complete(pile) is True
    
    def test_foundation_complete_neapolitan_deck(self) -> None:
        """CRITICAL: Foundation complete with Neapolitan King (10)."""
        deck = NeapolitanDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Place Re (value 10) on top
        king = Card("Re", "coppe")
        king.set_int_value(10)
        king.set_uncover()
        pile.aggiungi_carta(king)
        
        assert rules.is_foundation_complete(pile) is True
    
    def test_foundation_incomplete_with_queen(self) -> None:
        """Test foundation incomplete with Queen on top."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Place Queen (not King)
        queen = Card("Regina", "cuori")
        queen.set_int_value(12)
        queen.set_uncover()
        pile.aggiungi_carta(queen)
        
        assert rules.is_foundation_complete(pile) is False


class TestSequenceRules:
    """Test sequence movement rules."""
    
    def test_valid_sequence_can_move(self) -> None:
        """Test valid sequence can be moved."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        target = Pile()
        
        # Create valid sequence: red 7, black 6, red 5
        sequence = []
        
        red_seven = Card("7", "cuori")
        red_seven.set_int_value(7)
        red_seven.set_uncover()
        red_seven.set_color("rosso")
        sequence.append(red_seven)
        
        black_six = Card("6", "picche")
        black_six.set_int_value(6)
        black_six.set_uncover()
        black_six.set_color("blu")
        sequence.append(black_six)
        
        red_five = Card("5", "cuori")
        red_five.set_int_value(5)
        red_five.set_uncover()
        red_five.set_color("rosso")
        sequence.append(red_five)
        
        # Target has black 8
        eight = Card("8", "picche")
        eight.set_int_value(8)
        eight.set_uncover()
        eight.set_color("blu")
        target.aggiungi_carta(eight)
        
        assert rules.can_move_sequence(sequence, target) is True
    
    def test_covered_card_in_sequence_rejected(self) -> None:
        """Test sequence with covered card rejected."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        target = Pile()
        
        # Create sequence with one covered card
        sequence = []
        
        red_seven = Card("7", "cuori")
        red_seven.set_int_value(7)
        red_seven.set_uncover()
        red_seven.set_color("rosso")
        sequence.append(red_seven)
        
        black_six = Card("6", "picche")
        black_six.set_int_value(6)
        # black_six stays covered (no set_uncover())
        black_six.set_color("blu")
        sequence.append(black_six)
        
        assert rules.can_move_sequence(sequence, target) is False
    
    def test_invalid_sequence_colors_rejected(self) -> None:
        """Test sequence with same colors rejected."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        target = Pile()
        
        # Create invalid sequence: red 7, red 6 (same color)
        sequence = []
        
        red_seven = Card("7", "cuori")
        red_seven.set_int_value(7)
        red_seven.set_uncover()
        red_seven.set_color("rosso")
        sequence.append(red_seven)
        
        red_six = Card("6", "cuori")  # Same color!
        red_six.set_int_value(6)
        red_six.set_uncover()
        red_six.set_color("rosso")
        sequence.append(red_six)
        
        assert rules.can_move_sequence(sequence, target) is False
    
    def test_invalid_sequence_values_rejected(self) -> None:
        """Test sequence with non-descending values rejected."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        target = Pile()
        
        # Create invalid sequence: 7, 5 (skips 6)
        sequence = []
        
        red_seven = Card("7", "cuori")
        red_seven.set_int_value(7)
        red_seven.set_uncover()
        red_seven.set_color("rosso")
        sequence.append(red_seven)
        
        black_five = Card("5", "picche")
        black_five.set_int_value(5)
        black_five.set_uncover()
        black_five.set_color("blu")
        sequence.append(black_five)
        
        assert rules.can_move_sequence(sequence, target) is False


class TestVictoryRules:
    """Test victory condition rules."""
    
    def test_victory_with_4_complete_foundations_french(self) -> None:
        """Test victory with 4 complete French foundations."""
        deck = FrenchDeck()
        deck.crea()
        rules = SolitaireRules(deck)
        
        # Create 4 complete foundations (King on top)
        foundations = []
        kings = [c for c in deck.cards if c.get_value == 13]
        
        for i in range(4):
            pile = Pile()
            pile.aggiungi_carta(kings[i])
            foundations.append(pile)
        
        assert rules.is_victory(foundations) is True
    
    def test_victory_with_4_complete_foundations_neapolitan(self) -> None:
        """CRITICAL: Victory with 4 complete Neapolitan foundations."""
        deck = NeapolitanDeck()
        deck.crea()
        rules = SolitaireRules(deck)
        
        # Create 4 complete foundations (Re value 10 on top)
        foundations = []
        kings = [c for c in deck.cards if c.get_value == 10]
        
        for i in range(4):
            pile = Pile()
            pile.aggiungi_carta(kings[i])
            foundations.append(pile)
        
        assert rules.is_victory(foundations) is True
    
    def test_not_victory_with_3_complete_foundations(self) -> None:
        """Test no victory with only 3 complete foundations."""
        deck = FrenchDeck()
        deck.crea()
        rules = SolitaireRules(deck)
        
        # Create only 3 complete foundations
        foundations = []
        kings = [c for c in deck.cards if c.get_value == 13]
        
        for i in range(3):
            pile = Pile()
            pile.aggiungi_carta(kings[i])
            foundations.append(pile)
        
        # Add empty 4th foundation
        foundations.append(Pile())
        
        assert rules.is_victory(foundations) is False
    
    def test_not_victory_with_incomplete_foundations(self) -> None:
        """Test no victory with incomplete foundations."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        
        # Create 4 foundations with Queens (not Kings)
        foundations = []
        for i in range(4):
            pile = Pile()
            queen = Card("Regina", "cuori")
            queen.set_int_value(12)
            queen.set_uncover()
            pile.aggiungi_carta(queen)
            foundations.append(pile)
        
        assert rules.is_victory(foundations) is False
    
    def test_not_victory_with_wrong_number_foundations(self) -> None:
        """Test no victory with wrong number of foundations."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        
        # Only 2 foundations
        foundations = [Pile(), Pile()]
        
        assert rules.is_victory(foundations) is False


class TestStockWasteRules:
    """Test stock and waste pile rules."""
    
    def test_can_draw_from_non_empty_stock(self) -> None:
        """Test can draw from non-empty stock."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        stock = Pile()
        
        card = Card("7", "cuori")
        card.set_int_value(7)
        stock.aggiungi_carta(card)
        
        assert rules.can_draw_from_stock(stock) is True
    
    def test_cannot_draw_from_empty_stock(self) -> None:
        """Test cannot draw from empty stock."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        stock = Pile()
        
        assert rules.can_draw_from_stock(stock) is False
    
    def test_can_recycle_waste_when_stock_empty(self) -> None:
        """Test can recycle waste when stock is empty."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        stock = Pile()
        waste = Pile()
        
        # Add card to waste
        card = Card("7", "cuori")
        card.set_int_value(7)
        waste.aggiungi_carta(card)
        
        assert rules.can_recycle_waste(waste, stock) is True
    
    def test_cannot_recycle_when_stock_not_empty(self) -> None:
        """Test cannot recycle waste when stock has cards."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        stock = Pile()
        waste = Pile()
        
        # Add cards to both
        card1 = Card("7", "cuori")
        card1.set_int_value(7)
        stock.aggiungi_carta(card1)
        
        card2 = Card("6", "picche")
        card2.set_int_value(6)
        waste.aggiungi_carta(card2)
        
        assert rules.can_recycle_waste(waste, stock) is False
    
    def test_cannot_recycle_empty_waste(self) -> None:
        """Test cannot recycle empty waste."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        stock = Pile()
        waste = Pile()
        
        assert rules.can_recycle_waste(waste, stock) is False


class TestUtilityMethods:
    """Test utility methods."""
    
    def test_empty_sequence_rejected(self) -> None:
        """Test empty sequence is rejected."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        target = Pile()
        
        assert rules.can_move_sequence([], target) is False
    
    def test_get_movable_cards_from_empty_pile(self) -> None:
        """Test get movable cards from empty pile returns empty list."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        assert rules.get_movable_cards_from_pile(pile) == []
    
    def test_get_movable_cards_all_covered(self) -> None:
        """Test get movable cards when all cards are covered."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Add covered cards
        card1 = Card("7", "cuori")
        card1.set_int_value(7)
        card1.set_color("rosso")
        # Keep card covered (default)
        pile.aggiungi_carta(card1)
        
        card2 = Card("6", "picche")
        card2.set_int_value(6)
        card2.set_color("blu")
        # Keep card covered
        pile.aggiungi_carta(card2)
        
        assert rules.get_movable_cards_from_pile(pile) == []
    
    def test_get_movable_cards_valid_sequence(self) -> None:
        """Test get movable cards with valid sequence."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Add covered card
        covered = Card("10", "cuori")
        covered.set_int_value(10)
        covered.set_color("rosso")
        # Keep covered
        pile.aggiungi_carta(covered)
        
        # Add valid sequence
        red_seven = Card("7", "cuori")
        red_seven.set_int_value(7)
        red_seven.set_uncover()
        red_seven.set_color("rosso")
        pile.aggiungi_carta(red_seven)
        
        black_six = Card("6", "picche")
        black_six.set_int_value(6)
        black_six.set_uncover()
        black_six.set_color("blu")
        pile.aggiungi_carta(black_six)
        
        movable = rules.get_movable_cards_from_pile(pile)
        assert len(movable) == 2
        assert movable[0].get_value == 7
        assert movable[1].get_value == 6
    
    def test_get_movable_cards_invalid_sequence(self) -> None:
        """Test get movable cards with invalid sequence returns empty."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        # Add invalid sequence (same colors)
        red_seven = Card("7", "cuori")
        red_seven.set_int_value(7)
        red_seven.set_uncover()
        red_seven.set_color("rosso")
        pile.aggiungi_carta(red_seven)
        
        red_six = Card("6", "cuori")  # Same color
        red_six.set_int_value(6)
        red_six.set_uncover()
        red_six.set_color("rosso")
        pile.aggiungi_carta(red_six)
        
        movable = rules.get_movable_cards_from_pile(pile)
        assert movable == []
    
    def test_single_card_sequence_valid(self) -> None:
        """Test single card always forms valid sequence."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        target = Pile()
        
        # Create sequence with single card
        sequence = []
        red_seven = Card("7", "cuori")
        red_seven.set_int_value(7)
        red_seven.set_uncover()
        red_seven.set_color("rosso")
        sequence.append(red_seven)
        
        # Target has black 8
        eight = Card("8", "picche")
        eight.set_int_value(8)
        eight.set_uncover()
        eight.set_color("blu")
        target.aggiungi_carta(eight)
        
        assert rules.can_move_sequence(sequence, target) is True


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_deck_without_king_definition(self) -> None:
        """Test handling of deck without King definition."""
        # Create a minimal deck without proper FIGURE_VALUES
        class BrokenDeck(ProtoDeck):
            SUITES = ["test"]
            VALUES = ["1"]
            FIGURE_VALUES = {}  # No King defined
        
        deck = BrokenDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        card = Card("Test", "test")
        card.set_int_value(10)
        pile.aggiungi_carta(card)
        
        # Should return False when King is not defined
        assert rules.is_foundation_complete(pile) is False
    
    def test_empty_foundation_check(self) -> None:
        """Test foundation complete check on empty pile."""
        deck = FrenchDeck()
        rules = SolitaireRules(deck)
        pile = Pile()
        
        assert rules.is_foundation_complete(pile) is False
