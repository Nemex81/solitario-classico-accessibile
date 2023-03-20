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

	#@@# sezione metodi di supporto per comandi utente

	def vocalizza(self, string):
		self.screen_reader.vocalizza(string)

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
		stri = ""
		if pygame.key.get_mods() and KMOD_CTRL:
			string = self.engine.test_vittoria()
		else:
			string = self.engine.change_deck_type()
		self.vocalizza(string)

	def f2_press(self):
		string = self.engine.change_difficulty_level()
		self.vocalizza(string)

	def f3_press(self):
		string = self.engine.change_game_time()
		self.vocalizza(string)

	def f4_press(self):
		string = self.engine.change_game_time()
		self.vocalizza(string)

	def f5_press(self):
		string = ""
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

	def enter_press(self):
		if pygame.key.get_mods() and KMOD_CTRL:
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
		string = self.engine.move_cursor("0")
		if string:
			self.vocalizza(string)

	def press_2(self):
		string = self.engine.move_cursor("1")
		if string:
			self.vocalizza(string)

	def press_3(self):
		string = self.engine.move_cursor("2")
		if string:
			self.vocalizza(string)

	def press_4(self):
		string = self.engine.move_cursor("3")
		if string:
			self.vocalizza(string)

	def press_5(self):
		string = self.engine.move_cursor("4")
		if string:
			self.vocalizza(string)

	def press_6(self):
		string = self.engine.move_cursor("5")
		if string:
			self.vocalizza(string)

	def press_7(self):
		string = self.engine.move_cursor("6")
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

	def esc_press(self):
		if self.engine.is_game_running:
			self.create_yes_or_no_box("Sei sicuro di voler abbandonare la partita?", "Abbandonare la partita??")
			result = self.answare
			if result:
				string = self.engine.chiudi_partita()
				self.vocalizza(string)

		else:
			self.quit_app()

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
			pygame.K_m: self.m_press,
			pygame.K_n: self.n_press,
			pygame.K_o: self.o_press,
			pygame.K_p: self.p_press,
			pygame.K_r: self.r_press,
			pygame.K_s: self.s_press,
			pygame.K_t: self.t_press,
			pygame.K_x: self.x_press,
			pygame.K_F1: self.f1_press,
			pygame.K_F2: self.f2_press,
			pygame.K_F3: self.f3_press,
			pygame.K_F4: self.f4_press,
			pygame.K_F5: self.f5_press,
			pygame.K_LEFT: self.left_press,
			pygame.K_RIGHT: self.right_press,
			pygame.K_UP: self.up_press,
			pygame.K_DOWN: self.down_press,
			pygame.K_RETURN: self.enter_press,
			pygame.K_SPACE: self.space_press,
			pygame.K_TAB: self.tab_press,
			pygame.K_DELETE: self.canc_press,
			pygame.K_ESCAPE: self.esc_press,
		}

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

	def handle_EVENTS(self, event):
		""" gestione ciclo eventi """

		if event.type == QUIT:
			self.quit_app()

		if event.type == self.TIME_CHECK_EVENT:
			self.check_time()
			self.ceck_winner()

		if event.type == pygame.KEYDOWN:
			if self.callback_dict.get(event.key):
				self.callback_dict[event.key]()

		# verifichiamo la sconfitta per tempo scaduto
		#if self.engine.is_game_running and self.engine.max_time_game > 0 and not self.engine.is_time_over:
			#if self.engine.ceck_lost_by_time():
				#self.engine.you_lost_by_time()

		#elif self.engine.is_game_running and self.engine.max_time_game > 0 and self.engine.is_time_over:
			#self.engine.you_lost_by_time()

		# verifichiamo la vittoria
		#if self.engine.is_game_running and self.engine.winner:
			#str_winner = self.engine.get_info_game()
			#self.create_alert_box(str_winner, "Vittoria Spumeggiante")
			#self.create_yes_or_no_box("Vuoi giocare un'altra partita?", "Domanda")
			#if self.answare:
				#self.engine.nuova_partita()
			#else:
				#self.engine.chiudi_partita()




#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
