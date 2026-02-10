"""Unit tests for GameEngine facade.

Tests the orchestration layer that coordinates domain services and infrastructure.
Uses mocking to isolate GameEngine behavior from its dependencies.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, Any

from src.application.game_engine import GameEngine
from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck
from src.domain.models.pile import Pile
from src.domain.models.card import Card
from src.domain.services.game_service import GameService
from src.domain.rules.solitaire_rules import SolitaireRules
from src.infrastructure.audio.screen_reader import ScreenReader


class TestGameEngineCreation:
    """Test GameEngine initialization and factory methods."""
    
    def test_initialization_with_components(self):
        """Test direct initialization with all components."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        screen_reader = Mock(spec=ScreenReader)
        
        # Act
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Assert
        assert engine.table is table
        assert engine.service is service
        assert engine.rules is rules
        assert engine.screen_reader is screen_reader
        assert engine.audio_enabled is True
    
    def test_factory_method_create(self):
        """Test factory method creates fully initialized engine."""
        # Act
        engine = GameEngine.create(audio_enabled=False)
        
        # Assert
        assert engine.table is not None
        assert engine.service is not None
        assert engine.rules is not None
        assert engine.screen_reader is None
        assert engine.audio_enabled is False
        
        # Verify table initialized
        assert len(engine.table.pile_base) == 7
        assert len(engine.table.pile_semi) == 4
        assert engine.table.pile_mazzo is not None
        assert engine.table.pile_scarti is not None
    
    def test_create_with_audio_enabled(self):
        """Test factory method with audio enabled attempts TTS creation."""
        with patch('src.application.game_engine.create_tts_provider') as mock_create_tts:
            # Setup mock
            mock_tts = Mock()
            mock_create_tts.return_value = mock_tts
            
            # Act
            engine = GameEngine.create(audio_enabled=True, tts_engine="sapi5")
            
            # Assert
            mock_create_tts.assert_called_once_with("sapi5")
            assert engine.screen_reader is not None
            assert engine.audio_enabled is True
    
    def test_create_with_audio_disabled(self):
        """Test graceful degradation when TTS unavailable."""
        with patch('src.application.game_engine.create_tts_provider') as mock_create_tts:
            # Setup mock to raise error
            mock_create_tts.side_effect = RuntimeError("TTS not available")
            
            # Act
            engine = GameEngine.create(audio_enabled=True)
            
            # Assert - engine created successfully without audio
            assert engine.screen_reader is None
            assert engine.audio_enabled is False
            assert engine.service is not None


