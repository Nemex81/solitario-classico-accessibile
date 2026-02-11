"""Integration tests for scoring system with GameService.

Tests the integration between GameService and ScoringService to ensure
scoring events are correctly recorded during gameplay.

These tests focus on verifying that:
1. Scoring events are recorded when moves are made
2. Scoring is optional (scoring=None works)
3. reset_game() clears scoring state
4. Recycle events are recorded correctly
"""

import pytest
from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck
from src.domain.models.pile import Pile
from src.domain.models.card import Card
from src.domain.services.game_service import GameService
from src.domain.services.scoring_service import ScoringService
from src.domain.rules.solitaire_rules import SolitaireRules
from src.domain.models.scoring import ScoringConfig, ScoreEventType


@pytest.fixture
def scoring_config():
    """Create default scoring configuration."""
    return ScoringConfig()


@pytest.fixture
def scoring_service(scoring_config):
    """Create scoring service with default configuration."""
    return ScoringService(
        config=scoring_config,
        difficulty_level=1,
        deck_type="french",
        draw_count=1,
        timer_enabled=False
    )


@pytest.fixture
def game_table():
    """Create initialized game table."""
    deck = FrenchDeck()
    deck.crea()
    table = GameTable(deck)
    return table


@pytest.fixture
def game_service(game_table, scoring_service):
    """Create game service with scoring enabled."""
    rules = SolitaireRules(game_table.mazzo)
    service = GameService(game_table, rules, scoring=scoring_service)
    service.start_game()
    return service


@pytest.fixture
def game_service_no_scoring(game_table):
    """Create game service without scoring (free-play mode)."""
    rules = SolitaireRules(game_table.mazzo)
    service = GameService(game_table, rules, scoring=None)
    service.start_game()
    return service


def create_card(value: str, suit: str) -> Card:
    """Helper to create a properly initialized card."""
    card = Card(value, suit)
    # Set numeric value for foundation rules
    if value == "1" or value.lower() == "asso":
        card.set_int_value(1)
    elif value.isdigit():
        card.set_int_value(int(value))
    card.set_suit(suit.lower())
    card.set_uncover()
    return card


class TestWasteToFoundationScoring:
    """Tests for waste to foundation scoring events."""
    
    def test_waste_to_foundation_records_event(self, game_service, scoring_service):
        """Moving card from waste to foundation records +10 points."""
        # Setup: Place an Ace in waste (foundation accepts Aces first)
        waste = game_service.table.pile_scarti
        foundation = game_service.table.pile_semi[0]
        
        # Clear waste and add an Ace
        waste.clear()
        ace = create_card("1", "Cuori")
        waste.aggiungi_carta(ace)
        
        # Execute move
        success, msg = game_service.move_card(waste, foundation, 1, is_foundation_target=True)
        
        # Assert
        assert success, f"Move failed: {msg}"
        assert scoring_service.get_event_count() == 1
        assert scoring_service.get_base_score() == 10
        
        events = scoring_service.get_recent_events(1)
        assert events[0].event_type == ScoreEventType.WASTE_TO_FOUNDATION
        assert events[0].points == 10


class TestTableauToFoundationScoring:
    """Tests for tableau to foundation scoring events."""
    
    def test_tableau_to_foundation_records_event(self, game_service, scoring_service):
        """Moving card from tableau to foundation records +10 points."""
        # Setup: Place an Ace in first tableau pile
        tableau = game_service.table.pile_base[0]
        foundation = game_service.table.pile_semi[0]
        
        # Clear tableau and add an Ace
        tableau.clear()
        ace = create_card("1", "Cuori")
        tableau.aggiungi_carta(ace)
        
        # Execute move
        success, msg = game_service.move_card(tableau, foundation, 1, is_foundation_target=True)
        
        # Assert
        assert success, f"Move failed: {msg}"
        assert scoring_service.get_event_count() == 1
        assert scoring_service.get_base_score() == 10
        
        events = scoring_service.get_recent_events(1)
        assert events[0].event_type == ScoreEventType.TABLEAU_TO_FOUNDATION
        assert events[0].points == 10


