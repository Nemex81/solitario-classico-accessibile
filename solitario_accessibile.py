"""
	file solitario_accessibile.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/solitario_accessibile.py

	Solitario Accessibile con pygame
"""

#import accessible_output2.outputs.auto
import os, sys, random, time, pygame
from pygame.locals import *
# moduli personali
from scr.screen_reader import ScreenReader
from scr.game_engine import EngineSolitario
from scr.pygame_menu import PyMenu
from my_lib.dialog_box import DialogBox
#import pdb

pygame.init()
pygame.font.init()

class SolitarioAccessibile:
	menu = None

	def __init__(self):
		# impostazioni della finestra dell'app		self.schermo = pygame.display.set_mode((800, 600))
		pygame.display.set_caption("Solitario Accessibile")
		self.schermo.fill((255, 255, 255))  # Sfondo bianco
		# Aggiungi qui i tuoi elementi grafici come testo, pulsanti e immagini
		# oppure disegnali direttamente sullo schermo utilizzando i metodi di Pygame

		pygame.display.flip()  # Aggiorna il display

		self.screen_reader = ScreenReader() # gestore screen reader per le vocalizzazioni delle stringhe
		self.dialog_box = DialogBox() # gestore dialog box
		self.game_engine = EngineSolitario() # motore di gioco
		self.menu = PyMenu(["Nuova partita", "Esci dal gioco"], self.schermo, self.handle_menu_selection, self.screen_reader)
		self.build_commands_list() # inizializzo la lista dei comandi di gioco
		self.is_menu_open = True
		self.selected_menu_item = 0
		self.is_running = True # boleanan per tenere il ciclo principale degli eventi aperto

	def vocalizza(self, string):
		"""
			chiamata al metodo vocalizza del modulo screen_reader
		"""

		self.screen_reader.vocalizza(string)

	def handle_menu_selection(self, selected_item):
		if selected_item == 0:
			self.is_menu_open = False
		else:
			pygame.quit()
			sys.exit()

	def run(self):
		while self.is_running:
			if self.is_menu_open:
				self.menu.handle_keyboard_EVENTS(pygame.event.get())
			else:
				self.handle_gameplay_events(pygame.event.get())

	def handle_gameplay_events(self, event):
		# implementazione della gestione degli eventi del gioco
		pass


	def crea_menu(cls):
		cls.menu = Menu(cls.screen_reader)
		cls.menu.aggiungi_voce("Nuova partita", cls.nuova_partita)
		cls.menu.aggiungi_voce("Esci", cls.esc_press)

	@classmethod
	def avvia_menu(cls):
		cls.crea_menu()
		cls.menu.avvia()
		cls.menu.chiudi()

	def quit_app(self):
		self.vocalizza("chiusura in corso.  ")
		time.sleep(.3)
		result = self.dialog_box.create_question_box("Sei sicuro di voler uscire?")
		if result:
			self.is_running = False

	def gioca(self):
		# Aggiungi qui il codice per la logica del gioco
		pass
		
	def mostra_messaggio(self, testo):
		# Aggiungi qui il codice per mostrare un messaggio all'utente attraverso un output vocale
		pass

	#@@# sezione comandi di gioco

	def esc_press(self):
		self.quit_app()

	def enter_press(self):
		pass

	def space_press(self):
		pass

	def key_up_press(self):
		pass

	def key_dn_press(self):
		pass

	def key_left_press(self):
		pass

	def key_right_press(self):
		pass

	def build_commands_list(self):
		#@@# sezione dizionari per la gestione del comandi di gioco

		# quando il tasto viene premuto
		self.EVENTS_DN = {
			pygame.K_ESCAPE: self.esc_press,
		}

		# quando il tasto viene rilasciato
		self.EVENTS_UP = {}

	def last_handle_keyboard_EVENTS(self):
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

			elif event.type == KEYUP:
				if self.EVENTS_UP.get(event.key):
					self.EVENTS_UP[event.key]()
				else:
					self.vocalizza("Comando non supportato!\n")

	def last_run(self):
		""" metodo per il ciclo principale dell'applicazione """
		while self.is_running:
			# in ascolto sugli eventi da tastiera
			self.handle_keyboard_EVENTS()

			# aggiornamento dei dati del personaggio
			#if self.player:
				#self.player.update()

			# aggiornamento del bannerv visivo
			#self.screen.fill((0, 0, 0))
			#self.draw_label(self.screen, self.show_text_banner())
			# Aggiorna la finestra di gioco
			pygame.display.update()

			# aggiornamento dei tick di gioco
			#self.py_clock.tick(self.fps)
			time.sleep(.005) # piccolo ritardo nel ciclo principale per non stressare il processore



#@@@# start del modulo
if __name__ == "__main__":
	SolitarioAccessibile().run()

