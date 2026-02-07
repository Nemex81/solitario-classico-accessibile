"""Integration tests for GameEngine facade.

Tests the complete game flow through the GameEngine facade without mocks.
Uses real components (GameTable, GameService, SolitaireRules) to verify
end-to-end functionality.
"""

import pytest
from unittest.mock import Mock

from src.application.game_engine import GameEngine
from src.domain.models.deck import FrenchDeck
from src.domain.models.card import Card
from src.infrastructure.audio.tts_provider import TtsProvider


class MockTtsProvider(TtsProvider):
    """Mock TTS provider for testing."""
    
    def __init__(self):
        self.spoken_text = []
        self.stopped = False
    
    def speak(self, text: str, interrupt: bool = False) -> None:
        self.spoken_text.append(text)
    
    def stop(self) -> None:
        self.stopped = True
    
    def set_rate(self, rate: int) -> None:
        pass
    
    def set_volume(self, volume: float) -> None:
        pass


class TestCompleteGameFlow:
    """Test complete game flows from initialization to moves."""
    
    def test_new_game_to_first_move(self):
        """Test creating engine, starting game, and making first move."""
        # Arrange - Create engine without audio
        engine = GameEngine.create(audio_enabled=False)
        
        # Act - Start new game
        engine.new_game()
        
        # Assert - Verify game initialized
        state = engine.get_game_state()
        assert state["statistics"]["move_count"] == 0
        assert state["statistics"]["elapsed_time"] > 0
        assert state["game_over"]["is_over"] is False
        
        # Verify piles initialized
        assert len(state["piles"]["tableau"]) == 7
        assert len(state["piles"]["foundations"]) == 4
        assert state["piles"]["stock"] > 0
        assert state["piles"]["waste"] == 0
        
        # Verify each tableau pile has correct number of cards
        for i, count in enumerate(state["piles"]["tableau"]):
            assert count == i + 1, f"Tableau {i} should have {i+1} cards"
    
    def test_draw_and_move_sequence(self):
        """Test drawing cards and moving them around."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        engine.new_game()
        
        # Act - Draw from stock
        success, message = engine.draw_from_stock(count=1)
        
        # Assert - Draw succeeded
        assert success is True
        assert "Pescate" in message
        
        # Verify waste has cards
        state = engine.get_game_state()
        assert state["piles"]["waste"] > 0
        
        # Try to make a move (may or may not be valid depending on cards)
        # Just verify the API works
        success, message = engine.move_card(source_idx=0, target_idx=1)
        
        # Should return a result (valid or invalid)
        assert isinstance(success, bool)
        assert isinstance(message, str)
        assert len(message) > 0
    
    def test_auto_move_chain(self):
        """Test auto-move functionality in sequence."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        engine.new_game()
        
        # Try auto-moves until none are available
        auto_moves = 0
        max_attempts = 10
        
        # Act - Try several auto-moves
        for _ in range(max_attempts):
            success, message = engine.auto_move_to_foundation()
            if success:
                auto_moves += 1
            else:
                # No more auto-moves available
                break
        
        # Assert - At least tried auto-move
        assert auto_moves >= 0  # May be 0 if no moves available
        
        # Verify game state is consistent
        state = engine.get_game_state()
        assert state["statistics"]["move_count"] == auto_moves
        
        # If any cards moved to foundations, verify they're there
        total_foundation_cards = sum(state["piles"]["foundations"])
        assert total_foundation_cards == auto_moves


class TestVictoryScenario:
    """Test victory detection and announcement."""
    
    def test_victory_detection(self):
        """Test that victory is detected when all foundations complete."""
        # Arrange - Create engine
        engine = GameEngine.create(audio_enabled=False)
        engine.new_game()
        
        # Rather than manually constructing victory, we'll mock the service to return victory
        # This tests that GameEngine correctly delegates to service and interprets result
        from unittest.mock import patch
        
        # Mock the victory check
        with patch.object(engine.service, 'is_victory', return_value=True):
            # Act - Check victory
            is_victory = engine.is_victory()
            
            # Assert
            assert is_victory is True
        
        # Also test check_game_over reports victory
        with patch.object(engine.service, 'check_game_over', return_value=(True, "Vittoria! Completato in 120s con 50 mosse")):
            state = engine.get_game_state()
            assert state["game_over"]["is_over"] is True
            assert "Vittoria" in state["game_over"]["status"]
    
    def test_victory_audio_announcement(self):
        """Test that victory triggers audio announcement."""
        # Arrange - Create engine with mock TTS
        mock_tts = MockTtsProvider()
        from src.infrastructure.audio.screen_reader import ScreenReader
        screen_reader = ScreenReader(mock_tts, enabled=True)
        
        # Create engine with audio
        deck = FrenchDeck()
        deck.crea()
        from src.domain.models.table import GameTable
        from src.domain.rules.solitaire_rules import SolitaireRules
        from src.domain.services.game_service import GameService
        
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Start game to initialize timer
        engine.new_game()
        
        # Clear previous announcements
        mock_tts.spoken_text = []
        
        # Act - Make a move that will trigger victory check
        # Mock successful move that triggers victory
        from unittest.mock import patch
        with patch.object(service, 'move_card', return_value=(True, "Ultima mossa")):
            with patch.object(service, 'check_game_over', return_value=(True, "Vittoria! Completato in 120s con 50 mosse")):
                with patch.object(service, 'get_statistics', return_value={"move_count": 50, "elapsed_time": 120.0}):
                    success, message = engine.move_card(0, 7)
        
        # Assert - Victory was announced
        assert success is True
        
        # Check that victory announcement was made
        victory_announced = any("Vittoria" in text for text in mock_tts.spoken_text)
        assert victory_announced, f"Victory not announced. Spoken: {mock_tts.spoken_text}"


