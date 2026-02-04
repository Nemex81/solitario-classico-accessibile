"""Game orchestration service."""

import random
from typing import List, Tuple

from src.domain.models.card import Card, Rank, Suit
from src.domain.models.game_state import GameConfiguration, GameState, GameStatus
from src.domain.models.pile import (
    Pile,
    create_foundation_pile,
    create_stock_pile,
    create_tableau_pile,
    create_waste_pile,
)
from src.domain.rules.move_validator import MoveValidator


class GameService:
    """
    Orchestrates game logic and state transitions.

    This service coordinates domain models and rules to implement
    game actions. It does not depend on infrastructure (UI, persistence).
    """

    def __init__(self, validator: MoveValidator):
        """Initialize with move validator."""
        self.validator = validator

    def new_game(self, config: GameConfiguration) -> GameState:
        """
        Start new game with initial state.

        Args:
            config: Game configuration (difficulty, deck type)

        Returns:
            Initial GameState with shuffled deck
        """
        # Create and shuffle deck
        deck = self._create_deck(config.deck_type)
        random.shuffle(deck)

        # Deal tableau (7 piles: 1, 2, 3, 4, 5, 6, 7 cards)
        tableaus = []
        deck_index = 0
        for i in range(7):
            pile_size = i + 1
            pile_cards = deck[deck_index : deck_index + pile_size]
            tableaus.append(tuple(str(c) for c in pile_cards))
            deck_index += pile_size

        # Remaining cards to stock
        stock = tuple(str(c) for c in deck[deck_index:])

        return GameState(
            foundations=((), (), (), ()),
            tableaus=tuple(tableaus),
            stock=stock,
            waste=(),
            status=GameStatus.IN_PROGRESS,
            config=config,
        )

    def move_to_foundation(
        self,
        state: GameState,
        source_pile_type: str,
        source_index: int,
        foundation_index: int,
    ) -> GameState:
        """
        Move card to foundation pile.

        Args:
            state: Current game state
            source_pile_type: "tableau" or "waste"
            source_index: Source pile index
            foundation_index: Target foundation (0-3)

        Returns:
            New game state after move

        Raises:
            ValueError: If move is invalid
        """
        # Get source card
        if source_pile_type == "tableau":
            if not state.tableaus[source_index]:
                raise ValueError("Source tableau is empty")
            card_str = state.tableaus[source_index][-1]
        elif source_pile_type == "waste":
            if not state.waste:
                raise ValueError("Waste is empty")
            card_str = state.waste[-1]
        else:
            raise ValueError(f"Invalid source: {source_pile_type}")

        card = Card.from_string(card_str)

        # Validate move
        if not self.validator.can_move_to_foundation(card, foundation_index, state):
            raise ValueError(f"Cannot move {card} to foundation {foundation_index}")

        # Update piles
        new_foundations = list(state.foundations)
        new_foundations[foundation_index] = state.foundations[foundation_index] + (card_str,)

        if source_pile_type == "tableau":
            new_tableaus = list(state.tableaus)
            new_tableaus[source_index] = state.tableaus[source_index][:-1]
            new_state = state.with_move(
                foundations=tuple(new_foundations),
                tableaus=tuple(new_tableaus),
                moves_count=state.moves_count + 1,
                score=state.score + 10,
            )
        else:  # waste
            new_state = state.with_move(
                foundations=tuple(new_foundations),
                waste=state.waste[:-1],
                moves_count=state.moves_count + 1,
                score=state.score + 10,
            )

        # Check victory
        if new_state.is_victory():
            new_state = new_state.with_move(status=GameStatus.WON)

        return new_state

    def draw_from_stock(self, state: GameState) -> GameState:
        """
        Draw cards from stock to waste.

        Args:
            state: Current game state

        Returns:
            New game state with cards drawn

        Raises:
            ValueError: If stock is empty
        """
        if not self.validator.can_draw_from_stock(state):
            raise ValueError("Stock is empty")

        draw_count = state.config.draw_count
        cards_to_draw = min(draw_count, len(state.stock))

        drawn_cards = state.stock[-cards_to_draw:]
        new_stock = state.stock[:-cards_to_draw]
        new_waste = state.waste + drawn_cards

        return state.with_move(stock=new_stock, waste=new_waste, moves_count=state.moves_count + 1)

    def recycle_waste(self, state: GameState) -> GameState:
        """
        Recycle waste back to stock.

        Args:
            state: Current game state

        Returns:
            New game state with waste recycled

        Raises:
            ValueError: If cannot recycle
        """
        if not self.validator.can_recycle_waste(state):
            raise ValueError("Cannot recycle: stock not empty or waste is empty")

        return state.with_move(
            stock=state.waste[::-1],  # Reverse order
            waste=(),
            moves_count=state.moves_count + 1,
        )

    def _create_deck(self, deck_type: str) -> List[Card]:
        """Create deck based on type."""
        deck = []

        if deck_type == "french":
            suits = [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES]
        elif deck_type == "neapolitan":
            suits = [Suit.COPPE, Suit.DENARI, Suit.SPADE_IT, Suit.BASTONI]
        else:
            # Default to french
            suits = [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES]

        ranks = [
            Rank.ACE,
            Rank.TWO,
            Rank.THREE,
            Rank.FOUR,
            Rank.FIVE,
            Rank.SIX,
            Rank.SEVEN,
            Rank.EIGHT,
            Rank.NINE,
            Rank.TEN,
            Rank.JACK,
            Rank.QUEEN,
            Rank.KING,
        ]

        for suit in suits:
            for rank in ranks:
                deck.append(Card(rank, suit))

        return deck
