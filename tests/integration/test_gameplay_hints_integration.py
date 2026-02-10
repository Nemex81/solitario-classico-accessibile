"""Integration tests for Command Hints v1.5.0 feature.

Tests the complete flow of hint generation and conditional vocalization:
- Domain layer generates hints (CursorManager, GameService)
- Application layer vocalizes conditionally (GameplayController)
- Settings control vocalization (command_hints_enabled)
"""

import pytest
from unittest.mock import Mock, patch, call
import pygame

from src.domain.services.game_settings import GameSettings, GameState
from src.application.game_engine import GameEngine
from src.application.gameplay_controller import GamePlayController
from src.domain.models.deck import FrenchDeck
from src.domain.models.table import GameTable
from src.domain.rules.solitaire_rules import SolitaireRules
from src.domain.services.game_service import GameService
from src.domain.services.cursor_manager import CursorManager
from src.domain.services.selection_manager import SelectionManager


@pytest.fixture
def mock_screen_reader():
    """Create mock screen reader with TTS."""
    sr = Mock()
    sr.tts = Mock()
    sr.tts.speak = Mock()
    return sr


@pytest.fixture
def game_table():
    """Create game table for tests."""
    deck = FrenchDeck()
    deck.crea()
    return GameTable(deck)


@pytest.fixture
def game_components(game_table):
    """Create game components (service, cursor, etc.)."""
    deck = FrenchDeck()
    rules = SolitaireRules(deck)
    service = GameService(game_table, rules)
    cursor = CursorManager(game_table)
    selection = SelectionManager()
    return service, cursor, selection


@pytest.fixture
def game_engine(game_components, mock_screen_reader):
    """Create game engine."""
    service, cursor, selection = game_components
    deck = FrenchDeck()
    rules = SolitaireRules(deck)
    return GameEngine(
        table=service.table,
        service=service,
        rules=rules,
        cursor=cursor,
        selection=selection,
        screen_reader=mock_screen_reader,
        settings=None
    )


@pytest.fixture
def settings_hints_enabled():
    """Create settings with hints enabled."""
    game_state = GameState()
    settings = GameSettings(game_state=game_state)
    settings.command_hints_enabled = True
    return settings


@pytest.fixture
def settings_hints_disabled():
    """Create settings with hints disabled."""
    game_state = GameState()
    settings = GameSettings(game_state=game_state)
    settings.command_hints_enabled = False
    return settings


@pytest.fixture
def controller_hints_enabled(game_engine, mock_screen_reader, settings_hints_enabled):
    """Create gameplay controller with hints enabled."""
    return GamePlayController(
        engine=game_engine,
        screen_reader=mock_screen_reader,
        settings=settings_hints_enabled
    )


@pytest.fixture
def controller_hints_disabled(game_engine, mock_screen_reader, settings_hints_disabled):
    """Create gameplay controller with hints disabled."""
    return GamePlayController(
        engine=game_engine,
        screen_reader=mock_screen_reader,
        settings=settings_hints_disabled
    )


# ============================================================================
# GROUP 1: Hints Enabled → 2 speak calls (message + hint)
# ============================================================================

def test_cursor_up_hints_enabled(controller_hints_enabled, mock_screen_reader):
    """Test cursor up with hints enabled calls speak twice."""
    with patch.object(controller_hints_enabled.engine, 'move_cursor',
                      return_value=("Regina di Fiori", "Premi INVIO per selezionare")):
        controller_hints_enabled._cursor_up()
        
        assert mock_screen_reader.tts.speak.call_count == 2
        calls = mock_screen_reader.tts.speak.call_args_list
        assert calls[0] == call("Regina di Fiori", interrupt=True)
        assert calls[1] == call("Premi INVIO per selezionare", interrupt=False)


def test_cursor_down_hints_enabled(controller_hints_enabled, mock_screen_reader):
    """Test cursor down with hints enabled calls speak twice."""
    with patch.object(controller_hints_enabled.engine, 'move_cursor',
                      return_value=("Sette di Cuori", "Usa frecce per navigare")):
        controller_hints_enabled._cursor_down()
        
        assert mock_screen_reader.tts.speak.call_count == 2
        calls = mock_screen_reader.tts.speak.call_args_list
        assert calls[0] == call("Sette di Cuori", interrupt=True)
        assert calls[1] == call("Usa frecce per navigare", interrupt=False)


