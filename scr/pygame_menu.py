"""
	file pygame_menu.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/pygame_menu.py

	Modulo per la gestione dei menù di gioco

"""

import sys, os, time, pygame
from pygame.locals import *
from my_lib.dialog_box import DialogBox
# inizializzo pygame
pygame.init()
pygame.font.init()

class PyMenu(DialogBox):
	def __init__(self, items, callback, screen, screen_reader):
		super().__init__()
		self.items = items
		self.selected_item = 0
		self.exit_menu_index = self.items.index("Esci dal gioco")
		self.callback = callback
		self.screen = screen
		self.screen_reader = screen_reader
		#self.dialog_box = DialogBox()
		self.font = pygame.font.Font(None, 36)
		self.build_commands_list()

	def build_commands_list(self):
		self.EVENTS_DN = {
			pygame.K_ESCAPE: self.esc_press,
			pygame.K_RETURN: self.execute,
			pygame.K_UP: self.prev_item,
			pygame.K_DOWN: self.next_item
		}

	def handle_keyboard_EVENTS(self, event):
		if event.type == KEYDOWN:
			if self.EVENTS_DN.get(event.key):
				self.EVENTS_DN[event.key]()

	def next_item(self):
		self.selected_item = (self.selected_item + 1) % len(self.items)
		self.screen_reader.vocalizza(self.items[self.selected_item])

	def prev_item(self):
		self.selected_item = (self.selected_item - 1) % len(self.items)
		self.screen_reader.vocalizza(self.items[self.selected_item])

	def execute(self):
		#self.screen_reader.vocalizza("Hai selezionato " + self.items[self.selected_item])
		#self.callback(self.selected_item)
		if self.selected_item == self.exit_menu_index:
			self.quit_app()
		else:
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
		self.screen_reader.vocalizza("chiusura in corso.  ")
		pygame.time.wait(500)
		self.create_question_box("Sei sicuro di voler uscire?")
		result = self.answare
		if result:
			pygame.quit()
			sys.exit()

	def esc_press(self):
		self.quit_app()



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
