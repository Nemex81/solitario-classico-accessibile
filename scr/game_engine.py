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
		"""Crea un nuovo gioco di solitario."""
		self.mazzo.reset()
		self.crea_pile_gioco()
		self.distribuisci_carte()

	def distribuisci_carte(self):
		# distribuisci le carte alle pile base
		for i in range(7):
			for j in range(i+1):
				carta = self.mazzo.pesca()
				carta.coperta = True #if j < i else False
				self.pile[i].aggiungi_carta(carta)

		# distribuisci le restanti carte alla pila mazzo riserve
		for i in range(24):
			carta = self.mazzo.pesca()
			carta.coperta = True
			self.pile[12].aggiungi_carta(carta)

		# scopro l'ultima carta di ogni pila
		for i in range(7):
			pila = self.pile[i]
			carta = pila.carte[-1]
			carta.flip()#coperta = False

	def check_legal_move(self, source_pile_index, dest_pile_index):
		"""
		Verifica se lo spostamento di una o più carte dalla pila sorgente a quella destinazione è legale.
		"""
		source_pile = self.pile[source_pile_index]
		dest_pile = self.pile[dest_pile_index]

		# Verifica se la pila di destinazione è vuota e la carta spostata è un re
		if not dest_pile.carte and source_pile.carte[-1].valore_numerico == 13:
			return True

		# Verifica se la pila di destinazione non è vuota e la carta spostata è di un valore inferiore rispetto all'ultima carta della pila di destinazione
		if dest_pile.carte and source_pile.carte[-1].valore_numerico == dest_pile.carte[-1].valore_numerico - 1 and source_pile.carte[-1].seme != dest_pile.carte[-1].seme:
			return True

		return False

	def new_sposta_carte(self, source_row, source_col, dest_row, dest_col, cards):
		# Ottieni la pila di partenza e quella di destinazione
		source_pile = self.tavolo.pile[source_col]
		dest_pile = self.tavolo.pile[dest_col]

		# Verifica se lo spostamento delle carte è consentito
		if not self.verifica_spostamento_carte(source_pile, dest_pile, cards):
			return False

		# Rimuovi le carte dalla pila di partenza e aggiungile alla pila di destinazione
		carte_rimosse = source_pile.rimuovi_carte(source_row, source_row+len(cards)-1)
		dest_pile.aggiungi_carta(carte_rimosse)

		return True

	def sposta_carte(self, carte_da_spostare, pila_destinazione=None):
		"""
		Sposta le carte indicate nella pila di destinazione. Se la pila di destinazione
		non è specificata, cerca la prima pila disponibile e sposta le carte in quella.
		"""
		if pila_destinazione is not None:
			# Verifica se le carte possono essere spostate nella pila di destinazione
			if not self.check_legal_move(carte_da_spostare, pila_destinazione):
				return False
			
			# Sposta le carte nella pila di destinazione
			pila_destinazione.aggiungi_carte(carte_da_spostare)
			return True

		# Cerca la prima pila disponibile e sposta le carte in quella
		for pila in self.pile:
			if pila.is_empty() or pila.check_mossa_valida(carte_da_spostare):
				pila.aggiungi_carte(carte_da_spostare)
				return True
		return False

	def get_card_pile(self, card):
		"""
		Restituisce l'oggetto Pila a cui appartiene la carta passata come parametro
		"""
		for pila in self.pile:
			if card in pila.carte:
				return pila
		return None





#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
