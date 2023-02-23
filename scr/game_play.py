"""
	file game_play.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/game_play.py

"""

import sys, os, time, random, pygame
from pygame.locals import *
from scr.game_engine import EngineSolitario
from scr.pygame_menu import PyMenu
from my_lib.dialog_box import DialogBox

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
		#self.dialog_box = DialogBox()
		self.tableau = self.engine.tableau
		self.foundations = self.engine.foundations
		self.waste_pile = self.engine.waste_pile
		self.cursor_pos = [0, 0]  # posizione iniziale del cursore sul tableau
		self.min_row = 0
		self.max_row = len(self.engine.tableau) - 1
		self.min_col = 0
		self.max_col = max([len(col) for col in self.engine.tableau])
		self.selected_card = None  # carta selezionata dal cursore
		self.selected_card_index = 0  # indice della carta selezionata nella pila di tableau
		self.build_commands_list()
		self.new_game()

	def create_tableau(self):
		deck = self.crea_mazzo() # crea un mazzo ordinato
		random.shuffle(deck) # mescola il mazzo

		# distribuisci le carte sul tableau
		for i, row in enumerate(self.tableau):
			for j in range(i+1):
				card = deck.pop()
				#if j == i:
					#card.flip() # scopri l'ultima carta di ogni colonna
				row.append(card)

		self.waste_pile = [] # svuota la pila di scarti
		self.foundations = [[] for _ in range(4)] # svuota le fondazioni

	def draw_table(self):
		"""
		# disegna le pile di tableau
		for i in range(7):
			for j, card in enumerate(self.tableau[i]):
				if card is not None:
					img = self.get_card_image(card)
					self.screen.blit(img, (self.tableau_x_pos[i], self.tableau_y_pos + self.card_height*j))
				else:
					img = self.get_card_back_image()
					self.screen.blit(img, (self.tableau_x_pos[i], self.tableau_y_pos + self.card_height*j))

		# disegna le pile di fondazione
		for i in range(4):
			if len(self.foundations[i]) > 0:
				top_card = self.foundations[i][-1]
				img = self.get_card_image(top_card)
				self.screen.blit(img, (self.foundations_x_pos[i], self.foundations_y_pos))
			else:
				img = self.get_card_back_image()
				self.screen.blit(img, (self.foundations_x_pos[i], self.foundations_y_pos))

		# disegna la pila di scarto
		if len(self.waste_pile) > 0:
			top_card = self.waste_pile[-1]
			img = self.get_card_image(top_card)
			self.screen.blit(img, (self.waste_pile_x_pos, self.waste_pile_y_pos))
		else:
			img = self.get_card_back_image()
			self.screen.blit(img, (self.waste_pile_x_pos, self.waste_pile_y_pos))

		pygame.display.flip()

		"""
		pass


	def new_game(self):
		#self.engine.create_tableau() # crea il tavolo di gioco
		self.engine.crea_gioco()
		#self.engine.distribuisci_carte()# distribuisci le carte sul tableau
		#self.draw_table() # disegna il tableau

	def is_valid_move(self, origin_pile, dest_pile):
		# Check if origin and destination piles are valid
		if not self.is_valid_pile(origin_pile) or not self.is_valid_pile(dest_pile):
			return False
		
		# Check if the origin pile is empty
		if self.is_empty_pile(origin_pile):
			return False
		
		# Get the top card of the origin pile
		top_card = self.get_top_card(origin_pile)
		
		# Check if the top card can be moved to the destination pile
		if self.is_valid_card_move(top_card, dest_pile):
			return True
		
		return False

	def last_move_cursor_left(self):
		if self.cursor_pos[0] > 0:
			self.cursor_pos[0] -= 1

	#def move_cursor_left(self):
		#if self.cursor_pos[0] > 0:
			#self.cursor_pos[0] -= 1
		#else:
			# Aggiungi qui la logica per gestire il limite di movimento sinistro
			#pass

	def last_move_cursor_right(self):
		if self.cursor_pos[0] < len(self.engine.tableau) - 1:
			self.cursor_pos[0] += 1

	def last_move_cursor_up(self):
		if self.cursor_pos[1] > 0:
			self.cursor_pos[1] -= 1

	def last_move_cursor_down(self):
		if self.cursor_pos[1] < len(self.engine.tableau[self.cursor_pos[0]]) - 1:
			self.cursor_pos[1] += 1

	def move_cursor_left(self):
		if self.cursor_pos[0] > 0:
			self.cursor_pos[0] -= 1
			self.cursor_pos[1] = min(self.cursor_pos[1], len(self.engine.tableau[self.cursor_pos[0]])-1)

	def move_cursor_right(self):
		if self.cursor_pos[0] < len(self.engine.tableau) - 1:
			self.cursor_pos[0] += 1
			self.cursor_pos[1] = min(self.cursor_pos[1], len(self.engine.tableau[self.cursor_pos[0]])-1)

	def move_cursor_up(self):
		if self.cursor_pos[1] > 0:
			self.cursor_pos[1] -= 1

	def move_cursor_down(self):
		if self.cursor_pos[1] < len(self.engine.tableau[self.cursor_pos[0]]) - 1:
			self.cursor_pos[1] += 1

	def move_cursor(self, direction):
		if direction == "up":
			if self.cursor_pos[0] > self.min_row:
				self.cursor_pos[0] -= 1
		elif direction == "down":
			if self.cursor_pos[0] < self.max_row:
				self.cursor_pos[0] += 1
		elif direction == "left":
			if self.cursor_pos[1] > self.min_col:
				self.cursor_pos[1] -= 1
		elif direction == "right":
			if self.cursor_pos[1] < self.max_col:
				self.cursor_pos[1] += 1


	def select_card(self):
		row, col = self.cursor_pos
		card = self.engine.get_card_at_position(row, col)

		if card is not None:
			self.selected_card = card

	def last_select_card(self):
		self.selected_card = self.engine.get_card(self.cursor_pos[0], self.cursor_pos[1])

	def move_card(self):
		if self.selected_card is not None:
			dest_row = self.cursor_pos[0]
			dest_col = len(self.engine.tableau[dest_row])
			self.engine.move_card(self.selected_card, dest_row, dest_col)
			self.selected_card = None
			#self.update_game_state()

	def vocalizza_selezioni(self):
		row, col = self.cursor_pos
		card = self.engine.get_card_at_position(row, col)
		if card is not None:
			card_name = self.engine.mazzo.get_card_name(card.valore + (card.seme * 13))
			pile_name = self.get_pile_name(row, col)
			message = f"Carta selezionata: {card_name}. Pila selezionata: {pile_name}."
			self.screen_reader.vocalizza(message)

	def update_game_state(self):
		# Aggiorna lo stato del tavolo di gioco
		self.engine.check_for_win()
		self.engine.update_tableau()
		self.engine.update_foundations()
		self.engine.update_waste_pile()

	def handle_keyboard_EVENTS(self, event):
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				self.quit_app()

			elif event.key == K_LEFT:
				self.move_cursor_left()

			elif event.key == K_RIGHT:
				self.move_cursor_right()

			elif event.key == K_UP:
				self.move_cursor_up()

			elif event.key == K_DOWN:
				self.move_cursor_down()

			elif event.key == K_RETURN:
				self.select_card()

			elif event.key == K_SPACE:
				self.move_card()

		row, col = self.cursor_pos
		current_card = self.engine.get_card_at_position(row, col)
		current_pile = self.engine.get_pile_name(row, col)
		card_name = self.engine.get_card_name(current_card) if current_card else "carta coperta"
		self.screen_reader.vocalizza(f"Cursore spostato a colonna {col}, riga {row}. {card_name} nella pila {current_pile}")


	def last_handle_keyboard_EVENTS(self, event):
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				self.quit_app()

			elif event.key == K_LEFT:
				self.move_cursor_left()

			elif event.key == K_RIGHT:
				self.move_cursor_right()

			elif event.key == K_UP:
				self.move_cursor_up()

			elif event.key == K_DOWN:
				self.move_cursor_down()

			elif event.key == K_RETURN:
				self.select_card()

			elif event.key == K_SPACE:
				self.move_card()

		self.screen_reader.vocalizza(f"Cursore spostato a colonna {self.cursor_pos[1]}, riga {self.cursor_pos[0]}")

	def quit_app(self):
		self.screen_reader.vocalizza("chiusura in corso.  ")
		pygame.time.wait(500)
		self.dialog_box.create_question_box("Sei sicuro di voler uscire?")
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

	def last_handle_keyboard_EVENTS(self, event):
		if event.type == KEYDOWN:
			if self.EVENTS_DN.get(event.key):
				self.EVENTS_DN[event.key]()



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
