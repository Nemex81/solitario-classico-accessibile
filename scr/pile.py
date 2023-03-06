"""
	file pile.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/pile.py

	Modulo per la creazione e gestione delle pile di gioco
"""

# lib
import logging, random
# moduli personali
from my_lib.myglob import *
import my_lib.myutyls as mu
from scr.cards import Carta, Mazzo
# import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.setLevel(logging.DEBUG)

class Pila:
	def __init__(self, id, tipo_pila):
		self.id = id
		self.nome = None
		self.tipo = tipo_pila
		self.seme = None
		self.carte = []

	def aggiungi_carta(self, carta):
		self.carte.append(carta)

	def rimuovi_carta(self, pos):
		carta_rimossa = self.carte.pop(pos)
		return carta_rimossa

	def rimuovi_carte(self, pos_iniziale, pos_finale):
		carte_rimosse = self.carte[pos_iniziale:pos_finale+1]
		self.carte = self.carte[:pos_iniziale] + self.carte[pos_finale+1:]
		return carte_rimosse

	def prendi_carte(self, num_carte):
		carte_pescate = []
		for i in range(num_carte):
			if len(self.carte) == 0:
				break

			carta = self.rimuovi_carta(-1)
			carte_pescate.insert(0, carta)
		return carte_pescate

	def get_carte(self):
		return self.carte

	def get_carta(self, pos):
		return self.carte[pos]

	def set_coperte(self, inizio, fine, coperte):
		for carta in self.carte[inizio:fine+1]:
			carta.coperta = coperte

	def numero_carte(self):
		return len(self.carte)

	def get_card_index(self, card):
		""" Restituisce l'indice della carta. """
		return self.carte.index(card)

	def get_pile_type(self):
		""" Restituisce il tipo di pila """
		return self.tipo

	def get_pile_suit(self):
		if self.seme is None:
			return "nessuno"

		return self.seme

	def get_pile_info(self):
		info_pila = f"nome: {self.nome}\n"
		info_pila += f"id: {self.id}\n"
		info_pila += f"tipo: {self.get_pile_type()}"
		info_pila += f"seme: {self.get_pile_suit()}"
		return info_pila

	#@@# sezione convalide spostamenti carte

	def is_empty_pile(self):
		max = self.numero_carte()
		if max > 0:
			return False

		return True

	def is_pila_base(self):
		type = self.get_pile_type()
		if type != "base":
			return False

		return True

	def is_pila_seme(self):
		type = self.get_pile_type()
		if type != "seme":
			return False

		return True

	def is_pila_scarti(self):
		type = self.get_pile_type()
		if type != "scarti":
			return False

		return True

	def is_pila_riserve(self):
		type = self.get_pile_type()
		if type != "mazzo_riserve":
			return False

		return True



