"""
	file pygame_menu.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/pygame_menu.py

	Modulo per la gestione dei menù di gioco

"""

import sys, os, time, pygame
from pygame.locals import *
from my_lib.dialog_box import DialogBox
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
#logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger.setLevel(logging.DEBUG)

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
		self.draw_menu()

	def build_commands_list(self):
		"""Build keyboard command mappings for menu navigation.
		
		Maps keyboard events to handler methods, including:
		- Arrow keys for navigation
		- ENTER for selection
		- ESC for quit
		- Numeric keys 1-5 for direct item selection
		"""
		self.EVENTS_DN = {
			pygame.K_ESCAPE: self.esc_press,
			pygame.K_RETURN: self.execute,
			pygame.K_UP: self.prev_item,
			pygame.K_DOWN: self.next_item,
			# Numeric shortcuts (1 = first item, 2 = second, ...)
			pygame.K_1: self.press_1,
			pygame.K_2: self.press_2,
			pygame.K_3: self.press_3,
			pygame.K_4: self.press_4,
			pygame.K_5: self.press_5,
		}

	def handle_keyboard_EVENTS(self, event):
		if event.type == KEYDOWN:
			if self.EVENTS_DN.get(event.key):
				self.EVENTS_DN[event.key]()
				self.draw_menu()

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

	# === NUMERIC SHORTCUTS ===
	
	def press_1(self):
		"""Shortcut: select first menu item and execute.
		
		Equivalent to navigating to item 1 and pressing ENTER.
		"""
		if len(self.items) >= 1:
			self.selected_item = 0
			self.execute()

	def press_2(self):
		"""Shortcut: select second menu item and execute.
		
		Equivalent to navigating to item 2 and pressing ENTER.
		"""
		if len(self.items) >= 2:
			self.selected_item = 1
			self.execute()

	def press_3(self):
		"""Shortcut: select third menu item and execute."""
		if len(self.items) >= 3:
			self.selected_item = 2
			self.execute()

	def press_4(self):
		"""Shortcut: select fourth menu item and execute."""
		if len(self.items) >= 4:
			self.selected_item = 3
			self.execute()

	def press_5(self):
		"""Shortcut: select fifth menu item and execute."""
		if len(self.items) >= 5:
			self.selected_item = 4
			self.execute()
	
	# === DRAWING ===

	def draw_menu(self):
		"""Draw menu items on screen with numeric prefixes.
		
		Adds "1.", "2.", etc. prefixes to visually indicate shortcuts.
		Last item ("Esci dal gioco") has no prefix (uses ESC key).
		"""
		self.screen.fill((255, 255, 255))

		for i, item in enumerate(self.items):
			if i == self.selected_item:
				color = (255, 0, 0)
			else:
				color = (0, 0, 0)

			# Add numeric prefix for non-exit items
			# Example: "1. Gioca al solitario classico"
			if i < len(self.items) - 1:  # Don't number "Esci" (uses ESC)
				item_text = f"{i + 1}. {item}"
			else:
				item_text = item

			text = self.font.render(item_text, True, color)
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
