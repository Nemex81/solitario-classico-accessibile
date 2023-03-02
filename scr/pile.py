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
# import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
# logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger.setLevel(logging.DEBUG)

class Pila:
	def __init__(self, id, tipo_pila):
		self.id = id
		self.nome = None
		self.tipo = tipo_pila
		self.carte = []

	def aggiungi_carta(self, carta):
		self.carte.append(carta)

	def rimuovi_carta(self, pos):
		carta_rimossa = self.carte.pop(pos)
		return carta_rimossa

	def rimuovi_carte(self, pos_iniziale, pos_finale):
		carte_rimosse = self.carte[pos_iniziale:pos_finale+1]
		self.carte = self.carte[:pos_iniziale] + self.carte[pos_finale+1:]
		return carte_rimosse

	def prendi_carte(self, num_carte):
		carte_pescate = []
		for i in range(num_carte):
			if len(self.carte) == 0:
				break

			carta = self.rimuovi_carta(-1)
			carte_pescate.insert(0, carta)
		return carte_pescate

	def get_carte(self):
		return self.carte

	def get_carta(self, pos):
		return self.carte[pos]

	def set_coperte(self, inizio, fine, coperte):
		for carta in self.carte[inizio:fine+1]:
			carta.coperta = coperte

	def numero_carte(self):
		return len(self.carte)

	def get_pile_type(self):
		""" Restituisce il tipo di pila """
		return self.tipo

	def get_card_index(self, row, col):
		"""
		Restituisce l'indice della carta alla posizione (row, col) nella pila.
		"""
		try:
			if col != self.id:
				return None
			return row

		except IndexError:
			return None



class PileSolitario:
	semi = ["cuori", "quadri", "picche", "fiori"]
	def __init__(self):
		self.mazzo = Mazzo()
		self.mazzo.reset()
		self.pile = []  # lista delle pile di gioco

	def crea_pile_gioco(self):
		# crea le sette pile base
		self.pile = [] # resettiamo tutte le pile di gioco a 0
		id = 0
		for i in range(7):
			pile_base = Pila(id, "base")
			pile_base.nome = f"pila {i+1}"
			self.pile.append(pile_base)
			id += 1

		# crea le quattro pile semi
		for i in range(4):
			pile_semi = Pila(id, "semi")
			pile_semi.nome = f"pila {self.semi[i]}"
			self.pile.append(pile_semi)
			id += 1

		# crea la pila di scarti
		pila_scarti = Pila(id, "scarti")
		pila_scarti.nome = "pila scarti"
		self.pile.append(pila_scarti)
		id += 1

		# crea la pila di mazzo riserve
		pila_mazzo_riserve = Pila(id, "mazzo_riserve")
		pila_mazzo_riserve.nome = "pila riserve"
		self.pile.append(pila_mazzo_riserve)

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

	def get_pile_name(self, col):
		pila = self.pile[col]
		return pila.nome

	def get_card_parent(self, card):
		""" Restituisce l'oggetto Pila a cui appartiene la carta passata come parametro """
		for pila in self.pile:
			if card in pila.carte:
				return pila

	def get_card_position(self, row, col):
		""" Restituisce la carta corrispondente alla colonna e riga specificate."""
		# Calcola l'indice della pila corrispondente alla colonna
		pila_index = col 

		# Se la colonna specificata è invalida, restituisci None
		if not 0 <= pila_index < len(self.pile):
			return None

		# Se la riga specificata è maggiore del numero di carte nella pila,
		# restituisci None
		if row >= len(self.pile[pila_index].carte):
			return None

		# Restituisci la carta corrispondente
		return self.pile[pila_index].carte[row]



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
