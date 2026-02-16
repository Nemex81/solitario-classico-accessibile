"""Integration tests for STOCK_DRAW event registration in GameService.

Tests the critical fix for Phase 0 (v2.6.0) that ensures STOCK_DRAW events
are properly recorded during gameplay, enabling progressive penalties at
thresholds 21 and 41.

These tests use direct GameService setup (no GameEngine overhead) for
deterministic behavior and complete control over draw_count parameter.

Test Strategy:
- Setup GameService directly with controlled configuration
- Use event filtering for robust assertions (isolation from other events)
- Test both draw-1 and draw-3 modes for per-card counting verification
"""

import pytest

# Import directly from modules to avoid circular imports through __init__.py
import sys
sys.path.insert(0, '/home/runner/work/solitario-classico-accessibile/solitario-classico-accessibile')

from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck
from src.domain.rules.solitaire_rules import SolitaireRules
from src.domain.models.scoring import ScoringConfig, ScoreEventType

# Import services directly without going through __init__.py
from src.domain.services import scoring_service as scoring_mod
from src.domain.services import game_service as game_mod

ScoringService = scoring_mod.ScoringService
GameService = game_mod.GameService


@pytest.fixture
def game_service_draw1():
    """Create GameService with draw-1 mode and scoring enabled.
    
    Direct setup ensures deterministic behavior:
    - 1 card drawn per draw_cards() call
    - No external config interference
    - Full control over scoring parameters
    """
    deck = FrenchDeck()
    deck.crea()
    deck.mischia()
    table = GameTable(deck)
    rules = SolitaireRules(deck)
    scoring = ScoringService(
        config=ScoringConfig(),
        deck_type="french",
        difficulty_level=1,
        draw_count=1  # Force 1-card draw for determinism
    )
    service = GameService(table, rules, scoring)
    service.start_game()
    return service


@pytest.fixture
def game_service_draw3():
    """Create GameService with draw-3 mode and scoring enabled.
    
    Tests that event counting is per-card, not per-action.
    """
    deck = FrenchDeck()
    deck.crea()
    deck.mischia()
    table = GameTable(deck)
    rules = SolitaireRules(deck)
    scoring = ScoringService(
        config=ScoringConfig(),
        deck_type="french",
        difficulty_level=1,
        draw_count=3  # Draw-3 mode
    )
    service = GameService(table, rules, scoring)
    service.start_game()
    return service


