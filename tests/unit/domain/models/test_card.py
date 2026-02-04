"""Unit tests for Card model."""
import pytest

from src.domain.models.card import Card, Rank, Suit


class TestSuit:
    """Test suite for Suit enum."""

    def test_color_red_suits(self) -> None:
        """Test red suits return 'red' color."""
        assert Suit.HEARTS.color == "red"
        assert Suit.DIAMONDS.color == "red"

    def test_color_black_suits(self) -> None:
        """Test black suits return 'black' color."""
        assert Suit.CLUBS.color == "black"
        assert Suit.SPADES.color == "black"

    def test_symbol(self) -> None:
        """Test suit symbols are correct."""
        assert Suit.HEARTS.symbol == "♥"
        assert Suit.DIAMONDS.symbol == "♦"
        assert Suit.CLUBS.symbol == "♣"
        assert Suit.SPADES.symbol == "♠"


class TestRank:
    """Test suite for Rank enum."""

    def test_value_ace(self) -> None:
        """Test Ace has value 1."""
        assert Rank.ACE.numeric_value == 1

    def test_value_numeric(self) -> None:
        """Test numeric cards have correct values."""
        assert Rank.TWO.numeric_value == 2
        assert Rank.FIVE.numeric_value == 5
        assert Rank.TEN.numeric_value == 10

    def test_value_face_cards(self) -> None:
        """Test face cards have correct values."""
        assert Rank.JACK.numeric_value == 11
        assert Rank.QUEEN.numeric_value == 12
        assert Rank.KING.numeric_value == 13


class TestCard:
    """Test suite for Card model."""

    def test_initialization(self) -> None:
        """Test Card initializes correctly."""
        card = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        assert card.rank == Rank.ACE
        assert card.suit == Suit.HEARTS

    def test_color_property(self) -> None:
        """Test card color matches suit color."""
        red_card = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        black_card = Card(rank=Rank.ACE, suit=Suit.SPADES)

        assert red_card.color == "red"
        assert black_card.color == "black"

    def test_value_property(self) -> None:
        """Test card value matches rank value."""
        ace = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        king = Card(rank=Rank.KING, suit=Suit.SPADES)

        assert ace.value == 1
        assert king.value == 13

    def test_can_stack_on_foundation_ace_on_empty(self) -> None:
        """Test Ace can be placed on empty foundation."""
        ace = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        assert ace.can_stack_on_foundation(None)

    def test_can_stack_on_foundation_two_on_ace(self) -> None:
        """Test Two can be placed on Ace of same suit."""
        ace = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        two = Card(rank=Rank.TWO, suit=Suit.HEARTS)
        assert two.can_stack_on_foundation(ace)

    def test_can_stack_on_foundation_wrong_suit(self) -> None:
        """Test card cannot be placed on foundation with wrong suit."""
        ace_hearts = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        two_spades = Card(rank=Rank.TWO, suit=Suit.SPADES)
        assert not two_spades.can_stack_on_foundation(ace_hearts)

    def test_can_stack_on_tableau_king_on_empty(self) -> None:
        """Test King can be placed on empty tableau."""
        king = Card(rank=Rank.KING, suit=Suit.SPADES)
        assert king.can_stack_on_tableau(None)

    def test_can_stack_on_tableau_opposite_color(self) -> None:
        """Test card can be placed on opposite color."""
        red_seven = Card(rank=Rank.SEVEN, suit=Suit.HEARTS)
        black_six = Card(rank=Rank.SIX, suit=Suit.SPADES)
        assert black_six.can_stack_on_tableau(red_seven)

    def test_can_stack_on_tableau_same_color(self) -> None:
        """Test card cannot be placed on same color."""
        red_seven = Card(rank=Rank.SEVEN, suit=Suit.HEARTS)
        red_six = Card(rank=Rank.SIX, suit=Suit.DIAMONDS)
        assert not red_six.can_stack_on_tableau(red_seven)

    def test_str_representation(self) -> None:
        """Test string representation of card."""
        ace_hearts = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        king_spades = Card(rank=Rank.KING, suit=Suit.SPADES)

        assert str(ace_hearts) == "A♥"
        assert str(king_spades) == "K♠"

    def test_from_string_ace(self) -> None:
        """Test creating card from string - Ace."""
        card = Card.from_string("AH")
        assert card.rank == Rank.ACE
        assert card.suit == Suit.HEARTS

    def test_from_string_ten(self) -> None:
        """Test creating card from string - Ten."""
        card = Card.from_string("10D")
        assert card.rank == Rank.TEN
        assert card.suit == Suit.DIAMONDS

    def test_from_string_invalid(self) -> None:
        """Test from_string raises error for invalid input."""
        with pytest.raises(ValueError):
            Card.from_string("X")

        with pytest.raises(ValueError):
            Card.from_string("1Z")
