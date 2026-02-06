"""
	file game_play.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/game_play.py

	Modulo per la gestione dellinterfaccia utente durante la partita al solitario

"""

import logging, sys, os, time, random, pygame
from pygame.locals import *
from my_lib.dialog_box import DialogBox
from scr.decks import FrenchDeck, NeapolitanDeck
from scr.game_table import TavoloSolitario
from scr.game_engine import EngineSolitario

#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# inizializzo pygame
pygame.init()
pygame.font.init()

class GamePlay(DialogBox):
	"""	Classe per la gestione dellinterfaccia utente durante la partita al solitario """

	TIME_CHECK_EVENT = pygame.USEREVENT + 1	# ceck eventi pygame personalizzati

	def __init__(self, screen, screen_reader):
		super().__init__()
		#self.callback = callback_dict
		self.screen = screen # import config schermo
		self.screen_reader = screen_reader # import motore di vocalizzazione
		self.mazzo = FrenchDeck() # inizializzazione mazzo di gioco
		self.tavolo = TavoloSolitario(self.mazzo) # inizializzazione tavolo di gioco
		self.engine = EngineSolitario(self.tavolo) # inizializzazione motore di gioco per il solitario classico
		self.build_commands_list() # creazione lista dei comandi utente
		self.engine.crea_gioco() # avvio una nuova partita

	#@@# sezione metodi di supporto

	def vocalizza(self, string):
		self.screen_reader.vocalizza(string)
		pygame.time.wait(500)

	def quit_app(self):
		self.vocalizza("chiusura in corso.  ")
		pygame.time.wait(500)
		self.create_question_box("Sei sicuro di voler uscire?")
		result = self.answare
		if result:
			pygame.quit()
			sys.exit()

	#@@# sezione comandi utente

	def f1_press(self):
		# F1 = cambio mazzo (principale)
		# CTRL+F1 = test vittoria (secondario)
		if pygame.key.get_mods() & KMOD_CTRL:
			string = self.engine.test_vittoria()
		else:
			string = self.engine.change_deck_type()
		self.vocalizza(string)

	def f2_press(self):
		string = self.engine.change_difficulty_level()
		self.vocalizza(string)

	def f3_press(self):
		if pygame.key.get_mods() & KMOD_CTRL:
			string = self.engine.disable_timer()
		else:
			string = self.engine.change_game_time(increment=False)

		self.vocalizza(string)

	def f4_press(self):
		string = self.engine.change_game_time(increment=True)
		self.vocalizza(string)

	def f5_press(self):
		string = self.engine.toggle_shuffle_mode()
		self.vocalizza(string)

	def up_press(self):
		string = self.engine.move_cursor("up")
		if string:
			self.vocalizza(string)

	def down_press(self):
		string = self.engine.move_cursor("down")
		if string:
			self.vocalizza(string)

	def left_press(self):
		string = self.engine.move_cursor("left")
		if string:
			self.vocalizza(string)

	def right_press(self):
		string = self.engine.move_cursor("right")
		if string:
			self.vocalizza(string)

	def home_press(self):
		"""Handler per tasto HOME: vai a prima carta pila corrente"""
		string = self.engine.move_cursor_to_first()
		self.vocalizza(string)

	def end_press(self):
		"""Handler per tasto END: vai a ultima carta pila corrente"""
		string = self.engine.move_cursor_to_last()
		self.vocalizza(string)

	def enter_press(self):
		if pygame.key.get_mods() & KMOD_CTRL:
			string = self.engine.select_scarto()
		else:
			string = self.engine.select_card()

		if string:
			self.vocalizza(string)

	def space_press(self):
		string = self.engine.sposta_carte()
		if string:
			self.vocalizza(string)

	def tab_press(self):
		string = self.engine.move_cursor("tab")
		if string:
			self.vocalizza(string)

	def canc_press(self):
		string = self.engine.cancel_selected_cards()
		if string:
			self.vocalizza(string)

	def press_1(self):
		string = self.engine.move_cursor_to_pile_with_select(0)
		if string:
			self.vocalizza(string)

	def press_2(self):
		string = self.engine.move_cursor_to_pile_with_select(1)
		if string:
			self.vocalizza(string)

	def press_3(self):
		string = self.engine.move_cursor_to_pile_with_select(2)
		if string:
			self.vocalizza(string)

	def press_4(self):
		string = self.engine.move_cursor_to_pile_with_select(3)
		if string:
			self.vocalizza(string)

	def press_5(self):
		string = self.engine.move_cursor_to_pile_with_select(4)
		if string:
			self.vocalizza(string)

	def press_6(self):
		string = self.engine.move_cursor_to_pile_with_select(5)
		if string:
			self.vocalizza(string)

	def press_7(self):
		string = self.engine.move_cursor_to_pile_with_select(6)
		if string:
			self.vocalizza(string)

	def c_press(self):
		string = self.engine.get_selected_cards()
		self.vocalizza(string)

	def d_press(self):
		string = self.engine.pesca()
		if string:
			self.vocalizza(string)

	def f_press(self):
		string = self.engine.get_focus()
		if string:
			self.vocalizza(string)

	def g_press(self):
		string = self.engine.get_info_tavolo()
		if string:
			self.vocalizza(string)

	def i_press(self):
		string = self.engine.get_settings_info()
		if string:
			self.vocalizza(string)

	def m_press(self):
		string = self.engine.get_tot_dek()
		if string:
			self.vocalizza(string)

	def n_press(self):
		# avviamo una nuova partita richiedendo il livello di difficoltà.
		if self.engine.is_game_running:
			self.create_yes_or_no_box("Sei sicuro di voler avviare una nuova partita?", "Partita in corso rilevata")
			if not self.answare:
				return

		self.engine.nuova_partita()

	def o_press(self):
		string = self.engine.change_game_settings()
		if string:
			self.vocalizza(string)

	def p_press(self):
		string = self.engine.pesca()
		if string:
			self.vocalizza(string)

	def r_press(self):
		string = self.engine.get_info_game()
		if string:
			self.vocalizza(string)

	def s_press(self):
		string = self.engine.get_top_scarto()
		if string:
			self.vocalizza(string)

	def t_press(self):
		string = self.engine.get_timer_status()
		if string:
			self.vocalizza(string)

	def x_press(self):
		string = self.engine.get_info_carta()
		self.vocalizza(string)

	def h_press(self):
		"""Mostra aiuto comandi disponibili"""
		help_text = """COMANDI DI GIOCO:

NAVIGAZIONE:
- Frecce SU/GIÙ: muovi cursore nella pila
- Frecce SINISTRA/DESTRA: cambia pila
- TAB: salta a tipo di pila diverso
- Numeri 1-7: vai alla pila base + doppio tocco seleziona
- SHIFT+1-4: vai alla pila semi (Cuori/Quadri/Fiori/Picche) + doppio tocco seleziona
- SHIFT+S: sposta cursore su scarti
- SHIFT+M: sposta cursore su mazzo

AZIONI:
- INVIO: seleziona carta sotto cursore (su mazzo: pesca carte)
- CTRL+INVIO: seleziona carta dagli scarti
- SPAZIO: sposta le carte selezionate
- CANC: annulla selezione
- D o P: pesca dal mazzo (da qualunque posizione)

INFORMAZIONI:
- F: posizione cursore attuale
- G: stato tavolo completo
- R: report partita (tempo, mosse, rimischiate)
- T: tempo rimanente
- X: dettagli carta sotto cursore
- S: ultima carta negli scarti (read-only)
- M: numero carte nel mazzo (read-only)
- C: carte selezionate
- I: visualizza impostazioni correnti
- H: questo aiuto

IMPOSTAZIONI:
- N: nuova partita
- O: apri/chiudi opzioni
- F1: cambia tipo mazzo (francesi/napoletane)
- F2: cambia difficoltà (1-3)
- F3: decrementa tempo limite (-5 min)
- F4: incrementa tempo limite (+5 min)
- F5: alterna modalità riciclo scarti (inversione/mescolata)
- CTRL+F3: disabilita timer
- ESC: abbandona partita / esci dal gioco

DEBUG:
- CTRL+F1: simula vittoria (test)"""
		self.create_alert_box(help_text, "Aiuto Comandi")

	def esc_press(self):
		if self.engine.is_game_running:
			self.create_yes_or_no_box("Sei sicuro di voler abbandonare la partita?", "Abbandonare la partita??")
			result = self.answare
			if result:
				string = self.engine.chiudi_partita()
				self.vocalizza(string)

		else:
			self.quit_app()

	# NUOVI HANDLER: Pile Semi (SHIFT+1-4)

	def shift_1_press(self):
		"""SHIFT+1: Pila semi Cuori (indice 7)"""
		string = self.engine.move_cursor_to_pile_with_select(7)
		if string:
			self.vocalizza(string)

	def shift_2_press(self):
		"""SHIFT+2: Pila semi Quadri (indice 8)"""
		string = self.engine.move_cursor_to_pile_with_select(8)
		if string:
			self.vocalizza(string)

	def shift_3_press(self):
		"""SHIFT+3: Pila semi Fiori (indice 9)"""
		string = self.engine.move_cursor_to_pile_with_select(9)
		if string:
			self.vocalizza(string)

	def shift_4_press(self):
		"""SHIFT+4: Pila semi Picche (indice 10)"""
		string = self.engine.move_cursor_to_pile_with_select(10)
		if string:
			self.vocalizza(string)

	# NUOVI HANDLER: Scarti e Mazzo (SHIFT+S, SHIFT+M)

	def shift_s_press(self):
		"""SHIFT+S: Sposta cursore su pila scarti (11)"""
		string = self.engine.move_cursor_to_pile_with_select(11)
		if string:
			self.vocalizza(string)

	def shift_m_press(self):
		"""SHIFT+M: Sposta cursore su pila mazzo (12)"""
		string = self.engine.move_cursor_to_pile_with_select(12)
		if string:
			self.vocalizza(string)

	#@@# sezione metodi per verifiche di fine partita

	def check_time(self):
		""" controlliamo il tempo rimanente per la partita """

		# verifichiamo la sconfitta per tempo scaduto
		if self.engine.is_game_running and self.engine.max_time_game > 0 and not self.engine.is_time_over:
			if self.engine.ceck_lost_by_time():
				self.engine.you_lost_by_time()

	def ceck_winner(self):
		""" controlliamo se c'è un vincitore """

		if self.engine.is_game_running and self.engine.winner:
			self.engine.you_winner()

	def check_auto_events(self):
		""" controlliamo gli eventi automatici """

		# controlliamo il tempo rimanente per la partita
		self.check_time()

		# controlliamo se c'è un vincitore
		self.ceck_winner()

	#@@# sezione per la gestione degli eventi di gioco

	def build_commands_list(self):
		self.callback_dict = {
			pygame.K_1: self.press_1,
			pygame.K_2: self.press_2,
			pygame.K_3: self.press_3,
			pygame.K_4: self.press_4,
			pygame.K_5: self.press_5,
			pygame.K_6: self.press_6,
			pygame.K_7: self.press_7,
			pygame.K_c: self.c_press,
			pygame.K_d: self.d_press,
			pygame.K_f: self.f_press,
			pygame.K_g: self.g_press,
			pygame.K_i: self.i_press,
			pygame.K_m: self.m_press,
			pygame.K_n: self.n_press,
			pygame.K_o: self.o_press,
			pygame.K_p: self.p_press,
			pygame.K_r: self.r_press,
			pygame.K_s: self.s_press,
			pygame.K_t: self.t_press,
			pygame.K_x: self.x_press,
			pygame.K_h: self.h_press,
			pygame.K_F1: self.f1_press,
			pygame.K_F2: self.f2_press,
			pygame.K_F3: self.f3_press,
			pygame.K_F4: self.f4_press,
			pygame.K_F5: self.f5_press,
			pygame.K_LEFT: self.left_press,
			pygame.K_RIGHT: self.right_press,
			pygame.K_UP: self.up_press,
			pygame.K_DOWN: self.down_press,
			pygame.K_HOME: self.home_press,
			pygame.K_END: self.end_press,
			pygame.K_RETURN: self.enter_press,
			pygame.K_SPACE: self.space_press,
			pygame.K_TAB: self.tab_press,
			pygame.K_DELETE: self.canc_press,
			pygame.K_ESCAPE: self.esc_press,
		}

	def handle_keyboard_EVENTS(self, event):
		"""gestione eventi da tastiera con supporto modificatori"""
		
		if event.type == pygame.KEYDOWN:
			# Check modificatori
			mods = pygame.key.get_mods()
			
			# --- SHIFT + 1/2/3/4/S/M (PRIORITÀ SU COMANDI NORMALI) ---
			if mods & KMOD_SHIFT:
				if event.key == pygame.K_1:
					self.shift_1_press()
					return  # IMPORTANTE: return per non eseguire press_1() normale
				elif event.key == pygame.K_2:
					self.shift_2_press()
					return
				elif event.key == pygame.K_3:
					self.shift_3_press()
					return
				elif event.key == pygame.K_4:
					self.shift_4_press()
					return
				elif event.key == pygame.K_s:
					self.shift_s_press()
					return
				elif event.key == pygame.K_m:
					self.shift_m_press()
					return
			
			# --- Gestione normale (senza SHIFT) ---
			if self.callback_dict.get(event.key):
				self.callback_dict[event.key]()
		
		if event.type == pygame.KEYUP:
			pass

	def handle_EVENTS(self, event):
		""" gestione ciclo eventi principali """

		# verifichiamo se è stato avviato l'evento di chiusura della finestra
		if event.type == QUIT:
			self.quit_app()

		# verifichiamo se possono essere eseguiti gli eventi personalizzati per il gioco
		if event.type == self.TIME_CHECK_EVENT:
			self.check_auto_events()

		# verifichiamo se è stato avviato un evento della tastiera
		if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
			self.handle_keyboard_EVENTS(event)



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
