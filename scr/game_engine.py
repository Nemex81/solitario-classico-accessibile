"""
	file game_engine.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/game_engine.py

	Modulo per l'implementazione del gioco del solitario accessibile
"""

# lib
import os
import sys
import time
import random

# moduli personali
from my_lib.dialog_box import DialogBox
from my_lib.myglob import *
import my_lib.myutyls as mu
from scr.cards import Carta, Mazzo
from scr.pile import PileGioco

class EngineSolitario:
	def __init__(self):
		self.mazzo = Mazzo()
		self.cards = []
		##self.mazzo = Mazzo()
		super().__init__()
		self.primo_giro = True
		self.valid_positions = [(i, j) for i in range(7) for j in range(20)]
		self.situazione_attuale = []
		self._scarti = []
		self._pile = [[] for _ in range(7)]
		self._inizio_pile = [1, 2, 3, 4, 5, 6, 7]
		self._fine_pile = [7, 7, 7, 7, 7, 7, 6]
		self.tableau = [[] for _ in range(7)]
		self.foundations = [[] for _ in range(4)]
		self.waste_pile = []
		self.stock_pile = []
		self.pile = PileGioco()

	def distribuisci_carte(self):
		# Distribuisce le carte sul tableau
		n_carte = 0
		for i in range(7):
			for j in range(i+1):
				carta = self.mazzo.get_carta(n_carte)
				if j == i:
					self.tableau[j].append(carta)
				else:
					self.tableau[j].append(None)
				n_carte += 1

		# Mette le rimanenti carte nel stock pile
		self.stock_pile = [self.mazzo.get_carta(i) for i in range(n_carte, len(self.mazzo.carte))]

	def crea_gioco(self):
		self.cards = self.mazzo.crea_mazzo()
		self.mazzo.mischia_carte(self.cards)
		self.distribuisci_carte()
		self.pile.reset()
		self.pile.distribuisci_carte()

	def get_card(self, row, col):
		card = self.tableau[row][col]
		return card

	def move_card(self, card, src_row, src_col, dest_row, dest_col):
		self.tableau[dest_row].append(card)
		self.tableau[src_row].pop(src_col)
		self.selected_card = None
		self.update_game_state()

	def get_pile_name(self, row, col):
		pile_name = ""
		if col < 7:
			pile_name = f"Tableau colonna {col + 1}"

		elif col < 11:
			pile_name = f"Foundations {col - 6}"

		else:
			pile_name = "Waste pile"

		return pile_name

	def get_top_card(self, pile):
		if not self.is_empty_pile(pile):
			return pile[-1]
		else:
			return None

	def get_card_at_position(self, row, col):
		"""
		Ritorna la carta nella posizione specificata, o None se la posizione ?? vuota o non valida.
		"""
		if len(self.tableau[row]) > col:
			return self.tableau[row][col]
		else:
			return None

	def get_card_name(self, current_card):
		"""
		Restituisce il nome della carta data la riga e la colonna della pila di tableau.
		"""
		card = current_card
		if card is None:
			return "Nessuna carta presente"

		elif card.coperta:
			return "Carta coperta"

		else:
			return card.nome

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
			raise ValueError("La pila di gioco selezionata ?? vuota.")

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

		raise ValueError("Non ?? possibile muovere la carta selezionata in nessuna pila semi.")

	def muovi_da_gioco_su_foundation(self, pila_gioco, pila_semi):
		"""Muove una carta specifica dalla pila di gioco ad una pila semi specifica."""
		if not pila_gioco:
			raise ValueError("La pila di gioco selezionata ?? vuota.")

		carta = pila_gioco[-1]
		semi_carta = carta.get_seme()
		valore_carta = carta.get_valore()

		if pila_semi[-1].get_seme() == semi_carta:
			if pila_semi[-1].get_valore() == valore_carta - 1:
				pila_semi.append(carta)
				pila_gioco.pop()
				self.controlla_vittoria()
				return True

		raise ValueError("Non ?? possibile muovere la carta selezionata nella pila semi specificata.")

	def muovi_carta_foundation(self, carta):
		"""
		Muove una carta dalle pile di gioco alle fondazioni, se possibile.
		Restituisce True se la mossa ?? stata effettuata, False altrimenti.
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
				raise ValueError("La carta selezionata non pu?? essere mossa in questa pila di gioco.")
		else:
			ultima_carta_pila = self._pile[n_pila][-1]
			if ultima_carta_pila.colore == carta.colore:
				raise ValueError("La carta selezionata non pu?? essere mossa in questa pila di gioco.")
			elif ultima_carta_pila.valore - 1 != carta.valore:
				raise ValueError("La carta selezionata non pu?? essere mossa in questa pila di gioco.")
			else:
				self._pile[n_pila].append(self._scarti.pop(-n_carta))

	def muovi_da_scarti_su_foundation(self, n_carta):
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
				raise ValueError("La carta selezionata non pu?? essere mossa in questa pila semi.")

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
		Muove la carta pi?? in alto dalla pile semi di indice 'indice_semi' alla pile di gioco di indice 'indice_pila'
		se la carta pu?? essere messa nella pile di gioco.
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

		# Verifica se la carta pu?? essere messa nella pila di gioco
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

	#@@@# sezione metodi per convalidare lo spsotamento di una carta

	def is_valid_position(self, row, col):
		"""
		Verifica se la posizione indicata ?? valida per il gioco del solitario.
		"""
		if row < 0 or row >= 7:
			return False
		if col < 0 or col >= len(self.tableau[row]):
			return False
		if (row, col) not in self.valid_positions:
			return False
		return True

	def is_valid_pile(self, pile_index: int, card_index: int) -> bool:
		"""
		Verifica se l'indice della pila e della carta sono validi.
		"""
		if 0 <= pile_index < 7 and 0 <= card_index < len(self.tableau[pile_index]):
			return True

		return False

	def is_empty_pile(self, pile: str) -> bool:
		"""
		Verifica se una pila ?? vuota
		:param pile: Il nome della pila da verificare
		:return: True se la pila ?? vuota, False altrimenti
		"""
		return len(getattr(self, pile)) == 0

	def is_valid_card_move(self, start_pile, end_pile):
		"""Verifica se il movimento di una carta da una pila all'altra ?? valido"""
		start_pile_cards = self.get_pile_cards(start_pile)
		end_pile_cards = self.get_pile_cards(end_pile)

		# Verifica che la pila di partenza contenga almeno una carta
		if len(start_pile_cards) == 0:
			return False

		# Verifica se la carta da spostare ?? l'ultima carta della pila di partenza
		card_to_move = start_pile_cards[-1]
		if card_to_move not in self.get_top_cards(start_pile):
			return False

		# Verifica che la carta da spostare possa essere posizionata sulla pila di destinazione
		if not self.is_valid_pile(end_pile, card_to_move):
			return False

		# Verifica che il valore della carta da spostare sia uno in meno rispetto alla carta in cima alla pila di destinazione
		if len(end_pile_cards) > 0 and card_to_move.value != end_pile_cards[-1].value - 1:
			return False

		return True

	def render(self, screen):
		self.draw_background(screen)
		self.tableau.render(screen)
		self.foundation_piles.render(screen)
		self.stock_pile[-1].render(screen) # render only the top card of stock pile
		self.waste_pile[-1].render(screen) # render only the top card of waste pile

		if self.message_box:
			self.message_box.render(screen)

		if self.is_win():
			self.vittoria()

		pygame.display.flip()




#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
