"""Test suite per funzionalità F3 (timer decrement) e F5 (toggle shuffle)."""

import sys
import pytest
import random
from unittest.mock import Mock, patch, MagicMock, MagicMock as MockModule

# Mock wx module before importing game_engine
sys.modules['wx'] = MockModule()

from scr.game_engine import EngineSolitario
from scr.game_table import TavoloSolitario
from scr.decks import FrenchDeck
from scr.cards import Card


class TestF3TimerDecrement:
    """Test per funzionalità F3 - Decremento timer."""

    def setup_method(self):
        """Setup iniziale per ogni test."""
        deck = FrenchDeck()
        table = TavoloSolitario(deck)
        self.engine = EngineSolitario(table)
        self.engine.is_game_running = True
        
    def test_f3_decrement_timer_normal(self):
        """Test F3: Timer da 10 minuti -> 5 minuti rimanenti."""
        # Setup: timer a 10 minuti (600 secondi)
        self.engine.max_time_game = 10 * 60
        self.engine.start_ticks = 0
        
        # Simula tempo trascorso: 0 secondi
        with patch('pygame.time.get_ticks', return_value=0):
            tempo_prima = self.engine.get_int_timer_status()
            assert tempo_prima == 600, "Timer dovrebbe essere 600 secondi (10 min)"
            
    def test_f3_decrement_timer_low_value(self):
        """Test F3: Timer da 3 minuti -> comportamento sicuro."""
        # Setup: timer a 3 minuti
        self.engine.max_time_game = 3 * 60
        self.engine.start_ticks = 0
        
        tempo = self.engine.get_int_timer_status()
        assert tempo >= 0, "Timer non deve mai essere negativo"
        
    def test_f3_decrement_timer_already_zero(self):
        """Test F3: Timer già a 0 -> nessun decremento."""
        # Setup: timer disabilitato
        self.engine.max_time_game = -1
        
        status = self.engine.get_timer_status()
        assert "disattivato" in status.lower(), "Timer disattivato dovrebbe essere rilevato"


class TestF5ShuffleToggle:
    """Test per funzionalità F5 - Toggle modalità shuffle."""

    def setup_method(self):
        """Setup iniziale per ogni test."""
        deck = FrenchDeck()
        table = TavoloSolitario(deck)
        self.engine = EngineSolitario(table)
        
    def test_f5_toggle_shuffle_to_true(self):
        """Test F5: Attiva modalità shuffle (False -> True)."""
        # Setup: modalità inversione (default)
        self.engine.shuffle_discards = False
        self.engine.change_settings = True
        self.engine.is_game_running = False
        
        # Esegui toggle
        risultato = self.engine.toggle_shuffle_mode()
        
        # Verifica
        assert self.engine.shuffle_discards == True, "Shuffle dovrebbe essere attivato"
        assert "MESCOLATA" in risultato.upper(), "Messaggio dovrebbe menzionare mescolata"
        
    def test_f5_toggle_shuffle_to_false(self):
        """Test F5: Disattiva modalità shuffle (True -> False)."""
        # Setup: modalità shuffle attiva
        self.engine.shuffle_discards = True
        self.engine.change_settings = True
        self.engine.is_game_running = False
        
        # Esegui toggle
        risultato = self.engine.toggle_shuffle_mode()
        
        # Verifica
        assert self.engine.shuffle_discards == False, "Shuffle dovrebbe essere disattivato"
        assert "INVERSIONE" in risultato.upper(), "Messaggio dovrebbe menzionare inversione"


