"""
	file decks.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/decks.py

	modulo per la gestione dei mazzi di carte
"""

#lib
import logging, random
# moduli personali
import my_lib.myutyls as mu
from my_lib.myglob import *
from scr.cards import Card
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class ProtoDeck:
	""" 
	Modello base per la gestione dei mazzi di carte 

	comprende anche la possibilità di istanziare diversi tipi di mazzi
	come le carte francesi o le carte napoletane
	"""

	# costanti
	SUITES = []
	VALUES = []
	FIGURE_VALUES = {}

	def __init__(self):
		self.cards = []  # lista delle carte nel mazzo
		self.tipo = None  # tipo di mazzo

	def get_suits(self):
		""" restituisce la lista dei semi del mazzo """
		return self.SUITES

	def crea(self):
		pass

	def inserisci_carte(self, carte_aggiuntive):
		""" 
			permette di inserire un altro set di carte  nel mazzo 
			da utilizzare per altri tip di solitario.
		"""
		for carta in carte_aggiuntive:
			self.cards.append(carta)

	def rimuovi_carte(self, n):
		""" Rimuove n carte dal mazzo e le restituisce come lista """
		carte_rimosse = self.cards[:n]
		self.cards = self.cards[n:]
		return carte_rimosse

	def pesca(self):
		""" pesca una carta dal mazzo """
		carta_pescata = self.cards.pop(0)
		return carta_pescata

	def get_carta(self, i):
		""" restituisce la carta in posizione i se esistente """
		if i < len(self.cards):
			return self.cards[i]

	def get_len(self):
		""" restituisce il numero di carte nel mazzo """
		return len(self.cards)

	def get_type(self):
		""" restituisce il tipo di mazzo """
		return self.tipo

	@staticmethod
	def get_type_suits(self):
		""" restituisce la lista dei semi del mazzo """
		return self.SUITES

	def mischia(self):
		""" mischia le carte nel mazzo """
		random.shuffle(self.cards)

	def is_french_deck(self):
		""" restituisce true se il mazzo è di carte francesi """
		if self.SUITES == ["cuori", "quadri", "fiori", "picche"]:
			return True

		return False

	def is_neapolitan_deck(self):
		""" restituisce true se il mazzo è di carte napoletane """
		if self.SUITES == ["bastoni", "coppe", "denari", "spade"]:
			return True

		return False

	def is_empty_dek(self):
		""" se il mazzo è vuoto restituiamo true """
		if len(self.cards) == 0:
			return True

	def is_king(self, card):
		"""Verifica se la carta è un Re indipendentemente dal tipo di mazzo.
		
		Funziona confrontando il valore numerico con il valore del Re per questo mazzo.
		
		Returns:
			bool: True se la carta è un Re, False altrimenti
		"""
		# Il Re è sempre nell'array FIGURE_VALUES con chiave "Re"
		king_value = self.FIGURE_VALUES.get("Re")
		if king_value is None:
			# Se il mazzo non ha un Re definito, nessuna carta può essere un Re
			return False
		return card.get_value == king_value

	def reset(self):
		""" Resetta il mazzo """
		self.cards = []
		self.crea()
		self.mischia()


class NeapolitanDeck(ProtoDeck):
	""" Classe per la gestione del mazzo napoletano """

	# costanti
	SUITES = ["bastoni", "coppe", "denari", "spade"]
	VALUES = ["Asso", "2", "3", "4", "5", "6", "7", "Regina", "Cavallo", "Re"]
	FIGURE_VALUES = {"Regina": 8, "Cavallo": 9, "Re": 10, "Asso": 1}

	def __init__(self):
		self.tipo = "carte napoletane"
		self.cards = []
		self.reset()

	def get_total_cards(self):
		""" Restituisce il numero totale di carte nel mazzo completo """
		return len(self.SUITES) * len(self.VALUES)  # 4 * 10 = 40

	def crea(self):
		""" Crea il mazzo di carte """
		semi = self.SUITES
		valori = self.VALUES
		mazzo = []
		i = 0
		for seme in semi:
			for valore in valori:
				carta = Card(valore, seme)
				carta.set_name(f"{valore} di {seme}")
				if valore in ["Regina", "Cavallo", "Re", "Asso"]:
					carta.set_int_value(int(self.FIGURE_VALUES[valore]))
				else:
					carta.set_int_value(int(valore))

				carta.set_id(i)
				carta.set_color(carta._determine_color(seme))
				mazzo.append(carta)
				i += 1

		self.cards = mazzo
		return mazzo


class FrenchDeck(ProtoDeck):
	""" Classe per la gestione del mazzo francese """

	# costanti
	SUITES = ["cuori", "quadri", "fiori", "picche"]
	VALUES = ["Asso", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Regina", "Re"]
	FIGURE_VALUES = {"Jack": 11, "Regina": 12, "Re": 13, "Asso" : 1}

	def __init__(self):
		self.tipo = "carte francesi"
		self.cards = []  # lista delle carte nel mazzo
		self.reset()

	def get_total_cards(self):
		""" Restituisce il numero totale di carte nel mazzo completo """
		return len(self.SUITES) * len(self.VALUES)  # 4 * 13 = 52

	def crea(self):
		""" Crea il mazzo di carte """
		semi = self.SUITES
		valori = self.VALUES
		mazzo = []
		i = 0
		for seme in semi:
			for valore in valori:
				carta = Card(valore, seme)
				carta.set_name(f"{valore} di {seme}")
				if valore in ["Jack", "Regina", "Re", "Asso"]:
					carta.set_int_value(int(self.FIGURE_VALUES[valore]))
				else:
					carta.set_int_value(int(valore))

				carta.set_id(i)
				carta.set_color(carta._determine_color(seme))
				mazzo.append(carta)
				i += 1

		self.cards = mazzo
		return mazzo




#@@@# Start del modulo
if __name__ == "__main__":
	print("compilazione di %s completata." % __name__)

else:
	print("Carico: %s" % __name__)
