"""Unit tests for GameService."""

import pytest
import time
from src.domain.services.game_service import GameService
from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck
from src.domain.models.card import Card
from src.domain.models.pile import Pile
from src.domain.rules.solitaire_rules import SolitaireRules


class TestGameServiceLifecycle:
    """Test game lifecycle management."""
    
    def test_start_game_initializes_timer(self):
        """Test start_game() sets start_time."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        assert service.start_time is None
        service.start_game()
        assert service.start_time is not None
    
    def test_reset_game_clears_state(self):
        """Test reset_game() clears all counters."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        service.start_game()
        service.move_count = 10
        service.draw_count = 5
        
        service.reset_game()
        
        assert service.move_count == 0
        assert service.start_time is None
        assert service.draw_count == 0
    
    def test_get_elapsed_time_returns_seconds(self):
        """Test elapsed time calculation."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        service.start_game()
        time.sleep(0.1)  # Wait 100ms
        elapsed = service.get_elapsed_time()
        
        assert elapsed >= 0.1
        assert elapsed < 1.0  # Sanity check


class TestCardMovement:
    """Test card movement between piles."""
    
    def test_move_card_valid_tableau(self):
        """Test valid card move between tableau piles."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        # Setup: red 7 on pile 1, black 6 to move
        pile1 = Pile()
        pile2 = Pile()
        
        red_7 = Card("7", "cuori")
        red_7.set_int_value(7)
        red_7.set_color("rosso")
        red_7.set_uncover()
        pile1.aggiungi_carta(red_7)
        
        black_6 = Card("6", "picche")
        black_6.set_int_value(6)
        black_6.set_color("blu")
        black_6.set_uncover()
        pile2.aggiungi_carta(black_6)
        
        success, msg = service.move_card(pile2, pile1, 1, False)
        
        assert success is True
        assert service.move_count == 1
        assert pile1.get_card_count() == 2
        assert pile2.get_card_count() == 0
    
    def test_move_card_invalid_same_color(self):
        """Test invalid move (same color)."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        pile1 = Pile()
        pile2 = Pile()
        
        red_7 = Card("7", "cuori")
        red_7.set_int_value(7)
        red_7.set_color("rosso")
        red_7.set_uncover()
        pile1.aggiungi_carta(red_7)
        
        red_6 = Card("6", "cuori")  # Same color!
        red_6.set_int_value(6)
        red_6.set_color("rosso")
        red_6.set_uncover()
        pile2.aggiungi_carta(red_6)
        
        success, msg = service.move_card(pile2, pile1, 1, False)
        
        assert success is False
        assert "non valida" in msg.lower()
        assert service.move_count == 0
    
    def test_move_card_empty_source(self):
        """Test moving from empty pile fails."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        pile1 = Pile()
        pile2 = Pile()
        
        success, msg = service.move_card(pile1, pile2, 1, False)
        
        assert success is False
        assert "vuota" in msg.lower()


