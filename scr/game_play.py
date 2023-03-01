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
		self.target_card = None
		self.selected_card = []  # lista delle carte selezionate dal giocatore
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
		if len(self.selected_card) == 1:
			self.vocalizza("Hai già selezionato la carta da spostare!  premi canc per annullare la selezione.\n")
			return

		elif len(self.selected_card) > 1:
			self.vocalizza("Hai già selezionato le carte da spostare!  premi canc per annullare la selezione.\n")
			return

		row, colun = self.cursor_pos
		card = self.engine.get_card(row, colun)
		if not card:
			self.vocalizza("la pila è vuota!\n")
			return

		if card.coperta:
			self.vocalizza("non puoi selezionare una carta coperta!\n")
			return

		self.id_row_origine = row
		self.id_col_origine = colun
		pila = self.engine.pile[colun]
		if row == len(pila.carte) - 1:
			self.selected_card.append(card)
		else:
			maxcarte = len(pila.carte) -1
			for c in range(row, maxcarte):
				card = self.engine.get_card(c, colun)
				self.selected_card.append(card)

		tot = len(self.selected_card)
		nome_carta = card.get_name()
		string = f"carte selezionate: {tot}: {nome_carta}\n"
		self.vocalizza(string)

	def set_destination_pile(self):
		if not self.selected_card:
			self.vocalizza("Nessuna carta selezionata.\n")
			return

		dest_row, dest_col = self.cursor_pos
		dest_pile = self.engine.pile[dest_col]
		dest_pile_type = dest_pile.get_pile_type()

		# Utilizziamo get_card_pile per ottenere l'oggetto Pila di provenienza delle carte selezionate
		source_pile = self.engine.get_card_pile(self.selected_card[0])

		if not self.engine.check_legal_move(source_pile.id, dest_col):
			self.vocalizza("Mossa non valida.\n")
			return

		if dest_pile_type == "semi":
			if len(self.selected_card) != 1:
				self.vocalizza("Puoi spostare solo una carta alla volta in questa pila.\n")
				return

			card = self.selected_card[0]
			if card.valore_numerico != 1 and source_pile.carte:
				self.vocalizza("Solo l'asso può essere spostato in questa pila.\n")
				return

		self.engine.sposta_carte(self.id_row_origine, self.id_col_origine, dest_row, dest_col, self.selected_card)
		#self.engine.sposta_carte(source_pile, dest_col, self.selected_card)
		self.selected_card = []
		self.vocalizza("spostamento completato!\n")

	def cancel_selected_cards(self):
		if self.selected_card:
			self.selected_card = []
			self.vocalizza("Carte selezionate annullate.\n")
		else:
			self.vocalizza("Non ci sono carte selezionate da annullare.\n")

	def pesca(self):
		if not self.engine.pescata():
			self.vocalizza("qualcosa è andato storto!")
			return

		string = ""
		if self.target_card:
			card_name = self.target_card.get_name()
			string = f"Hai pescato: {card_name}"

		self.vocalizza(string)

	#@@# sezione metodi per vocalizzare informazioni

	def vocalizza(self, string):
		self.screen_reader.vocalizza(string)

	def vocalizza_colonna(self):
		row, col = self.cursor_pos
		current_pile = self.engine.get_pile_name(col)
		string = current_pile
		self.vocalizza(string)

	def vocalizza_riga(self):
		row, col = self.cursor_pos
		current_card = self.engine.get_card(row, col)
		card_name = current_card.get_name()
		string_carta = f"{row+1}: {card_name}"
		string = string_carta
		self.vocalizza(string)

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

		self.vocalizza(string)

	def quit_app(self):
		self.vocalizza("chiusura in corso.  ")
		pygame.time.wait(500)
		self.create_question_box("Sei sicuro di voler uscire?")
		result = self.answare
		if result:
			pygame.quit()
			sys.exit()

	def build_commands_list(self):
		self.callback_dict = {
			pygame.K_f: self.vocalizza_focus,
			pygame.K_p: self.pesca,
			pygame.K_LEFT: self.move_cursor_left,
			pygame.K_RIGHT: self.move_cursor_right,
			pygame.K_UP: self.move_cursor_up,
			pygame.K_DOWN: self.move_cursor_down,
			pygame.K_RETURN: self.select_card,
			pygame.K_SPACE: self.set_destination_pile,
			pygame.K_DELETE: self.cancel_selected_cards,
			pygame.K_ESCAPE: self.quit_app,
		}

	def handle_keyboard_EVENTS(self, event):
			if self.callback_dict.get(event.key):
				self.callback_dict[event.key]()



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
