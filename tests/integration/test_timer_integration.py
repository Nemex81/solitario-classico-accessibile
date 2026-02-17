"""Integration tests for timer system in GameEngine."""

import pytest
import time
from unittest.mock import Mock, patch

from src.domain.models.game_end import EndReason
from src.domain.models.table import GameTable
from src.domain.services.game_service import GameService
from src.domain.services.game_settings import GameSettings
from src.domain.rules.solitaire_rules import SolitaireRules

# We need to directly build the GameEngine without going through application.__init__
# to avoid pygame dependency in tests
import sys
sys.path.insert(0, '/home/runner/work/solitario-classico-accessibile/solitario-classico-accessibile')

# Import GameEngine directly from the module file
import importlib.util
spec = importlib.util.spec_from_file_location(
    "game_engine",
    "/home/runner/work/solitario-classico-accessibile/solitario-classico-accessibile/src/application/game_engine.py"
)
game_engine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game_engine_module)
GameEngine = game_engine_module.GameEngine


class TestStrictModeTimeout:
    """Integration tests for STRICT mode timer."""
    
    @pytest.fixture
    def game_engine_strict(self):
        """Create a GameEngine with STRICT mode timer."""
        # Create mocks for dependencies
        table = Mock(spec=GameTable)
        table.mazzo = Mock()
        table.pile_base = []
        table.pile_semi = []
        table.pile_mazzo = Mock()
        table.pile_scarti = Mock()
        
        rules = Mock(spec=SolitaireRules)
        service = GameService(table, rules)
        cursor = Mock()
        selection = Mock()
        
        # Create settings with STRICT mode
        settings = GameSettings()
        settings.max_time_game = 60  # 60 seconds
        settings.timer_strict_mode = True
        
        # Create engine
        engine = GameEngine(
            table=table,
            service=service,
            rules=rules,
            cursor=cursor,
            selection=selection,
            settings=settings
        )
        
        # Start game
        service.is_game_running = True
        service.start_game()
        
        return engine
    
    def test_strict_timeout_ends_game(self, game_engine_strict):
        """Test that STRICT mode timeout ends the game."""
        # Simulate game started 61 seconds ago
        game_engine_strict.service.start_time = time.time() - 61
        
        # Mock end_game to capture the call
        with patch.object(game_engine_strict, 'end_game') as mock_end_game:
            # Trigger tick check
            game_engine_strict.on_timer_tick()
            
            # Verify end_game called with TIMEOUT_STRICT
            mock_end_game.assert_called_once_with(EndReason.TIMEOUT_STRICT)
    
    def test_strict_timeout_announces_expiry(self, game_engine_strict):
        """Test that STRICT mode timeout announces expiry."""
        # Simulate game started 61 seconds ago
        game_engine_strict.service.start_time = time.time() - 61
        
        # Mock _speak to capture announcement
        with patch.object(game_engine_strict, '_speak') as mock_speak:
            # Mock end_game to prevent actual game end
            with patch.object(game_engine_strict, 'end_game'):
                # Trigger tick check
                game_engine_strict.on_timer_tick()
                
                # Verify announcement
                mock_speak.assert_called_once()
                call_args = mock_speak.call_args[0][0]
                assert "Tempo scaduto!" in call_args
