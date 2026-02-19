"""
Test suite per verificare il fix del bug critico: Re napoletano non può essere spostato in pila vuota.

Bug: Il metodo put_to_base() aveva un check hardcoded per valore 13 (Re francese),
bloccando il Re napoletano (valore 10) quando si tentava di spostarlo in una pila vuota.

Fix: Aggiunto metodo is_king() in ProtoDeck che verifica semanticamente se una carta è un Re,
e modificato put_to_base() per usare self.mazzo.is_king(card) invece del check su valore 13.
"""

import pytest
from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck, NeapolitanDeck
from src.domain.models.card import Card


class TestIsKingMethod:
    """Test per il metodo is_king() aggiunto alla classe ProtoDeck."""

    def test_is_king_french_deck_with_king(self):
        """Test: is_king() riconosce il Re francese (valore 13)."""
        deck = FrenchDeck()
        # Crea un Re francese
        king_card = Card("Re", "cuori", coperta=False)
        king_card.set_int_value(13)
        
        assert deck.is_king(king_card) is True, "is_king() dovrebbe restituire True per Re francese"

    def test_is_king_french_deck_with_queen(self):
        """Test: is_king() NON riconosce la Regina francese (valore 12)."""
        deck = FrenchDeck()
        # Crea una Regina francese
        queen_card = Card("Regina", "cuori", coperta=False)
        queen_card.set_int_value(12)
        
        assert deck.is_king(queen_card) is False, "is_king() dovrebbe restituire False per Regina francese"

    def test_is_king_french_deck_with_jack(self):
        """Test: is_king() NON riconosce il Jack francese (valore 11)."""
        deck = FrenchDeck()
        # Crea un Jack francese
        jack_card = Card("Jack", "cuori", coperta=False)
        jack_card.set_int_value(11)
        
        assert deck.is_king(jack_card) is False, "is_king() dovrebbe restituire False per Jack francese"

    def test_is_king_neapolitan_deck_with_king(self):
        """Test: is_king() riconosce il Re napoletano (valore 10)."""
        deck = NeapolitanDeck()
        # Crea un Re napoletano
        king_card = Card("Re", "coppe", coperta=False)
        king_card.set_int_value(10)
        
        assert deck.is_king(king_card) is True, "is_king() dovrebbe restituire True per Re napoletano"

    def test_is_king_neapolitan_deck_with_cavallo(self):
        """Test: is_king() NON riconosce il Cavallo napoletano (valore 9)."""
        deck = NeapolitanDeck()
        # Crea un Cavallo napoletano
        cavallo_card = Card("Cavallo", "coppe", coperta=False)
        cavallo_card.set_int_value(9)
        
        assert deck.is_king(cavallo_card) is False, "is_king() dovrebbe restituire False per Cavallo napoletano"

    def test_is_king_neapolitan_deck_with_regina(self):
        """Test: is_king() NON riconosce la Regina napoletana (valore 8)."""
        deck = NeapolitanDeck()
        # Crea una Regina napoletana
        regina_card = Card("Regina", "coppe", coperta=False)
        regina_card.set_int_value(8)
        
        assert deck.is_king(regina_card) is False, "is_king() dovrebbe restituire False per Regina napoletana"