def test_nav_pile_base_hints_enabled(controller_hints_enabled, mock_screen_reader):
    """Test navigation to base pile with hints enabled."""
    with patch.object(controller_hints_enabled.engine, 'jump_to_pile',
                      return_value=("Pila 3. Asso di Quadri", "Premi ancora 3 per selezionare")):
        controller_hints_enabled._nav_pile_base(3)
        
        assert mock_screen_reader.tts.speak.call_count == 2
        calls = mock_screen_reader.tts.speak.call_args_list
        assert calls[0] == call("Pila 3. Asso di Quadri", interrupt=True)
        assert calls[1] == call("Premi ancora 3 per selezionare", interrupt=False)


def test_cursor_tab_hints_enabled(controller_hints_enabled, mock_screen_reader):
    """Test TAB navigation with hints enabled."""
    with patch.object(controller_hints_enabled.engine, 'move_cursor',
                      return_value=("Pile semi", "Premi TAB ancora per prossimo tipo")):
        controller_hints_enabled._cursor_tab()
        
        assert mock_screen_reader.tts.speak.call_count == 2
        calls = mock_screen_reader.tts.speak.call_args_list
        assert calls[0] == call("Pile semi", interrupt=True)
        assert calls[1] == call("Premi TAB ancora per prossimo tipo", interrupt=False)


# ============================================================================
# GROUP 2: Hints Disabled → 1 speak call (message only)
# ============================================================================

def test_cursor_up_hints_disabled(controller_hints_disabled, mock_screen_reader):
    """Test cursor up with hints disabled calls speak once."""
    with patch.object(controller_hints_disabled.engine, 'move_cursor',
                      return_value=("Regina di Fiori", "Premi INVIO per selezionare")):
        controller_hints_disabled._cursor_up()
        
        assert mock_screen_reader.tts.speak.call_count == 1
        mock_screen_reader.tts.speak.assert_called_once_with("Regina di Fiori", interrupt=True)


def test_nav_pile_base_hints_disabled(controller_hints_disabled, mock_screen_reader):
    """Test navigation to base pile with hints disabled."""
    with patch.object(controller_hints_disabled.engine, 'jump_to_pile',
                      return_value=("Pila 3. Asso di Quadri", "Premi ancora 3 per selezionare")):
        controller_hints_disabled._nav_pile_base(3)
        
        assert mock_screen_reader.tts.speak.call_count == 1
        mock_screen_reader.tts.speak.assert_called_once_with("Pila 3. Asso di Quadri", interrupt=True)


def test_info_command_hints_disabled(controller_hints_disabled, mock_screen_reader):
    """Test info command with hints disabled."""
    with patch.object(controller_hints_disabled.engine.service, 'get_timer_info',
                      return_value=("Tempo: 5 minuti", "Premi O per opzioni")):
        controller_hints_disabled._get_timer()
        
        assert mock_screen_reader.tts.speak.call_count == 1
        mock_screen_reader.tts.speak.assert_called_once_with("Tempo: 5 minuti", interrupt=True)


# ============================================================================
# GROUP 3: Timing Validation (200ms pause)
# ============================================================================

@patch('pygame.time.wait')
def test_pause_200ms_between_message_hint(mock_wait, controller_hints_enabled, mock_screen_reader):
    """Test 200ms pause occurs between message and hint."""
    with patch.object(controller_hints_enabled.engine, 'jump_to_pile',
                      return_value=("Pila 3", "Premi ancora 3")):
        controller_hints_enabled._nav_pile_base(3)
        
        mock_wait.assert_called_once_with(200)
        # Verify wait called between the two speaks
        assert mock_screen_reader.tts.speak.call_count == 2


