"""Unit tests for ScoreFormatter.

Tests TTS-optimized Italian message formatting for:
- Provisional scores
- Final scores
- Score events
- Scoring disabled messages
"""

import pytest
from datetime import datetime, timezone
from src.presentation.formatters.score_formatter import ScoreFormatter
from src.domain.models.scoring import (
    ProvisionalScore,
    FinalScore,
    ScoreEvent,
    ScoreEventType
)


class TestProvisionalScoreFormatting:
    """Tests for provisional score formatting."""
    
    def test_format_provisional_score_basic(self):
        """Test basic provisional score formatting."""
        score = ProvisionalScore(
            base_score=10,
            deck_bonus=150,
            draw_bonus=0,
            difficulty_multiplier=1.0
        )
        
        result = ScoreFormatter.format_provisional_score(score)
        
        assert "Punteggio provvisorio: 160 punti" in result
        assert "Punteggio base: 10 punti" in result
        assert "Bonus mazzo: 150 punti" in result
        assert "Moltiplicatore difficoltà: 1 punto 0" in result
    
    def test_format_provisional_score_with_draw_bonus(self):
        """Test provisional score with draw bonus."""
        score = ProvisionalScore(
            base_score=20,
            deck_bonus=150,
            draw_bonus=100,
            difficulty_multiplier=1.5
        )
        
        result = ScoreFormatter.format_provisional_score(score)
        
        assert "Punteggio provvisorio: 405 punti" in result
        assert "Bonus carte pescate: 100 punti" in result
        assert "Moltiplicatore difficoltà: 1 punto 5" in result
    
    def test_format_provisional_score_no_bonuses(self):
        """Test provisional score with no bonuses."""
        score = ProvisionalScore(
            base_score=50,
            deck_bonus=0,
            draw_bonus=0,
            difficulty_multiplier=2.0
        )
        
        result = ScoreFormatter.format_provisional_score(score)
        
        assert "Punteggio provvisorio: 100 punti" in result
        assert "Punteggio base: 50 punti" in result
        assert "Bonus mazzo" not in result
        assert "Bonus carte pescate" not in result
        assert "Moltiplicatore difficoltà: 2 punto 0" in result


class TestFinalScoreFormatting:
    """Tests for final score formatting."""
    
    def test_format_final_score_victory(self):
        """Test final score formatting with victory."""
        score = FinalScore(
            base_score=85,
            deck_bonus=150,
            draw_bonus=100,
            difficulty_multiplier=2.0,
            time_bonus=345,
            victory_bonus=500,
            total_score=1015,
            is_victory=True,
            elapsed_seconds=180.5,
            difficulty_level=4,
            deck_type="french",
            draw_count=2,
            recycle_count=1,
            move_count=42
        )
        
        result = ScoreFormatter.format_final_score(score)
        
        assert "Vittoria!" in result
        assert "Punteggio finale: 1015 punti" in result
        assert "Punteggio base: 85 punti" in result
        assert "Bonus mazzo: 150 punti" in result
        assert "Bonus carte pescate: 100 punti" in result
        assert "Bonus tempo: 345 punti" in result
        assert "Bonus vittoria: 500 punti" in result
        assert "3 minuti e 0 secondi" in result
        assert "Mosse: 42" in result
        assert "Ricicli: 1" in result
    
    def test_format_final_score_defeat(self):
        """Test final score formatting with defeat."""
        score = FinalScore(
            base_score=30,
            deck_bonus=0,
            draw_bonus=0,
            difficulty_multiplier=1.0,
            time_bonus=0,
            victory_bonus=0,
            total_score=30,
            is_victory=False,
            elapsed_seconds=120.0,
            difficulty_level=1,
            deck_type="neapolitan",
            draw_count=1,
            recycle_count=5,
            move_count=15
        )
        
        result = ScoreFormatter.format_final_score(score)
        
        assert "Partita terminata" in result
        assert "Vittoria!" not in result
        assert "Punteggio finale: 30 punti" in result
        assert "Bonus vittoria" not in result
        assert "2 minuti e 0 secondi" in result
    
    def test_format_final_score_negative_time_bonus(self):
        """Test final score with negative time bonus (timer expired)."""
        score = FinalScore(
            base_score=50,
            deck_bonus=0,
            draw_bonus=0,
            difficulty_multiplier=1.0,
            time_bonus=-500,
            victory_bonus=0,
            total_score=0,
            is_victory=False,
            elapsed_seconds=1800.0,
            difficulty_level=1,
            deck_type="french",
            draw_count=1,
            recycle_count=0,
            move_count=10
        )
        
        result = ScoreFormatter.format_final_score(score)
        
        assert "Penalità tempo: 500 punti" in result
        assert "30 minuti e 0 secondi" in result