class TestCardRevealedScoring:
    """Tests for card revealed scoring events."""
    
    def test_card_revealed_records_event(self, game_service, scoring_service):
        """Revealing a card records +5 points."""
        # Setup: Create tableau with covered card that will be revealed
        tableau = game_service.table.pile_base[0]
        foundation = game_service.table.pile_semi[0]
        
        # Clear tableau and set up: covered 2, then uncovered Ace on top
        tableau.clear()
        covered_card = create_card("2", "Cuori")
        covered_card.set_cover()  # Make it covered
        tableau.aggiungi_carta(covered_card)
        
        top_card = create_card("1", "Cuori")  # Ace
        tableau.aggiungi_carta(top_card)
        
        # Execute move (should reveal covered card)
        success, msg = game_service.move_card(tableau, foundation, 1, is_foundation_target=True)
        
        # Assert
        assert success, f"Move failed: {msg}"
        # Should have 2 events: TABLEAU_TO_FOUNDATION + CARD_REVEALED
        assert scoring_service.get_event_count() == 2
        
        events = scoring_service.get_recent_events(2)
        # Most recent event should be CARD_REVEALED
        assert events[0].event_type == ScoreEventType.CARD_REVEALED
        assert events[0].points == 5
        assert events[1].event_type == ScoreEventType.TABLEAU_TO_FOUNDATION


class TestRecycleWasteScoring:
    """Tests for recycle waste scoring events."""
    
    def test_recycle_records_no_penalty_first_three(self, game_service, scoring_service):
        """First 3 recycles don't deduct points."""
        waste = game_service.table.pile_scarti
        stock = game_service.table.pile_mazzo
        
        # Clear both piles
        waste.clear()
        stock.clear()
        
        # First 3 recycles - no penalty
        for i in range(3):
            # Add some cards to waste
            for j in range(5):
                card = create_card(str(j + 2), "Cuori")
                waste.aggiungi_carta(card)
            
            success, msg = game_service.recycle_waste()
            assert success, f"Recycle {i+1} failed: {msg}"
            assert scoring_service.get_base_score() == 0
            
            # Move cards back to waste for next recycle
            waste.clear()
            while not stock.is_empty():
                card = stock.remove_last_card()
                waste.aggiungi_carta(card)
        
        assert scoring_service.get_event_count() == 3
    
    def test_recycle_records_penalty_after_third(self, game_service, scoring_service):
        """4th recycle deducts -20 points."""
        waste = game_service.table.pile_scarti
        stock = game_service.table.pile_mazzo
        
        # Clear both piles
        waste.clear()
        stock.clear()
        
        # First 3 recycles (no penalty)
        for i in range(3):
            # Add cards to waste
            for j in range(5):
                card = create_card(str(j + 2), "Quadri")
                waste.aggiungi_carta(card)
            
            game_service.recycle_waste()
            
            # Move back to waste
            waste.clear()
            while not stock.is_empty():
                card = stock.remove_last_card()
                waste.aggiungi_carta(card)
        
        # 4th recycle - penalty
        for j in range(5):
            card = create_card(str(j + 2), "Picche")
            waste.aggiungi_carta(card)
        
        success, msg = game_service.recycle_waste()
        assert success
        assert scoring_service.get_event_count() == 4
        assert scoring_service.get_base_score() == -20
        
        events = scoring_service.get_recent_events(1)
        assert events[0].event_type == ScoreEventType.RECYCLE_WASTE
        assert events[0].points == -20


class TestScoringOptional:
    """Tests for optional scoring dependency."""
    
    def test_scoring_none_doesnt_crash(self, game_service_no_scoring):
        """Game works normally when scoring=None."""
        # Setup: Place an Ace in waste
        waste = game_service_no_scoring.table.pile_scarti
        foundation = game_service_no_scoring.table.pile_semi[0]
        
        waste.clear()
        ace = create_card("1", "Cuori")
        waste.aggiungi_carta(ace)
        
        # Execute move
        success, msg = game_service_no_scoring.move_card(waste, foundation, 1, is_foundation_target=True)
        
        # Assert - no crash
        assert success, f"Move failed: {msg}"
        assert game_service_no_scoring.scoring is None
    
    def test_recycle_without_scoring_works(self, game_service_no_scoring):
        """Recycle works normally when scoring=None."""
        waste = game_service_no_scoring.table.pile_scarti
        stock = game_service_no_scoring.table.pile_mazzo
        
        # Clear and setup
        waste.clear()
        stock.clear()
        
        # Add cards
        for i in range(5):
            card = create_card(str(i + 2), "Cuori")
            waste.aggiungi_carta(card)
        
        # Recycle
        success, msg = game_service_no_scoring.recycle_waste()
        
        # Assert - no crash
        assert success


