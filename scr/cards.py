"""
	file cards.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/cards.py

	Modulo per la gestione delle carte di gioco
"""

#lib
import logging, random
# moduli personali
import my_lib.myutyls as mu
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger.setLevel(logging.DEBUG)

class Carta:
	def __init__(self, valore, seme, coperta=True):
		self.valore = valore
		self.seme = seme
		self.id = None
		self.nome = None
		self.valore_numerico = None
		self.coperta = coperta

	def flip(self):
		self.coperta = not self.coperta

	def get_name(self):
		return self.nome

	def set_name(self):
		self.nome = f"{self.valore} di {self.seme}"



class Mazzo:
	SUITES = ["Cuori", "Quadri", "Fiori", "Picche"]
	VALUES = ["Asso", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Regina", "Re"]
	FIGURE_VALUES = {"Jack": 11, "Regina": 12, "Re": 13, "Asso" : 1}

	def __init__(self):
		self.cards = []  # lista delle carte nel mazzo
		#self.cards = self.crea_mazzo()

	def crea_mazzo(self):
		semi = self.SUITES
		valori = self.VALUES
		mazzo = []
		i = 0
		for seme in semi:
			for valore in valori:
				carta = Carta(valore, seme)
				carta.set_name()
				if valore in ["Jack", "Regina", "Re", "Asso"]:
					carta.valore_numerico = int(self.FIGURE_VALUES[valore])
				else:
					carta.valore_numerico = int(valore)

				carta.id = i
				mazzo.append(carta)
				i += 1

		self.cards = mazzo
		return mazzo

	def mischia_carte(self):
		random.shuffle(self.cards)

	def pesca(self):
		carta_pescata = self.cards.pop(0)
		return carta_pescata

	def get_carta(self, i):
		return self.cards[i]



#@@@# Start del modulo
if __name__ == "__main__":
	print("compilazione di %s completata." % __name__)

else:
	print("Carico: %s" % __name__)
