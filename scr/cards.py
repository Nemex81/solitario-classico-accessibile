"""
	Modulo per la gestione delle carte di gioco
"""

#lib
import random, time
# moduli personali
from my_lib.dialog_box import DialogBox
import my_lib.myutyls as mu
#import pdb

class Carta:
	def __init__(self, valore, seme):
		self.valore = valore
		self.seme = seme

class Mazzo:
	def __init__(self):
		self.semi = ["Cuori", "Quadri", "Fiori", "Picche"]
		self.valori = ["Asso", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Regina", "Re"]
		self.mazzo = [Carta(valore, seme) for seme in self.semi for valore in self.valori]

	def crea_mazzo(self):
		random.shuffle(self.mazzo)
