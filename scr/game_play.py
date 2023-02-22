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
		self.screen = screen
		self.screen_reader = screen_reader
		self.dialog_box = DialogBox()
		self.tableau = self.engine.tableau
		self.foundations = self.engine.foundations
		self.waste_pile = self.engine.waste_pile
		self.cursor_pos = [0, 0]  # posizione iniziale del cursore sul tableau
		self.selected_card = None  # carta selezionata dal cursore

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

	def move_card(self, from_pile_idx, to_pile_idx):
		from_pile = self.tableau[from_pile_idx]
		to_pile = self.tableau[to_pile_idx]

		if from_pile.is_empty():
			self.screen_reader.vocalizza("La pila di partenza è vuota")
			return False

		card = from_pile.peek()
		if not to_pile.can_add_card(card):
			self.screen_reader.vocalizza("Non è possibile spostare la carta nella pila di destinazione")
			return False

		to_pile.add_card(from_pile.pop())
		return True

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