class TestKingToEmptyBasePile:
    """Test per verificare che i Re possano essere spostati in pile vuote."""

    def test_french_king_to_empty_base_pile(self):
        """Test: Re francese (valore 13) può essere spostato in pila base vuota."""
        # Setup
        deck = FrenchDeck()
        tavolo = TavoloSolitario(deck)
        tavolo.crea_pile_gioco()
        
        # Crea un Re francese
        king_card = Card("Re", "cuori", coperta=False)
        king_card.set_int_value(13)
        king_card.set_color("rosso")
        
        # Pile base sono le colonne 0-6
        base_pile = tavolo.pile[0]
        base_pile.carte = []  # Svuota la pila
        
        # Verifica che la pila sia vuota
        assert base_pile.is_empty_pile(), "La pila base dovrebbe essere vuota"
        
        # Tenta di spostare il Re nella pila vuota
        result = tavolo.put_to_base(None, base_pile, [king_card])
        
        assert result is True, "Re francese dovrebbe poter essere spostato in pila base vuota"

    def test_neapolitan_king_to_empty_base_pile(self):
        """Test CRITICO: Re napoletano (valore 10) può essere spostato in pila base vuota."""
        # Setup
        deck = NeapolitanDeck()
        tavolo = TavoloSolitario(deck)
        tavolo.crea_pile_gioco()
        
        # Crea un Re napoletano
        king_card = Card("Re", "coppe", coperta=False)
        king_card.set_int_value(10)
        king_card.set_color("rosso")
        
        # Pile base sono le colonne 0-6
        base_pile = tavolo.pile[0]
        base_pile.carte = []  # Svuota la pila
        
        # Verifica che la pila sia vuota
        assert base_pile.is_empty_pile(), "La pila base dovrebbe essere vuota"
        
        # Tenta di spostare il Re nella pila vuota (questo era bloccato prima del fix!)
        result = tavolo.put_to_base(None, base_pile, [king_card])
        
        assert result is True, "Re napoletano dovrebbe poter essere spostato in pila base vuota"

    def test_french_queen_blocked_on_empty_base_pile(self):
        """Test: Regina francese (valore 12) NON può essere spostata in pila base vuota."""
        # Setup
        deck = FrenchDeck()
        tavolo = TavoloSolitario(deck)
        tavolo.crea_pile_gioco()
        
        # Crea una Regina francese
        queen_card = Card("Regina", "cuori", coperta=False)
        queen_card.set_int_value(12)
        queen_card.set_color("rosso")
        
        # Pile base sono le colonne 0-6
        base_pile = tavolo.pile[0]
        base_pile.carte = []  # Svuota la pila
        
        # Verifica che la pila sia vuota
        assert base_pile.is_empty_pile(), "La pila base dovrebbe essere vuota"
        
        # Tenta di spostare la Regina nella pila vuota (dovrebbe essere bloccato)
        result = tavolo.put_to_base(None, base_pile, [queen_card])
        
        assert result is False, "Regina francese NON dovrebbe poter essere spostata in pila base vuota"

    def test_neapolitan_cavallo_blocked_on_empty_base_pile(self):
        """Test: Cavallo napoletano (valore 9) NON può essere spostato in pila base vuota."""
        # Setup
        deck = NeapolitanDeck()
        tavolo = TavoloSolitario(deck)
        tavolo.crea_pile_gioco()
        
        # Crea un Cavallo napoletano
        cavallo_card = Card("Cavallo", "coppe", coperta=False)
        cavallo_card.set_int_value(9)
        cavallo_card.set_color("rosso")
        
        # Pile base sono le colonne 0-6
        base_pile = tavolo.pile[0]
        base_pile.carte = []  # Svuota la pila
        
        # Verifica che la pila sia vuota
        assert base_pile.is_empty_pile(), "La pila base dovrebbe essere vuota"
        
        # Tenta di spostare il Cavallo nella pila vuota (dovrebbe essere bloccato)
        result = tavolo.put_to_base(None, base_pile, [cavallo_card])
        
        assert result is False, "Cavallo napoletano NON dovrebbe poter essere spostato in pila base vuota"

    def test_neapolitan_regina_blocked_on_empty_base_pile(self):
        """Test: Regina napoletana (valore 8) NON può essere spostata in pila base vuota."""
        # Setup
        deck = NeapolitanDeck()
        tavolo = TavoloSolitario(deck)
        tavolo.crea_pile_gioco()
        
        # Crea una Regina napoletana
        regina_card = Card("Regina", "coppe", coperta=False)
        regina_card.set_int_value(8)
        regina_card.set_color("rosso")
        
        # Pile base sono le colonne 0-6
        base_pile = tavolo.pile[0]
        base_pile.carte = []  # Svuota la pila
        
        # Verifica che la pila sia vuota
        assert base_pile.is_empty_pile(), "La pila base dovrebbe essere vuota"
        
        # Tenta di spostare la Regina nella pila vuota (dovrebbe essere bloccato)
        result = tavolo.put_to_base(None, base_pile, [regina_card])
        
        assert result is False, "Regina napoletana NON dovrebbe poter essere spostata in pila base vuota"


