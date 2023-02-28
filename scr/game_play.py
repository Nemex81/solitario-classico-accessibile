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
		self.cursor_pos = [0, 0]  # posizione iniziale del cursore sul tableau
		self.min_row = 0
		self.max_row = len(self.engine.tableau) - 1
		self.min_col = 0
		self.max_col = max([len(col) for col in self.engine.tableau])
		self.selected_card = None  # carta selezionata dal cursore
		self.engine.selected_card_index = 0  # indice della carta selezionata nella pila di tableau
		self.build_commands_list()
		self.new_game()

	def new_game(self):
		self.engine.crea_gioco()

	def vocalizza_selezioni(self):
		row, col = self.cursor_pos
		card = self.engine.get_card_at_position(row, col)
		if card is not None:
			card_name = self.engine.mazzo.get_card_name(card.valore + (card.seme * 13))
			pile_name = self.get_pile_name(row, col)
			message = f"Carta selezionata: {card_name}. Pila selezionata: {pile_name}."
			self.screen_reader.vocalizza(message)
			self.update_game_state()

	def check_for_win(self):
		"""
		Verifica se il gioco è stato vinto.
		"""
		# implementazione del metodo check_for_win
		if self.engine.controlla_vittoria():
			pass

	#@@@# sezione comandi utente per il game play

	def move_cursor_up(self):
		if self.cursor_pos[0] > 0:
			self.cursor_pos[0] -= 1
			self.cursor_pos[1] = min(self.cursor_pos[1], len(self.engine.tableau[self.cursor_pos[0]])-1)

	def move_cursor_down(self):
		if self.cursor_pos[0] < len(self.engine.tableau) - 1:
			self.cursor_pos[0] += 1
			self.cursor_pos[1] = min(self.cursor_pos[1], len(self.engine.tableau[self.cursor_pos[0]])-1)

	def move_cursor_left(self):
		if self.cursor_pos[1] > 0:
			self.cursor_pos[1] -= 1

	def move_cursor_right(self):
		if self.cursor_pos[1] < len(self.engine.tableau[self.cursor_pos[0]]) - 1:
			self.cursor_pos[1] += 1

	def select_card(self):
		row, col = self.cursor_pos
		card = self.engine.get_card_at_position(row, col)
		if card is not None:
			self.selected_card = card

	def move_card(self):
		if self.selected_card is not None:
			from_row, from_col = self.engine.get_card_indices_at_position(*self.cursor_pos)
			to_col = self.engine.selected_card_index
			if self.engine.move_card(from_col, to_col, len(self.engine.tableau[from_col])-from_row):
				self.selected_card = None
				self.update_game_state()

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
				# vocalizziamo lo spostamento
				row, col = self.cursor_pos
				current_card = self.engine.get_card(row, col)
				current_pile = self.engine.get_pile_name(row, col)
				card_name = self.engine.get_card_name(current_card)
				self.screen_reader.vocalizza(f"Cursore spostato a colonna {col+1}, riga {row+1}. {card_name} nella pila {current_pile}")



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
