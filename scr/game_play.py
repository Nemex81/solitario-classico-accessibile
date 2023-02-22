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



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