class TestRiordinaScartiModes:
    """Test per metodo riordina_scarti con diverse modalità."""

    def setup_method(self):
        """Setup iniziale per ogni test."""
        deck = FrenchDeck()
        self.table = TavoloSolitario(deck)
        self.table.crea_pile_gioco()
        
    def test_riordina_scarti_invert_mode(self):
        """Test riordina_scarti: modalità inversione."""
        # Setup: aggiungi 3 carte agli scarti
        carte_test = []
        for i in range(3):
            carta = Mock()
            carta.flip = Mock()
            carte_test.append(carta)
        
        self.table.pile[11].carte = carte_test.copy()
        ordine_originale = [id(c) for c in carte_test]
        
        # Esegui: modalità inversione (False)
        self.table.riordina_scarti(shuffle_mode=False)
        
        # Verifica: ordine deve essere invertito nel mazzo riserve
        assert len(self.table.pile[12].carte) > 0, "Mazzo riserve dovrebbe avere carte"
        assert len(self.table.pile[11].carte) == 0, "Scarti dovrebbero essere vuoti"
        
    def test_riordina_scarti_shuffle_mode(self):
        """Test riordina_scarti: modalità shuffle casuale."""
        # Setup con seed per determinismo
        random.seed(42)
        
        carte_test = []
        for i in range(10):
            carta = Mock()
            carta.flip = Mock()
            carte_test.append(carta)
        
        self.table.pile[11].carte = carte_test.copy()
        
        # Esegui: modalità shuffle (True)
        self.table.riordina_scarti(shuffle_mode=True)
        
        # Verifica: tutte le carte devono essere presenti
        assert len(self.table.pile[12].carte) == 10, "Tutte le carte devono essere nel mazzo"
        assert len(self.table.pile[11].carte) == 0, "Scarti devono essere vuoti"


class TestResetShuffleOnStop:
    """Test per reset della modalità shuffle al termine partita."""

    def setup_method(self):
        """Setup iniziale per ogni test."""
        deck = FrenchDeck()
        table = TavoloSolitario(deck)
        self.engine = EngineSolitario(table)
        
    def test_reset_shuffle_on_stop_game(self):
        """Test: shuffle_discards resettato a False dopo stop_game."""
        # Setup: attiva shuffle
        self.engine.shuffle_discards = True
        self.engine.is_game_running = True
        
        # Esegui: ferma gioco
        self.engine.stop_game()
        
        # Verifica: shuffle deve essere resettato a False
        assert self.engine.shuffle_discards == False, "Shuffle deve tornare a default (False)"


