"""
	file game_engine.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/game_engine.py

	Modulo per le regole del gioco del solitario
"""

# lib
import os, sys, random, logging
# moduli personali
from my_lib.myglob import *
import my_lib.myutyls as mu
from scr.cards import Carta, Mazzo
from scr.pile import PileSolitario
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger.setLevel(logging.DEBUG)
# Esempio di scrittura di una stringa di log
#logger.debug("Il mio messaggio di debug")
#logging.debug("Esempio di stringa di log")

class EngineSolitario(PileSolitario):
	def __init__(self):
		super().__init__()
		self.mazzo = Mazzo()
		self.tavolo = PileSolitario()
		self.difficulty_level = 3
		self.primo_giro = True
		self.conta_giri = 0
		self.cursor_pos = [0, 0]  # posizione iniziale del cursore sul tavolo
		self.selected_card = []  # lista delle carte selezionate dal giocatore
		self.target_card = None # oggetto carta nel focus

	#@@# sezione vocalizza info

	def vocalizza_colonna(self):
		row, col = self.cursor_pos
		current_pile = self.get_pile_name(col)
		string = current_pile
		return string

	def vocalizza_riga(self):
		row, col = self.cursor_pos
		current_card = self.get_card_position(row, col)
		card_name = current_card.get_name()
		string_carta = f"{row+1}: {card_name}"
		string = string_carta
		return string

	def vocalizza_focus(self):
		# vocalizziamo lo spostamento
		row, col = self.cursor_pos
		current_card = self.get_card_position(row, col)
		current_pile = self.get_pile_name(col)
		#string_cursore = f"Cursore spostato a colonna {col+1}, riga {row+1}. "
		try:
			card_name = current_card.get_name()
			string_carta = f"{current_pile}.  "
			string_carta += f"{row+1}: {card_name}"
			string = string_carta

		except AttributeError:
			string = current_pile

		return string

	#@@# sezione metodi supporto comandi  utente

	def move_cursor_up(self):
		if self.cursor_pos[0] > 0:
			self.cursor_pos[0] -= 1
			speack =self.vocalizza_riga()
			return speack

	def move_cursor_down(self):
		pila = self.pile[self.cursor_pos[1]]
		if self.cursor_pos[0] < len(pila.carte) - 1:
			self.cursor_pos[0] += 1
			speack =self.vocalizza_riga()
			return speack

	def move_cursor_left(self):
		if self.cursor_pos[1] > 0:
			self.cursor_pos[1] -= 1
			self.cursor_pos[0] = 0
			speack = self.vocalizza_colonna()
			return speack

	def move_cursor_right(self):
		pile = self.pile
		if self.cursor_pos[1] < len(pile) - 1:
			self.cursor_pos[1] += 1
			self.cursor_pos[0] = 0
			speack = self.vocalizza_colonna()
			return speack

	def select_card(self):
		""" seleziona le carte che il giocatore intende tentare di spostare """
		carteprese = []
		if len(self.selected_card) == 1:
			return "Hai già selezionato la carta da spostare!  premi canc per annullare la selezione.\n"

		elif len(self.selected_card) > 1:
			return "Hai già selezionato le carte da spostare!  premi canc per annullare la selezione.\n"

		row , col = self.cursor_pos
		card = self.get_card_position(row, col)
		if not card:
			return "la pila è vuota!\n"

		if card.coperta:
			return "non puoi selezionare una carta coperta!\n"

		self.id_row_origine = row
		self.id_col_origine = col
		pila = self.pile[col]
		if row == len(pila.carte) - 1:
			self.selected_card.append(card)

		elif row < len(pila.carte) - 1:
			max_carte = len(pila.carte) - 1
			tot_carte = max_carte - row
			self.selected_card = pila.prendi_carte(tot_carte)
			#for c in range(row, maxcarte):
				#card = self.get_card_position(c, colun)
				#self.selected_card.append(card)

		tot = len(self.selected_card)
		nome_carta = card.get_name()
		string = f"carte selezionate: {tot}: {nome_carta}\n"
		return string

	def set_destination_pile(self):
		if not self.selected_card:
			return "Nessuna carta selezionata.\n"

		dest_row, dest_col = self.cursor_pos
		dest_pile = self.pile[dest_col]
		dest_pile_type = dest_pile.get_pile_type()

		# Utilizziamo get_card_parent per ottenere l'oggetto Pila di provenienza delle carte selezionate
		source_pile = self.get_card_parent(self.selected_card[0])

		if not self.check_legal_move(source_pile.id, dest_col):
			return "Mossa non valida.\n"

		if dest_pile_type == "semi":
			if len(self.selected_card) > 1:
				return "Puoi spostare solo una carta alla volta in questa pila.\n"

			card = self.selected_card[0]
			if card.valore_numerico != 1 and source_pile.carte:
				return "Solo l'asso può essere spostato in questa pila.\n"

		self.sposta_carte(self.id_row_origine, self.id_col_origine, dest_row, dest_col, self.selected_card)
		self.selected_card = []
		return "spostamento completato!\n"

	def cancel_selected_cards(self):
		string = ""
		if self.selected_card:
			self.selected_card = []
			string = "Carte selezionate annullate.\n"
		else:
			string = "Non ci sono carte selezionate da annullare.\n"

		return string

	def pesca(self):
		if not self.pescata():
			return "qualcosa è andato storto!"

		string = ""
		self.target_card = self.pile[11].carte[-1]
		if self.target_card:
			card_name = self.target_card.get_name()
			string = f"Hai pescato: {card_name}"
		else:
			string = "evento da verificare"

		return string

	def crea_gioco(self):
		"""Crea un nuovo gioco del solitario."""
		self.mazzo.reset()
		self.tavolo.crea_pile_gioco()
		self.tavolo.distribuisci_carte()
		self.crea_pile_gioco()
		self.distribuisci_carte()

	def distribuisci_carte(self):
		# distribuisci le carte alle pile base
		for i in range(7):
			for j in range(i+1):
				carta = self.mazzo.pesca()
				carta.coperta = True #if j < i else False
				self.pile[i].aggiungi_carta(carta)

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

	def can_stack_card_on_top(self, pile_index, card):
		pile = self.pile[pile_index]
		if not pile.carte:
			# la pila è vuota, quindi la carta deve essere un Re
			return card.valore_numerico == 13

		top_card = pile.carte[-1]
		return (top_card.valore_numerico - card.valore_numerico == 1) and (top_card.seme != card.seme)

	def get_valid_destinations(self, source_pile_index, card):
		valid_destinations = []
		for i, pile in enumerate(self.pile):
			if i == source_pile_index:
				continue
			if self.can_stack_card_on_top(i, card):
				valid_destinations.append(i)

		return valid_destinations

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

	def sposta_carte(self, source_row, source_col, dest_row, dest_col, cards):
		# Ottieni la pila di partenza e quella di destinazione
		source_pile = self.pile[source_col]
		dest_pile = self.pile[dest_col]

		# Verifica se lo spostamento delle carte è consentito
		if not self.check_legal_move(source_col, dest_col):
			return False

		# Rimuovi le carte dalla pila di partenza e aggiungile alla pila di destinazione
		carte_rimosse = source_pile.rimuovi_carte(source_row, source_row+len(cards)-1)
		for c in carte_rimosse:
			dest_pile.aggiungi_carta(c)

		# scopri l'ultima carta della pila di origine
		if len(self.pile[source_col].carte) > 0:
			self.pile[source_col].carte[-1].flip()

		# aggiorniamo le coordinate memorizzate nel cursore di navigazione
		self.cursor_pos = [dest_row, dest_col]
		return True

	def get_card_parent(self, card):
		"""
		Restituisce l'oggetto Pila a cui appartiene la carta passata come parametro
		"""
		for pila in self.pile:
			if card in pila.carte:
				return pila

		return None

	def pescata(self):
			# Definiamo il numero di carte da pescare in base al livello di difficoltà impostato
			num_cards = self.difficulty_level
			# Controllo se ci sono ancora carte nel mazzo riserve
			if len(self.pile[12].carte) < num_cards:
				# Non ci sono abbastanza carte nel mazzo riserve, gestire l'errore come si preferisce
				return

			# Pesco le carte dal mazzo riserve
			cards = self.pile[12].prendi_carte(num_cards)
			# Sposto le carte pescate sulla pila scoperta (numero 11)
			if len(self.pile[11].carte) > 0:
				self.pile[11].carte.extend(cards)
			else:
				self.pile[11].carte = cards

			# Aggiorno la posizione del cursore
			self.cursor_position = len(self.pile[11].carte) - 1
			# Aggiorno lo stato della pila scoperta
			for c in self.pile[11].carte:
				c.coperta = False

			return True



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
