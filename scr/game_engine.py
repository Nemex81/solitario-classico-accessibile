"""
	file game_engine.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/game_engine.py

	Modulo per le regole del gioco del solitario
"""

# lib
import os, sys, random
# moduli personali
from my_lib.myglob import *
import my_lib.myutyls as mu
from scr.cards import Carta, Mazzo
from scr.pile import Tavolo
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
#logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger.setLevel(logging.DEBUG)

class EngineSolitario(Tavolo):
	def __init__(self):
		super().__init__()
		self.mazzo = Mazzo()
		#self.primo_giro = True
		#self.conta_giri = 0
		#self.valid_positions = [(i, j) for i in range(7) for j in range(20)]
		#self.situazione_attuale = []

	def crea_gioco(self):
		self.mazzo.reset()
		self.crea_pile_gioco()
		self.distribuisci_carte()




#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
