"""
	file game_engine.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/game_engine.py

	Modulo per le regole del gioco del solitario
"""

# lib
import sys, random, logging
# moduli personali
from scr.pile import TavoloSolitario
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger.setLevel(logging.DEBUG)
# Esempio di scrittura di una stringa di log
#logger.debug("Il mio messaggio di debug")

class EngineSolitario:
	def __init__(self):
		super().__init__()
		self.tavolo = TavoloSolitario()
		self.difficulty_level = 1
		self.primo_giro = True
		self.conta_giri = 0
		self.cursor_pos = [0, 0]  # posizione iniziale del cursore sul tavolo
		self.selected_card = []  # lista delle carte selezionate dal giocatore
		self.target_card = None # oggetto carta nel focus
		self.origin_pile = None # salvo pila origine per gestione spostamenti
		self.dest_pile = None # salvo pile destinazione valide per gestione spostamenti

	def crea_gioco(self):
		"""Crea un nuovo gioco del solitario."""
		self.tavolo.crea_pile_gioco()
		self.tavolo.distribuisci_carte()

	#@@# sezione prepara stringhe per il vocalizza info

	def vocalizza_carta(self):
		string = ""
		infocarta = ""
		row, col = self.cursor_pos
		pila = self.tavolo.pile[col]
		totcarte = pila.numero_carte()
		if totcarte > 0:
			carta = pila.get_carta(row)
			if not carta:
				return "non riesco ad identificare la carta alle coordinate specificate"
			
			id_carta = pila.get_card_index(carta)
			infocarta = carta.get_info_card()
			infocarta += f"pos in pila: {id_carta+1}\n"
			string += "scheda carta: %s\n" % infocarta
		
		return string

	def vocalizza_pila(self):
		string = ""
		infopila = ""
		row, col = self.cursor_pos
		pila = self.tavolo.pile[col]
		infopila = pila .get_pile_info()
		string += "scheda pila: %s\n" % infopila
		return string

	def vocalizza_colonna(self):
		row, col = self.cursor_pos
		current_pile = self.tavolo.get_pile_name(col)
		if current_pile:
			string = current_pile
			string += self.say_top_card(self.tavolo.pile[col])
		else:
			string = "pila non riconosciuta.\n"

		return string

	def vocalizza_riga(self):
		row, col = self.cursor_pos
		current_card = self.tavolo.get_card_position(row, col)
		if not current_card:
			return "non riesco ad identificare la carta alle coordinate specificate"

		card_name = current_card.get_name()
		string_carta = f"{row+1}: {card_name}"
		string = string_carta
		return string

	def vocalizza_focus(self):
		# vocalizziamo lo spostamento
		row, col = self.cursor_pos
		pila = self.tavolo.pile[col]
		if pila.is_empty_pile():
			return "la pila è vuota!\n"

		current_card = self.tavolo.get_card_position(row, col)
		try:
			card_name = current_card.get_name()
			string_carta = f"{pila.nome}.  "
			string_carta += f"{row+1}: {card_name}"
			string = string_carta

		except AttributeError:
			string = pila.get_name()

		return string

	def say_origin(self):
		string = f"pila di origine: {self.origin_pile.nome}"
		string += f"tipo di pila: {self.origin_pile.tipo}"
		return string

	def say_dest(self):
		string = f"pila di destinazione: {self.dest_pile.nome}"
		string += f"tipo di pila: {self.dest_pile.tipo}"
		return string

	def say_selected_cards(self):
		tot = len(self.selected_card)
		string = f"carte selezionate: {tot}"
		string += f"carta da collegare: {self.target_card.nome}"
		string += f"valore della carta: {self.target_card.get_value()}"
		return string

	def say_top_card(self, pila):
		# vocalizziamo la carta in cima alla pila
		# se non è vuota
		string = "la pila è vuota!\n"
		if not pila.is_empty_pile():
			string = f"carta in cima: {pila.carte[-1].get_name()}"

		return string

	def say_top_scarto(self):
		# vocalizziamo la carta in cima alla pila scarti se non è vuota
		string = "la pila scarti è vuota!\n"
		pila = self.tavolo.pile[11]
		if not pila.is_empty_pile():
			string = f"ultimo scarto: {pila.carte[-1].get_name()}"

		return string

	def say_tot_dek(self):
		# vocalizziamo il numero di carte nel mazzo
		string = "il mazzo è vuoto!\n"
		mazzo = self.tavolo.pile[12]
		if not mazzo.is_empty_pile():
			string = f"carte nel mazzo: {mazzo.numero_carte()}"
		else:
			string = "il mazzo è vuoto!\n"

		return string



	#@@# sezione metodi per il movimento del cursore di navigazione

	def move_cursor_up(self):
		pila = self.tavolo.pile[self.cursor_pos[1]]
		if not pila.is_pila_base():
			return "non sei su una pila base.\n"

		if self.cursor_pos[0] > 0:
			self.cursor_pos[0] -= 1
			speack =self.vocalizza_riga()
			return speack

	def move_cursor_down(self):
		pila = self.tavolo.pile[self.cursor_pos[1]]
		if not pila.is_pila_base():
			return "non sei su una pila base.\n"

		if self.cursor_pos[0] < len(pila.carte) - 1:
			self.cursor_pos[0] += 1
			speack = self.vocalizza_riga()
			return speack

	def move_cursor_left(self):
		pile = self.tavolo.pile
		if self.cursor_pos[1] > 0:
			self.cursor_pos[1] -= 1
			self.cursor_pos[0] = self.move_cursor_top_card(pile[self.cursor_pos[1]])
			speack = self.vocalizza_colonna()
			return speack

	def move_cursor_right(self):
		pile = self.tavolo.pile
		if self.cursor_pos[1] < len(pile) - 1:
			self.cursor_pos[1] += 1
			self.cursor_pos[0] = self.move_cursor_top_card(pile[self.cursor_pos[1]])
			speack = self.vocalizza_colonna()
			return speack

	def move_cursor_pile_type(self):
		""" Sposta il cursore di navigazione sulla prima pila di tipo diverso da quello iniziale"""
		pile = self.tavolo.pile
		pila_iniziale = pile[self.cursor_pos[1]]
		tipo_iniziale = pila_iniziale.tipo
		for i in range(self.cursor_pos[1] + 1, len(pile)):
			if pile[i].tipo == "mazzo_riserve":
				speack = "pile base:  \n"
				self.cursor_pos[1] = 0
				self.cursor_pos[0] = self.move_cursor_top_card(pile[0])
				speack += self.vocalizza_colonna()
				return speack

			elif pile[i].tipo != tipo_iniziale:
				speack = f"pile {pile[i].tipo}:  \n"
				self.cursor_pos[1] = i
				self.cursor_pos[0] = self.move_cursor_top_card(pile[i])
				speack += self.vocalizza_colonna()
				return speack

	def move_cursor_to_base(self, pos):
		""" Sposta il cursore di navigazione sulla pila base richiesta """
		i = int(pos)
		pile = self.tavolo.pile
		self.cursor_pos[1] = i
		self.cursor_pos[0] = self.move_cursor_top_card(pile[i])
		speack = self.vocalizza_colonna()
		return speack

	def move_cursor_top_card(self, pila):
		""" Sposta il cursore di navigazione  in cima alla pila in cui ci si trova durante lospostamento con le frecce orizzontali"""
		if not pila.is_empty_pile():
			return len(pila.carte) - 1

	def move_cursor(self, direction):
		""" Sposta il cursore nella direzione specificata """
		string = ""
		if direction == 'up':
			string = self.move_cursor_up()

		elif direction == 'down':
			string = self.move_cursor_down()

		elif direction == 'left':
			string = self.move_cursor_left()

		elif direction == 'right':
			string = self.move_cursor_right()

		elif direction == "tab":
			string = self.move_cursor_pile_type()

		#da qui dovrei controllare se sono lettere da 0 a 6 e far partire il metodo move_cursor_to_base
		elif direction in "0123456":
			string = self.move_cursor_to_base(direction)

		return string



	#@@# sezione metodi per selezionare e deselezionare le carte

	def cancel_selected_cards(self):
		string = ""
		self.selected_card = []
		self.target_card = None
		self.origin_pile = None
		self.dest_pile = None
		string = "Mossa annullata!\n"
		return string

	def select_scarto(self):
		# seleziona la carta in cima allo scarto
		string = ""
		if self.selected_card:
			string = "Hai già selezionato le carte da spostare!  premi canc per annullare la selezione.\n"
			return string

		scarti = self.tavolo.pile[11]
		if scarti.is_empty_pile():
			string = "la pila scarti è vuota!\n"
			return string

		self.selected_card.append(scarti.carte[-1])
		self.target_card = scarti.carte[-1]
		self.origin_pile = scarti
		string = "carta selezionata: %s!\n" % self.target_card.get_name()
		return string

	def select_card(self):
		""" seleziona le carte che il giocatore intende tentare di spostare """
		carteprese = []
		if len(self.selected_card) == 1:
			return "Hai già selezionato la carta da spostare!  premi canc per annullare la selezione.\n"

		elif len(self.selected_card) > 1:
			return "Hai già selezionato le carte da spostare!  premi canc per annullare la selezione.\n"

		row , col = self.cursor_pos
		card = self.tavolo.get_card_position(row, col)
		if not card:
			return "la pila è vuota!\n"

		if card.coperta:
			return "non puoi selezionare una carta coperta!\n"

		self.id_row_origine = row
		self.id_col_origine = col
		pila = self.tavolo.pile[col]
		# salvo la pila di origine su variabile interna
		self.origin_pile = pila
		if row == len(pila.carte) - 1:
			self.selected_card.append(card)

		elif row < len(pila.carte) - 1 and len(pila.carte) > 0:
			max_carte  = 0
			max_carte = len(pila.carte) - 1
			for i in range(row, max_carte):
				carteprese.append(pila.carte[i])

			self.selected_card = carteprese

		# salvo la carta da collegare su variabile interna
		self.target_card = self.selected_card[0]
		# preparo la stringa da vocalizzare
		tot = len(self.selected_card)
		nome_carta = card.get_name()
		string = f"carte selezionate: {tot}\n carta da collegare: {nome_carta}\n"
		return string

	def new_set_destination_pile(self):
		row , col = self.cursor_pos
		pila = self.tavolo.pile[col]
		self.dest_pile = pila

	def new_sposta_carte(self):
		string = "mossa non consentita!\n"
		if not self.selected_card:
			return "devi prima selezionare la carta da spostare!\n"

		self.new_set_destination_pile()
		dest_pila = self.dest_pile
		origin_pila = self.origin_pile
		cards = self.selected_card
		if self.tavolo.verifica_spostamenti(origin_pila, dest_pila, cards):
			# rimuovo le carte dalla pila di origine
			card_index = self.origin_pile.get_card_index(cards[0])
			totcards = len(cards)
			carte_rimosse = self.origin_pile.prendi_carte(totcards)
			self.dest_pile.carte.extend(carte_rimosse)

			# scopro l'ultima carta della pila di origine, se è una pila base
			if self.origin_pile.is_pila_base():
				if not self.origin_pile.is_empty_pile():
					self.origin_pile.carte[-1].flip()

			string = "spostamento consentito!\n"
			self.reset_data_moving()


		return string

	def reset_data_moving(self):
		# azzero i parametri utilizzati per gli spostamenti
		self.origin_pile = None
		self.dest_pile = None
		self.target_card = None
		self.selected_card = []

	def prova_verifica(self):
		string = "mossa non consentita!\n"
		self.new_set_destination_pile()
		col = self.cursor_pos[1]
		dest_pila = self.tavolo.pile[col]
		origin_pila = self.origin_pile
		cards = self.selected_card
		card = self.target_card
		#if self.tavolo.put_to_seme(origin_pila, dest_pila, card):
		if self.tavolo.verifica_spostamenti(origin_pila, dest_pila, card):
			string = "spostamento consentito finalmente!  "

		return string

	def set_destination_pile(self):
		if not self.selected_card:
			return "Nessuna carta selezionata.\n"

		dest_row, dest_col = self.cursor_pos
		dest_pile = self.tavolo.pile[dest_col]
		dest_pile_type = dest_pile.get_pile_type()

		# Utilizziamo get_card_parent per ottenere l'oggetto Pila di provenienza delle carte selezionate
		source_pile = self.tavolo.get_card_parent(self.selected_card[0])
		if not self.tavolo.check_legal_move(source_pile.id, dest_col):
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

	def sposta_carte(self, source_row, source_col, dest_row, dest_col, cards):
		# Ottieni la pila di partenza e quella di destinazione
		source_pile = self.tavolo.pile[source_col]
		dest_pile = self.tavolo.pile[dest_col]

		 #Verifica se lo spostamento delle carte è consentito
		if not self.tavolo.check_legal_move(source_col, dest_col):
			return False

		# Rimuovi le carte dalla pila di partenza e aggiungile alla pila di destinazione
		carte_rimosse = source_pile.rimuovi_carte(source_row, source_row+len(cards)-1)
		for c in carte_rimosse:
			dest_pile.aggiungi_carta(c)

		# scopri l'ultima carta della pila di origine
		if len(self.tavolo.pile[source_col].carte) > 0:
			self.tavolo.pile[source_col].carte[-1].flip()

		# aggiorniamo le coordinate memorizzate nel cursore di navigazione
		self.cursor_pos = [dest_row, dest_col]
		return True

	def pesca(self):
		liv = self.difficulty_level
		ver = self.tavolo.pescata(liv)
		if not ver:
			self.tavolo.riordina_scarti()
			return "rimescolo gli scarti in mazzo riserve!"

		row = -1
		col = 11
		carta = self.tavolo.get_card_position(row, col)
		string = "hai pescato: %s" % carta.get_name()
		return string



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