class TestGameLifecycle:
    """Test game lifecycle methods (new_game, reset_game)."""
    
    def test_new_game_initializes_state(self):
        """Test new_game resets state and announces start."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        screen_reader = Mock(spec=ScreenReader)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Make some moves to change state
        service.move_count = 5
        service.start_time = 100.0
        
        # Act
        with patch.object(deck, 'mischia') as mock_shuffle:
            engine.new_game()
        
        # Assert
        mock_shuffle.assert_called_once()
        assert service.move_count == 0
        assert service.start_time is not None
        screen_reader.announce_move.assert_called_once_with(
            success=True,
            message="Nuova partita iniziata",
            interrupt=True
        )
    
    def test_reset_game_clears_statistics(self):
        """Test reset_game clears stats without redistributing cards."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        screen_reader = Mock(spec=ScreenReader)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Make some moves
        service.move_count = 10
        service.start_time = 100.0
        
        # Remember initial card positions
        initial_pile_counts = [p.get_card_count() for p in table.pile_base]
        
        # Act
        engine.reset_game()
        
        # Assert
        assert service.move_count == 0
        assert service.start_time is None
        
        # Cards not redistributed
        final_pile_counts = [p.get_card_count() for p in table.pile_base]
        assert initial_pile_counts == final_pile_counts
        
        screen_reader.announce_move.assert_called_once_with(
            success=True,
            message="Partita resettata",
            interrupt=True
        )
    
    def test_new_game_starts_timer(self):
        """Test new_game starts the game timer."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        
        # Act
        engine.new_game()
        
        # Assert
        assert engine.service.start_time is not None


class TestMoveExecution:
    """Test move execution methods with audio feedback."""
    
    def test_move_card_success(self):
        """Test successful card move with audio feedback."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Mock successful move
        service.move_card.return_value = (True, "Mossa eseguita (#1)")
        service.check_game_over.return_value = (False, "In corso")
        
        # Act
        success, message = engine.move_card(source_idx=0, target_idx=1, card_count=1)
        
        # Assert
        assert success is True
        assert "eseguita" in message
        service.move_card.assert_called_once()
        screen_reader.announce_move.assert_called_once_with(
            True,
            "Mossa eseguita (#1)",
            interrupt=False
        )
    
    def test_move_card_invalid_indices(self):
        """Test move with invalid pile indices."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        screen_reader = Mock(spec=ScreenReader)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Act
        success, message = engine.move_card(source_idx=99, target_idx=1)
        
        # Assert
        assert success is False
        assert "non valido" in message
        screen_reader.announce_error.assert_called_once_with("Indice pila non valido")
    
    def test_move_card_to_foundation(self):
        """Test move card to foundation pile (indices 7-10)."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Mock successful foundation move
        service.move_card.return_value = (True, "Carta aggiunta a fondazione")
        service.check_game_over.return_value = (False, "In corso")
        
        # Act
        success, message = engine.move_card(source_idx=0, target_idx=7)
        
        # Assert
        assert success is True
        # Verify is_foundation was passed as True
        call_args = service.move_card.call_args
        # The 4th positional argument is is_foundation_target
        assert call_args[0][3] is True  # positional args
    
    def test_draw_from_stock(self):
        """Test drawing cards from stock."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Mock draw
        mock_cards = [Mock(spec=Card)]
        service.draw_cards.return_value = (True, "Pescate 3 carte", mock_cards)
        
        # Act
        success, message = engine.draw_from_stock(count=3)
        
        # Assert
        assert success is True
        assert "Pescate" in message
        service.draw_cards.assert_called_once_with(3)
        screen_reader.announce_move.assert_called_once()
    
    def test_recycle_waste(self):
        """Test recycling waste pile back to stock."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Mock recycle
        service.recycle_waste.return_value = (True, "Tallone riciclato (12 carte)")
        
        # Act
        success, message = engine.recycle_waste(shuffle=True)
        
        # Assert
        assert success is True
        assert "riciclato" in message
        service.recycle_waste.assert_called_once_with(True)
        screen_reader.announce_move.assert_called_once()
    
    def test_auto_move_to_foundation(self):
        """Test automatic move to foundation."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Mock auto move with card
        mock_card = Mock(spec=Card)
        service.auto_move_to_foundation.return_value = (
            True,
            "Carta spostata automaticamente",
            mock_card
        )
        
        # Act
        success, message = engine.auto_move_to_foundation()
        
        # Assert
        assert success is True
        service.auto_move_to_foundation.assert_called_once()
        screen_reader.announce_card.assert_called_once_with(mock_card)
        assert screen_reader.announce_move.call_count == 1


class TestStateQueries:
    """Test game state query methods."""
    
    def test_get_game_state(self):
        """Test getting complete game state."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        engine = GameEngine(table, service, rules, None)
        
        # Mock statistics
        service.get_statistics.return_value = {
            "move_count": 15,
            "elapsed_time": 120.5,
            "draw_count": 3,
            "foundation_progress": [5, 3, 0, 0],
            "total_foundation_cards": 8
        }
        service.check_game_over.return_value = (False, "Partita in corso")
        
        # Act
        state = engine.get_game_state()
        
        # Assert
        assert "statistics" in state
        assert "game_over" in state
        assert "piles" in state
        
        assert state["statistics"]["move_count"] == 15
        assert state["game_over"]["is_over"] is False
        assert len(state["piles"]["tableau"]) == 7
        assert len(state["piles"]["foundations"]) == 4
    
    def test_is_victory(self):
        """Test victory check."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        engine = GameEngine(table, service, rules, None)
        
        # Mock victory
        service.is_victory.return_value = True
        
        # Act
        result = engine.is_victory()
        
        # Assert
        assert result is True
        service.is_victory.assert_called_once()
    
    def test_get_pile_info(self):
        """Test getting info about specific pile."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        
        # Act - Get info for first tableau pile
        info = engine.get_pile_info(0)
        
        # Assert
        assert info is not None
        assert "card_count" in info
        assert "is_empty" in info
        assert "top_card" in info
        assert isinstance(info["card_count"], int)
    
    def test_get_pile_info_invalid_index(self):
        """Test getting pile info with invalid index."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        
        # Act
        info = engine.get_pile_info(999)
        
        # Assert
        assert info is None


class TestAudioControl:
    """Test audio control methods."""
    
    def test_set_audio_enabled(self):
        """Test enabling/disabling audio."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        screen_reader = Mock(spec=ScreenReader)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Act
        engine.set_audio_enabled(False)
        
        # Assert
        screen_reader.set_enabled.assert_called_once_with(False)
        assert engine.audio_enabled is False
        
        # Act - enable again
        engine.set_audio_enabled(True)
        
        # Assert
        assert screen_reader.set_enabled.call_count == 2
        assert engine.audio_enabled is True
    
    def test_set_audio_verbose(self):
        """Test setting audio verbosity level."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        screen_reader = Mock(spec=ScreenReader)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Act
        engine.set_audio_verbose(2)
        
        # Assert
        screen_reader.set_verbose.assert_called_once_with(2)
    
    def test_audio_feedback_on_moves(self):
        """Test that moves trigger appropriate audio feedback."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Mock move results
        service.move_card.return_value = (True, "Mossa valida")
        service.check_game_over.return_value = (False, "In corso")
        
        # Act
        engine.move_card(0, 1)
        
        # Assert - verify audio was called
        screen_reader.announce_move.assert_called()