class TestRegressionNonEmptyPile:
    """Test di regressione per verificare che le mosse su pile non vuote funzionino ancora."""

    def test_normal_move_french_deck(self):
        """Test: Mosse normali su pile non vuote continuano a funzionare con mazzo francese."""
        # Setup
        deck = FrenchDeck()
        tavolo = TavoloSolitario(deck)
        tavolo.crea_pile_gioco()
        
        # Pile base 0
        base_pile = tavolo.pile[0]
        base_pile.carte = []
        
        # Aggiungi un Re nero nella pila
        king_card = Card("Re", "picche", coperta=False)
        king_card.set_int_value(13)
        king_card.set_color("nero")
        base_pile.carte.append(king_card)
        
        # Tenta di spostare una Regina rossa (valore 12) sul Re nero
        queen_card = Card("Regina", "cuori", coperta=False)
        queen_card.set_int_value(12)
        queen_card.set_color("rosso")
        
        result = tavolo.put_to_base(None, base_pile, [queen_card])
        assert result is True, "Regina rossa (12) dovrebbe poter essere messa su Re nero (13)"

    def test_normal_move_neapolitan_deck(self):
        """Test: Mosse normali su pile non vuote continuano a funzionare con mazzo napoletano."""
        # Setup
        deck = NeapolitanDeck()
        tavolo = TavoloSolitario(deck)
        tavolo.crea_pile_gioco()
        
        # Pile base 0
        base_pile = tavolo.pile[0]
        base_pile.carte = []
        
        # Aggiungi un Re nero nella pila
        king_card = Card("Re", "bastoni", coperta=False)
        king_card.set_int_value(10)
        king_card.set_color("nero")
        base_pile.carte.append(king_card)
        
        # Tenta di spostare un Cavallo rosso (valore 9) sul Re nero
        cavallo_card = Card("Cavallo", "coppe", coperta=False)
        cavallo_card.set_int_value(9)
        cavallo_card.set_color("rosso")
        
        result = tavolo.put_to_base(None, base_pile, [cavallo_card])
        assert result is True, "Cavallo rosso (9) dovrebbe poter essere messo su Re nero (10)"

    def test_same_color_blocked(self):
        """Test: Mosse con stesso colore continuano ad essere bloccate."""
        # Setup
        deck = FrenchDeck()
        tavolo = TavoloSolitario(deck)
        tavolo.crea_pile_gioco()
        
        # Pile base 0
        base_pile = tavolo.pile[0]
        base_pile.carte = []
        
        # Aggiungi un Re rosso nella pila
        king_card = Card("Re", "cuori", coperta=False)
        king_card.set_int_value(13)
        king_card.set_color("rosso")
        base_pile.carte.append(king_card)
        
        # Tenta di spostare una Regina rossa (stesso colore!) sul Re rosso
        queen_card = Card("Regina", "quadri", coperta=False)
        queen_card.set_int_value(12)
        queen_card.set_color("rosso")
        
        result = tavolo.put_to_base(None, base_pile, [queen_card])
        assert result is False, "Regina rossa NON dovrebbe poter essere messa su Re rosso (stesso colore)"

    def test_wrong_value_blocked(self):
        """Test: Mosse con valore scorretto continuano ad essere bloccate."""
        # Setup
        deck = FrenchDeck()
        tavolo = TavoloSolitario(deck)
        tavolo.crea_pile_gioco()
        
        # Pile base 0
        base_pile = tavolo.pile[0]
        base_pile.carte = []
        
        # Aggiungi un Re nero nella pila
        king_card = Card("Re", "picche", coperta=False)
        king_card.set_int_value(13)
        king_card.set_color("nero")
        base_pile.carte.append(king_card)
        
        # Tenta di spostare un Jack rosso (valore 11, non 12!) sul Re nero
        jack_card = Card("Jack", "cuori", coperta=False)
        jack_card.set_int_value(11)
        jack_card.set_color("rosso")
        
        result = tavolo.put_to_base(None, base_pile, [jack_card])
        assert result is False, "Jack (11) NON dovrebbe poter essere messo su Re (13) - valore scorretto"
