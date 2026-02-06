"""
Test suite per verificare il fix del bug critico in distribuisci_carte().

Bug: Il metodo distribuisci_carte() aveva un valore hardcoded di 24 carte per il mazzo
riserve, causando un IndexError quando si usava il mazzo napoletano (40 carte totali).

Fix: Calcolo dinamico delle carte rimanenti basato su self.mazzo.get_total_cards()
"""

import pytest
from scr.game_table import TavoloSolitario
from scr.decks import FrenchDeck, NeapolitanDeck


class TestDistribuisciCarteDynamicCalculation:
    """Test per verificare il calcolo dinamico delle carte nel mazzo riserve."""

    def test_distribuisci_carte_french_deck(self):
        """Test: Mazzo francese (52 carte) - 28 pile base + 24 riserve."""
        # Setup
        deck = FrenchDeck()
        tavolo = TavoloSolitario(deck)
        tavolo.crea_pile_gioco()
        
        # Esegui distribuzione
        tavolo.distribuisci_carte()
        
        # Verifica: 28 carte nelle pile base (1+2+3+4+5+6+7)
        carte_pile_base = sum(len(tavolo.pile[i].carte) for i in range(7))
        assert carte_pile_base == 28, f"Pile base dovrebbero avere 28 carte, trovate {carte_pile_base}"
        
        # Verifica: 24 carte nel mazzo riserve (pile[12])
        carte_riserve = len(tavolo.pile[12].carte)
        assert carte_riserve == 24, f"Mazzo riserve dovrebbe avere 24 carte, trovate {carte_riserve}"
        
        # Verifica totale: 28 + 24 = 52
        totale_carte = carte_pile_base + carte_riserve
        assert totale_carte == 52, f"Totale carte dovrebbe essere 52, trovate {totale_carte}"

    def test_distribuisci_carte_neapolitan_deck(self):
        """Test: Mazzo napoletano (40 carte) - 28 pile base + 12 riserve."""
        # Setup
        deck = NeapolitanDeck()
        tavolo = TavoloSolitario(deck)
        tavolo.crea_pile_gioco()
        
        # Esegui distribuzione (non dovrebbe crashare!)
        tavolo.distribuisci_carte()
        
        # Verifica: 28 carte nelle pile base
        carte_pile_base = sum(len(tavolo.pile[i].carte) for i in range(7))
        assert carte_pile_base == 28, f"Pile base dovrebbero avere 28 carte, trovate {carte_pile_base}"
        
        # Verifica: 12 carte nel mazzo riserve (pile[12])
        carte_riserve = len(tavolo.pile[12].carte)
        assert carte_riserve == 12, f"Mazzo riserve dovrebbe avere 12 carte, trovate {carte_riserve}"
        
        # Verifica totale: 28 + 12 = 40
        totale_carte = carte_pile_base + carte_riserve
        assert totale_carte == 40, f"Totale carte dovrebbe essere 40, trovate {totale_carte}"

    def test_cambio_mazzo_french_to_neapolitan(self):
        """Test: Cambia da mazzo francese a napoletano senza crash."""
        # Setup: inizia con mazzo francese
        deck_french = FrenchDeck()
        tavolo = TavoloSolitario(deck_french)
        tavolo.crea_pile_gioco()
        tavolo.distribuisci_carte()
        
        # Verifica iniziale: 24 carte riserve
        assert len(tavolo.pile[12].carte) == 24, "Mazzo francese dovrebbe avere 24 carte riserve"
        
        # Cambio mazzo a napoletano (simula F1)
        deck_neapolitan = NeapolitanDeck()
        tavolo.mazzo = deck_neapolitan
        tavolo.reset_pile()
        
        # Verifica: 12 carte riserve dopo il cambio, nessun crash
        assert len(tavolo.pile[12].carte) == 12, "Mazzo napoletano dovrebbe avere 12 carte riserve"
        
        # Verifica totale corretto
        carte_pile_base = sum(len(tavolo.pile[i].carte) for i in range(7))
        totale_carte = carte_pile_base + len(tavolo.pile[12].carte)
        assert totale_carte == 40, f"Totale carte napoletano dovrebbe essere 40, trovate {totale_carte}"

    def test_cambio_mazzo_neapolitan_to_french(self):
        """Test: Cambia da mazzo napoletano a francese senza crash."""
        # Setup: inizia con mazzo napoletano
        deck_neapolitan = NeapolitanDeck()
        tavolo = TavoloSolitario(deck_neapolitan)
        tavolo.crea_pile_gioco()
        tavolo.distribuisci_carte()
        
        # Verifica iniziale: 12 carte riserve
        assert len(tavolo.pile[12].carte) == 12, "Mazzo napoletano dovrebbe avere 12 carte riserve"
        
        # Cambio mazzo a francese (simula F1)
        deck_french = FrenchDeck()
        tavolo.mazzo = deck_french
        tavolo.reset_pile()
        
        # Verifica: 24 carte riserve dopo il cambio, nessun crash
        assert len(tavolo.pile[12].carte) == 24, "Mazzo francese dovrebbe avere 24 carte riserve"
        
        # Verifica totale corretto
        carte_pile_base = sum(len(tavolo.pile[i].carte) for i in range(7))
        totale_carte = carte_pile_base + len(tavolo.pile[12].carte)
        assert totale_carte == 52, f"Totale carte francese dovrebbe essere 52, trovate {totale_carte}"

    def test_cambio_mazzo_multiplo(self):
        """Test: Alterna F1 più volte senza crash."""
        # Setup iniziale con mazzo francese
        deck_french = FrenchDeck()
        tavolo = TavoloSolitario(deck_french)
        tavolo.crea_pile_gioco()
        tavolo.distribuisci_carte()
        
        # Test 3 cambi consecutivi
        for i in range(3):
            # Cambio a napoletano
            deck_neapolitan = NeapolitanDeck()
            tavolo.mazzo = deck_neapolitan
            tavolo.reset_pile()
            assert len(tavolo.pile[12].carte) == 12, f"Iterazione {i}: napoletano dovrebbe avere 12 carte"
            
            # Cambio a francese
            deck_french = FrenchDeck()
            tavolo.mazzo = deck_french
            tavolo.reset_pile()
            assert len(tavolo.pile[12].carte) == 24, f"Iterazione {i}: francese dovrebbe avere 24 carte"

    def test_no_index_error_on_neapolitan_deck(self):
        """Test regressione: verifica che non ci sia più IndexError con mazzo napoletano."""
        # Setup
        deck = NeapolitanDeck()
        tavolo = TavoloSolitario(deck)
        tavolo.crea_pile_gioco()
        
        # Questo doveva crashare con IndexError prima del fix
        try:
            tavolo.distribuisci_carte()
            success = True
        except IndexError as e:
            success = False
            pytest.fail(f"IndexError ancora presente: {e}")
        
        assert success, "distribuisci_carte() non dovrebbe più generare IndexError"