class TestVictoryDetection:
    """Test victory detection and announcement."""
    
    def test_victory_triggers_announcement(self):
        """Test that victory triggers audio announcement."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Mock victory condition
        service.move_card.return_value = (True, "Ultima carta spostata")
        service.check_game_over.return_value = (
            True,
            "Vittoria! Completato in 120s con 50 mosse"
        )
        service.get_statistics.return_value = {
            "move_count": 50,
            "elapsed_time": 120.0,
            "draw_count": 10
        }
        
        # Act
        success, message = engine.move_card(0, 7)
        
        # Assert
        assert success is True
        # Verify victory was announced
        screen_reader.announce_victory.assert_called_once_with(
            moves=50,
            time=120
        )


class TestHelperMethods:
    """Test private helper methods."""
    
    def test_get_pile_tableau(self):
        """Test getting tableau pile by index."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        
        # Act & Assert
        for i in range(7):
            pile = engine._get_pile(i)
            assert pile is engine.table.pile_base[i]
    
    def test_get_pile_foundation(self):
        """Test getting foundation pile by index."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        
        # Act & Assert
        for i in range(7, 11):
            pile = engine._get_pile(i)
            assert pile is engine.table.pile_semi[i - 7]
    
    def test_get_pile_stock(self):
        """Test getting stock pile."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        
        # Act
        pile = engine._get_pile(11)
        
        # Assert
        assert pile is engine.table.pile_mazzo
    
    def test_get_pile_waste(self):
        """Test getting waste pile."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        
        # Act
        pile = engine._get_pile(12)
        
        # Assert
        assert pile is engine.table.pile_scarti
    
    def test_get_pile_invalid(self):
        """Test getting pile with invalid index returns None."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        
        # Act & Assert
        assert engine._get_pile(-1) is None
        assert engine._get_pile(13) is None
        assert engine._get_pile(100) is None


