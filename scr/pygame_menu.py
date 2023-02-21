"""
	file pygame_menu.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/pygame_menu.py

"""

import pygame
from pygame.locals import *
pygame.init()
pygame.font.init()

class PyMenu:
	def __init__(self, items, callback, screen, screen_reader):
		self.items = items
		self.selected_item = 0
		self.callback = callback
		self.screen = screen
		self.screen_reader = screen_reader
		self.font = pygame.font.Font(None, 36)

		self.build_commands_list()

	def build_commands_list(self):
		#@@# sezione dizionari per la gestione del comandi di gioco

		# quando il tasto viene premuto
		self.EVENTS_DN = {
			pygame.K_ESCAPE: self.esc_press,
			pygame.K_RETURN: self.execute,
			pygame.K_UP: self.prev_item,
			pygame.K_DOWN: self.next_item
		}

		# quando il tasto viene rilasciato
		self.EVENTS_UP = {}

	def handle_keyboard_EVENTS(self, event):
		""" metodo per la gestione degli eventi da tastiera """
		for event in pygame.event.get():
			# processa gli eventi in coda
			pygame.event.pump()
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

			elif event.type == KEYDOWN:
				if self.EVENTS_DN.get(event.key):
					self.EVENTS_DN[event.key]()

	def next_item(self):
		self.selected_item = (self.selected_item + 1) % len(self.items)
		self.screen_reader.vocalizza(self.items[self.selected_item])

	def prev_item(self):
		self.selected_item = (self.selected_item - 1) % len(self.items)
		self.screen_reader.vocalizza(self.items[self.selected_item])

	def execute(self):
		self.screen_reader.vocalizza("Hai selezionato " + self.items[self.selected_item])
		self.callback(self.selected_item)

	def draw_menu(self):
		self.screen.fill((255, 255, 255))

		for i, item in enumerate(self.items):
			if i == self.selected_item:
				color = (255, 0, 0)
			else:
				color = (0, 0, 0)

			text = self.font.render(item, True, color)
			text_rect = text.get_rect(center=(self.screen.get_width() / 2, (i + 1) * 50))
			self.screen.blit(text, text_rect)

		pygame.display.flip()

	def quit_app(self):
		self.vocalizza("chiusura in corso.  ")
		time.sleep(.3)
		result = self.dialog_box.create_question_box("Sei sicuro di voler uscire?")
		if result:
			self.is_running = False

	def esc_press(self):
		self.quit_app()


