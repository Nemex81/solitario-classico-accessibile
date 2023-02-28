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
# import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
# logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger.setLevel(logging.DEBUG)

class Pila:
	def __init__(self, tipo_pila):
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
		"""
		Restituisce il tipo di pila, ovvero:
		- "base": per le pile di gioco principali
		- "riserva": per la pila di mazzo riserve
		- "semi": per le pile di semi
		"""
		if len(self.carte) == 0:
			return "riserva"
		elif self.carte[-1].valore == 1:
			return "semi"
		else:
			return "base"


class Tavolo:
	semi = ["cuori", "quadri", "picche", "fiori"]
	def __init__(self):
		self.pile = []  # lista di pile di gioco

	def crea_pile_gioco(self):
		# crea le sette pile base
		self.pile = [] # resettiamo tutte le pile di gioco a 0
		for i in range(7):
			pile_base = Pila("base")
			pile_base.nome = f"pila {i+1}"
			self.pile.append(pile_base)

		# crea le quattro pile semi
		for i in range(4):
			pile_semi = Pila("semi")
			pile_semi.nome = f"pila {self.semi[i]}"
			self.pile.append(pile_semi)

		# crea la pila di scarti
		pila_scarti = Pila("scarti")
		pila_scarti.nome = "pila scarti"
		self.pile.append(pila_scarti)

		# crea la pila di mazzo riserve
		pila_mazzo_riserve = Pila("mazzo_riserve")
		pila_mazzo_riserve.nome = "pila riserve"
		self.pile.append(pila_mazzo_riserve)

	def get_pile_name(self, col):
		pila = self.pile[col]
		return pila.nome

	def get_card(self, row, col):
		"""Restituisce la carta corrispondente alla colonna e riga specificate."""
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
