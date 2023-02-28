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
		self.engine = EngineSolitario()
		self.screen = screen
		self.screen_reader = screen_reader
		self.cursor_pos = [0, 0]  # posizione iniziale del cursore sul tavolo
		self.selected_card = None  # carta selezionata dal cursore
		self.build_commands_list()
		self.new_game()

	def new_game(self):
		self.engine.crea_gioco()

	def check_for_win(self):
		"""
		Verifica se il gioco è stato vinto.
		"""
		# implementazione del metodo check_for_win
		pass

	#@@@# sezione comandi utente per il game play

	def move_cursor_up(self):
		if self.cursor_pos[0] > 0:
			self.cursor_pos[0] -= 1
			self.vocalizza_riga()

	def move_cursor_down(self):
		pila = self.engine.pile[self.cursor_pos[1]]
		if self.cursor_pos[0] < len(pila.carte) - 1:
			self.cursor_pos[0] += 1
			self.vocalizza_riga()

	def move_cursor_left(self):
		if self.cursor_pos[1] > 0:
			self.cursor_pos[1] -= 1
			self.cursor_pos[0] = 0
			self.vocalizza_colonna()

	def move_cursor_right(self):
		pile = self.engine.pile
		if self.cursor_pos[1] < len(pile) - 1:
			self.cursor_pos[1] += 1
			self.cursor_pos[0] = 0
			self.vocalizza_colonna()

	def select_card(self):
		self.vocalizza_focus()

	def move_card(self):
		pass

	def vocalizza_colonna(self):
		row, col = self.cursor_pos
		current_pile = self.engine.get_pile_name(col)
		string = current_pile
		self.screen_reader.vocalizza(string)

	def vocalizza_riga(self):
		row, col = self.cursor_pos
		current_card = self.engine.get_card(row, col)
		card_name = current_card.get_name()
		string_carta = f"{row+1}: {card_name}"
		string = string_carta
		self.screen_reader.vocalizza(string)

	def vocalizza_focus(self):
		# vocalizziamo lo spostamento
		row, col = self.cursor_pos
		current_card = self.engine.get_card(row, col)
		current_pile = self.engine.get_pile_name(col)
		#string_cursore = f"Cursore spostato a colonna {col+1}, riga {row+1}. "
		try:
			card_name = current_card.get_name()
			string_carta = f"{current_pile}.  "
			string_carta += f"{row+1}: {card_name}"
			string = string_carta

		except AttributeError:
			string = current_pile

		self.screen_reader.vocalizza(string)

	def quit_app(self):
		self.screen_reader.vocalizza("chiusura in corso.  ")
		pygame.time.wait(500)
		self.create_question_box("Sei sicuro di voler uscire?")
		result = self.answare
		if result:
			pygame.quit()
			sys.exit()

	def build_commands_list(self):
		self.callback_dict = {
			pygame.K_LEFT: self.move_cursor_left,
			pygame.K_RIGHT: self.move_cursor_right,
			pygame.K_UP: self.move_cursor_up,
			pygame.K_DOWN: self.move_cursor_down,
			pygame.K_RETURN: self.select_card,
			pygame.K_SPACE: self.move_card,
			pygame.K_ESCAPE: self.quit_app,
		}

	def handle_keyboard_EVENTS(self, event):
			if self.callback_dict.get(event.key):
				self.callback_dict[event.key]()
				#self.vocalizza_focus()



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
