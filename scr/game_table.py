"""
	file game_table.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/game_table.py

	Modulo per la creazione e gestione del tavolo di gioco
"""

# lib
import logging
# moduli personali
from my_lib.myglob import *
import my_lib.myutyls as mu
from scr.cards import  Mazzo
from scr.pile import PilaClassica
# import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)



class TavoloSolitario:
	""" Gestisce il tavolo di gioco del solitario """
	semi = ["cuori", "quadri", "fiori", "picche"]
	def __init__(self):
		self.mazzo = Mazzo()
		self.mazzo.reset()
		self.pile = []  # lista delle pile di gioco

	def crea_pile_gioco(self):
		# crea le sette pile base
		self.pile = [] # resettiamo tutte le pile di gioco a 0
		id = 0
		for i in range(7):
			pile_base = PilaClassica(id, "base")
			pile_base.set_pile_name(f"pila {i+1}")
			self.pile.append(pile_base)
			id += 1

		# crea le quattro pile semi
		for i in range(4):
			pile_semi = PilaClassica(id, "semi")
			pile_semi.set_pile_name(f"pila {self.semi[i]}")
			pile_semi.set_pile_suit(self.semi[i])
			self.pile.append(pile_semi)
			id += 1

		# crea la pila di scarti
		pila_scarti = PilaClassica(id, "scarti")
		pila_scarti.set_pile_name("pila scarti")
		self.pile.append(pila_scarti)
		id += 1

		# crea la pila di mazzo riserve
		pila_mazzo_riserve = PilaClassica(id, "pila riserve")
		pila_mazzo_riserve.set_pile_name("pila riserve")
		self.pile.append(pila_mazzo_riserve)

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

		# distribuisci le restanti carte alla pila mazzo riserve
		for i in range(24):
			carta = self.mazzo.pesca()
			carta.set_cover()
			self.pile[12].aggiungi_carta(carta)

		# scopro l'ultima carta di ogni pila
		self.uncover_top_all_base_piles()

	def pescata(self, num_cards):
		# Controllo se ci sono ancora carte nel mazzo riserve
		if not self.pile[12].carte:
			return False

		# Pesco le carte dal mazzo riserve
		cards = self.pile[12].prendi_carte(num_cards)
		# Sposto le carte pescate sulla pila scoperta (numero 11)
		if len(self.pile[11].carte) > 0:
			self.pile[11].carte.extend(cards)
		else:
			self.pile[11].carte = cards

		# Aggiorno lo stato della pila scoperta
		for c in self.pile[11].carte:
			c.set_uncover()

		return True

	def riordina_scarti(self):
		if not self.pile[11].carte:
			# La pila di scarti è vuota
			return

		# Rimuovi le carte dalla pila di scarti e inverti l'ordine
		carte_scarti = self.pile[11].carte[::-1]
		self.pile[11].carte.clear()

		# Riaggiungi le carte al mazzo riserve
		for carta in carte_scarti:
			carta.flip()
			self.pile[12].carte.append(carta)

		# mazzo riserve intertito
		self.pile[12].carte.reverse()

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

	def scopri_ultima_carta(self, origin_pile):
		# scopro l'ultima carta della pila di origine, se è una pila base
		if origin_pile.is_pila_base():
			if not origin_pile.is_empty_pile():
				if origin_pile.carte[-1].get_covered:
					origin_pile.carte[-1].flip()

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
		# verificare la vittoria controllando che le 4 pile  semi siano composte da 13 carte
		for i in range(7, 10):
			if len(self.pile[i].carte) != 13:
				return False
			
		return True


#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
