"""
	parte 1
	nome file: solitario_accessibile.py
	Modulo per l'implementazione del gioco del solitario accessibile
"""

# lib
import os
import sys
import time
import random

# moduli personali
from my_lib.dialog_box import DialogBox
import my_lib.myutyls as mu
from scr.cards import Carta, Mazzo

# costanti
M_TAV = 7  # numero di tavoli nel gioco
M_RIS = 4  # numero di riserve nel gioco
M_CRX = 13  # numero massimo di carte per tavolo
M_MSG = 40  # lunghezza massima messaggio in console
M_AZZ = M_TAV * M_CRX + M_RIS * 13 + 1  # numero di carte nel mazzo
M_SEMI = ["Quadri", "Fiori", "Cuori", "Picche"]
M_VALORI = ["Asso", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Regina", "Re"]
M_SX = 50  # posizione x del tavolo da gioco
M_SY = 50  # posizione y del tavolo da gioco
M_DX = 125  # spostamento orizzontale tra le carte sul tavolo
M_DY = 25  # spostamento verticale tra le carte sul tavolo

# var globali
debug_mode = False
tavolo = [[] for i in range(M_TAV)]
riserva = [[] for i in range(M_RIS)]
mazzo = []
dialog_box = DialogBox()

#@@@# inizio parte 2
# costanti
M_TITOLO = "Solitario Accessibile"

#@@# end parte 2


#@@# inizio parte 3
class EngineSolitario:
    def __init__(self):
        self.primo_giro = True
        self.situazione_attuale = []
		self._scarti = []
		self._pile = [[] for _ in range(7)]
		self._inizio_pile = [1, 2, 3, 4, 5, 6, 7]
		self._fine_pile = [7, 7, 7, 7, 7, 7, 6]


    def crea_mazzo(self):
        random.shuffle(mazzo)

    def crea_gioco(self):
        global tavolo, riserva, mazzo
        mazzo = Mazzo().mazzo
        self.crea_mazzo()
        tavolo = [[] for i in range(M_TAV)]
        riserva = [[] for i in range(M_RIS)]
        for t in range(M_TAV):
            for i in range(t+1):
                carta = mazzo.pop(0)
                if i == t:
                    carta.aperta = True
                tavolo[t].append(carta)
        for r in range(M_RIS):
            riserva[r] = [mazzo.pop(0)]

	def distribuisci_carte(self):
		"""Distribuisce le carte inizialmente sul tavolo da gioco."""
		# Crea il mazzo di 52 carte e lo mischia
		mazzo = Mazzo()
		mazzo.mischia()

		# Distribuisce le carte sul tavolo da gioco
		pila1 = []
		pila2 = []
		pila3 = []
		pila4 = []
		pila5 = []
		pila6 = []
		pila7 = []

		for i in range(7):
			for j in range(i):
				mazzo.estrai_carta()
			if i == 0:
				pila1.append(mazzo.estrai_carta())
			else:
				pila2.append(mazzo.estrai_carta())
				pila3.append(mazzo.estrai_carta())
				pila4.append(mazzo.estrai_carta())
				pila5.append(mazzo.estrai_carta())
				pila6.append(mazzo.estrai_carta())
				pila7.append(mazzo.estrai_carta())

		# Imposta le carte sul tavolo da gioco
		self.tavolo_da_gioco = [
			pila1,
			pila2,
			pila3,
			pila4,
			pila5,
			pila6,
			pila7,
			[],
			[],
			[],
			[],
			[],
			[],
			[]
		]

		# Aggiorna il conteggio delle carte
		self.numero_carte_mazzo = len(mazzo)
		self.numero_carte_scarti = 0

	def muovi_carte(self, from_colonna, to_colonna, quanti):
		"""
		Muove n carte dalla colonna from_colonna alla colonna to_colonna.
		"""
		if from_colonna == to_colonna:
			return False
		if not self.colonne[from_colonna]:
			return False
		if not quanti:
			quanti = len(self.colonne[from_colonna])
		if quanti > len(self.colonne[from_colonna]):
			return False
		if to_colonna == 8:
			if not self.fondazione[to_colonna]:
				if self.colonne[from_colonna][-quanti].valore == "Re":
					for carta in self.colonne[from_colonna][-quanti:]:
						self.fondazione[to_colonna].append(carta)
					del self.colonne[from_colonna][-quanti:]
					return True
				else:
					return False
			else:
				if self.colonne[from_colonna][-quanti].seme == self.fondazione[to_colonna][-1].seme and \
				   self.colonne[from_colonna][-quanti].valore == self.fondazione[to_colonna][-1].valore + 1:
					for carta in self.colonne[from_colonna][-quanti:]:
						self.fondazione[to_colonna].append(carta)
					del self.colonne[from_colonna][-quanti:]
					return True
				else:
					return False
		elif to_colonna in range(4):
			if not self.fondazione[to_colonna]:
				if self.colonne[from_colonna][-quanti].valore == "Asso":
					for carta in self.colonne[from_colonna][-quanti:]:
						self.fondazione[to_colonna].append(carta)
					del self.colonne[from_colonna][-quanti:]
					return True
				else:
					return False
			else:
				if self.colonne[from_colonna][-quanti].seme != self.fondazione[to_colonna][-1].seme or \
				   self.colonne[from_colonna][-quanti].valore != self.fondazione[to_colonna][-1].valore + 1:
					return False
				else:
					for carta in self.colonne[from_colonna][-quanti:]:
						self.fondazione[to_colonna].append(carta)
					del self.colonne[from_colonna][-quanti:]
					return True
		elif to_colonna in range(4,8):
			if not self.colonne[to_colonna]:
				if self.colonne[from_colonna][-quanti].valore == "Re":
					for carta in self.colonne[from_colonna][-quanti:]:
						self.colonne[to_colonna].append(carta)
					del self.colonne[from_colonna][-quanti:]
					return True
				else:
					return False
			else:
				if self.colonne[from_colonna][-quanti].colore == self.colonne[to_colonna][-1].colore or \
				   self.colonne[from_colonna][-quanti].valore != self.colonne[to_colonna][-1].valore - 1:
					return False
				else:
					for carta in self.colonne[from_colonna][-quanti:]:
						self.colonne[to_colonna].append(carta)
					del self.colonne[from_colonna][-quanti:]
					return True
		else:
			return False

	def muovi_foundation(self, pila_gioco):
		"""Muove una carta dalla pila di gioco alla pila semi corrispondente."""
		if not pila_gioco:
			raise ValueError("La pila di gioco selezionata è vuota.")

		carta = pila_gioco[-1]
		semi_carta = carta.get_seme()
		valore_carta = carta.get_valore()

		for pila_semi in self._semi:
			if pila_semi[-1].get_seme() == semi_carta:
				if pila_semi[-1].get_valore() == valore_carta - 1:
					pila_semi.append(carta)
					pila_gioco.pop()
					self.controlla_vittoria()
					return True

		raise ValueError("Non è possibile muovere la carta selezionata in nessuna pila semi.")

	def muovi_su_foundation(self, pila_gioco, pila_semi):
		"""Muove una carta specifica dalla pila di gioco ad una pila semi specifica."""
		if not pila_gioco:
			raise ValueError("La pila di gioco selezionata è vuota.")

		carta = pila_gioco[-1]
		semi_carta = carta.get_seme()
		valore_carta = carta.get_valore()

		if pila_semi[-1].get_seme() == semi_carta:
			if pila_semi[-1].get_valore() == valore_carta - 1:
				pila_semi.append(carta)
				pila_gioco.pop()
				self.controlla_vittoria()
				return True

		raise ValueError("Non è possibile muovere la carta selezionata nella pila semi specificata.")

	def muovi_carta_foundation(self, carta):
		"""
		Muove una carta dalle pile di gioco alle fondazioni, se possibile.
		Restituisce True se la mossa è stata effettuata, False altrimenti.
		"""
		n_carta = carta.get_numero()
		seme_carta = carta.get_seme()
		if n_carta != 1 and self._fondazioni[seme_carta][-1].get_numero() != n_carta - 1:
			return False
		else:
			self._fondazioni[seme_carta].append(carta)
			self._pile[carta.get_pila()].remove(carta)
			return True

	def muovi_su_pile_gioco(self, n_carta, n_pila):
		"""Muove la carta selezionata dalla pila degli scarti ad una pila di gioco"""
		carta = self._scarti[-n_carta]
		if len(self._pile[n_pila]) == 0:
			if carta.valore == 13:
				self._pile[n_pila].append(self._scarti.pop(-n_carta))
			else:
				raise ValueError("La carta selezionata non può essere mossa in questa pila di gioco.")
		else:
			ultima_carta_pila = self._pile[n_pila][-1]
			if ultima_carta_pila.colore == carta.colore:
				raise ValueError("La carta selezionata non può essere mossa in questa pila di gioco.")
			elif ultima_carta_pila.valore - 1 != carta.valore:
				raise ValueError("La carta selezionata non può essere mossa in questa pila di gioco.")
			else:
				self._pile[n_pila].append(self._scarti.pop(-n_carta))

	def muovi_su_foundation(self, n_carta):
		"""Muove la carta selezionata dalla pila degli scarti ad una pila semi"""
		carta = self._scarti[-n_carta]
		semi = {'cuori': 0, 'quadri': 1, 'fiori': 2, 'picche': 3}
		if carta.valore == 1:
			if carta.seme == 'cuori':
				self._semi[0].append(self._scarti.pop(-n_carta))
			elif carta.seme == 'quadri':
				self._semi[1].append(self._scarti.pop(-n_carta))
			elif carta.seme == 'fiori':
				self._semi[2].append(self._scarti.pop(-n_carta))
			elif carta.seme == 'picche':
				self._semi[3].append(self._scarti.pop(-n_carta))
		else:
			semi_carta = semi[carta.seme]
			if len(self._semi[semi_carta]) == carta.valore - 1:
				self._semi[semi_carta].append(self._scarti.pop(-n_carta))
			else:
				raise ValueError("La carta selezionata non può essere mossa in questa pila semi.")

	def muovi_su_foundation(self, pila_gioco):
		carta = self._pile[pila_gioco][-1]
		seme = carta.seme
		if carta.valore == 1:
			self._foundations[seme].append(carta)
			self._pile[pila_gioco].pop()
			return True
		if self._foundations[seme] and self._foundations[seme][-1].valore == carta.valore - 1:
			self._foundations[seme].append(carta)
			self._pile[pila_gioco].pop()
			return True
		return False

	def muovi_su_foundation_tutte(self):
		mosse_fatte = False
		for pila_gioco in range(7):
			while self.muovi_su_foundation(pila_gioco):
				mosse_fatte = True
		return mosse_fatte

	def muovi_da_semi_a_pile(self, indice_semi, indice_pila):
		"""
		Muove la carta più in alto dalla pile semi di indice 'indice_semi' alla pile di gioco di indice 'indice_pila'
		se la carta può essere messa nella pile di gioco.
		"""
		semi = self._semi
		pile = self._pile

		# Verifica che la pila semi e la pila di gioco siano valide
		if indice_semi < 0 or indice_semi > 3:
			raise ValueError("Indice semi non valido")
		if indice_pila < 0 or indice_pila > 6:
			raise ValueError("Indice pila non valido")

		# Verifica che ci sia almeno una carta nella pila semi
		if len(semi[indice_semi]) == 0:
			raise ValueError("Pila semi vuota")

		# Verifica se la carta può essere messa nella pila di gioco
		carta = semi[indice_semi][-1]
		pila_destinazione = pile[indice_pila]
		if not self.posso_muovere_carta(carta, pila_destinazione):
			raise ValueError("Impossibile muovere la carta in questa pila di gioco")

		# Muove la carta dalla pila semi alla pila di gioco
		carta = semi[indice_semi].pop()
		pila_destinazione.append(carta)

	def muovi_tutte_da_semi_a_pile(self):
		"""
		Muove tutte le carte dalle pile semi alle pile di gioco
		"""
		semi = self._semi

		# Muove le carte dalle pile semi alle pile di gioco
		for i in range(4):
			while len(semi[i]) > 0:
				for j in range(7):
					try:
						self.muovi_da_semi_a_pile(i, j)
						break
					except ValueError:
						pass


	def controlla_vittoria(self):
		for foundation in self._foundations:
			if len(foundation) < 13:
				return False

		return True

