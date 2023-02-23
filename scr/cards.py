"""
	file cards.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/cards.py

	Modulo per la gestione delle carte di gioco
"""

#lib
import random, time
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


class Mazzo:
	SUITES = ["Cuori", "Quadri", "Fiori", "Picche"]
	VALUES = ["Asso", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Regina", "Re"]

	def __init__(self):
		self.mazzo = [Carta(valore, seme) for seme in self.SUITES for valore in self.VALUES]

	def crea_mazzo(self):
		random.shuffle(self.mazzo)
		return self.mazzo

	def get_card_name(self, card_id):
		"""
		Restituisce il nome della carta a partire dall'id.
		"""
		card_value = card_id % 13
		card_suite = card_id // 13
		name = Mazzo.VALUES[card_value]
		return f"{name} di {Mazzo.SUITES[card_suite]}"



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
