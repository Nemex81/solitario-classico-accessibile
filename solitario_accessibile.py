"""
	file solitario_accessibile.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/solitario_accessibile.py

	Solitario Accessibile con pygame
"""

# lib
import os
import sys
import random
import time
import pygame
from pygame.locals import *
from scr.screen_reader import ScreenReader
from scr.game_engine import EngineSolitario
from scr.game_play import GamePlay
from scr.pygame_menu import PyMenu
from my_lib.dialog_box import DialogBox

pygame.init()
pygame.font.init()

class SolitarioAccessibile:
	menu = None

	def __init__(self):
		# Impostazioni della finestra dell'app
		self.schermo = pygame.display.set_mode((800, 600))
		pygame.display.set_caption("Solitario Accessibile")
		self.schermo.fill((255, 255, 255))  # Sfondo bianco
		pygame.display.flip()  # Aggiorna il display

		self.screen_reader = ScreenReader()  # gestore screen reader per le vocalizzazioni delle stringhe
		self.dialog_box = DialogBox()  # gestore dialog box
		self.game_engine = EngineSolitario()  # motore di gioco
		gameplay = GamePlay(self.schermo, self.screen_reader)
		self.menu = PyMenu(["Nuova partita", "Esci dal gioco"], self.handle_menu_selection, self.schermo, self.screen_reader)

		self.EVENTS_DN = self.menu.build_commands_list()  # inizializzo la lista dei comandi di gioco
		self.is_menu_open = True
		self.selected_menu_item = 0
		self.is_running = True  # boolean per tenere il ciclo principale degli eventi aperto

	def vocalizza(self, string):
		"""
		chiamata al metodo vocalizza del modulo screen_reader
		"""
		self.screen_reader.vocalizza(string)

	def draw_game(self):
		"""
		Metodo per disegnare la finestra di gioco.
		"""
		self.game_engine.render(self.schermo)

	def handle_menu_selection(self, selected_item):
		if selected_item < 0:
			self.is_menu_open = False
		else:
			result = self.menu.quit_app()
			if result:
				self.is_running = False

	def handle_menu_selection(self, selected_item):
		if selected_item == self.exit_menu_index:
			result = self.menu.quit_app()
			if result:
				self.is_running = False
		else:
			self.is_menu_open = False

	def last_handle_keyboard_events(self, event):
		"""
		Metodo per la gestione degli eventi da tastiera.
		"""
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

			elif event.type == KEYDOWN:
				if self.is_menu_open:
					self.menu.handle_keyboard_EVENTS(event)
					if event.key == K_RETURN:
						self.execute()
					elif event.key == K_UP:
						self.prev_item()
					elif event.key == K_DOWN:
						self.next_item()

			elif event.type == KEYUP:
				pass

	def next_item(self):
		self.menu.next_item()

	def prev_item(self):
		self.menu.prev_item()

	def execute(self):
		self.menu.execute()

	def handle_menu_selection(self, selected_item):
		if selected_item == len(self.menu.items) - 1:
			self.quit_app()
		else:
			self.is_menu_open = False

	def handle_keyboard_events(self, event):
		"""
		Metodo per la gestione degli eventi da tastiera.
		"""
		for event in pygame.event.get():
			if event.type == QUIT:
				self.menu.quit()

			elif event.type == KEYDOWN:
				if self.is_menu_open:
					self.menu.handle_keyboard_EVENTS(event)
				else:
					self.handle_gameplay_events(event)

			elif event.type == KEYUP:
				pass

	def handle_gameplay_events(self, event):
		#for event in pygame.event.get():
		if event.type == pygame.QUIT:
			self.running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				self.running = False

			elif event.key == pygame.K_LEFT:
				self.selected_pile_index = (self.selected_pile_index - 1) % 7

			elif event.key == pygame.K_RIGHT:
				self.selected_pile_index = (self.selected_pile_index + 1) % 7

			elif event.key == pygame.K_UP:
				self.selected_card_index = (self.selected_card_index - 1) % len(self.game_engine.tableau[self.selected_pile_index])

			elif event.key == pygame.K_DOWN:
				self.gameplay.selected_card_index = (self.gameplay.selected_card_index + 1) % len(self.gameplay.tableau[self.selected_pile_index])

			elif event.key == pygame.K_RETURN:
				self.game_engine.select_card(self.selected_pile_index, self.selected_card_index)

			elif event.key == pygame.K_SPACE:
				self.game_engine.move_selected_card()

	def run(self):
		while self.is_running:
			for event in pygame.event.get():
				if event.type == QUIT:
					self.quit_app()

				elif self.is_menu_open:
					self.menu.handle_keyboard_EVENTS(event)
				else:
					self.handle_gameplay_events(event)

			if self.is_menu_open:
				self.menu.draw_menu()
			else:
				#self.game_engine.render(self.schermo)
				pass

			pygame.display.update()



#@@@# avvio del modulo
if __name__ == '__main__':
	SolitarioAccessibile().run()
