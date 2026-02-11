"""Unit tests for GameService.get_game_report() with scoring integration (v1.5.2).

Tests verify:
- Provisional score included when scoring enabled
- "Disattivato" message when scoring OFF
- Correct report structure order
- Zero score edge case
"""

import pytest
from src.domain.services.game_service import GameService
from src.domain.services.scoring_service import ScoringService
from src.domain.models.scoring import ScoringConfig, ScoreEventType
from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck
from src.domain.rules.solitaire_rules import SolitaireRules


class TestGameReportWithScoring:
    """Test get_game_report() integration with scoring system (v1.5.2)."""
    
    def test_report_includes_provisional_score_when_enabled(self, game_service_with_scoring):
        """Report includes provisional score breakdown when scoring enabled.
        
        Given: Scoring service is enabled
        And: Some scoring events have been recorded
        When: get_game_report() is called
        Then: Report includes provisional score with breakdown
        And: Breakdown shows base score, multiplier, and deck bonus
        """
        # Setup: Record some scoring events
        game_service_with_scoring.scoring.record_event(
            ScoreEventType.TABLEAU_TO_FOUNDATION, "3 di Cuori"
        )
        game_service_with_scoring.scoring.record_event(
            ScoreEventType.CARD_REVEALED, "Asso di Quadri"
        )
        
        # Execute
        message, hint = game_service_with_scoring.get_game_report()
        
        # Verify scoring info included
        assert "Punteggio provvisorio:" in message
        assert "punti" in message
        assert "Base:" in message
        assert "Moltiplicatore" in message
        assert "Bonus mazzo:" in message
        
        # Verify no hint (report is complete)
        assert hint is None
    
    def test_report_shows_disabled_when_scoring_off(self, game_service_without_scoring):
        """Report shows 'Sistema punti disattivato' when scoring OFF.
        
        Given: Scoring service is None (disabled)
        When: get_game_report() is called
        Then: Report includes "Sistema punti disattivato" message
        And: No score breakdown is shown
        """
        # Execute
        message, hint = game_service_without_scoring.get_game_report()
        
        # Verify disabled message
        assert "Sistema punti disattivato" in message
        
        # Verify no score info
        assert "Punteggio" not in message or "Sistema punti disattivato" in message
        assert "Base:" not in message
        assert "Moltiplicatore" not in message
        
        # Verify no hint
        assert hint is None
    
    def test_report_structure_order_with_scoring(self, game_service_with_scoring):
        """Report follows correct line order: mosse → tempo → score → carte.
        
        Given: Scoring is enabled
        When: get_game_report() is called
        Then: Report lines are in expected order:
            1. "Report partita."
            2. "Mosse: X."
            3. "Tempo trascorso: X:XX."
            4. "Punteggio provvisorio: X punti..."
            5. "Carte nelle pile semi: X."
        """
        # Execute
        message, _ = game_service_with_scoring.get_game_report()
        
        # Parse lines
        lines = message.strip().split("\n")
        
        # Verify structure
        assert len(lines) == 5
        assert "Report partita" in lines[0]
        assert lines[1].startswith("Mosse:")
        assert lines[2].startswith("Tempo trascorso:")
        assert lines[3].startswith("Punteggio provvisorio:")
        assert lines[4].startswith("Carte nelle pile semi:")
    
    def test_report_structure_order_without_scoring(self, game_service_without_scoring):
        """Report follows correct line order when scoring OFF.
        
        Given: Scoring is disabled (None)
        When: get_game_report() is called
        Then: Report lines are in expected order:
            1. "Report partita."
            2. "Mosse: X."
            3. "Tempo trascorso: X:XX."
            4. "Sistema punti disattivato."
            5. "Carte nelle pile semi: X."
        """
        # Execute
        message, _ = game_service_without_scoring.get_game_report()
        
        # Parse lines
        lines = message.strip().split("\n")
        
        # Verify structure
        assert len(lines) == 5
        assert "Report partita" in lines[0]
        assert lines[1].startswith("Mosse:")
        assert lines[2].startswith("Tempo trascorso:")
        assert lines[3].startswith("Sistema punti disattivato")
        assert lines[4].startswith("Carte nelle pile semi:")
    
    def test_report_shows_zero_score_when_no_events(self, game_service_with_scoring):
        """Report correctly shows score when no scoring events recorded.
        
        Given: Scoring is enabled
        And: No scoring events have been recorded
        When: get_game_report() is called
        Then: Report shows provisional score (may include deck bonus)
        And: Base score is 0
        """
        # Execute (no events recorded)
        message, _ = game_service_with_scoring.get_game_report()
        
        # Verify score info present
        assert "Punteggio provvisorio:" in message
        assert "Base: 0" in message


# ========================================
# FIXTURES
# ========================================

@pytest.fixture
def game_table():
    """Create initialized game table with French deck."""
    deck = FrenchDeck()
    deck.crea()
    table = GameTable(deck)
    return table


@pytest.fixture
def game_service_with_scoring(game_table):
    """GameService instance with scoring enabled (medium difficulty).
    
    Returns:
        GameService with ScoringService configured for level 2 (1.25x multiplier)
    """
    config = ScoringConfig()
    scoring = ScoringService(
        config=config,
        difficulty_level=2,
        deck_type="french",
        draw_count=1,
        timer_enabled=False,
        timer_limit_seconds=-1
    )
    rules = SolitaireRules(game_table.mazzo)
    service = GameService(game_table, rules, scoring=scoring)
    service.start_game()
    return service


@pytest.fixture
def game_service_without_scoring(game_table):
    """GameService instance with scoring disabled (None).
    
    Returns:
        GameService without scoring service (free-play mode)
    """
    rules = SolitaireRules(game_table.mazzo)
    service = GameService(game_table, rules, scoring=None)
    service.start_game()
    return service