@patch('pygame.time.wait')
def test_no_pause_when_hints_disabled(mock_wait, controller_hints_disabled, mock_screen_reader):
    """Test no pause occurs when hints disabled."""
    with patch.object(controller_hints_disabled.engine, 'move_cursor',
                      return_value=("Asso di Fiori", "Hint non vocalizzato")):
        controller_hints_disabled._cursor_down()
        
        mock_wait.assert_not_called()
        assert mock_screen_reader.tts.speak.call_count == 1


# ============================================================================
# GROUP 4: Edge Cases (hint=None)
# ============================================================================

def test_hint_none_only_one_speak(controller_hints_enabled, mock_screen_reader):
    """Test that hint=None results in only one speak call."""
    with patch.object(controller_hints_enabled.engine.service, 'get_game_report',
                      return_value=("Report completo", None)):
        controller_hints_enabled._get_game_report()
        
        assert mock_screen_reader.tts.speak.call_count == 1
        mock_screen_reader.tts.speak.assert_called_once_with("Report completo", interrupt=True)


def test_table_info_no_hint(controller_hints_enabled, mock_screen_reader):
    """Test table info returns no hint."""
    with patch.object(controller_hints_enabled.engine.service, 'get_table_info',
                      return_value=("Panoramica tavolo completa", None)):
        controller_hints_enabled._get_table_info()
        
        assert mock_screen_reader.tts.speak.call_count == 1


# ============================================================================
# GROUP 5: Info Commands Integration
# ============================================================================

def test_waste_info_with_hint(controller_hints_enabled, mock_screen_reader):
    """Test waste info command vocalizes hint."""
    with patch.object(controller_hints_enabled.engine.service, 'get_waste_info',
                      return_value=("Scarti: 5 carte", "Usa SHIFT+S per navigare")):
        controller_hints_enabled._get_scarto_top()
        
        assert mock_screen_reader.tts.speak.call_count == 2
        calls = mock_screen_reader.tts.speak.call_args_list
        assert calls[0] == call("Scarti: 5 carte", interrupt=True)
        assert calls[1] == call("Usa SHIFT+S per navigare", interrupt=False)


def test_stock_info_with_hint(controller_hints_enabled, mock_screen_reader):
    """Test stock info command vocalizes hint."""
    with patch.object(controller_hints_enabled.engine.service, 'get_stock_info',
                      return_value=("Mazzo: 10 carte", "Premi D o P per pescare")):
        controller_hints_enabled._get_deck_count()
        
        assert mock_screen_reader.tts.speak.call_count == 2
        calls = mock_screen_reader.tts.speak.call_args_list
        assert calls[0] == call("Mazzo: 10 carte", interrupt=True)
        assert calls[1] == call("Premi D o P per pescare", interrupt=False)


def test_settings_info_with_hint(controller_hints_enabled, mock_screen_reader):
    """Test settings info command vocalizes hint."""
    with patch.object(controller_hints_enabled.engine.service, 'get_settings_info',
                      return_value=("Impostazioni correnti", "Premi O per menu opzioni")):
        controller_hints_enabled._get_settings()
        
        assert mock_screen_reader.tts.speak.call_count == 2
        calls = mock_screen_reader.tts.speak.call_args_list
        assert calls[0] == call("Impostazioni correnti", interrupt=True)
        assert calls[1] == call("Premi O per menu opzioni", interrupt=False)


# ============================================================================
# GROUP 6: Interrupt Flags Validation
# ============================================================================

def test_message_uses_interrupt_true(controller_hints_enabled, mock_screen_reader):
    """Test message always uses interrupt=True."""
    with patch.object(controller_hints_enabled.engine, 'move_cursor',
                      return_value=("Message", "Hint")):
        controller_hints_enabled._cursor_left()
        
        calls = mock_screen_reader.tts.speak.call_args_list
        assert calls[0][1]['interrupt'] is True


def test_hint_uses_interrupt_false(controller_hints_enabled, mock_screen_reader):
    """Test hint always uses interrupt=False."""
    with patch.object(controller_hints_enabled.engine, 'move_cursor',
                      return_value=("Message", "Hint")):
        controller_hints_enabled._cursor_right()
        
        calls = mock_screen_reader.tts.speak.call_args_list
        assert calls[1][1]['interrupt'] is False
