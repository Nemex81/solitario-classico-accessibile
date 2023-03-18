"""
	file game_engine.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/game_engine.py

	Modulo per la gestione delle regole del gioco del solitario
"""

# lib
import sys, random, logging, time, pygame
# moduli personali
from my_lib.dialog_box import DialogBox
from scr.pile import TavoloSolitario
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
#logger.debug("Il mio messaggio di debug")

class EngineSolitario(DialogBox):
	def __init__(self):
		super().__init__()
		self.tavolo = TavoloSolitario()
		self.winner = False
		self.is_time_over = False
		self.is_game_running = False
		self.difficulty_level = 1
		self.conta_giri = 0 # contatore per gestire il numero di mosse fatte dal player
		self.conta_rimischiate = 0 # contatore per gestire il numero di rimischiate fatte dal player
		self.cursor_pos = [0, 0]  # posizione iniziale del cursore sul tavolo
		self.selected_card = []  # lista delle carte selezionate dal giocatore
		self.target_card = None # oggetto carta nel focus
		self.origin_pile = None # salvo pila origine per gestione spostamenti
		self.dest_pile = None # salvo pile destinazione valide per gestione spostamenti

		# imposto il tempo di gioco
		self.clock = pygame.time.Clock()
		self.fps = 60
		self.start_ticks = 0

	def test_set_time_out(self):
	#																																																																																																																																												 impostare manualmente il tempo a 60 minuti
		self.is_time_over = True
		return "Prova verifica tempo scaduto.  \n"

	def test_vittoria(self):
		# creiamo una simulazione di vittoria partita per testare il ceck nel ciclo principale
		self.winner = True
		return "Prova verifica vittoria partita.  \n"

	def crea_gioco(self):

		"""Crea un nuovo gioco del solitario."""
		self.tavolo.crea_pile_gioco()
		self.tavolo.distribuisci_carte()

		# copri tutte le ultime carte delle pile base
		for i in range(7):
			pila = self.tavolo.pile[i]
			if pila.is_pila_base() and not self.is_game_running:
				pila.carte[-1].cover()

		# apre una alertbox per notificare l'apertura della partita specificando il livello impostato
		if self.is_game_running and not self.winner:
			self.create_alert_box("Livello di difficoltà impostato: %s" % self.difficulty_level, "Nuova partita creata")

	def nuova_partita(self):
		"""Crea un nuovo gioco del solitario."""
		self.winner = False
		self.is_time_over = False
		self.is_game_running = True

		# imposto il livello di difficoltà ed avvio la partita
		self.difficulty_level = self.get_difficulty_level()
		self.crea_gioco()

		# resetto cronometro partita e dati orologio
		self.clock = pygame.time.Clock()
		self.fps = 60
		self.start_ticks = pygame.time.get_ticks()
		return "avvio di una nuova partita in corso.  \n"

	def chiudi_partita(self):
		""" Chiude la partita aperta del solitario. """
		self.is_game_running = False
		self.winner = False
		self.is_time_over = False
		self.tavolo.crea_pile_gioco()
		self.tavolo.distribuisci_carte()
		# copri tutte le ultime carte delle pile base
		self.copri_tutto()

		self.conta_giri = 0
		self.conta_rimischiate = 0
		self.start_ticks = pygame.time.get_ticks()
		self.difficulty_level = 1
		self.cursor_pos = [0, 0]
		self.selected_card = []
		self.target_card = None
		self.origin_pile = None
		self.dest_pile = None
		return "partita attuale chiusa.  \n"

	#@@# sezione getter

	def get_difficulty_level(self):
		"""Richiede il livello di difficoltà tramite dialog box."""
		level = 1
		# richiediamo all'utente tramite dialog box il livello di difficoltà
		self.create_input_box("Inserisci il livello di difficoltà da 1 a 3.", "Configuro Nuova Partita")
		try: #verifichiamo che sia stato immesso un numero e che sia compreso tra 1 e 3.
			level = self.answare
			if not level.isdigit():
				raise ValueError

			level = int(level)
			if level < 1 or level > 3:
				raise ValueError

		except ValueError:
			self.create_alert_box("Livello di difficoltà non valido, impostato a 1.", "Livello di difficoltà")
			level = 1

		return level

	def get_info_carta(self):
		infocarta = ""
		row, col = self.cursor_pos
		pila = self.tavolo.pile[col]
		totcarte = pila.numero_carte()
		if totcarte > 0:
			carta = pila.get_carta(row)
			if not carta:
				return "non riesco ad identificare la carta alle coordinate specificate"

			id_carta = pila.get_card_index(carta)
			infocarta = carta.get_info_card
			infocarta += f"genitore:  {pila.nome}  \n"
			infocarta += f"pos in pila: {id_carta+1}  \n"
			return "scheda carta: %s\n" % infocarta

	def get_info_pila(self):
		infopila = ""
		row, col = self.cursor_pos
		pila = self.tavolo.pile[col]
		infopila = pila .get_pile_info()
		return "scheda pila: %s\n" % infopila

	def get_string_colonna(self):
		row, col = self.cursor_pos
		current_pile = self.tavolo.get_pile_name(col)
		if current_pile:
			string = current_pile
			string += self.get_top_card(self.tavolo.pile[col])
		else:
			string = "pila non riconosciuta.\n"

		return string

	def get_string_riga(self):
		row, col = self.cursor_pos
		current_card = self.tavolo.get_card_position(row, col)
		if not current_card:
			return "non riesco ad identificare la carta alle coordinate specificate"

		card_name = current_card.get_name
		return f"{row+1}: {card_name}"

	def get_focus(self):
		# vocalizziamo la posizione del cursore di navigazione
		row, col = self.cursor_pos
		pila = self.tavolo.pile[col]
		if pila.is_empty_pile():
			return "la pila è vuota!\n"

		current_card = self.tavolo.get_card_position(row, col)
		if not current_card:
			return "non riesco ad identificare la carta alle coordinate specificate"

		try:
			card_name = current_card.get_name
			string_carta = f"{pila.nome}.  "
			string_carta += f"{row+1}: {card_name}"
			string = string_carta

		except AttributeError:
			string = pila.get_name

		return string

	def get_origin(self):
		if not self.origin_pile:
			return "nessuna pila di origine selezionata"

		string = f"pila di origine: {self.origin_pile.nome}"
		string += f"tipo di pila: {self.origin_pile.tipo}"
		return string

	def get_dest(self):
		if not self.dest_pile:
			return "nessuna pila di destinazione selezionata"

		string = f"pila di destinazione: {self.dest_pile.nome}"
		string += f"tipo di pila: {self.dest_pile.tipo}"
		return string

	def get_selected_cards(self):
		if not self.selected_card:
			return "nessuna carta selezionata"

		tot = len(self.selected_card)
		string = f"carte selezionate: {tot}"
		string += f"carta da collegare: {self.target_card.get_name}"
		string += f"valore della carta: {self.target_card.get_value}"
		return string

	def get_top_card(self, pila):
		# vocalizziamo la carta in cima alla pila
		# se non è vuota
		string = "la pila è vuota!\n"
		if not pila.is_empty_pile():
			string = f"carta in cima: {pila.carte[-1].get_name}"

		return string

	def get_top_scarto(self):
		# vocalizziamo la carta in cima alla pila scarti se non è vuota
		string = "la pila scarti è vuota!\n"
		pila = self.tavolo.pile[11]
		if not pila.is_empty_pile():
			string = f"ultimo scarto: {pila.carte[-1].get_name}"

		return string

	def get_tot_dek(self):
		# vocalizziamo il numero di carte nel mazzo
		string = "il mazzo è vuoto!\n"
		mazzo = self.tavolo.pile[12]
		if not mazzo.is_empty_pile():
			string = f"carte nel mazzo: {mazzo.numero_carte()}"
		else:
			string = "il mazzo è vuoto!\n"

		return string

	def get_rimischiate(self):
		# vocalizza il numero di rimischiate effettuate dal giocatore
		rimischiate = self.conta_rimischiate
		return F"Fin'ora hai rimischiato gli scarti nel mazzo {rimischiate} volte.  \n"

	def get_mosse(self):
		# vocalizziamo il punteggionumero di spostamenti feseguiti dal player 
		mosse =  self.conta_giri
		return F"Fin'ora hai eseguito {mosse} spostamenti.\n"

	def get_time(self):
		if not self.is_game_running:
			return 0

		return (pygame.time.get_ticks() - self.start_ticks) // 1000

	def get_info_game(self):
		# vocalizza il numero di mosse ed il numero di rimischiate fatte dal giocatore
		if not self.is_game_running:
			return "nessuna partita in corso"

		string = "Partita in corso,  \n"
		elapsed_time = self.get_time()
		minuti = time.strftime("%M:%S", time.gmtime(elapsed_time))
		string += f"minuti trascorsi:  {minuti}.  \n"
		string += f"difficoltà impostata:  livello {self.difficulty_level}.  \n"
		string += f"Spostamenti totali:  {self.get_mosse()}  \n"
		string += f"Rimischiate:  {self.get_rimischiate()}  \n"
		return string

	def get_info_tavolo(self):
		#vocalizza le ultime carte di tutte le pile di tipo base
		string = "ultime carte sul tavolo:  \n"
		for pila in self.tavolo.pile:
			if pila.tipo == "base":
				string += f"{pila.nome}:  \n"
				if pila.is_empty_pile():
					string += "la pila è vuota!  \n"
				else:
					string += f"{pila.carte[-1].get_name}.  \n"

		# vocalizza il nuero totale dicarte nella pila scarti
		string += f"negli scarti ci sono:  {self.tavolo.pile[11].numero_carte()} Carte.  \n"
		# vocalizza il numero totale di carte nel mazzo
		string += f"Carte nel mazzo:  {self.tavolo.pile[12].numero_carte()} carte.  \n"
		return string

	def get_report_mossa(self):
		""" vocalizziamo il report della mossa """
		string = ""
		if self.selected_card:
			tot_cards = len(self.selected_card)
			string += "sposti:  \n"
			if tot_cards  > 3:
				string += f"{self.selected_card[0].get_name} e altre {tot_cards - 1} carte.  \n"
			else:
				for carta in self.selected_card:
					string += f"{carta.get_name}.  \n"

		if self.origin_pile:
			string += f"da: {self.origin_pile.nome},  \n"

		if self.dest_pile:
			string += f"a: {self.dest_pile.nome},  \n"
			id = (len(self.dest_pile.carte) - 1) - tot_cards
			if not self.dest_pile.carte[id].get_value != 13 and self.dest_pile.carte[id] != self.selected_card[0]:
				string += f"sopra alla carta: {self.dest_pile.carte[id].get_name}.  \n"

		if not self.origin_pile.is_empty_pile():
			string += f"hai scoperto : {self.origin_pile.carte[-1].get_name} in:  {self.origin_pile.nome}.  \n"

		return string

	#@@# sezione metodi di supporto

	def incrementa_mossa(self):
		if self.is_game_running:
			self.conta_giri += 1

	def copri_tutto(self):
		# copriamo tutte le carte del mazzo
		for i in range(0, 6):
			pila = self.tavolo.pile[i]
			if pila.is_pila_base() and not self.is_game_running:
				pila.carte[-1].cover()

	#@@# sezione metodi per il movimento del cursore di navigazione

	def move_cursor_up(self):
		pila = self.tavolo.pile[self.cursor_pos[1]]
		if not pila.is_pila_base():
			return "non sei su una pila base.\n"

		if pila.is_empty_pile():# and self.cursor_pos[0] == 0:
			return "La pila è vuota!  \n"

		if self.cursor_pos[0] > 0:
			self.cursor_pos[0] -= 1
			speack =self.get_string_riga()
			return speack

	def move_cursor_down(self):
		pila = self.tavolo.pile[self.cursor_pos[1]]
		if not pila.is_pila_base():
			return "non sei su una pila base.\n"

		if pila.is_empty_pile():# and self.cursor_pos[0] == 0:
			return "La pila è vuota!  \n"

		if self.cursor_pos[0] < len(pila.carte) - 1:
			self.cursor_pos[0] += 1
			speack = self.get_string_riga()
			return speack

	def move_cursor_left(self):
		pile = self.tavolo.pile
		if self.cursor_pos[1] > 0:
			self.cursor_pos[1] -= 1
			self.cursor_pos[0] = self.move_cursor_top_card(pile[self.cursor_pos[1]])
			speack = self.get_string_colonna()
			return speack

	def move_cursor_right(self):
		pile = self.tavolo.pile
		if self.cursor_pos[1] < len(pile) - 1:
			self.cursor_pos[1] += 1
			self.cursor_pos[0] = self.move_cursor_top_card(pile[self.cursor_pos[1]])
			speack = self.get_string_colonna()
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
				speack += self.get_string_colonna()
				return speack

			elif pile[i].tipo != tipo_iniziale:
				speack = f"pile {pile[i].tipo}:  \n"
				self.cursor_pos[1] = i
				self.cursor_pos[0] = self.move_cursor_top_card(pile[i])
				speack += self.get_string_colonna()
				return speack

	def move_cursor_to_base(self, pos):
		""" Sposta il cursore di navigazione sulla pila base richiesta """
		i = int(pos)
		pile = self.tavolo.pile
		self.cursor_pos[1] = i
		self.cursor_pos[0] = self.move_cursor_top_card(pile[i])
		speack = self.get_string_colonna()
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
		return "annullo carte selezionate!  \n"

	def select_scarto(self):
		# seleziona la carta in cima allo scarto
		string = ""
		if self.selected_card:
			return "Hai già selezionato le carte da spostare!  premi canc per annullare la selezione.\n"

		scarti = self.tavolo.pile[11]
		if scarti.is_empty_pile():
			return "la pila scarti è vuota!\n"

		self.selected_card.append(scarti.carte[-1])
		self.target_card = scarti.carte[-1]
		self.origin_pile = scarti
		return "carta selezionata: %s!\n" % self.target_card.get_name

	def select_card(self):
		""" seleziona le carte che il giocatore intende tentare di spostare """
		string = ""
		if self.selected_card:
			return "Hai già selezionato le carte da spostare!  premi canc per annullare la selezione.\n"

		row , col = self.cursor_pos
		pile = self.tavolo.pile[col]
		if pile.is_empty_pile():
			return "la pila è vuota!\n"

		if pile.carte[row].coperta:
			return "non puoi selezionare una carta coperta!\n"

		self.origin_pile = pile
		self.selected_card = pile.carte[row:]
		self.target_card = pile.carte[row]
		tot = len(self.selected_card)
		string = f"carte selezionate: {tot }\n"
		for card in self.selected_card:
			string += "%s, " % card.get_name

		return string[:-2] + "!\n"

	def execute_draw(self):
		""" esegue la pescata e ritorna le carte pescate """
		liv = int(self.difficulty_level)
		row = -1
		col = 11
		carte = []
		for i in range(liv):
			# pesco una carta dal mazzo
			carta = self.tavolo.get_card_position(row, col)
			carte.append(carta)
			row -= 1

		carte.reverse() # inverto l'ordine degli scarti
		return carte

	def pesca(self):
		""" pesca le carte dal mazzo riserve """
		carte = []
		liv = int(self.difficulty_level)
		ver = self.tavolo.pescata(liv)
		if not ver:
			self.tavolo.riordina_scarti()
			self.conta_rimischiate += 1
			return "Rimescolo gli scarti in mazzo riserve!  \n"

		# se la pescata è andata a buon fine ritorno la stringa da vocalizzare con le carte pescate
		carte = self.execute_draw()
		string = "hai pescato: "
		for carta in carte:
			string += "%s,  \n" % carta.get_name

		return string

	def set_destination_pile(self):
		row , col = self.cursor_pos
		pila = self.tavolo.pile[col]
		self.dest_pile = pila

	def reset_data_moving(self):
		# azzero i parametri utilizzati per gli spostamenti
		self.origin_pile = None
		self.dest_pile = None
		self.target_card = None
		self.selected_card = []

	def sposta_carte(self):
		string = "mossa non consentita!\n"
		if not self.selected_card:
			return "devi prima selezionare la carta da spostare!\n"

		self.set_destination_pile()
		dest_pila = self.dest_pile
		origin_pila = self.origin_pile
		cards = self.selected_card
		if self.tavolo.verifica_spostamenti(self.origin_pile, self.dest_pile, self.selected_card):
			# rimuovo le carte dalla pila di origine e le aggiungo a quella di destinazione
			self.tavolo.esegui_spostamento(self.origin_pile, self.dest_pile, cards)
			# scopro l'ultima carta della pila di origine, se è una pila base
			self.tavolo.scopri_ultima_carta(self.origin_pile)
			# alla fine di tutto:
			self.incrementa_mossa() # incremento il numero di mosse effettuate
			string = self.get_report_mossa()

			# verifichiamo la vittoria
			if self.dest_pile.is_pila_seme():
				ver_win = self.ceck_victory()
				if ver_win:
					string += ver_win

		# aggiorno la posizione del cursore
		self.cursor_pos[1] = self.dest_pile.id
		self.cursor_pos[0] = self.dest_pile.get_last_card_index()
		self.reset_data_moving() # resettiamo anche i dati di spostamento
		return string

	def ceck_victory(self):
		""" verifica se il giocatore ha vinto utilizzando il metodo verifica_vittoria del tavolo """
		if self.tavolo.verifica_vittoria():
			self.winner = True
			return "Complimenti!  \nHai vinto!\n"

		return False

	def ceck_lost(self):
		""" verifica se il giocatore ha perso controllando se la partita è durata più di 60 minuti """
		tempo_partita = self.get_tempo_partita()
		if self.tempo_partita > 3600:
			self.is_time_over = True
			return "Hai perso!  \nHai superato il tempo limite di 60 minuti!\n"

		return False



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
