"""
	file pile.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/pile.py

	Modulo per la creazione e gestione delle pile di gioco
"""

# lib
import logging, random
# moduli personali
from my_lib.myglob import *
import my_lib.myutyls as mu
# import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.setLevel(logging.DEBUG)

class Pila:
	def __init__(self, id, tipo_pila):
		self.id = id
		self.nome = None
		self.tipo = tipo_pila
		self.carte = []

	#@@# sezione metodi getter

	def get_len(self):
		return len(self.carte)

	def get_carte(self):
		return self.carte

	def get_top_card(self):
		if len(self.carte) == 0:
			return None

		return self.carte[-1]

	def get_carta(self, pos):
		return self.carte[pos]

	def get_card_index(self, card):
		""" Restituisce l'indice della carta se presente. """
		if card in self.carte:
			return self.carte.index(card)

	def get_last_card_index(self):
		""" Restituisce l'indice della carta scoperta in ultima posizione della pila, se la pila non è vuota. """
		if len(self.carte) == 0:
			return None

		for i in range(len(self.carte)-1, -1, -1):
			if not self.carte[i].get_covered:
				return i

	def get_pile_type(self):
		""" Restituisce il tipo di pila """
		return self.tipo

	def get_pile_suit(self):
		if self.seme is None:
			return "nessuno"

		return self.seme

	def get_pile_info(self):
		info_pila = f"nome: {self.nome}.  \n"
		info_pila += f"id: {self.id}.  \n"
		info_pila += f"tipo: {self.get_pile_type()}.  \n"
		info_pila += f"seme: {self.get_pile_suit()}.  \n"
		return info_pila

	#@@# sezione metodi setter

	def set_pile_id(self, id):
		self.id = id

	def set_pile_name(self, nome):
		self.nome = nome

	def set_pile_type(self, tipo):
		self.tipo = tipo

	def set_pile_cards(self, carte):
		self.carte = carte

	def set_all_cover(self):
		""" Imposta tutte le carte della pila come coperte. """
		for carta in self.carte:
			carta.set_cover()

	def set_all_uncover(self):
		""" Imposta tutte le carte della pila come scoperte. """
		for carta in self.carte:
			carta.set_uncover()

	def set_uncover_top_card(self):
		if len(self.carte) == 0:
			return

		self.carte[-1].set_uncover()

	def set_coperte(self, inizio, fine, coperte):
		""" Imposta le carte come coperte o scoperte in un range da passargli """
		for carta in self.carte[inizio:fine+1]:
			carta.coperta = coperte

	#@@# sezione convalide

	def is_empty_pile(self):
		max = len(self.carte)
		if max >= 1:
			return False

		return True

	def is_pila_base(self):
		pass

	def is_pila_seme(self):
		pass

	def is_pila_scarti(self):
		pass

	def is_pila_riserve(self):
		pass

	#@@# sezione metodi di gestione

	def aggiungi_carta(self, carta):
		""" Aggiunge una carta alla pila. """
		self.carte.append(carta)

	def rimuovi_carta(self, pos):
		""" Rimuove una carta dalla pila. """
		carta_rimossa = self.carte.pop(pos)
		return carta_rimossa

	def rimuovi_carte(self, pos_iniziale, pos_finale):
		""" Rimuove le carte dalla pila all'interno del range passato """
		carte_rimosse = self.carte[pos_iniziale:pos_finale+1]
		self.carte = self.carte[:pos_iniziale] + self.carte[pos_finale+1:]
		return carte_rimosse

	def prendi_carte(self, num_carte):
		""" Prende le carte dalla pila e le restituisce in ordine inverso. """
		carte_pescate = []
		for i in range(num_carte):
			if len(self.carte) == 0:
				break

			carta = self.rimuovi_carta(-1)
			carte_pescate.insert(0, carta)
		return carte_pescate


class PilaScarti(Pila):
	""" Gestisce la pila degli scarti """
	def __init__(self, id):
		super().__init__(id, "scarti")
		self.set_pile_name("Pila scarti")

	def is_pila_scarti(self):
		return True


class PilaRiserve(Pila):
	""" Gestisce la pila delle riserve """
	def __init__(self, id):
		super().__init__(id, "riserve")
		self.set_pile_name("pila riserve")

	def is_pila_riserve(self):
		return True


class PilaSemi(Pila):
	""" Gestisce la pila dei semi """
	def __init__(self, id, name):
		super().__init__(id, "semi")
		self.seme = None
		self.set_pile_name(f"Pila {name}")
		self.set_pile_suit(name)

	def set_pile_suit(self, seme):
		self.seme = seme

	def is_pila_seme(self):
		return True


class PilaBase(Pila):
	""" Gestisce la pila delle carte base """
	def __init__(self, id):
		super().__init__(id, "base")
		self.set_pile_name(f"pila {id+1}")

	def is_pila_base(self):
		return True



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
