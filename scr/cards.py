"""
	file cards.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/cards.py

	Modulo per la gestione delle carte di gioco
"""

#lib
import random
from itertools import product
# moduli personali
from my_lib.dialog_box import DialogBox
import my_lib.myutyls as mu
#import pdb

class Carta:
	def __init__(self, valore, seme, coperta=True):
		self.valore = valore
		self.seme = seme
		self.nome = None
		self.coperta = coperta

	def flip(self):
		self.coperta = not self.coperta

	def get_nome(self):
		nome = f"{self.valore} di {self.seme}"
		return nome

class Mazzo:
	SUITES = ["Cuori", "Quadri", "Fiori", "Picche"]
	VALUES = ["Asso", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Regina", "Re"]

	def __init__(self):
		self.carte = self.crea_mazzo()

	def crea_mazzo(self):
		mazzo = [Carta(valore, seme) for valore, seme in product(Mazzo.VALUES, Mazzo.SUITES)]
		return mazzo

	def mischia_carte(self, mazzo):
		random.shuffle(mazzo)
		return mazzo

	def pesca(self):
		carta_pescata = self.carte.pop(0)
		return carta_pescata

	def get_carta(self, i):
		return self.carte[i]

	def get_carta(self, i):
		return self.carte[i]



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
