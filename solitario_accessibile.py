"""
	file solitario_accessibile.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/solitario_accessibile.py

	Solitario Accessibile con pygame
"""

import os
import sys
import random
import time
import pygame
from pygame.locals import *
from scr.screen_reader import ScreenReader
from scr.game_engine import EngineSolitario
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
		#self.menu = PyMenu(["Nuova partita", "Esci dal gioco"], self.schermo, self.handle_menu_selection, self.screen_reader)
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

	def next_item(self):
		self.menu.next_item()

	def prev_item(self):
		self.menu.prev_item()

	def execute(self):
		self.menu.execute()

	def handle_gameplay_events(self, event):
		"""
		Implementazione della gestione degli eventi del gioco.
		"""
		pass

	def handle_menu_selection(self, selected_item):
		if selected_item < 0:
			self.is_menu_open = False
		else:
			result = self.menu.quit_app()
			if result:
				self.is_running = False

	def handle_keyboard_events(self, event):
		"""
		Metodo per la gestione degli eventi da tastiera.
		"""
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

			elif event.type == KEYDOWN:
				if self.is_menu_open:
					self.menu.handle_keyboard_events(event)
				else:
					self.handle_gameplay_events(event)

			elif event.type == KEYUP:
				pass

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
				self.game_engine.render(self.schermo)
			pygame.display.update()


	def last_run(self):
		"""
		Loop principale del gioco.
		"""
		while self.is_running:
			#self.handle_keyboard_events(pygame.event.get())
			if not self.is_menu_open:
				self.handle_gameplay_events(pygame.event.get())
			else:
				self.menu.handle_keyboard_EVENTS(pygame.event.get())

#@@@# avvio del modulo
SolitarioAccessibile().run()