class TestStockWasteManagement:
    """Test stock and waste pile operations."""
    
    def test_draw_cards_from_stock(self):
        """Test drawing cards from stock to waste."""
        deck = FrenchDeck()
        deck.crea()
        
        # Create table but manually setup piles to avoid auto-distribution
        table = GameTable(deck)
        table.pile_mazzo = Pile()
        table.pile_scarti = Pile()
        
        # Create a fresh deck for testing
        test_deck = FrenchDeck()
        test_deck.crea()
        
        # Add cards to stock
        for card in test_deck.cards[:10]:
            card.set_cover()
            table.pile_mazzo.aggiungi_carta(card)
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        success, msg, drawn = service.draw_cards(3)
        
        assert success is True
        assert len(drawn) == 3
        assert table.pile_mazzo.get_card_count() == 7
        assert table.pile_scarti.get_card_count() == 3
        assert all(not card.get_covered for card in drawn)
    
    def test_draw_cards_less_than_requested(self):
        """Test drawing when stock has fewer cards than requested."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable(deck)
        table.pile_mazzo = Pile()
        table.pile_scarti = Pile()
        
        # Create a fresh deck for testing
        test_deck = FrenchDeck()
        test_deck.crea()
        
        # Add only 2 cards to stock
        for card in test_deck.cards[:2]:
            card.set_cover()
            table.pile_mazzo.aggiungi_carta(card)
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        success, msg, drawn = service.draw_cards(3)
        
        assert success is True
        assert len(drawn) == 2  # Only 2 available
    
    def test_recycle_waste_inverts_order(self):
        """Test recycling waste back to stock (invert mode)."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable(deck)
        table.pile_mazzo = Pile()
        table.pile_scarti = Pile()
        
        # Create a fresh deck for testing
        test_deck = FrenchDeck()
        test_deck.crea()
        
        # Add cards to waste
        cards = test_deck.cards[:5]
        for card in cards:
            card.set_uncover()
            table.pile_scarti.aggiungi_carta(card)
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        success, msg = service.recycle_waste(shuffle=False)
        
        assert success is True
        assert table.pile_scarti.get_card_count() == 0
        assert table.pile_mazzo.get_card_count() == 5
        # Cards should be covered
        assert all(card.get_covered for card in table.pile_mazzo.get_all_cards())
    
    def test_recycle_waste_with_shuffle(self):
        """Test recycling waste with shuffle mode."""
        deck = FrenchDeck()
        deck.crea()
        
        table = GameTable(deck)
        table.pile_mazzo = Pile()
        table.pile_scarti = Pile()
        
        # Create a fresh deck for testing
        test_deck = FrenchDeck()
        test_deck.crea()
        
        # Add cards to waste
        cards = test_deck.cards[:5]
        for card in cards:
            card.set_uncover()
            table.pile_scarti.aggiungi_carta(card)
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        success, msg = service.recycle_waste(shuffle=True)
        
        assert success is True
        assert table.pile_scarti.get_card_count() == 0
        assert table.pile_mazzo.get_card_count() == 5


