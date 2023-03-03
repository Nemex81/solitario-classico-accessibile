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
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Carta:
	def __init__(self, valore, seme, coperta=True):
		self.valore = valore
		self.seme = seme
		self.colore = None
		self.id = None
		self.nome = None
		self.valore_numerico = None
		self.coperta = coperta

	def flip(self):
		self.coperta = not self.coperta

	def get_name(self):
		if self.nome is None:
			return "nessuna nome"

		if self.coperta:
			return "carta coperta"

		return self.nome

	def get_suit(self):
		if self.seme is None:
			return "nessuna seme"

		if self.coperta:
			return "carta coperta"

		return self.seme

	def get_value(self):
		if self.valore_numerico is None:
			return "nessun valore"

		if self.coperta:
			return "carta coperta"

		return self.valore_numerico

	def get_color(self):
		if self.colore is None:
			return "nessuna colore"

		if self.coperta:
			return "carta coperta"

		return self.colore

	def get_info_card(self):
		nome = self.get_name()
		seme = self.get_suit()
		valore = self.get_value()
		colore = self.get_color()
		details = f"nome: {nome}\n"
		details += f"seme: {seme}\n"
		details += f"valore: {valore}\n"
		details += f"colore: {colore}\n"
		return details

	def set_name(self):
		self.nome = f"{self.valore} di {self.seme}"

	def set_color(self):
		seme = self.seme
		colore = ""
		if seme == "cuori" or seme == "quadri":
			colore = "rosso"

		elif seme == "picche" or seme == "fiori":
			colore = "blu"

		else:
			colore = "indefinito"

		self.colore = colore


class Mazzo:
	SUITES = ["cuori", "quadri", "fiori", "picche"]
	VALUES = ["Asso", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Regina", "Re"]
	FIGURE_VALUES = {"Jack": 11, "Regina": 12, "Re": 13, "Asso" : 1}

	def __init__(self):
		self.cards = []  # lista delle carte nel mazzo
		#self.cards = self.crea()

	def crea(self):
		semi = self.SUITES
		valori = self.VALUES
		mazzo = []
		i = 0
		for seme in semi:
			for valore in valori:
				carta = Carta(valore, seme)
				carta.set_name()
				carta.set_color()
				if valore in ["Jack", "Regina", "Re", "Asso"]:
					carta.valore_numerico = int(self.FIGURE_VALUES[valore])
				else:
					carta.valore_numerico = int(valore)

				carta.id = i
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
		"""Rimuove n carte dal mazzo e le restituisce come lista."""
		carte_rimosse = self.cards[:n]
		self.cards = self.cards[n:]
		return carte_rimosse

	def pesca(self):
		carta_pescata = self.cards.pop(0)
		return carta_pescata

	def get_carta(self, i):
		return self.cards[i]

	def get_numero_carte(self):
		return len(self.cards)

	def mischia(self):
		random.shuffle(self.cards)

	def reset(self):
		self.cards = []
		self.crea()
		self.mischia()



#@@@# Start del modulo
if __name__ == "__main__":
	print("compilazione di %s completata." % __name__)

else:
	print("Carico: %s" % __name__)