class TestAutoRecycleWaste:
    """Test Bug #4 fix: Auto-recycle waste when stock is exhausted."""
    
    def test_auto_recycle_with_shuffle(self):
        """Test auto-recycle when stock empty, waste has cards, shuffle=True."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        screen_reader.tts = Mock()
        cursor = Mock()
        selection = Mock()
        engine = GameEngine(table, service, rules, cursor, selection, screen_reader)
        engine.shuffle_on_recycle = True
        
        # Setup: stock empty, waste has cards
        stock = Mock(spec=Pile)
        waste = Mock(spec=Pile)
        stock.is_empty.return_value = True
        waste.is_empty.return_value = False
        table.pile_mazzo = stock
        table.pile_scarti = waste
        
        # Mock recycle_waste to succeed
        service.recycle_waste.return_value = (True, "Tallone riciclato (15 carte)")
        
        # Mock draw_cards to return cards after recycle
        mock_cards = [Mock(spec=Card)]
        mock_cards[0].get_display_name.return_value = "7 di Cuori"
        service.draw_cards.return_value = (True, "Pescate 1 carte", mock_cards)
        
        # Act
        success, message = engine.draw_from_stock()
        
        # Assert
        assert success is True
        service.recycle_waste.assert_called_once_with(shuffle=True)
        service.draw_cards.assert_called_once_with(1)
        assert "Hai pescato" in message
        # Verify TTS was called for both recycle and draw
        assert screen_reader.tts.speak.call_count == 2
    
    def test_auto_recycle_without_shuffle(self):
        """Test auto-recycle when stock empty, waste has cards, shuffle=False."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        screen_reader.tts = Mock()
        cursor = Mock()
        selection = Mock()
        engine = GameEngine(table, service, rules, cursor, selection, screen_reader)
        engine.shuffle_on_recycle = False
        
        # Setup: stock empty, waste has cards
        stock = Mock(spec=Pile)
        waste = Mock(spec=Pile)
        stock.is_empty.return_value = True
        waste.is_empty.return_value = False
        table.pile_mazzo = stock
        table.pile_scarti = waste
        
        # Mock recycle_waste to succeed
        service.recycle_waste.return_value = (True, "Tallone riciclato (10 carte)")
        
        # Mock draw_cards to return cards after recycle
        mock_cards = [Mock(spec=Card)]
        mock_cards[0].get_display_name.return_value = "Regina di Quadri"
        service.draw_cards.return_value = (True, "Pescate 1 carte", mock_cards)
        
        # Act
        success, message = engine.draw_from_stock()
        
        # Assert
        assert success is True
        service.recycle_waste.assert_called_once_with(shuffle=False)
        service.draw_cards.assert_called_once_with(1)
        assert "Hai pescato" in message
    
    def test_both_piles_empty(self):
        """Test when both stock and waste are empty (no recycle)."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        screen_reader.tts = Mock()
        cursor = Mock()
        selection = Mock()
        engine = GameEngine(table, service, rules, cursor, selection, screen_reader)
        
        # Setup: both stock and waste empty
        stock = Mock(spec=Pile)
        waste = Mock(spec=Pile)
        stock.is_empty.return_value = True
        waste.is_empty.return_value = True
        table.pile_mazzo = stock
        table.pile_scarti = waste
        
        # Mock draw_cards to fail (both empty)
        service.draw_cards.return_value = (False, "Tallone e scarti vuoti - impossibile pescare", [])
        
        # Act
        success, message = engine.draw_from_stock()
        
        # Assert
        assert success is False
        assert "vuoti" in message.lower()
        service.recycle_waste.assert_not_called()
        service.draw_cards.assert_called_once_with(1)
    
    def test_stock_has_cards_no_recycle(self):
        """Test normal draw when stock has cards (no recycle needed)."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        screen_reader.tts = Mock()
        cursor = Mock()
        selection = Mock()
        engine = GameEngine(table, service, rules, cursor, selection, screen_reader)
        
        # Setup: stock has cards
        stock = Mock(spec=Pile)
        waste = Mock(spec=Pile)
        stock.is_empty.return_value = False
        waste.is_empty.return_value = False
        table.pile_mazzo = stock
        table.pile_scarti = waste
        
        # Mock draw_cards to succeed normally
        mock_cards = [Mock(spec=Card)]
        mock_cards[0].get_display_name.return_value = "Asso di Fiori"
        service.draw_cards.return_value = (True, "Pescate 1 carte", mock_cards)
        
        # Act
        success, message = engine.draw_from_stock()
        
        # Assert
        assert success is True
        service.recycle_waste.assert_not_called()
        service.draw_cards.assert_called_once_with(1)
        assert "Hai pescato" in message
    
    def test_recycle_fails(self):
        """Test when recycle_waste fails (edge case)."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        screen_reader.tts = Mock()
        cursor = Mock()
        selection = Mock()
        engine = GameEngine(table, service, rules, cursor, selection, screen_reader)
        
        # Setup: stock empty, waste has cards
        stock = Mock(spec=Pile)
        waste = Mock(spec=Pile)
        stock.is_empty.return_value = True
        waste.is_empty.return_value = False
        table.pile_mazzo = stock
        table.pile_scarti = waste
        
        # Mock recycle_waste to fail
        service.recycle_waste.return_value = (False, "Impossibile riciclare tallone")
        
        # Act
        success, message = engine.draw_from_stock()
        
        # Assert
        assert success is False
        assert "Impossibile riciclare" in message
        service.recycle_waste.assert_called_once_with(shuffle=False)
        service.draw_cards.assert_not_called()
    
    def test_multiple_recycles(self):
        """Test multiple recycles in sequence."""
        # Arrange
        deck = FrenchDeck()
        deck.crea()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = Mock(spec=GameService)
        screen_reader = Mock(spec=ScreenReader)
        screen_reader.tts = Mock()
        cursor = Mock()
        selection = Mock()
        engine = GameEngine(table, service, rules, cursor, selection, screen_reader)
        engine.shuffle_on_recycle = True
        
        # Setup: stock empty, waste has cards
        stock = Mock(spec=Pile)
        waste = Mock(spec=Pile)
        table.pile_mazzo = stock
        table.pile_scarti = waste
        
        # First recycle
        stock.is_empty.return_value = True
        waste.is_empty.return_value = False
        service.recycle_waste.return_value = (True, "Tallone riciclato")
        mock_cards1 = [Mock(spec=Card)]
        mock_cards1[0].get_display_name.return_value = "7 di Cuori"
        service.draw_cards.return_value = (True, "Pescate 1 carte", mock_cards1)
        
        success1, msg1 = engine.draw_from_stock()
        
        # Second recycle
        stock.is_empty.return_value = True
        waste.is_empty.return_value = False
        mock_cards2 = [Mock(spec=Card)]
        mock_cards2[0].get_display_name.return_value = "Regina di Quadri"
        service.draw_cards.return_value = (True, "Pescate 1 carte", mock_cards2)
        
        success2, msg2 = engine.draw_from_stock()
        
        # Assert
        assert success1 is True
        assert success2 is True
        assert service.recycle_waste.call_count == 2
        assert service.draw_cards.call_count == 2
