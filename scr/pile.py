"""
	file pile.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/pile.py

	Modulo per la creazione e gestione delle pile di gioco
"""

# lib
import random
# moduli personali
from my_lib.myglob import *
import my_lib.myutyls as mu
from scr.cards import Carta, Mazzo
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
#logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger.setLevel(logging.DEBUG)

class PileGioco(Mazzo):
	def __init__(self):
		super().__init__()
		self.tableau = [[] for _ in range(7)]
		self.foundations = [[] for _ in range(4)]
		self.waste_pile = []
		self.stock_pile = []

	def distribuisci_carte(self):
		# Distribuisce le carte sul tableau
		n_carte = 0
		for i in range(7):
			for j in range(i + 1):
				carta = self.pesca()
				carta.coperta = True
				self.tableau[j].append(carta)
				carta.colun = j
				carta.row = len(self.tableau[j]) - 1
				#if len(self.tableau[j]) - 1 == carta.row:
					#carta.flip()  # Scopre l'ultima carta della colonna

				n_carte += 1

		# imposto l'ultima carta di ogni colonna come scoperta
		for c in range(7):
			carta = self.tableau[c][-1]
			carta.flip()

		# Mette le rimanenti carte nel stock pile
		self.stock_pile = [self.mazzo.get_carta(i) for i in range(n_carte, len(self.cards))]

	def get_card(self, row, col):
		card = self.tableau[row][col]
		return card

	def get_pile_name(self, row, col):
		pile_name = ""
		if col < 7:
			pile_name = f"Tableau colonna {col + 1}"

		elif col < 11:
			pile_name = f"Foundations {col - 6}"

		else:
			pile_name = "Waste pile"

		return pile_name

	def get_top_card(self, pile):
		if not self.is_empty_pile(pile):
			return pile[-1]
		else:
			return None

	def get_card_at_position(self, row, col):
		"""
		Ritorna la carta nella posizione specificata, o None se la posizione è vuota o non valida.
		"""
		#if len(self.tableau[row]) > col:
		return self.tableau[row][col]
		#else:
			#return None

	def get_card_name(self, current_card):
		"""
		Restituisce il nome della carta data la riga e la colonna della pila di tableau.
		"""
		card = current_card
		if card is None:
			return "Nessuna carta presente"

		elif card.coperta:
			return "Carta coperta"

		else:
			return card.nome

	def move_card(self):
		pass


#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