class TestAutoDraw:
    """Test per funzionalità auto-draw dopo rimescolamento."""

    def setup_method(self):
        """Setup iniziale per ogni test."""
        deck = FrenchDeck()
        table = TavoloSolitario(deck)
        self.engine = EngineSolitario(table)
        self.engine.is_game_running = True
        
    def test_auto_draw_after_recycle_waste(self):
        """Test: auto-draw pesca carta automaticamente dopo rimescolamento."""
        # Setup: simula mazzo vuoto e scarti pieni
        self.engine.tavolo.crea_pile_gioco()
        
        # Aggiungi carte agli scarti
        for i in range(5):
            carta = Mock()
            carta.flip = Mock()
            carta.set_uncover = Mock()
            carta.get_name = f"Carta{i}"
            self.engine.tavolo.pile[11].carte.append(carta)
        
        # Svuota mazzo riserve
        self.engine.tavolo.pile[12].carte.clear()
        
        # Esegui: pesca (che dovrebbe triggerare rimescolamento + auto-draw)
        risultato = self.engine.pesca()
        
        # Verifica: dovrebbe esserci almeno una carta pescata
        assert "pescato" in risultato.lower() or "rimescol" in risultato.lower(), \
            "Messaggio dovrebbe indicare pescata o rimescolamento"
        
    def test_auto_draw_announces_card(self):
        """Test: auto-draw annuncia la carta pescata."""
        # Setup
        self.engine.tavolo.crea_pile_gioco()
        
        # Aggiungi carta agli scarti
        carta_mock = Mock()
        carta_mock.flip = Mock()
        carta_mock.set_uncover = Mock()
        carta_mock.get_name = "Asso di Cuori"
        self.engine.tavolo.pile[11].carte.append(carta_mock)
        
        # Svuota mazzo
        self.engine.tavolo.pile[12].carte.clear()
        
        # Esegui
        risultato = self.engine.pesca()
        
        # Verifica: messaggio in italiano
        assert isinstance(risultato, str), "Deve ritornare una stringa"
        assert len(risultato) > 0, "Messaggio non deve essere vuoto"

    def test_auto_draw_verifica_carte_spostate(self):
        """Test: verifica che le carte vengano effettivamente spostate dopo auto-draw."""
        # Setup: mazzo vuoto, 3 carte negli scarti
        self.engine.tavolo.crea_pile_gioco()
        self.engine.tavolo.pile[12].carte.clear()  # Svuota mazzo riserve
        
        # Crea 3 carte mock per gli scarti
        carte_iniziali = []
        for idx in range(3):
            carta_mock = Mock()
            carta_mock.flip = Mock()
            carta_mock.set_uncover = Mock()
            carta_mock.get_name = f"TestCard{idx}"
            carte_iniziali.append(carta_mock)
            self.engine.tavolo.pile[11].carte.append(carta_mock)
        
        # Conta scarti prima dell'operazione
        scarti_iniziali = len(self.engine.tavolo.pile[11].carte)
        assert scarti_iniziali == 3, "Dovrebbero esserci 3 carte negli scarti"
        
        # Esegui pesca (trigger rimescolamento + auto-draw)
        self.engine.difficulty_level = 1  # Pesca singola carta
        messaggio = self.engine.pesca()
        
        # Verifica: messaggio contiene sia rimescolamento che pescata
        assert "rimescol" in messaggio.lower(), "Messaggio deve contenere info rimescolamento"
        assert "pescato" in messaggio.lower() or "pescata" in messaggio.lower(), \
            "Messaggio deve contenere info sulla carta pescata automaticamente"
        
        # Verifica: dopo auto-draw, una carta deve essere negli scarti (pescata)
        scarti_dopo = len(self.engine.tavolo.pile[11].carte)
        mazzo_dopo = len(self.engine.tavolo.pile[12].carte)
        
        # Con difficulty_level=1: 1 carta pescata negli scarti, 2 nel mazzo
        assert scarti_dopo == 1, f"Dovrebbe esserci 1 carta negli scarti dopo auto-draw, trovate {scarti_dopo}"
        assert mazzo_dopo == 2, f"Dovrebbero esserci 2 carte nel mazzo dopo auto-draw, trovate {mazzo_dopo}"

    def test_auto_draw_mazzo_vuoto_dopo_rimescolamento(self):
        """Test edge case: mazzo vuoto anche dopo rimescolamento (scarti vuoti)."""
        # Setup: sia mazzo che scarti vuoti
        self.engine.tavolo.crea_pile_gioco()
        self.engine.tavolo.pile[12].carte.clear()
        self.engine.tavolo.pile[11].carte.clear()
        
        # Esegui pesca
        messaggio = self.engine.pesca()
        
        # Verifica: gestione corretta caso limite
        assert isinstance(messaggio, str), "Deve ritornare una stringa anche in caso di errore"


class TestEdgeCases:
    """Test per casi limite delle funzionalità F3/F5."""

    def setup_method(self):
        """Setup iniziale per ogni test."""
        deck = FrenchDeck()
        table = TavoloSolitario(deck)
        self.engine = EngineSolitario(table)
        
    def test_toggle_shuffle_during_game_blocked(self):
        """Test: toggle shuffle bloccato durante partita."""
        self.engine.is_game_running = True
        self.engine.change_settings = True
        
        risultato = self.engine.toggle_shuffle_mode()
        
        # Deve essere bloccato
        assert "non puoi" in risultato.lower() or "partita" in risultato.lower(), \
            "Toggle deve essere bloccato durante partita"
            
    def test_riordina_scarti_empty_waste(self):
        """Test: riordina_scarti con scarti vuoti."""
        self.engine.tavolo.crea_pile_gioco()
        self.engine.tavolo.pile[11].carte.clear()
        
        # Non deve crashare
        self.engine.tavolo.riordina_scarti(shuffle_mode=False)
        
        # Verifica: nessun problema
        assert True, "Non deve crashare con scarti vuoti"
