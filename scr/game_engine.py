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
from scr.pile import PileGioco
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
#logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger.setLevel(logging.DEBUG)

class EngineSolitario(PileGioco):
	def __init__(self):
		super().__init__()
		self.primo_giro = True
		self.conta_giri = 0
		self.valid_positions = [(i, j) for i in range(7) for j in range(20)]
		self.situazione_attuale = []

	def crea_gioco(self):
		self.crea_mazzo()
		self.mischia_carte()
		self.distribuisci_carte()

	def get_card_indices_at_position(self, row, col):
		# Restituisce gli indici delle carte corrispondenti alla posizione specificata
		if not self.is_valid_pile((row, col)):
			return None
		
		from_col = col
		from_row = row
		while from_row < len(self.tableau) and len(self.tableau[from_row]) <= from_col:
			from_col -= len(self.tableau[from_row])
			from_row += 1
		
		if from_row >= len(self.tableau):
			return None
		
		return (from_row, from_col)

	def controlla_vittoria(self):
		for foundation in self._foundations:
			if len(foundation) < 13:
				return False

		return True

	#@@@# sezione metodi per convalidare lo spostamento di una carta

	def is_valid_position(self, row, col):
		"""
		Verifica se la posizione indicata è valida per il gioco del solitario.
		"""
		if row < 0 or row >= 7:
			return False
		if col < 0 or col >= len(self.tableau[row]):
			return False
		if (row, col) not in self.valid_positions:
			return False
		return True

	def is_valid_pile(self, pile_index: int, card_index: int = None) -> bool:
		"""
		Verifica se l'indice della pila e della carta sono validi.
		Se card_index non viene passato, controlla solo se l'indice della pila è valido.
		"""
		if 0 <= pile_index < 7:
			if card_index is not None and 0 <= card_index < len(self.tableau[pile_index]):
				return True
			elif card_index is None:
				return True

		return False

	def is_empty_pile(self, pile: str) -> bool:
		"""
		Verifica se una pila è vuota
		:param pile: Il nome della pila da verificare
		:return: True se la pila è vuota, False altrimenti
		"""
		return len(getattr(self, pile)) == 0

	def is_valid_card_move(self, start_pile, end_pile):
		"""Verifica se il movimento di una carta da una pila all'altra è valido"""
		start_pile_cards = self.get_pile_cards(start_pile)
		end_pile_cards = self.get_pile_cards(end_pile)

		# Verifica che la pila di partenza contenga almeno una carta
		if len(start_pile_cards) == 0:
			return False

		# Verifica se la carta da spostare è l'ultima carta della pila di partenza
		card_to_move = start_pile_cards[-1]
		if card_to_move not in self.get_top_cards(start_pile):
			return False

		# Verifica che la carta da spostare possa essere posizionata sulla pila di destinazione
		if not self.is_valid_pile(end_pile, card_to_move):
			return False

		# Verifica che il valore della carta da spostare sia uno in meno rispetto alla carta in cima alla pila di destinazione
		if len(end_pile_cards) > 0 and card_to_move.value != end_pile_cards[-1].value - 1:
			return False

		return True



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