class TestAutoMove:
    """Test automatic move to foundation."""
    
    def test_auto_move_ace_to_empty_foundation(self):
        """Test auto-move Ace to empty foundation."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        table.pile_base = [Pile()]
        table.pile_semi = [Pile() for _ in range(4)]
        table.pile_scarti = Pile()
        
        # Put Ace on tableau
        ace = Card("Asso", "cuori")
        ace.set_int_value(1)
        ace.set_suit("cuori")
        ace.set_uncover()
        table.pile_base[0].aggiungi_carta(ace)
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        success, msg, moved_card = service.auto_move_to_foundation()
        
        assert success is True
        assert moved_card == ace
        assert table.pile_base[0].get_card_count() == 0
        assert any(p.get_card_count() == 1 for p in table.pile_semi)
    
    def test_auto_move_from_waste(self):
        """Test auto-move from waste pile."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        table.pile_base = [Pile() for _ in range(7)]
        table.pile_semi = [Pile() for _ in range(4)]
        table.pile_scarti = Pile()
        
        # Put Ace on waste
        ace = Card("Asso", "picche")
        ace.set_int_value(1)
        ace.set_suit("picche")
        ace.set_uncover()
        table.pile_scarti.aggiungi_carta(ace)
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        success, msg, moved_card = service.auto_move_to_foundation()
        
        assert success is True
        assert moved_card == ace
        assert table.pile_scarti.get_card_count() == 0
    
    def test_auto_move_no_valid_moves(self):
        """Test auto-move when no valid moves available."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        table.pile_base = [Pile()]
        table.pile_semi = [Pile() for _ in range(4)]
        table.pile_scarti = Pile()
        
        # Put non-Ace card on tableau
        two = Card("2", "cuori")
        two.set_int_value(2)
        two.set_suit("cuori")
        two.set_uncover()
        table.pile_base[0].aggiungi_carta(two)
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        success, msg, moved_card = service.auto_move_to_foundation()
        
        assert success is False
        assert moved_card is None


class TestGameStatus:
    """Test game over and victory checks."""
    
    def test_is_victory_with_complete_foundations(self):
        """Test victory detection."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        table.pile_semi = []
        
        # Create 4 complete foundations
        for i in range(4):
            pile = Pile()
            # Put a King (value 13) on top to simulate complete foundation
            king = Card("Re", deck.SUITES[i])
            king.set_int_value(13)
            king.set_suit(deck.SUITES[i])
            pile.aggiungi_carta(king)
            table.pile_semi.append(pile)
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        assert service.is_victory() is True
    
    def test_is_victory_with_incomplete_foundations(self):
        """Test no victory with incomplete foundations."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        table.pile_semi = [Pile() for _ in range(4)]
        
        # Only one foundation has cards
        ace = Card("Asso", "cuori")
        ace.set_int_value(1)
        table.pile_semi[0].aggiungi_carta(ace)
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        assert service.is_victory() is False
    
    def test_check_game_over_returns_victory_message(self):
        """Test game over check with victory."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        table.pile_semi = []
        
        for i in range(4):
            pile = Pile()
            king = Card("Re", deck.SUITES[i])
            king.set_int_value(13)
            king.set_suit(deck.SUITES[i])
            pile.aggiungi_carta(king)
            table.pile_semi.append(pile)
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        service.start_game()
        service.move_count = 150
        
        is_over, msg = service.check_game_over()
        
        assert is_over is True
        assert "Vittoria" in msg
        assert "150" in msg
    
    def test_check_game_over_game_in_progress(self):
        """Test game over check when game is still in progress."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        is_over, msg = service.check_game_over()
        
        assert is_over is False
        assert "corso" in msg.lower()


class TestStatistics:
    """Test statistics tracking."""
    
    def test_get_statistics_returns_all_metrics(self):
        """Test statistics dictionary."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        table.pile_semi = [Pile() for _ in range(4)]
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        service.start_game()
        service.move_count = 10
        service.draw_count = 3
        
        stats = service.get_statistics()
        
        assert "move_count" in stats
        assert "elapsed_time" in stats
        assert "draw_count" in stats
        assert "foundation_progress" in stats
        assert stats["move_count"] == 10
        assert stats["draw_count"] == 3
    
    def test_get_statistics_foundation_progress(self):
        """Test foundation progress tracking."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        table.pile_semi = [Pile() for _ in range(4)]
        
        # Add some cards to foundations
        ace = Card("Asso", "cuori")
        ace.set_int_value(1)
        table.pile_semi[0].aggiungi_carta(ace)
        
        two = Card("2", "cuori")
        two.set_int_value(2)
        table.pile_semi[0].aggiungi_carta(two)
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        stats = service.get_statistics()
        
        assert stats["foundation_progress"][0] == 2
        assert stats["total_foundation_cards"] == 2


class TestSequenceMovement:
    """Test moving sequences of cards."""
    
    def test_get_movable_sequence_valid(self):
        """Test extracting valid sequence."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        pile = Pile()
        
        # Add sequence: red 7, black 6, red 5
        red_7 = Card("7", "cuori")
        red_7.set_int_value(7)
        red_7.set_color("rosso")
        red_7.set_uncover()
        pile.aggiungi_carta(red_7)
        
        black_6 = Card("6", "picche")
        black_6.set_int_value(6)
        black_6.set_color("blu")
        black_6.set_uncover()
        pile.aggiungi_carta(black_6)
        
        red_5 = Card("5", "cuori")
        red_5.set_int_value(5)
        red_5.set_color("rosso")
        red_5.set_uncover()
        pile.aggiungi_carta(red_5)
        
        sequence = service._get_movable_sequence(pile, 3)
        
        assert len(sequence) == 3
        assert sequence[0] == red_7
        assert sequence[2] == red_5
    
    def test_get_movable_sequence_with_covered_cards(self):
        """Test sequence extraction fails with covered cards."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        pile = Pile()
        
        # Add covered card
        covered = Card("7", "cuori")
        covered.set_int_value(7)
        covered.set_cover()
        pile.aggiungi_carta(covered)
        
        # Add uncovered card
        uncovered = Card("6", "picche")
        uncovered.set_int_value(6)
        uncovered.set_uncover()
        pile.aggiungi_carta(uncovered)
        
        sequence = service._get_movable_sequence(pile, 2)
        
        assert len(sequence) == 0  # Should fail due to covered card
    
    def test_get_movable_sequence_invalid_count(self):
        """Test sequence extraction with invalid count."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        pile = Pile()
        card = Card("7", "cuori")
        pile.aggiungi_carta(card)
        
        # Try to get more cards than in pile
        sequence = service._get_movable_sequence(pile, 5)
        assert len(sequence) == 0
        
        # Try to get 0 cards
        sequence = service._get_movable_sequence(pile, 0)
        assert len(sequence) == 0
    
    def test_move_card_sequence_valid(self):
        """Test moving a valid sequence of cards."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        source = Pile()
        target = Pile()
        
        # Setup target: black 8
        black_8 = Card("8", "picche")
        black_8.set_int_value(8)
        black_8.set_color("blu")
        black_8.set_uncover()
        target.aggiungi_carta(black_8)
        
        # Setup source: red 7, black 6
        red_7 = Card("7", "cuori")
        red_7.set_int_value(7)
        red_7.set_color("rosso")
        red_7.set_uncover()
        source.aggiungi_carta(red_7)
        
        black_6 = Card("6", "picche")
        black_6.set_int_value(6)
        black_6.set_color("blu")
        black_6.set_uncover()
        source.aggiungi_carta(black_6)
        
        success, msg = service.move_card(source, target, 2, False)
        
        assert success is True
        assert source.get_card_count() == 0
        assert target.get_card_count() == 3
    
    def test_move_card_to_foundation(self):
        """Test moving card to foundation."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        source = Pile()
        foundation = Pile()
        
        # Setup source: Ace
        ace = Card("Asso", "cuori")
        ace.set_int_value(1)
        ace.set_suit("cuori")
        ace.set_uncover()
        source.aggiungi_carta(ace)
        
        success, msg = service.move_card(source, foundation, 1, True)
        
        assert success is True
        assert source.get_card_count() == 0
        assert foundation.get_card_count() == 1
    
    def test_uncover_top_card(self):
        """Test uncovering top card after move."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        pile = Pile()
        
        # Add covered card
        covered = Card("7", "cuori")
        covered.set_int_value(7)
        covered.set_cover()
        pile.aggiungi_carta(covered)
        
        # Add uncovered card on top
        uncovered = Card("6", "picche")
        uncovered.set_int_value(6)
        uncovered.set_uncover()
        pile.aggiungi_carta(uncovered)
        
        # Remove top card
        pile.remove_last_card()
        
        # Top card should still be covered
        assert pile.get_top_card().get_covered is True
        
        # Call _uncover_top_card
        service._uncover_top_card(pile)
        
        # Top card should now be uncovered
        assert pile.get_top_card().get_covered is False


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_draw_from_empty_stock(self):
        """Test drawing from empty stock fails."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        table.pile_mazzo = Pile()
        table.pile_scarti = Pile()
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        success, msg, drawn = service.draw_cards(3)
        
        assert success is False
        assert "vuoto" in msg.lower()
        assert len(drawn) == 0
    
    def test_recycle_with_non_empty_stock(self):
        """Test recycling fails when stock is not empty."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        table.pile_mazzo = Pile()
        table.pile_scarti = Pile()
        
        # Create fresh deck
        test_deck = FrenchDeck()
        test_deck.crea()
        
        # Add card to stock
        card1 = test_deck.cards[0]
        card1.set_cover()
        table.pile_mazzo.aggiungi_carta(card1)
        
        # Add card to waste
        card2 = test_deck.cards[1]
        card2.set_uncover()
        table.pile_scarti.aggiungi_carta(card2)
        
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        success, msg = service.recycle_waste(shuffle=False)
        
        assert success is False
        assert "impossibile" in msg.lower()
    
    def test_elapsed_time_before_start(self):
        """Test elapsed time returns 0 before game starts."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        elapsed = service.get_elapsed_time()
        assert elapsed == 0.0
    
    def test_start_game_multiple_times(self):
        """Test starting game multiple times keeps original start time."""
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        
        service.start_game()
        first_time = service.start_time
        
        time.sleep(0.05)
        service.start_game()  # Should not change start_time
        
        assert service.start_time == first_time
