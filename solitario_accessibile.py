"""
	parte 1
	nome file: solitario_accessibile.py
	Solitario Accessibile con pygame
"""

#import accessible_output2.outputs.auto
import random, time
import pygame
from pygame.locals import *
# moduli personali
from scr.screen_reader import ScreenReader
from scr.game_engine import EngineSolitario
from my_lib.dialog_box import DialogBox
#import pdb

class SolitarioAccessibile:
	def __init__(self):
		self.speack = ScreenReader()
		self.dialog_box = DialogBox()
		self.game_engine = EngineSolitario()
		self.is_running = True # boleanan per tenere il ciclo principale degli eventi aperto
		self.build_commands_list() # inizializzo la lista dei comandi di gioco

		self.schermo = pygame.display.set_mode((800, 600))
		pygame.display.set_caption("Solitario Accessibile")
		
		self.schermo.fill((255, 255, 255))  # Sfondo bianco
		
		# Aggiungi qui i tuoi elementi grafici come testo, pulsanti e immagini
		# oppure disegnali direttamente sullo schermo utilizzando i metodi di Pygame
		
		pygame.display.flip()  # Aggiorna il display

	def vocalizza(self, string):
		"""
			chiamata al metodo vocalizza del modulo screen_reader
		"""

		self.speack.vocalizza(string)

	def quit_app(self):
		self.vocalizza("chiusura in corso.  ")
		time.sleep(.3)
		result = self.dialog_box.create_question_box("Sei sicuro di voler uscire?")
		#if result:
		self.is_running = False

	def esc_press(self):
		self.quit_app()

	def gioca(self):
		# Aggiungi qui il codice per la logica del gioco
		pass
		
	def mostra_messaggio(self, testo):
		# Aggiungi qui il codice per mostrare un messaggio all'utente attraverso un output vocale
		pass

	def build_commands_list(self):
		#@@# sezione dizionari per la gestione del comandi di gioco

		# quando il tasto viene premuto
		self.EVENTS_DN = {
			pygame.K_ESCAPE: self.esc_press,
		}

		# quando il tasto viene rilasciato
		self.EVENTS_UP = {}

	def handle_keyboard_EVENTS(self):
		""" metodo per la gestione degli eventi da tastiera """
		for event in pygame.event.get():
			# processa gli eventi in coda
			pygame.event.pump()
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

			elif event.type == KEYDOWN:
				if event.key in self.EVENTS_DN:
					self.EVENTS_DN[event.key]()

			elif event.type == KEYUP:
				if event.key in self.EVENTS_UP:
					self.EVENTS_UP[event.key]()
				else:
					self.vocalizza("Comando non supportato!\n")

	def run(self):
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
