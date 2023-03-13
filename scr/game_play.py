"""
	file game_play.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/game_play.py

	Modulo per la gestione dellinterfaccia utente durante la partita al solitario

"""

import sys, os, time, random, pygame
from pygame.locals import *
from scr.game_engine import EngineSolitario
from my_lib.dialog_box import DialogBox
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
#logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger.setLevel(logging.DEBUG)

# inizializzo pygame
pygame.init()
pygame.font.init()

class GamePlay(DialogBox):
	def __init__(self, screen, screen_reader):
		super().__init__()
		#self.callback = callback_dict
		self.screen = screen # import config schermo
		self.screen_reader = screen_reader # import motore di vocalizzazione
		self.engine = EngineSolitario() # inizializzazione motore di gioco per il solitario classico
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
		string = self.engine.say_origin()
		self.vocalizza(string)

	def f2_press(self):
		string = self.engine.say_dest()
		self.vocalizza(string)

	def f3_press(self):
		string = self.engine.say_selected_cards()
		self.vocalizza(string)

	def f4_press(self):
		string = self.engine.prova_verifica()
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
		#string = self.engine.vocalizza_pila()
		string = self.engine.say_selected_cards()
		self.vocalizza(string)

	def x_press(self):
		string = self.engine.vocalizza_carta()
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

	def f_press(self):
		string = self.engine.vocalizza_focus()
		if string:
			self.vocalizza(string)

	def d_press(self):
		string = self.engine.pesca()
		if string:
			self.vocalizza(string)

	def m_press(self):
		string = self.engine.say_tot_dek()
		if string:
			self.vocalizza(string)

	def p_press(self):
		string = self.engine.pesca()
		if string:
			self.vocalizza(string)

	def s_press(self):
		string = self.engine.say_top_scarto()
		if string:
			self.vocalizza(string)

	def esc_press(self):
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
			pygame.K_m: self.m_press,
			pygame.K_p: self.p_press,
			pygame.K_s: self.s_press,
			pygame.K_x: self.x_press,
			pygame.K_F1: self.f1_press,
			pygame.K_F2: self.f2_press,
			pygame.K_F3: self.f3_press,
			pygame.K_F4: self.f4_press,
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

	def handle_keyboard_EVENTS(self, event):
		""" gestione ciclo eventi """
		if self.callback_dict.get(event.key):
			self.callback_dict[event.key]()



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