class TavoloSolitario:
	semi = ["cuori", "quadri", "picche", "fiori"]
	def __init__(self):
		self.mazzo = Mazzo()
		self.mazzo.reset()
		self.pile = []  # lista delle pile di gioco

	def crea_pile_gioco(self):
		logger.debug("creazione delle pile di gioco")
		# crea le sette pile base
		self.pile = [] # resettiamo tutte le pile di gioco a 0
		id = 0
		for i in range(7):
			pile_base = Pila(id, "base")
			pile_base.nome = f"pila {i+1}"
			self.pile.append(pile_base)
			id += 1

		# crea le quattro pile semi
		for i in range(4):
			pile_semi = Pila(id, "semi")
			pile_semi.nome = f"pila {self.semi[i]}"
			pile_semi.seme = self.semi[i]
			self.pile.append(pile_semi)
			id += 1

		# crea la pila di scarti
		pila_scarti = Pila(id, "scarti")
		pila_scarti.nome = "pila scarti"
		self.pile.append(pila_scarti)
		id += 1

		# crea la pila di mazzo riserve
		pila_mazzo_riserve = Pila(id, "mazzo_riserve")
		pila_mazzo_riserve.nome = "pila riserve"
		self.pile.append(pila_mazzo_riserve)

	def distribuisci_carte(self):
		logger.debug("inizio distribuzione delle carte nelle pile di gioco")
		# distribuisci le carte alle pile base
		if len(self.mazzo.cards) < 1:
			self.mazzo.reset()

		for i in range(7):
			for j in range(i+1):
				carta = self.mazzo.pesca()
				carta.coperta = True #if j < i else False
				self.pile[i].aggiungi_carta(carta)

		logger.debug("carte distribuite in pile base. carte restanti in mazzo: %s", len(self.mazzo.cards))
		# distribuisci le restanti carte alla pila mazzo riserve
		for i in range(24):
			carta = self.mazzo.pesca()
			carta.coperta = True
			self.pile[12].aggiungi_carta(carta)

		# scopro l'ultima carta di ogni pila
		for i in range(7):
			pila = self.pile[i]
			carta = pila.carte[-1]
			carta.flip()#coperta = False

	def pescata(self, num_cards):
		# Controllo se ci sono ancora carte nel mazzo riserve
		if not self.pile[12].carte:
			return False

		if self.pile[12].numero_carte() < num_cards:
			# Non ci sono abbastanza carte nel mazzo riserve, gestire l'errore come si preferisce
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
			c.coperta = False

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
			self.pile[12].carte.append(carta)

		# mazzo riserve intertito
		self.pile[12].carte.reverse()

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

	def from_base_to_base(self, pila_partenza_idx, pila_destinazione_idx, carta_selezionata_idx):
		"""
		Sposta una carta dalla pila di partenza di tipo "base" alla pila di destinazione di tipo "base".
		La carta deve essere l'ultima della pila di partenza e di valore inferiore di una unità rispetto alla carta
		di destinazione, la quale deve essere dello stesso seme.
		Se la pila di destinazione è vuota, la carta di partenza deve essere un Re.

		:param pila_partenza_idx: l'indice della pila di partenza
		:param pila_destinazione_idx: l'indice della pila di destinazione
		:param carta_selezionata_idx: l'indice della carta selezionata nella pila di partenza
		:return: True se lo spostamento è stato effettuato con successo, False altrimenti
		"""

	def from_base_to_seme(self):
		pass

	def from_scarti_to_base(self):
		pass

	def from_scarti_to_seme(self, origin_pila, dest_pila, select_card):
		card = select_card[0]
		#if card.seme != dest_pila.seme:
			#return False

		#if dest_pila.is_empty_pile():
			#if card.get_value() == 1:
				#return True

		#elif not dest_pila.is_empty_pile():
			#dest_card = dest_pila[-1]
			#if card.valore_numerico == (dest_card.valore_numerico - 1):
				#return True
		return True

	def from_seme_to_base(self):
		pass

	def verifica_spostamenti(self, origin_pila, dest_pila, select_card):
		ver = False
		if dest_pila.is_pila_seme():
			ver = self.from_scarti_to_seme(origin_pila, dest_pila, select_card)
			if ver:
				return True

		return ver

	#@@# sezione vecchio sistema di convalida mosse, da sostituire ed eliminare il prima possibile con quello sopra.

	def check_legal_move(self, source_pile_index, dest_pile_index):
		"""
		Verifica se lo spostamento di una o più carte dalla pila sorgente a quella destinazione è legale.
		"""
		source_pile = self.pile[source_pile_index]
		dest_pile = self.pile[dest_pile_index]

		if not dest_pile.carte and source_pile.carte[-1].valore_numerico == 13:
			return True

		top_card = source_pile.carte[-1]
		if self.can_stack_card_on_top(dest_pile_index, top_card):
			return True

		return False

	def can_stack_card_on_top(self, pile_index, card):
		pile = self.pile[pile_index]
		if not pile.carte:
			# la pila è vuota, quindi la carta deve essere un Re
			return card.valore_numerico == 13

		top_card = pile.carte[-1]
		return (top_card.valore_numerico - card.valore_numerico == 1) and (top_card.colore != card.colore)

	def get_valid_destinations(self, source_pile_index, card):
		""" creato con la tecnica delle liste comprensive """
		return [i for i, pile in enumerate(self.pile) if i != source_pile_index and self.can_stack_card_on_top(i, card)]

	def last_get_valid_destinations(self, source_pile_index, card):
		valid_destinations = []
		for i, pile in enumerate(self.pile):
			if i == source_pile_index:
				continue
			if self.can_stack_card_on_top(i, card):
				valid_destinations.append(i)

		return valid_destinations



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