class TestScoreEventFormatting:
    """Tests for score event formatting."""
    
    def test_format_waste_to_foundation(self):
        """Test formatting waste to foundation event."""
        event = ScoreEvent(
            event_type=ScoreEventType.WASTE_TO_FOUNDATION,
            points=10,
            context="Asso di Cuori"
        )
        
        result = ScoreFormatter.format_score_event(event)
        
        assert "Scarto a fondazione" in result
        assert "Asso di Cuori" in result
        assert "più 10 punti" in result
    
    def test_format_tableau_to_foundation(self):
        """Test formatting tableau to foundation event."""
        event = ScoreEvent(
            event_type=ScoreEventType.TABLEAU_TO_FOUNDATION,
            points=10
        )
        
        result = ScoreFormatter.format_score_event(event)
        
        assert "Tableau a fondazione" in result
        assert "più 10 punti" in result
    
    def test_format_card_revealed(self):
        """Test formatting card revealed event."""
        event = ScoreEvent(
            event_type=ScoreEventType.CARD_REVEALED,
            points=5,
            context="7 di Quadri"
        )
        
        result = ScoreFormatter.format_score_event(event)
        
        assert "Carta scoperta" in result
        assert "7 di Quadri" in result
        assert "più 5 punti" in result
    
    def test_format_recycle_waste_penalty(self):
        """Test formatting recycle waste with penalty."""
        event = ScoreEvent(
            event_type=ScoreEventType.RECYCLE_WASTE,
            points=-20
        )
        
        result = ScoreFormatter.format_score_event(event)
        
        assert "Riciclo scarti" in result
        assert "meno 20 punti" in result
    
    def test_format_recycle_waste_no_penalty(self):
        """Test formatting recycle waste with no penalty."""
        event = ScoreEvent(
            event_type=ScoreEventType.RECYCLE_WASTE,
            points=0
        )
        
        result = ScoreFormatter.format_score_event(event)
        
        assert "Riciclo scarti" in result
        assert "nessun punto" in result


class TestScoringDisabled:
    """Tests for scoring disabled message."""
    
    def test_format_scoring_disabled(self):
        """Test scoring disabled message."""
        result = ScoreFormatter.format_scoring_disabled()
        
        assert "Sistema di punteggio disattivato" in result
        assert "Attivalo nelle opzioni" in result


class TestBestScoreFormatting:
    """Tests for best score formatting."""
    
    def test_format_best_score_with_victory(self):
        """Test formatting best score with victory."""
        score_dict = {
            'total_score': 1250,
            'is_victory': True,
            'difficulty_level': 4
        }
        
        result = ScoreFormatter.format_best_score(score_dict)
        
        assert "Miglior punteggio: 1250 punti" in result
        assert "Vittoria: Sì" in result
        assert "Difficoltà: Esperto" in result
    
    def test_format_best_score_without_victory(self):
        """Test formatting best score without victory."""
        score_dict = {
            'total_score': 500,
            'is_victory': False,
            'difficulty_level': 1
        }
        
        result = ScoreFormatter.format_best_score(score_dict)
        
        assert "Miglior punteggio: 500 punti" in result
        assert "Vittoria: No" in result
        assert "Difficoltà: Facile" in result
    
    def test_format_best_score_empty(self):
        """Test formatting when no scores exist."""
        result = ScoreFormatter.format_best_score({})
        
        assert "Nessun punteggio registrato" in result
    
    def test_format_best_score_all_difficulties(self):
        """Test formatting with all difficulty levels."""
        difficulty_names = {
            1: "Facile",
            2: "Medio",
            3: "Difficile",
            4: "Esperto",
            5: "Maestro"
        }
        
        for level, name in difficulty_names.items():
            score_dict = {
                'total_score': 1000,
                'is_victory': True,
                'difficulty_level': level
            }
            
            result = ScoreFormatter.format_best_score(score_dict)
            assert name in result


class TestItalianTTSOptimization:
    """Tests for Italian TTS optimization."""
    
    def test_no_special_characters(self):
        """Test that messages don't contain problematic special characters."""
        score = ProvisionalScore(
            base_score=10,
            deck_bonus=0,
            draw_bonus=0,
            difficulty_multiplier=1.5
        )
        
        result = ScoreFormatter.format_provisional_score(score)
        
        # Should not contain problematic chars
        assert "/" not in result
        assert "#" not in result
        assert "@" not in result
    
    def test_decimal_separator_replaced(self):
        """Test that decimal points are replaced for TTS."""
        score = ProvisionalScore(
            base_score=10,
            deck_bonus=0,
            draw_bonus=0,
            difficulty_multiplier=2.5
        )
        
        result = ScoreFormatter.format_provisional_score(score)
        
        # Should say "2 punto 5" not "2.5"
        assert "2 punto 5" in result
        assert "2.5" not in result
    
    def test_all_messages_in_italian(self):
        """Test that all messages are in Italian."""
        # Test provisional score
        prov_score = ProvisionalScore(10, 0, 0, 1.0)
        prov_result = ScoreFormatter.format_provisional_score(prov_score)
        assert "punti" in prov_result
        assert "Punteggio" in prov_result
        
        # Test event
        event = ScoreEvent(ScoreEventType.CARD_REVEALED, 5)
        event_result = ScoreFormatter.format_score_event(event)
        assert "Carta scoperta" in event_result
        assert "più" in event_result or "meno" in event_result or "nessun" in event_result
        
        # Test scoring disabled
        disabled_result = ScoreFormatter.format_scoring_disabled()
        assert "disattivato" in disabled_result
        assert "opzioni" in disabled_result
