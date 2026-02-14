"""
Unit tests per game_logger module.

Testa:
- Funzioni helper chiamano logger corretto
- Parametri passati correttamente
- Livelli logging corretti per ogni evento
"""

import logging
from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.logging import game_logger


class TestGameLifecycle:
    """
    Test helper per lifecycle partita.
    """
    
    @patch('src.infrastructure.logging.game_logger._game_logger')
    def test_game_started_logs_info(self, mock_logger):
        """
        Test: game_started() logga a livello INFO.
        """
        # Act
        game_logger.game_started("draw_three", "medium", True)
        
        # Assert
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "New game started" in call_args
        assert "draw_three" in call_args
        assert "medium" in call_args
    
    @patch('src.infrastructure.logging.game_logger._game_logger')
    def test_game_won_includes_stats(self, mock_logger):
        """
        Test: game_won() include statistiche nel log.
        """
        # Act
        game_logger.game_won(elapsed_time=120, moves_count=45, score=850)
        
        # Assert
        call_args = mock_logger.info.call_args[0][0]
        assert "WON" in call_args
        assert "120s" in call_args
        assert "45" in call_args
        assert "850" in call_args


class TestPlayerActions:
    """
    Test helper per azioni giocatore.
    """
    
    @patch('src.infrastructure.logging.game_logger._game_logger')
    def test_card_moved_success_logs_info(self, mock_logger):
        """
        Test: card_moved() con success=True logga INFO.
        """
        # Act
        game_logger.card_moved("tableau_3", "foundation_1", "A♠", True)
        
        # Assert
        mock_logger.log.assert_called_once_with(
            logging.INFO,
            "Move SUCCESS: A♠ from tableau_3 to foundation_1"
        )
    
    @patch('src.infrastructure.logging.game_logger._game_logger')
    def test_card_moved_failure_logs_warning(self, mock_logger):
        """
        Test: card_moved() con success=False logga WARNING.
        """
        # Act
        game_logger.card_moved("tableau_3", "foundation_1", "A♠", False)
        
        # Assert
        mock_logger.log.assert_called_once_with(
            logging.WARNING,
            "Move FAILED: A♠ from tableau_3 to foundation_1"
        )


class TestUINavigation:
    """
    Test helper per navigazione UI.
    """
    
    @patch('src.infrastructure.logging.game_logger._ui_logger')
    def test_panel_switched_logs_transition(self, mock_logger):
        """
        Test: panel_switched() logga transizione.
        """
        # Act
        game_logger.panel_switched("menu", "gameplay")
        
        # Assert
        call_args = mock_logger.info.call_args[0][0]
        assert "menu → gameplay" in call_args


class TestErrorHandling:
    """
    Test helper per errori.
    """
    
    @patch('src.infrastructure.logging.game_logger._error_logger')
    def test_error_occurred_with_exception(self, mock_logger):
        """
        Test: error_occurred() con exception include traceback.
        """
        # Arrange
        exception = ValueError("Test error")
        
        # Act
        game_logger.error_occurred("Validation", "Invalid state", exception)
        
        # Assert
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert "Validation" in call_args[0][0]
        assert call_args[1]['exc_info'] == exception