class TestStockDrawEventsRecorded:
    """Tests for STOCK_DRAW event registration (Phase 0 - CRITICAL)."""
    
    def test_stock_draw_events_recorded_in_gameplay(self, game_service_draw1):
        """CRITICAL: Verify STOCK_DRAW events registered (deterministic setup).
        
        Uses GameService directly to avoid dependency on GameEngine config
        and ensure predictable draw behavior (1 card per call).
        
        This test catches the bug where draw_cards() increments draw_count
        but never calls scoring.record_event(ScoreEventType.STOCK_DRAW).
        """
        service = game_service_draw1
        scoring = service.scoring
        
        # Verify stock has enough cards
        assert service.table.pile_mazzo.get_card_count() >= 25, \
            "Stock must have at least 25 cards for test"
        
        # Draw exactly 25 cards (1 per call)
        for i in range(25):
            success, msg, cards = service.draw_cards(count=1)
            assert success, f"Draw {i+1} failed: {msg}"
            assert len(cards) == 1, f"Expected 1 card, got {len(cards)}"
        
        # VERIFY: Exactly 25 events registered
        assert scoring.stock_draw_count == 25, \
            f"Expected 25 STOCK_DRAW events, got {scoring.stock_draw_count}"
        
        # VERIFY: Correct penalty via EVENT FILTERING (isolation)
        # This approach isolates STOCK_DRAW events from other events
        # like CARD_REVEALED that might affect base_score
        draw_events = [
            e for e in scoring.score_events 
            if e.event_type == ScoreEventType.STOCK_DRAW
        ]
        assert len(draw_events) == 25, "Event count mismatch"
        
        # Draw 1-20: 0pt, Draw 21-25: 5 × -1pt = -5pt
        draw_penalty = sum(e.points for e in draw_events)
        assert draw_penalty == -5, \
            f"Expected -5pt penalty (draw 21-25), got {draw_penalty}pt"
    
    def test_stock_draw_penalties_progression(self, game_service_draw1):
        """Verify progressive penalties: 1-20 free, 21-40 = -1pt, 41+ = -2pt.
        
        Uses event filtering for robust assertion that doesn't depend
        on other scoring events that might occur during gameplay.
        """
        service = game_service_draw1
        scoring = service.scoring
        
        # Verify stock has enough cards
        # Note: French deck has 52 cards, 28 go to tableau, 24 remain in stock
        # We'll recycle if needed to reach 45 draws
        stock_count = service.table.pile_mazzo.get_card_count()
        
        # Draw as many as we can from initial stock
        draws_made = 0
        while draws_made < 45:
            stock = service.table.pile_mazzo
            waste = service.table.pile_scarti
            
            # Check if we need to recycle
            if stock.get_card_count() == 0 and not waste.is_empty():
                # Recycle waste back to stock
                success, msg = service.recycle_waste(shuffle=False)
                if not success:
                    break
            
            # Try to draw
            if stock.get_card_count() > 0:
                success, msg, cards = service.draw_cards(count=1)
                if success:
                    draws_made += len(cards)
                else:
                    break
            else:
                # Can't draw anymore
                break
        
        # We should have at least 45 draws (with recycling)
        assert draws_made >= 45, f"Only managed {draws_made} draws"
        
        # VERIFY: Event filtering (robust, isolated from other events)
        draw_events = [
            e for e in scoring.score_events
            if e.event_type == ScoreEventType.STOCK_DRAW
        ]
        assert len(draw_events) >= 45, \
            f"Expected at least 45 STOCK_DRAW events, got {len(draw_events)}"
        
        # Expected penalties for first 45 draws:
        # - Draw 1-20: 0pt (20 cards)
        # - Draw 21-40: -1pt × 20 = -20pt
        # - Draw 41-45: -2pt × 5 = -10pt
        # Total: -30pt
        first_45_events = draw_events[:45]
        total_penalty = sum(e.points for e in first_45_events)
        assert total_penalty == -30, \
            f"Expected -30pt total penalty for first 45 draws, got {total_penalty}pt"
        
        # Verify first 20 are free
        first_20 = sum(e.points for e in first_45_events[:20])
        assert first_20 == 0, f"First 20 draws should be free, got {first_20}pt"
        
        # Verify 21-40 are -1pt each
        draws_21_40 = sum(e.points for e in first_45_events[20:40])
        assert draws_21_40 == -20, f"Draws 21-40 should be -20pt, got {draws_21_40}pt"
        
        # Verify 41-45 are -2pt each
        draws_41_45 = sum(e.points for e in first_45_events[40:45])
        assert draws_41_45 == -10, f"Draws 41-45 should be -10pt, got {draws_41_45}pt"
    
    def test_stock_draw_penalties_with_draw3(self, game_service_draw3):
        """Verify penalties count per-card, not per-action with draw-3."""
        service = game_service_draw3
        scoring = service.scoring
        
        # Draw 7 actions × 3 cards = 21 cards total
        draws_made = 0
        actions = 0
        while actions < 7 and draws_made < 21:
            success, msg, cards = service.draw_cards(count=3)
            if success:
                draws_made += len(cards)
                actions += 1
            else:
                break
        
        # VERIFY: Exactly 21 events (not 7 actions)
        assert scoring.stock_draw_count >= 21, \
            f"Expected at least 21 events (per-card), got {scoring.stock_draw_count}"
        
        # VERIFY: Penalties start at card 21 (not action 21)
        draw_events = [
            e for e in scoring.score_events
            if e.event_type == ScoreEventType.STOCK_DRAW
        ]
        
        # Take first 21 events
        first_21 = draw_events[:21]
        assert len(first_21) >= 21, f"Expected 21 events, got {len(first_21)}"
        
        # Only 21st card has penalty (not cards 1-20)
        penalties = [e.points for e in first_21]
        assert penalties[:20] == [0] * 20, "First 20 draws should be free"
        assert penalties[20] == -1, "21st draw should have -1pt penalty"
    
    def test_stock_draw_events_without_scoring(self):
        """Verify game works normally when scoring=None (no crash)."""
        # Setup without scoring
        deck = FrenchDeck()
        deck.crea()
        deck.mischia()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules, scoring=None)
        service.start_game()
        
        # Draw cards should work without crash
        success, msg, cards = service.draw_cards(count=1)
        assert success, f"Draw failed: {msg}"
        assert len(cards) == 1
        
        # No scoring service to verify
        assert service.scoring is None
