"""
	file cards.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/cards.py

	Modulo per la gestione delle carte di gioco
"""

#lib
import logging, random
# moduli personali
import my_lib.myutyls as mu
from my_lib.myglob import *
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class ProtoCard:
	"""Modello base per la gestione delle carte di gioco """
	"""Classe base per la gestione delle carte di gioco """
	def __init__(self):
		self._nome = None
		self._id = None
		self._seme = None
		self._colore = None
		self._valore = None
		self._valore_numerico = None
		self._coperta = None

	def __str__(self):
		""" restituisce una stringa con le informazioni della carta"""
		details = f"nome: {self.get_name}\n"
		details += f"id: {self.get_id}\n"
		details += f"seme: {self.get_suit}\n"
		details += f"valore: {self.get_value}\n"
		details += f"colore: {self.get_color}\n"
		details += f"coperta: {self._coperta}\n"
		return details

	#@@# sezione metodi getter

	@property
	def get_name(self):
		""" restituisce il nome della carta """
		if self._nome is None:
			return "nessun nome"

		if self._seme is None:
			return "nessuna seme"

		return self._nome

	@property
	def get_id(self):
		""" restituisce l'id della carta """
		if self._seme is None:
			return "nessuna seme"

		return self._id

	@property
	def get_suit(self):
		""" restituisce il seme della carta """
		if self._seme is None:
			return "nessuna seme"

		if self.get_cover:
			return "carta coperta"

		return self._seme

	@property
	def get_value(self):
		""" restituisce il valore della carta """
		if self._valore_numerico is None:
			return "nessun valore"

		if self.get_cover:
			return "carta coperta"

		return self._valore_numerico

	@property
	def get_color(self):
		""" restituisce il colore della carta """
		if self._colore is None:
			return "nessun colore"

		if self.get_cover:
			return "carta coperta"

		return self._colore

	@property
	def get_cover(self):
		""" restituisce il valore della copertura della carta """
		return self._coperta

	#@@# sezione metodi setter

	def set_cover(self):
		""" Copre la carta """
		self._coperta = True

	def set_uncover(self):
		""" Copre la carta """
		self._coperta = False



class Card(ProtoCard):
	""" Classe per la gestione delle carte di gioco """
	def __init__(self, valore, seme, coperta=True):
		super().__init__()
		self._valore = valore
		self._seme = seme
		self._coperta = coperta


	@property
	def get_info_card(self):
		""" restituisce una stringa con le informazioni della carta """
		if self.coperta:
			return "Carta coperta  \n"

		details = f"nome: {self.get_name}.  \n"
		details += f"id: {self.get_id}"
		details += f"seme: {self.get_suit}.  \n"
		details += f"valore: {self.get_value}.  \n"
		details += f"colore: {self.get_color}.  \n"
		return details

	def set_name(self, name):
		""" Imposta il nome della carta """
		self._nome = name

	def set_id(self, id):
		""" Imposta l'id della carta """
		self._id = id

	def set_suit(self, suit):
		""" Imposta il seme della carta """
		self._seme = suit

	def set_str_value(self, value):
		""" Imposta il valore della carta """
		self._valore = value

	def set_int_value(self, value):
		""" Imposta il valore numerico della carta """
		self._valore_numerico = value

	def set_color(self, color):
		""" Imposta il colore della carta """
		self._colore = color

	@staticmethod
	def _determine_color(suit: Suit) -> Color:
		""" Determina il colore della carta in base al seme """
		if suit == Suit.CUORI.value  or suit == Suit.QUADRI.value:
			return Color.ROSSO.value
		
		return Color.BLU.value

	def flip(self):
		""" Ruota la carta usando i protometodi cover ed uncover"""
		if self.coperta:
			self.set_uncover()
		else:
			self.set_cover()



class Mazzo:
	""" Classe per la gestione del mazzo di carte """
	SUITES = ["cuori", "quadri", "fiori", "picche"]
	VALUES = ["Asso", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Regina", "Re"]
	FIGURE_VALUES = {"Jack": 11, "Regina": 12, "Re": 13, "Asso" : 1}

	def __init__(self):
		self.cards = []  # lista delle carte nel mazzo
		self.reset()

	def crea(self):
		""" Crea il mazzo di carte """
		semi = self.SUITES
		valori = self.VALUES
		mazzo = []
		i = 0
		for seme in semi:
			for valore in valori:
				carta = Card(valore, seme)
				#carta._nome = f"{valore} di {seme}"
				carta.set_name(f"{valore} di {seme}")
				if valore in ["Jack", "Regina", "Re", "Asso"]:
					#carta._valore_numerico = int(self.FIGURE_VALUES[valore])
					carta.set_int_value(int(self.FIGURE_VALUES[valore]))
				else:
					#carta._valore_numerico = int(valore)
					valore = int(valore)
					carta.set_int_value(valore)

				#carta._id = i
				carta.set_id(i)
				carta._colore = carta._determine_color(seme)
				mazzo.append(carta)
				i += 1

		self.cards = mazzo
		return mazzo

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

	def get_numero_carte(self):
		""" restituisce il numero di carte nel mazzo """
		return len(self.cards)

	def mischia(self):
		""" mischia le carte nel mazzo """
		random.shuffle(self.cards)

	def is_empty_dek(self):
		""" se il mazzo è vuoto restituiamo true """
		if len(self.cards) == 0:
			return True

	def reset(self):
		""" Resetta il mazzo """
		self.cards = []
		self.crea()
		self.mischia()



#@@@# Start del modulo
if __name__ == "__main__":
	print("compilazione di %s completata." % __name__)

else:
	print("Carico: %s" % __name__)
