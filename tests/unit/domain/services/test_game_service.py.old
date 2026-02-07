"""Unit tests for GameService."""

import pytest

from src.domain.models.game_state import GameConfiguration, GameState, GameStatus
from src.domain.rules.move_validator import MoveValidator
from src.domain.services.game_service import GameService


class TestGameService:
    """Test suite for GameService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.validator = MoveValidator()
        self.service = GameService(self.validator)

    def test_new_game_creates_valid_state(self) -> None:
        """Test new game initialization."""
        config = GameConfiguration(difficulty="easy", deck_type="french")
        state = self.service.new_game(config)

        assert state.status == GameStatus.IN_PROGRESS
        assert len(state.tableaus) == 7
        assert len(state.stock) > 0
        assert len(state.foundations) == 4
        assert all(len(f) == 0 for f in state.foundations)

    def test_new_game_deals_correct_tableau_sizes(self) -> None:
        """Test tableau piles have correct sizes."""
        config = GameConfiguration(difficulty="easy", deck_type="french")
        state = self.service.new_game(config)

        # First tableau has 1 card, second has 2, etc.
        for i in range(7):
            assert len(state.tableaus[i]) == i + 1

    def test_new_game_uses_all_cards(self) -> None:
        """Test all 52 cards are distributed."""
        config = GameConfiguration(difficulty="easy", deck_type="french")
        state = self.service.new_game(config)

        total_cards = sum(len(t) for t in state.tableaus) + len(state.stock)
        assert total_cards == 52

    def test_move_to_foundation_valid(self) -> None:
        """Test valid move to foundation."""
        state = GameState(tableaus=(("AH",), (), (), (), (), (), ()), foundations=((), (), (), ()))

        new_state = self.service.move_to_foundation(state, "tableau", 0, 0)

        assert len(new_state.foundations[0]) == 1
        assert new_state.foundations[0][0] == "AH"
        assert len(new_state.tableaus[0]) == 0
        assert new_state.score == 10

    def test_move_to_foundation_invalid_raises(self) -> None:
        """Test invalid move raises ValueError."""
        state = GameState(tableaus=(("2H",), (), (), (), (), (), ()), foundations=((), (), (), ()))

        with pytest.raises(ValueError, match="Cannot move"):
            self.service.move_to_foundation(state, "tableau", 0, 0)

    def test_move_to_foundation_from_waste(self) -> None:
        """Test moving card from waste to foundation."""
        state = GameState(waste=("AH",), foundations=((), (), (), ()))

        new_state = self.service.move_to_foundation(state, "waste", 0, 0)

        assert len(new_state.foundations[0]) == 1
        assert len(new_state.waste) == 0
        assert new_state.score == 10

    def test_move_to_foundation_empty_source_raises(self) -> None:
        """Test moving from empty source raises error."""
        state = GameState(tableaus=((), (), (), (), (), (), ()), foundations=((), (), (), ()))

        with pytest.raises(ValueError, match="empty"):
            self.service.move_to_foundation(state, "tableau", 0, 0)

    def test_move_to_foundation_victory_detection(self) -> None:
        """Test victory is detected when all foundations complete."""
        # Create state with 51 cards in foundations
        complete_suit = tuple(
            f"{rank}{suit}"
            for rank in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
            for suit in ["H"]
        )

        state = GameState(
            foundations=(
                complete_suit[:13],
                complete_suit[:13],
                complete_suit[:13],
                ("AH", "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "10H", "JH", "QH"),
            ),
            tableaus=(("KH",), (), (), (), (), (), ()),
        )

        new_state = self.service.move_to_foundation(state, "tableau", 0, 3)
        assert new_state.status == GameStatus.WON

    def test_draw_from_stock(self) -> None:
        """Test drawing cards from stock."""
        state = GameState(
            stock=("AH", "2D", "3C", "4S"), waste=(), config=GameConfiguration(draw_count=3)
        )

        new_state = self.service.draw_from_stock(state)

        assert len(new_state.waste) == 3
        assert len(new_state.stock) == 1
        assert new_state.moves_count == 1

    def test_draw_from_stock_less_than_draw_count(self) -> None:
        """Test drawing when stock has fewer cards than draw_count."""
        state = GameState(stock=("AH", "2D"), waste=(), config=GameConfiguration(draw_count=3))

        new_state = self.service.draw_from_stock(state)

        assert len(new_state.waste) == 2
        assert len(new_state.stock) == 0

    def test_draw_from_empty_stock_raises(self) -> None:
        """Test drawing from empty stock raises error."""
        state = GameState(stock=(), waste=())

        with pytest.raises(ValueError, match="Stock is empty"):
            self.service.draw_from_stock(state)

    def test_recycle_waste(self) -> None:
        """Test recycling waste to stock."""
        state = GameState(stock=(), waste=("AH", "2D", "3C"))

        new_state = self.service.recycle_waste(state)

        assert len(new_state.stock) == 3
        assert len(new_state.waste) == 0
        assert new_state.stock == ("3C", "2D", "AH")  # Reversed
        assert new_state.moves_count == 1

    def test_recycle_waste_with_non_empty_stock_raises(self) -> None:
        """Test recycling when stock is not empty raises error."""
        state = GameState(stock=("KH",), waste=("AH", "2D"))

        with pytest.raises(ValueError, match="Cannot recycle"):
            self.service.recycle_waste(state)

    def test_create_deck_french(self) -> None:
        """Test French deck creation."""
        config = GameConfiguration(deck_type="french")
        state = self.service.new_game(config)

        # Should have 52 cards
        total_cards = sum(len(t) for t in state.tableaus) + len(state.stock)
        assert total_cards == 52

    def test_create_deck_neapolitan(self) -> None:
        """Test Neapolitan deck creation."""
        config = GameConfiguration(deck_type="neapolitan")
        state = self.service.new_game(config)

        # Should have 52 cards (13 ranks x 4 Italian suits)
        total_cards = sum(len(t) for t in state.tableaus) + len(state.stock)
        assert total_cards == 52
