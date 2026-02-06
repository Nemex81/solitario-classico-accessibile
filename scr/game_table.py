"""
	file game_table.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/game_table.py

	Modulo per la creazione e gestione del tavolo di gioco
"""

# lib
import logging
import random
# moduli personali
from my_lib.myglob import *
import my_lib.myutyls as mu
from scr.pile import PilaBase, PilaSemi, PilaScarti, PilaRiserve
# import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class TavoloSolitario:
	""" Gestisce il tavolo di gioco del solitario """

	def __init__(self, mazzo):
		self.mazzo = mazzo
		self.pile = []  # lista delle pile di gioco

	def get_type_deck(self):
		""" Restituisce una lista con i semi per il tipo di mazzo in uso """
		return self.mazzo.get_suits()				
		#if self.mazzo.is_french_deck():
			#return ["cuori", "quadri", "fiori", "picche"]
		#else:
			#return ["spade", "bastoni", "coppe", "denari"]

	def reset_pile(self):
		""" Resetta le pile di gioco """

		self.pile.clear()
		self.crea_pile_gioco()
		self.distribuisci_carte()

	def crea_pile_gioco(self):
		# crea le sette pile base
		self.pile = [] # resettiamo tutte le pile di gioco a 0
		id = 0
		for i in range(7):
			pile_base = PilaBase(id)
			self.pile.append(pile_base)
			id += 1

		# crea le quattro pile semi
		dech_semi = self.get_type_deck()
		for i in range(4):
			name = dech_semi[i]
			pile_semi = PilaSemi(id, name)
			self.pile.append(pile_semi)
			id += 1

		# crea la pila di scarti
		pila_scarti = PilaScarti(id)
		pila_scarti.set_pile_name("pila scarti")
		self.pile.append(pila_scarti)
		id += 1

		# crea la pila di mazzo riserve
		mazzo_riserve = PilaRiserve(id)
		self.pile.append(mazzo_riserve)

	def distribuisci_carte(self):
		""" Distribuisce le carte sul tavolo """

		# se il mazzo è vuoto, lo resetto
		if self.mazzo.is_empty_dek():
			self.mazzo.reset()

		# pesco le carte dal mazzo e le aggiungo alle pile base
		for i in range(7):
			for j in range(i+1):
				carta = self.mazzo.pesca()
				self.pile[i].aggiungi_carta(carta)

		# Calcola dinamicamente quante carte restano per il mazzo riserve
		carte_totali = self.mazzo.get_total_cards()  # 52 per francese, 40 per napoletano
		carte_distribuite_pile_base = 28  # 1+2+3+4+5+6+7
		carte_rimanenti = carte_totali - carte_distribuite_pile_base  # 24 o 12

		# distribuisci le restanti carte alla pila mazzo riserve
		for i in range(carte_rimanenti):
			carta = self.mazzo.pesca()
			carta.set_cover()
			self.pile[12].aggiungi_carta(carta)

		# scopro l'ultima carta di ogni pila
		self.uncover_top_all_base_piles()

	def pescata(self, num_cards):
		""" Pesca le carte dal mazzo riserve e le aggiunge alla pila di scarti """

		# Controllo se ci sono ancora carte nel mazzo riserve
		if self.pile[12].is_empty_pile():
			return False

		# Pesco le carte dal mazzo riserve
		cards = self.pile[12].prendi_carte(num_cards)
		# Sposto le carte pescate sulla pila scoperta (numero 11)
		if len(self.pile[11].carte) > 0:
			self.pile[11].carte.extend(cards)
		else:
			self.pile[11].carte = cards

		# Aggiorno lo stato della pila scarti
		for c in self.pile[11].carte:
			c.set_uncover()

		return True

	def riordina_scarti(self, shuffle_mode=False):
		if not self.pile[11].carte:
			# La pila di scarti è vuota
			return

		# Rimuovi le carte dalla pila di scarti
		carte_scarti = self.pile[11].carte[:]
		self.pile[11].carte.clear()

		# Applica la modalità di riciclo scelta
		if shuffle_mode:
			# Modalità MESCOLATA: mescola casualmente le carte
			random.shuffle(carte_scarti)
		else:
			# Modalità INVERSIONE (default): inverti l'ordine
			carte_scarti = carte_scarti[::-1]

		# Riaggiungi le carte al mazzo riserve
		for carta in carte_scarti:
			carta.flip()
			self.pile[12].carte.append(carta)

		# inverto l'ordine delle carte nel mazzo riserve
		self.pile[12].carte.reverse()

	def scopri_ultima_carta(self, origin_pile):
		# scopro l'ultima carta della pila di origine, se è una pila base
		if origin_pile.is_pila_base():
			if not origin_pile.is_empty_pile():
				if origin_pile.carte[-1].get_covered:
					origin_pile.carte[-1].flip()

	def uncover_top_all_base_piles(self):
		""" Scopre l'ultima carta di tutte le pile base """

		for i in range(7):
			pila = self.pile[i]
			if pila.is_empty_pile():
				continue

			pila.set_uncover_top_card()

	def get_pile_name(self, col):
		pila = self.pile[col]
		return pila.nome

	def get_card_parent(self, card):
		""" Restituisce l'oggetto Pila a cui appartiene la carta passata come parametro """
		for pila in self.pile:
			if card in pila.carte:
				return pila

	def get_card_position(self, row, col):
		pila = self.pile[col]
		return pila.get_carta(row)

	#@@# sezione convalide spostamenti

	def put_to_base(self, origin_pila, dest_pila, select_card):
		"""
		Sposta una carta dalla pila di partenza alla pila di destinazione di tipo "base".
		"""

		if not dest_pila.is_pila_base():
			return False

		totcard = len(select_card)
		if totcard > 1:
			card = select_card[0]
		else:
			card = select_card[-1]

		if card.get_value > 1 and not dest_pila.is_empty_pile():
			if card.get_color == dest_pila.carte[-1].get_color :
				return False

		elif card.get_value < 13 and dest_pila.is_empty_pile():
			return False

		elif card.get_value == 13 and dest_pila.is_empty_pile():
			return True

		if not dest_pila.is_empty_pile():
			dest_card = dest_pila.carte[-1]
			dest_value = dest_card.get_value - 1
			if card.get_value != dest_value:
				return False

		return True

	def put_to_seme(self, origin_pila, dest_pila, select_card):
		if not dest_pila.is_pila_seme():
			return False

		card = select_card
		if card.get_suit != dest_pila.seme:
			return False

		if card.get_value > 1 and dest_pila.is_empty_pile():
			return False

		if not dest_pila.is_empty_pile():
			dest_card = dest_pila.carte[-1]
			dest_value = dest_card.get_value + 1
			if card.get_value != dest_value:
				return False

		return True

	def esegui_spostamento(self, origin_pile, dest_pile, cards):
		# rimuovo le carte dalla pila di origine
		card_index = origin_pile.get_card_index(cards[0])
		totcards = len(cards)
		carte_rimosse = origin_pile.prendi_carte(totcards)
		# aggiungo le carte alla pila di destinazione
		dest_pile.carte.extend(carte_rimosse)

	def verifica_spostamenti(self, origin_pila, dest_pila, select_card):
		card = select_card[0]
		if dest_pila.is_pila_seme():
			if self.put_to_seme(origin_pila, dest_pila, card):
				return True

		elif dest_pila.is_pila_base():
			if self.put_to_base(origin_pila, dest_pila, select_card):
				return True

		return False

	def verifica_vittoria(self):
		""" 
		Verifica la vittoria controllando che tutte le 4 pile semi siano complete.
		
		Per il mazzo francese: 13 carte per seme
		Per il mazzo napoletano: 10 carte per seme
		"""
		# Ottieni il numero di carte per seme dal mazzo in uso
		carte_per_seme = len(self.mazzo.VALUES)  # 13 per francese, 10 per napoletano
		
		# Controlla tutte e 4 le pile semi (indici 7, 8, 9, 10)
		for i in range(7, 11):  # FIX: era range(7, 10) che saltava la pila 10!
			if len(self.pile[i].carte) != carte_per_seme:
				return False
		
		return True


#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
