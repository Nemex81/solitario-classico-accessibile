"""
	file solitario_accessibile.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/solitario_accessibile.py

	Solitario Accessibile con pygame
"""

# lib
import os, sys, random, time, pygame
from pygame.locals import *
from scr.screen_reader import ScreenReader
from scr.game_play import GamePlay
from scr.pygame_menu import PyMenu
from my_lib.dialog_box import DialogBox
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
#logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger.setLevel(logging.DEBUG)

# inizializzo pygame
pygame.init()
pygame.font.init()

class SolitarioAccessibile(DialogBox):
	menu = None

	def __init__(self):
		super().__init__()
		# Impostazioni della finestra dell'app
		self.schermo = pygame.display.set_mode((800, 600))
		pygame.display.set_caption("Solitario Accessibile")
		self.schermo.fill((255, 255, 255))  # Sfondo bianco
		pygame.display.flip()  # Aggiorna il display
		# impostazioni funzionalità extra
		self.screen_reader = ScreenReader()  # gestore screen reader per le vocalizzazioni delle stringhe
		#self.dialog_box = DialogBox()  # gestore dialog box
		self.gameplay = GamePlay(self.schermo, self.screen_reader)
		self.menu = PyMenu(["Gioca al solitario classico", "Esci dal gioco"], self.handle_menu_selection, self.schermo, self.screen_reader)
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
		#for event in pygame.event.get():
		if event.type == QUIT:
			self.quit_app()

		elif event.type == KEYDOWN:
			if self.is_menu_open:
				self.menu.handle_keyboard_EVENTS(event)
			else:
				self.gameplay.handle_keyboard_EVENTS(event)

		elif event.type == KEYUP:
			pass

	def quit_app(self):
		question = "Sei sicuro di voler uscire?"
		title = "Conferma Uscita"
		self.screen_reader.vocalizza("chiusura in corso.  ")
		pygame.time.wait(500)
		self.create_yes_or_no_box(question, title)
		result = self.answare
		if result:
			self.is_running = False
			pygame.quit()
			sys.exit()

	def run(self):
		while self.is_running:
			for event in pygame.event.get():
				#if event.type == QUIT:
					#self.quit_app()

				self.handle_keyboard_events(event)

			#if self.is_menu_open:
				#self.menu.draw_menu()
			#else:
				#self.game_engine.render(self.schermo)

			pygame.display.update()



#@@@# avvio del modulo
if __name__ == '__main__':
	print("compilazione di %s completata." % __name__)
	SolitarioAccessibile().run()
else:
	print("Carico: %s" % __name__)