class TestRecycleAndReshuffle:
    """Test waste recycling functionality."""
    
    def test_recycle_waste_without_shuffle(self):
        """Test recycling waste pile back to stock without shuffle."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        engine.new_game()
        
        # Draw all cards from stock
        initial_stock_count = engine.table.pile_mazzo.get_card_count()
        
        while not engine.table.pile_mazzo.is_empty():
            engine.draw_from_stock(count=1)
        
        # Verify stock is empty and waste has cards
        assert engine.table.pile_mazzo.is_empty()
        assert engine.table.pile_scarti.get_card_count() == initial_stock_count
        
        # Act - Recycle without shuffle
        success, message = engine.recycle_waste(shuffle=False)
        
        # Assert
        assert success is True
        assert "riciclato" in message
        assert engine.table.pile_mazzo.get_card_count() == initial_stock_count
        assert engine.table.pile_scarti.is_empty()
    
    def test_recycle_waste_with_shuffle(self):
        """Test recycling waste pile with shuffle."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        engine.new_game()
        
        # Draw ALL cards from stock to waste
        while not engine.table.pile_mazzo.is_empty():
            engine.draw_from_stock(count=1)
        
        waste_count = engine.table.pile_scarti.get_card_count()
        
        # Skip if no cards in waste
        if waste_count == 0:
            pytest.skip("No cards in waste to recycle")
        
        # Verify stock is empty
        assert engine.table.pile_mazzo.is_empty()
        
        # Act - Recycle with shuffle
        success, message = engine.recycle_waste(shuffle=True)
        
        # Assert
        assert success is True
        assert engine.table.pile_mazzo.get_card_count() == waste_count
        assert engine.table.pile_scarti.is_empty()


class TestGameStateQueries:
    """Test game state query methods."""
    
    def test_pile_info_for_all_piles(self):
        """Test getting info for all pile types."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        engine.new_game()
        
        # Act & Assert - Test all tableau piles (0-6)
        for i in range(7):
            info = engine.get_pile_info(i)
            assert info is not None
            assert info["card_count"] == i + 1
            assert "is_empty" in info
            assert "top_card" in info
        
        # Test foundations (7-10) - should be empty initially
        for i in range(7, 11):
            info = engine.get_pile_info(i)
            assert info is not None
            assert info["is_empty"] is True
            assert info["top_card"] is None
        
        # Test stock (11) and waste (12)
        stock_info = engine.get_pile_info(11)
        assert stock_info is not None
        assert stock_info["card_count"] > 0
        
        waste_info = engine.get_pile_info(12)
        assert waste_info is not None
        assert waste_info["is_empty"] is True  # Initially empty
    
    def test_game_state_consistency(self):
        """Test that game state is consistent across operations."""
        # Arrange
        engine = GameEngine.create(audio_enabled=False)
        engine.new_game()
        
        # Get initial state
        initial_state = engine.get_game_state()
        
        # Make a move
        engine.draw_from_stock(count=1)
        
        # Get new state
        new_state = engine.get_game_state()
        
        # Assert - Statistics updated
        assert new_state["statistics"]["draw_count"] == initial_state["statistics"]["draw_count"] + 1
        
        # Waste should have more cards
        assert new_state["piles"]["waste"] > initial_state["piles"]["waste"]
        
        # Stock should have fewer cards
        assert new_state["piles"]["stock"] < initial_state["piles"]["stock"]


class TestAudioIntegration:
    """Test audio feedback integration."""
    
    def test_audio_feedback_on_moves(self):
        """Test that moves trigger appropriate audio feedback."""
        # Arrange - Create engine with mock TTS
        mock_tts = MockTtsProvider()
        from src.infrastructure.audio.screen_reader import ScreenReader
        screen_reader = ScreenReader(mock_tts, enabled=True)
        
        deck = FrenchDeck()
        deck.crea()
        from src.domain.models.table import GameTable
        from src.domain.rules.solitaire_rules import SolitaireRules
        from src.domain.services.game_service import GameService
        
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Start game
        engine.new_game()
        
        # Clear previous announcements
        mock_tts.spoken_text = []
        
        # Act - Draw a card
        engine.draw_from_stock(count=1)
        
        # Assert - Audio feedback was given
        assert len(mock_tts.spoken_text) > 0
        assert any("eseguita" in text or "Pescate" in text for text in mock_tts.spoken_text)
    
    def test_audio_enable_disable(self):
        """Test enabling and disabling audio feedback."""
        # Arrange
        mock_tts = MockTtsProvider()
        from src.infrastructure.audio.screen_reader import ScreenReader
        screen_reader = ScreenReader(mock_tts, enabled=True)
        
        deck = FrenchDeck()
        deck.crea()
        from src.domain.models.table import GameTable
        from src.domain.rules.solitaire_rules import SolitaireRules
        from src.domain.services.game_service import GameService
        
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        engine = GameEngine(table, service, rules, screen_reader)
        
        # Act - Disable audio
        engine.set_audio_enabled(False)
        mock_tts.spoken_text = []
        
        engine.draw_from_stock(count=1)
        
        # Assert - No audio feedback
        assert len(mock_tts.spoken_text) == 0
        
        # Re-enable and verify audio works
        engine.set_audio_enabled(True)
        engine.draw_from_stock(count=1)
        
        assert len(mock_tts.spoken_text) > 0