class TestResetGame:
    """Tests for reset_game clearing scoring state."""
    
    def test_reset_game_clears_scoring_events(self, game_service, scoring_service):
        """reset_game() clears all scoring events."""
        # Setup: Record some events by moving Aces to foundations
        waste = game_service.table.pile_scarti
        
        # Move 3 Aces from waste to 3 different foundations
        for i in range(3):
            foundation = game_service.table.pile_semi[i]
            foundation.clear()
            waste.clear()
            
            ace = create_card("1", f"Cuori")  # All Aces work
            waste.aggiungi_carta(ace)
            game_service.move_card(waste, foundation, 1, is_foundation_target=True)
        
        assert scoring_service.get_event_count() >= 1  # At least one move succeeded
        assert scoring_service.get_base_score() >= 10
        
        # Reset
        game_service.reset_game()
        
        # Assert
        assert scoring_service.get_event_count() == 0
        assert scoring_service.get_base_score() == 0


class TestMultipleMovesAccumulation:
    """Tests for score accumulation across multiple moves."""
    
    def test_multiple_moves_accumulate_score(self, game_service, scoring_service):
        """Multiple moves correctly accumulate score."""
        waste = game_service.table.pile_scarti
        
        # Move 1 Ace to foundation, then test recycle accumulation
        foundation = game_service.table.pile_semi[0]
        foundation.clear()
        waste.clear()
        
        # First move: Ace to foundation
        ace = create_card("1", "Cuori")
        waste.aggiungi_carta(ace)
        success, msg = game_service.move_card(waste, foundation, 1, is_foundation_target=True)
        assert success, f"Move 1 failed: {msg}"
        
        # Second and third moves: more recycles (testing accumulation)
        stock = game_service.table.pile_mazzo
        for i in range(2):
            waste.clear()
            stock.clear()
            for j in range(3):
                card = create_card(str(j + 2), "Quadri")
                waste.aggiungi_carta(card)
            game_service.recycle_waste()
            waste.clear()
            while not stock.is_empty():
                card = stock.remove_last_card()
                waste.aggiungi_carta(card)
        
        # Assert - 1 move + 2 recycles = 3 events
        assert scoring_service.get_event_count() == 3
        assert scoring_service.get_base_score() == 10  # 1 move (recycles are free)
    
    def test_mixed_events_calculate_correctly(self, game_service, scoring_service):
        """Mixed events (moves + recycles) calculate correctly."""
        waste = game_service.table.pile_scarti
        stock = game_service.table.pile_mazzo
        foundation = game_service.table.pile_semi[0]
        
        # Move 1 Ace (+10)
        waste.clear()
        foundation.clear()
        ace = create_card("1", "Cuori")
        waste.aggiungi_carta(ace)
        game_service.move_card(waste, foundation, 1, is_foundation_target=True)
        
        # Recycle 4 times (3 free + 1 penalty = -20)
        for i in range(4):
            waste.clear()
            stock.clear()
            
            for j in range(3):
                card = create_card(str(j + 2), "Quadri")
                waste.aggiungi_carta(card)
            
            game_service.recycle_waste()
            
            # Move cards back for next recycle
            waste.clear()
            while not stock.is_empty():
                card = stock.remove_last_card()
                waste.aggiungi_carta(card)
        
        # Assert
        expected_score = 10 - 20  # Move + 4th recycle penalty
        assert scoring_service.get_base_score() == expected_score


class TestProvisionalScoreQuery:
    """Tests for querying provisional score during gameplay."""
    
    def test_provisional_score_matches_events(self, game_service, scoring_service):
        """Provisional score matches sum of event points."""
        waste = game_service.table.pile_scarti
        
        # Move 1 Ace to foundation
        foundation = game_service.table.pile_semi[0]
        foundation.clear()
        waste.clear()
        
        ace = create_card("1", "Cuori")
        waste.aggiungi_carta(ace)
        game_service.move_card(waste, foundation, 1, is_foundation_target=True)
        
        # Do one more recycle to have 2 events
        stock = game_service.table.pile_mazzo
        waste.clear()
        stock.clear()
        for j in range(3):
            card = create_card(str(j + 2), "Quadri")
            waste.aggiungi_carta(card)
        game_service.recycle_waste()
        
        # Get provisional score
        provisional = scoring_service.calculate_provisional_score()
        
        # Assert - 1 move (10) + 1 recycle (0, first one is free)
        assert provisional.base_score == 10
        assert provisional.total_score == 160  # (10 + 150 deck bonus) * 1.0 difficulty
