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
		if self.get_covered:
			return "carta coperta.  \n"

		details = f"nome: {self.get_name}.  \n"
		details += f"id: {self.get_id}.  \n"
		details += f"seme: {self.get_suit}.  \n"
		details += f"valore: {self.get_value}.  \n"
		details += f"colore: {self.get_color}.  \n"
		return details

	#@@# sezione metodi getter

	@property
	def get_name(self):
		""" restituisce il nome della carta """
		if self._nome is None:
			return "nessun nome"

		if self.get_covered:
			return "carta coperta"

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

		if self.get_covered:
			return "carta coperta"

		return self._seme

	@property
	def get_value(self):
		""" restituisce il valore della carta """
		if self._valore_numerico is None:
			return "nessun valore"

		if self.get_covered:
			return "carta coperta"

		return self._valore_numerico

	@property
	def get_color(self):
		""" restituisce il colore della carta """
		if self._colore is None:
			return "nessun colore"

		if self.get_covered:
			return "carta coperta"

		return self._colore

	@property
	def get_covered(self):
		""" restituisce il valore della copertura della carta """
		return self._coperta

	#@@# sezione metodi setter

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

	def set_cover(self):
		""" Copre la carta """
		self._coperta = True

	def set_uncover(self):
		""" Copre la carta """
		self._coperta = False

	@staticmethod
	def _determine_color(suit: Suit) -> Color:
		""" Determina il colore della carta in base al seme """
		if suit == Suit.CUORI.value  or suit == Suit.QUADRI.value or suit == Suit.COPPE.value or suit == Suit.DENARI.value:
			return Color.ROSSO.value

		return Color.BLU.value



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
		details = self.__str__()
		return details

	def flip(self):
		""" Ruota la carta usando i protometodi set_cover ed set_uncover"""
		if self.get_covered:
			self.set_uncover()
		else:
			self.set_cover()



#@@@# Start del modulo
if __name__ == "__main__":
	print("compilazione di %s completata." % __name__)

else:
	print("Carico: %s" % __name__)
