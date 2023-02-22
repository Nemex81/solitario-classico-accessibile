"""
	file game_play.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/game_play.py

"""

import sys, os, time, pygame
from pygame.locals import *
from my_lib.dialog_box import DialogBox
from scr.pygame_menu import PyMenu
from my_lib.dialog_box import DialogBox

# inizializzo pygame
pygame.init()
pygame.font.init()

class GamePlay:
	def __init__(self, items, callback, screen, screen_reader):
		self.engine = EngineSolitario()
		self.create_tableau()  # distribuisce le carte sul tavolo
		self.screen = screen
		self.screen_reader = screen_reader
		self.dialog_box = DialogBox()
		self.tableau = self.engine.tableau
		self.foundations = self.engine.foundations
		self.waste_pile = self.engine.waste_pile
		self.cursor_pos = [0, 0]  # posizione iniziale del cursore sul tableau
		self.selected_card = None  # carta selezionata dal cursore

	def create_tableau(self):
		deck = self.engine.crea_mazzo() # crea un mazzo ordinato
		random.shuffle(deck) # mescola il mazzo

		# distribuisci le carte sul tableau
		for i, row in enumerate(self.tableau):
			for j in range(i+1):
				card = deck.pop()
				if j == i:
					card.flip() # scopri l'ultima carta di ogni colonna
				row.append(card)

		self.waste_pile = [] # svuota la pila di scarti
		self.foundations = [[] for _ in range(4)] # svuota le fondazioni

	def new_game(self):
		self.engine.create_tableau() # crea il tavolo di gioco
		self.engine.distribuisci_carte()# distribuisci le carte sul tableau
		self.draw_table() # disegna il tableau

	def move_cursor_up(self):
		if self.current_index > 0:
			self.current_index -= 1
		else:
			self.current_index = len(self.menu_items) - 1

	def move_cursor_dn(self):
		if self.selected_card is not None:
			# Check if selected card is last in tableau
			last_card = self.tableau[self.selected_card[0]][-1]
			if self.selected_card[1] == len(self.tableau[self.selected_card[0]])-1:
				# Check if there is a card on the stock pile
				if self.waste_pile:
					self.selected_card = None
					self.selected_pile = 'waste'
				else:
					return
			else:
				self.selected_card = (self.selected_card[0], self.selected_card[1]+1)
			self.draw_table()

	def select_card(self):
		row, col = self.cursor_pos
		card = self.tableau[row][col]

		if card is not None:
			self.selected_card = card

	def move_card(self):
		if self.selected_pile is None or self.destination_pile is None:
			return

		# Verifica se la mossa è valida
		if self.game_engine.is_valid_card_move(self.selected_pile, self.destination_pile):
			# Sposta la carta dalla pila di origine alla pila di destinazione
			self.game_engine.move_card(self.selected_pile, self.destination_pile)

			# Aggiorna lo stato del tavolo di gioco
			self.update_game_state()

			# Resetta le pile selezionate
			self.selected_pile = None
			self.destination_pile = None

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



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
