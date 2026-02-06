"""
	file game_engine.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/game_engine.py

	Modulo per la gestione delle regole del gioco del solitario
"""

# lib
import sys, random, logging, time, pygame
# moduli personali
from my_lib.dialog_box import DialogBox
from scr.decks import FrenchDeck, NeapolitanDeck
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
#logger.debug("Il mio messaggio di debug")

class EngineData(DialogBox):
	""" Classe per la gestione delle regole del gioco del solitario """

	TIME_CHECK_EVENT = pygame.USEREVENT + 1 # ceck eventi pygame personalizzati

	def __init__(self, tavolo):
		super().__init__()
		self.tavolo = tavolo
		self.winner = False # variabile per gestire la vittoria del gioco
		self.is_time_over = False # variabile per gestire il tempo di gioco
		self.is_game_running = False # variabile per gestire il ciclo principale del gioco
		self.change_settings = False # variabile per gestire il cambio impostazioni
		self.difficulty_level = 1 # livello di difficoltà impostato dal giocatore
		self.max_time_game = -1 # tempo di gioco impostato dal giocatore
		self.conta_giri = 0 # contatore per gestire il numero di mosse fatte dal player
		self.conta_rimischiate = 0 # contatore per gestire il numero di rimischiate fatte dal player
		self.shuffle_discards = False # modalità riciclo scarti: False=inversione (default), True=mescolata
		# Tracciamento carte per seme (live)
		# Indici: 0=Cuori, 1=Quadri, 2=Fiori, 3=Picche
		self.carte_per_seme = [0, 0, 0, 0]
		# Contatore semi completati (live)
		self.semi_completati = 0
		self.cursor_pos = [0, 0]  # posizione iniziale del cursore sul tavolo
		self.selected_card = []  # lista delle carte selezionate dal giocatore
		self.target_card = None # oggetto carta nel focus
		self.origin_pile = None # salvo pila origine per gestione spostamenti
		self.dest_pile = None # salvo pile destinazione valide per gestione spostamenti
		
		# Tracciamento per double-tap navigation
		self.last_quick_move_pile = None  # Ultima pila con movimento rapido

		# inizializzo il tempo di gioco
		self.clock = pygame.time.Clock() # inizializzo il clock
		self.fps = 60 # imposto il numero di frame per secondo
		self.start_ticks = 0 # inizializzo il contatore dei secondi

		# Statistiche finali dell'ultima partita completata
		self.final_time_elapsed = 0  # tempo trascorso in secondi
		self.final_mosse = 0  # numero di spostamenti
		self.final_rimischiate = 0  # numero di rimischiate
		self.final_difficulty = 1  # livello di difficoltà della partita
		# Statistiche semi salvate
		self.final_carte_per_seme = [0, 0, 0, 0]
		self.final_semi_completati = 0


class EngineSolitario(EngineData):
	""" Classe per la gestione delle regole del gioco del solitario """

	TIME_CHECK_EVENT = pygame.USEREVENT + 1 # ceck eventi pygame personalizzati

	def __init__(self, tavolo):
		super().__init__(tavolo)

	def validate_cursor_position(self):
		"""Valida e corregge automaticamente la posizione del cursore se non è valida
		
		Effetti collaterali:
		- Modifica self.cursor_pos[0] e self.cursor_pos[1] in place
		- Se la colonna non è valida, viene impostata a 0
		- Se la riga non è valida, viene corretta al valore valido più vicino
		- Per pile vuote, la riga viene impostata a 0
		"""
		# Valida colonna
		col = self.cursor_pos[1]
		if col < 0 or col >= len(self.tavolo.pile):
			logger.warning(f"Colonna cursore non valida corretta: {col} -> 0")
			self.cursor_pos[1] = 0
			col = 0
		
		# Valida riga
		pila = self.tavolo.pile[col]
		if pila.is_empty_pile():
			if self.cursor_pos[0] != 0:
				logger.debug(f"Riga cursore su pila vuota corretta: {self.cursor_pos[0]} -> 0")
				self.cursor_pos[0] = 0
		elif self.cursor_pos[0] >= len(pila.carte):
			old_row = self.cursor_pos[0]
			self.cursor_pos[0] = len(pila.carte) - 1
			logger.warning(f"Riga cursore oltre limite corretta: {old_row} -> {self.cursor_pos[0]}")
		elif self.cursor_pos[0] < 0:
			logger.warning(f"Riga cursore negativa corretta: {self.cursor_pos[0]} -> 0")
			self.cursor_pos[0] = 0

	def test_set_time_out(self):
		# impostare manualmente il tempo a 60 minuti
		self.is_time_over = True
		return "test time over!  \n"

	def test_vittoria(self):
		# creiamo una simulazione di vittoria partita per testare il ceck nel ciclo principale
		self.winner = True
		return "test vittoria!  \n"

	#@@# sezione per la gestione del gioco @##@

	def notify_new_game(self):
		""" Notifica l'avvio di una nuova partita con una alert box. """

		minuti = self.max_time_game // 60
		str_notify = f"Avvio di una nuova partita in corso.\n\nMazzo in uso: {self.tavolo.mazzo.tipo}\nLivello di difficoltà impostato: {self.difficulty_level}"
		str_notify += f"\ntimer di gioco impostato a: {minuti} minuti.  \n"
		self.create_alert_box(str_notify, "Tavolo di gioco allestito")

	def crea_gioco(self):

		"""Crea un nuovo gioco del solitario."""
		self.tavolo.crea_pile_gioco()
		self.tavolo.distribuisci_carte()

		# copri tutte le ultime carte delle pile base
		for i in range(7):
			pila = self.tavolo.pile[i]
			if pila.is_pila_base() and not self.is_game_running:
				pila.carte[-1].set_cover()

		# apre una alertbox per notificare l'apertura della partita specificando il livello impostato
		if self.is_game_running and not self.winner:
			self.notify_new_game()

	def nuova_partita(self):
		"""Crea un nuovo gioco del solitario."""

		if self.change_settings:
			#self.create_alert_box("Chiudi prima le impostazioni partita.", "Impossibile procedere")
			#return
			self.change_settings = False

		# imposto le variabili di gioco
		self.winner = False
		self.is_time_over = False
		self.is_game_running = True
		self.crea_gioco()

		# resetto cronometro partita e dati orologio
		self.clock = pygame.time.Clock() # inizializzo il clock
		self.fps = 60 # imposto il numero di frame per secondo
		self.start_ticks = pygame.time.get_ticks() # inizializzo il contatore dei secondi
		pygame.time.set_timer(self.TIME_CHECK_EVENT, 1000)  # imposto il timer per il controllo del tempo residuo di gioco
		return True

	def stop_game(self):
		""" Ferma il gioco e salva le statistiche finali prima di resettare """
		
		# PRIMA salviamo le statistiche della partita appena conclusa
		if self.is_game_running:
			self.final_time_elapsed = self.get_time()
			self.final_mosse = self.conta_giri
			self.final_rimischiate = self.conta_rimischiate
			self.final_difficulty = self.difficulty_level
			# Salva statistiche semi
			self.final_carte_per_seme = self.carte_per_seme.copy()  # IMPORTANTE: usa .copy()!
			self.final_semi_completati = self.semi_completati
		
		# POI resettiamo tutto
		self.is_game_running = False
		self.winner = False
		self.tavolo.crea_pile_gioco()
		self.tavolo.distribuisci_carte()
		self.copri_tutto() # copri tutte le ultime carte delle pile base

		# Resetto cronometro e contatori per la PROSSIMA partita
		self.is_time_over = False
		self.conta_giri = 0
		self.conta_rimischiate = 0
		self.carte_per_seme = [0, 0, 0, 0]
		self.semi_completati = 0
		self.start_ticks = pygame.time.get_ticks()
		self.difficulty_level = 1
		self.cursor_pos = [0, 0]
		self.selected_card = []
		self.target_card = None
		self.origin_pile = None
		self.dest_pile = None
		self.shuffle_discards = False  # Reset modalità shuffle

	def chiudi_partita(self):
		""" Chiude la partita aperta del solitario. """

		self.stop_game()
		self.create_alert_box("Partita chiusa con successo, torno al menù di inizio partita.", "Chiusura della partita")
		return "partita chiusa.  \n"

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
		totcarte = pila.get_len()
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
		self.validate_cursor_position()
		row, col = self.cursor_pos
		current_pile = self.tavolo.get_pile_name(col)
		if current_pile:
			string = current_pile
			string += self.get_top_card(self.tavolo.pile[col])
		else:
			string = "pila non riconosciuta.\n"

		return string

	def get_string_riga(self):
		self.validate_cursor_position()
		row, col = self.cursor_pos
		current_card = self.tavolo.get_card_position(row, col)
		if not current_card:
			return "non riesco ad identificare la carta alle coordinate specificate"

		card_name = current_card.get_name
		return f"{row+1}: {card_name}"

	def get_focus(self):
		# vocalizziamo la posizione del cursore di navigazione
		self.validate_cursor_position()
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
			string = f"carte nel mazzo: {mazzo.get_len()}"

		return string

	def get_rimischiate(self):
		# vocalizza il numero di rimischiate effettuate dal giocatore
		rimischiate = self.conta_rimischiate
		return F"Fin'ora hai rimischiato gli scarti nel mazzo {rimischiate} volte.  \n"

	def get_mosse(self):
		# vocalizziamo il punteggionumero di spostamenti feseguiti dal player 
		mosse =  self.conta_giri
		return F"Fin'ora hai eseguito {mosse} spostamenti.\n"

	def get_statistiche_semi(self):
		"""
		Vocalizza le statistiche correnti delle pile semi.
		
		Returns:
			str: Statistiche formattate per screen reader
		"""
		if not self.is_game_running:
			return "Nessuna partita in corso.\n"
		
		# Nomi dinamici in base al mazzo
		nomi_semi_raw = self.tavolo.get_type_deck()  # ["cuori", ...] o ["bastoni", ...]
		nomi_semi = [seme.capitalize() for seme in nomi_semi_raw]
		carte_per_seme_completo = len(self.tavolo.mazzo.VALUES)  # 13 o 10
		
		string = "Statistiche pile semi:  \n"
		
		for i in range(4):
			num_carte = self.carte_per_seme[i]
			nome_seme = nomi_semi[i]
			string += f"{nome_seme}: {num_carte} su {carte_per_seme_completo} carte.  \n"
		
		string += f"\nHai completato {self.semi_completati} semi su 4.  \n"
		
		return string

	def get_time(self):
		if not self.is_game_running:
			return 0

		return (pygame.time.get_ticks() - self.start_ticks) // 1000

	def get_int_timer_status(self):
		""" torna lo stato del timer in secondi """
		timer = self.max_time_game
		timer_minuti = timer // 60
		tempo_trascorso = self.get_time()
		return timer - tempo_trascorso

	def get_time_status(self):
		""" torna lo stato del timer in formato di tempo """
		secondi = self.get_time()
		minuti = time.strftime("%M:%S", time.gmtime(secondi))
		return minuti

	def get_timer_status(self):
		""" vocalizza lo stato del timer """

		if self.max_time_game == 0:
			return "timer disattivato!  \n"

		secondi_rimanenti = self.get_int_timer_status()
		 #per avere un formato di tempo simile a 00:00
		tempo_rimanente = time.strftime("%M:%S", time.gmtime(secondi_rimanenti))
		return f"Minuti mancanti:  {tempo_rimanente} secondi.  \n"

	def get_report_game(self):
		""" vocalizza il report finale della partita """
		
		string = ""
		# Nomi dei semi per output leggibile
		nomi_semi = ["Cuori", "Quadri", "Fiori", "Picche"]
		
		# Se la partita è terminata, usa le statistiche finali salvate
		if not self.is_game_running:
			string = "Partita terminata,  \n"
			
			# Usa le statistiche salvate da stop_game()
			secondi_trascorsi = self.final_time_elapsed
			minuti_trascorsi = time.strftime("%M:%S", time.gmtime(secondi_trascorsi))
			
			# Mostra timer impostato solo se era attivo
			if self.max_time_game > 0:
				timer_minuti = self.max_time_game // 60
				string += f"timer impostato a:  {timer_minuti} minuti.  \n"
			
			string += f"minuti trascorsi:  {minuti_trascorsi}.  \n"
			string += f"difficoltà impostata:  livello {self.final_difficulty}.  \n"
			string += f"Spostamenti totali:  {self.final_mosse}.  \n"
			string += f"Rimischiate:  {self.final_rimischiate}.  \n"
			
			# Statistiche semi
			string += "\n--- Statistiche Pile Semi ---\n"
			
			# Mostra carte per ogni seme
			for i in range(4):
				num_carte = self.final_carte_per_seme[i]
				nome_seme = nomi_semi[i]
				string += f"{nome_seme}: {num_carte} carte.  \n"
			
			# Mostra semi completati
			string += f"\nSemi completati: {self.final_semi_completati} su 4.  \n"
			
			# Percentuale completamento totale
			totale_carte_semi = sum(self.final_carte_per_seme)
			# Calcola totale carte del mazzo in uso
			totale_carte_mazzo = self.tavolo.mazzo.get_total_cards()  # 52 o 40
			percentuale = (totale_carte_semi / totale_carte_mazzo) * 100
			string += f"Completamento totale: {totale_carte_semi}/{totale_carte_mazzo} carte ({percentuale:.1f}%).  \n"
		
		# Se la partita è in corso, usa i contatori live
		else:
			string = "Partita in corso,  \n"
			
			timer = self.max_time_game
			tempo_rimanente = self.get_timer_status()
			if timer > 0:
				timer_minuti = timer // 60
				string += f"timer impostato a:  {timer_minuti} minuti.  \n"
				string += f"timer:  {tempo_rimanente}.  \n"
			
			minuti = self.get_time_status()
			string += f"minuti trascorsi:  {minuti}.  \n"
			string += f"difficoltà impostata:  livello {self.difficulty_level}.  \n"
			string += f"Spostamenti totali:  {self.conta_giri}.  \n"
			string += f"Rimischiate:  {self.conta_rimischiate}.  \n"
			
			# Statistiche semi live
			string += "\n--- Statistiche Pile Semi ---\n"
			
			for i in range(4):
				num_carte = self.carte_per_seme[i]
				nome_seme = nomi_semi[i]
				string += f"{nome_seme}: {num_carte} carte.  \n"
			
			string += f"\nSemi completati: {self.semi_completati} su 4.  \n"
			
			totale_carte_semi = sum(self.carte_per_seme)
			# Calcola totale carte del mazzo in uso
			totale_carte_mazzo = self.tavolo.mazzo.get_total_cards()  # 52 o 40
			percentuale = (totale_carte_semi / totale_carte_mazzo) * 100
			string += f"Completamento totale: {totale_carte_semi}/{totale_carte_mazzo} carte ({percentuale:.1f}%).  \n"
		
		return string

	def get_info_game(self):
		""" vocalizza il numero di mosse ed il numero di rimischiate fatte dal giocatore """
		if not self.is_game_running:
			return "nessuna partita in corso"

		string = self.get_report_game()
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
		string += f"negli scarti ci sono:  {self.tavolo.pile[11].get_len()} Carte.  \n"
		# vocalizza il numero totale di carte nel mazzo
		string += f"Carte nel mazzo:  {self.tavolo.pile[12].get_len()} carte.  \n"
		return string

	def get_report_mossa(self):
		""" vocalizziamo il report della mossa """
		
		string = ""
		tot_cards = 0
		if self.selected_card:
			tot_cards = len(self.selected_card)
			string += "sposti:  \n"
			if tot_cards > 2:
				string += f"{self.selected_card[0].get_name} e altre {tot_cards - 1} carte.  \n"
			else:
				for carta in self.selected_card:
					string += f"{carta.get_name}.  \n"

		if self.origin_pile:
			string += f"da: {self.origin_pile.nome},  \n"

		if self.dest_pile:
			string += f"a: {self.dest_pile.nome},  \n"
			
			# Verifica che ci siano abbastanza carte e che l'indice sia valido
			if tot_cards > 0 and len(self.dest_pile.carte) > tot_cards:
				id = len(self.dest_pile.carte) - tot_cards - 1
				
				# Verifica bounds dell'indice
				if 0 <= id < len(self.dest_pile.carte):
					carta_sotto = self.dest_pile.carte[id]
					
					# Mostra la carta sotto SOLO se NON è un Re E NON è la carta selezionata stessa
					if carta_sotto.get_value != 13 and carta_sotto != self.selected_card[0]:
						string += f"sopra alla carta: {carta_sotto.get_name}.  \n"

		# Verifica che origin_pile non sia None prima di controllare se è vuota
		if self.origin_pile and not self.origin_pile.is_empty_pile():
			string += f"hai scoperto : {self.origin_pile.carte[-1].get_name} in:  {self.origin_pile.nome}.  \n"
		
		return string


	#@@# sezione metodi di supporto

	def incrementa_mossa(self):
		if self.is_game_running:
			self.conta_giri += 1

	def aggiorna_statistiche_semi(self):
		"""
		Aggiorna le statistiche delle carte nelle pile semi.
		
		Conta quante carte ci sono in ogni pila seme e quanti semi sono completi.
		Chiamato dopo ogni spostamento verso una pila seme.
		
		Effetti collaterali:
		- Aggiorna self.carte_per_seme[0-3]
		- Aggiorna self.semi_completati
		"""
		if not self.is_game_running:
			return
		
		# Ottieni il numero di carte necessarie per completare un seme
		carte_per_seme_completo = len(self.tavolo.mazzo.VALUES)  # 13 o 10
		
		# Reset contatore semi completati per ricalcolo
		self.semi_completati = 0
		
		# Itera sulle 4 pile semi (indici 7-10)
		for i in range(4):
			pile_index = 7 + i  # Pile semi sono alle posizioni 7, 8, 9, 10
			pila_seme = self.tavolo.pile[pile_index]
			
			# Conta carte nella pila
			num_carte = pila_seme.get_len()
			self.carte_per_seme[i] = num_carte
			
			# Un seme è completo se ha tutte le carte (13 per francese, 10 per napoletano)
			if num_carte == carte_per_seme_completo:
				self.semi_completati += 1

	def copri_tutto(self):
		# copriamo tutte le carte del mazzo
		for i in range(0, 7):
			pila = self.tavolo.pile[i]
			if pila.is_pila_base() and not self.is_game_running:
				if not pila.is_empty_pile():
					pila.carte[-1].set_cover()

	def change_deck_type(self):
		""" cambiamo il tipo di mazzo """
		
		mazzo = None
		if self.is_game_running:
			return "Non puoi modificare il tipo di mazzo durante una partita!  \n"

		# Rimosso il controllo self.change_settings - ora funziona sia dentro che fuori dalle opzioni
		
		deck_type = self.tavolo.mazzo.get_type()
		if deck_type == "carte francesi":
			mazzo = NeapolitanDeck()
		elif deck_type == "carte napoletane":
			mazzo = FrenchDeck()
		else:
			mazzo = FrenchDeck()

		self.tavolo.mazzo = mazzo
		self.tavolo.reset_pile()
		return f"tipo di mazzo impostato a: {self.tavolo.mazzo.tipo}.  \n"

	def change_difficulty_level(self):
		""" cambiamo il livello di difficoltà """

		if self.is_game_running:
			return "Non puoi modificare il livello di difficoltà durante una partita!  \n"

		#level = self.difficulty_level
		level = self.difficulty_level
		if level == 1:
			level = 2
		elif level == 2:
			level = 3
		else:
			level = 1

		#if level:
		self.difficulty_level = int(level)
		#self.create_alert_box(f"Livello di difficoltà impostato a {self.difficulty_level}\n", "difficoltà cambiata")
		return F"livello di difficoltà impostato a:  {self.difficulty_level}.  \n"

	def change_game_time(self, increment=True):
		""" cambiamo il limite massimo di tempo iocabile """

		if self.is_game_running:
			return "Non puoi modificare il limite massimo per il tempo di gioco durante una partita!  \n"

		elif not self.is_game_running and self.change_settings:
			#timer = self.set_game_timer()
			timer = self.change_time_over(increment)
			secondi = int(timer) * 60
			minuti = int(timer)
			if secondi > 0:
				self.max_time_game = secondi
			else:
				self.max_time_game = -1

			msg_box = f"Il timer è stato disattivato!  \n"
			if secondi > 0:
				msg_box = f"Timer impostato a:  {minuti} minuti.  \n"

			#self.create_alert_box(msg_box, "impostazione del timer")
			return msg_box

	def disable_timer(self):
		""" disabilitiamo il timer """
		
		if not self.is_game_running and self.change_settings:
			self.max_time_game = -1
			return "il timer è stato disattivato!  \n"
		
		if self.is_game_running:
			return "Non puoi disabilitare il timer durante una partita!  \n"
		else:
			return "Devi prima aprire le opzioni con il tasto O!  \n"

	def change_time_over(self, increment=True):
		""" permette di personalizzare il tempo limite per il tempo di gioco """

		timer = 0
		min_settable = 5 * 60  # minimo durata per il timer 5 minuti
		max_settable = 60 * 60 # massima durata pe ril timer 60 minuti
		
		if self.max_time_game < 0:
			timer = 5

		elif increment and self.max_time_game >= max_settable:
			timer = self.max_time_game // 60
			timer = -1

		elif not increment and self.max_time_game <= min_settable:
			# Se siamo al minimo e stiamo decrementando, disabilitiamo il timer
			timer = -1

		else:
			timer = self.max_time_game // 60
			if increment:
				timer += 5
			else:
				timer -= 5

		return timer

	def set_game_timer(self):
		""" impostiamo il limite massimo di tempo iocabile """

		self.create_input_box("impostare il limite massimo di tempo di gioco", "impostazione del timer")
		timer = self.answare
		if timer:
			if timer.isdigit():
				if int(timer) > 0:
					return timer

		return -1

	def toggle_shuffle_mode(self):
		""" alterna tra modalità inversione e mescolata per riciclo scarti """
		
		if self.is_game_running:
			return "Non puoi modificare la modalità di riciclo scarti durante una partita!  \n"
		
		elif not self.is_game_running and self.change_settings:
			self.shuffle_discards = not self.shuffle_discards
			if self.shuffle_discards:
				return "Modalità riciclo scarti: MESCOLATA CASUALE.  \n"
			else:
				return "Modalità riciclo scarti: INVERSIONE SEMPLICE.  \n"
		
		else:
			return "Devi prima aprire le opzioni con il tasto O!  \n"

	def get_shuffle_mode_status(self):
		""" restituisce lo stato della modalità riciclo scarti """
		
		if self.shuffle_discards:
			return "Modalità riciclo scarti: MESCOLATA CASUALE"
		else:
			return "Modalità riciclo scarti: INVERSIONE SEMPLICE"

	def get_settings_info(self):
		""" vocalizza le impostazioni correnti di gioco """
		
		string = "Impostazioni di gioco:  \n"
		
		# Livello di difficoltà
		string += f"Livello di difficoltà: {self.difficulty_level}.  \n"
		
		# Timer
		if self.max_time_game < 0:
			string += "Timer: disattivato.  \n"
		else:
			minuti = self.max_time_game // 60
			string += f"Timer: {minuti} minuti.  \n"
		
		# Modalità riciclo scarti
		string += f"{self.get_shuffle_mode_status()}.  \n"
		
		return string


	def change_game_settings(self):
		""" cambiamo le impostazioni del gioco """

		if self.is_game_running:
			return "Non puoi modificare le impostazioni di gioco durante una partita!  \n"

		elif not self.is_game_running and self.change_settings:
			self.change_settings = False
			return "impostazioni di gioco chiuse.  \n"

		elif not self.is_game_running and not self.change_settings:
			self.change_settings = True
			return "impostazioni di gioco aperte.  \n"

	#@@# sezione metodi per il movimento del cursore di navigazione

	def move_cursor_up(self):
		self.last_quick_move_pile = None  # Reset tracking on manual movement
		col = self.cursor_pos[1]
		pila = self.tavolo.pile[col]
		
		# Gestione pila base (comportamento esistente)
		if pila.is_pila_base():
			if pila.is_empty_pile():
				self.cursor_pos[0] = 0
				return "La pila è vuota!  \n"
			
			# Valida prima l'indice corrente
			if self.cursor_pos[0] >= len(pila.carte):
				self.cursor_pos[0] = len(pila.carte) - 1
			
			if self.cursor_pos[0] > 0:
				self.cursor_pos[0] -= 1
				speack = self.get_string_riga()
				return speack
			else:
				return "Sei già alla prima carta della pila!\n"
		
		# Gestione pila scarti
		elif col == 11:
			if pila.is_empty_pile():
				return "Scarti vuoti, nessuna carta da consultare.\n"
			
			# Valida prima l'indice corrente
			if self.cursor_pos[0] >= len(pila.carte):
				self.cursor_pos[0] = len(pila.carte) - 1
			
			if self.cursor_pos[0] > 0:
				self.cursor_pos[0] -= 1
				posizione = self.cursor_pos[0] + 1
				totale = len(pila.carte)
				carta = pila.carte[self.cursor_pos[0]]
				
				# Hint solo per ultima carta
				is_last = (self.cursor_pos[0] == totale - 1)
				hint = " Premi CTRL+INVIO per selezionare." if is_last else ""
				
				return f"{posizione} di {totale}: {carta.get_name}{hint}\n"
			else:
				return "Sei già alla prima carta degli scarti!\n"
		
		# Pile semi/mazzo non consultabili
		else:
			return "Questa pila non è consultabile con le frecce.\n"

	def move_cursor_down(self):
		self.last_quick_move_pile = None  # Reset tracking on manual movement
		col = self.cursor_pos[1]
		pila = self.tavolo.pile[col]
		
		# Gestione pila base (comportamento esistente)
		if pila.is_pila_base():
			if pila.is_empty_pile():
				self.cursor_pos[0] = 0
				return "La pila è vuota!  \n"
			
			# Valida prima l'indice corrente
			if self.cursor_pos[0] >= len(pila.carte):
				self.cursor_pos[0] = len(pila.carte) - 1
			
			if self.cursor_pos[0] < len(pila.carte) - 1:
				self.cursor_pos[0] += 1
				speack = self.get_string_riga()
				return speack
			else:
				return "Sei già all'ultima carta della pila!\n"
		
		# Gestione pila scarti
		elif col == 11:
			if pila.is_empty_pile():
				return "Scarti vuoti, nessuna carta da consultare.\n"
			
			# Valida prima l'indice corrente
			if self.cursor_pos[0] >= len(pila.carte):
				self.cursor_pos[0] = len(pila.carte) - 1
			
			if self.cursor_pos[0] < len(pila.carte) - 1:
				self.cursor_pos[0] += 1
				posizione = self.cursor_pos[0] + 1
				totale = len(pila.carte)
				carta = pila.carte[self.cursor_pos[0]]
				
				# Hint solo per ultima carta
				is_last = (self.cursor_pos[0] == totale - 1)
				hint = " Premi CTRL+INVIO per selezionare." if is_last else ""
				
				return f"{posizione} di {totale}: {carta.get_name}{hint}\n"
			else:
				return "Sei già all'ultima carta degli scarti!\n"
		
		# Pile semi/mazzo non consultabili
		else:
			return "Questa pila non è consultabile con le frecce.\n"

	def move_cursor_to_first(self):
		"""Sposta il cursore alla prima carta della pila corrente (tasto HOME).
		
		Supportato su:
		- Pile base (0-6)
		- Pila scarti (11)
		
		Bloccato su:
		- Pile semi (7-10) - usa SHIFT+(1-4) per accesso rapido
		- Mazzo (12) - non consultabile
		
		Returns:
			str: Messaggio vocale per screen reader
		"""
		self.last_quick_move_pile = None
		col = self.cursor_pos[1]
		pila = self.tavolo.pile[col]
		
		# Pile base e scarti: supportate
		if pila.is_pila_base() or col == 11:
			if pila.is_empty_pile():
				return "La pila è vuota!\n"
			
			self.cursor_pos[0] = 0
			carta = pila.carte[0]
			
			if col == 11:  # Scarti
				totale = len(pila.carte)
				return f"1 di {totale}: {carta.get_name} Prima carta.\n"
			else:  # Pila base
				return f"1: {carta.get_name} Prima carta.\n"
		
		# Mazzo: non consultabile
		elif col == 12:
			return "Il mazzo non è consultabile.\n"
		
		# Pile semi: suggerisci alternativa
		else:
			return "Pile semi non consultabili. Usa SHIFT+(1-4) per accesso rapido.\n"

	def move_cursor_to_last(self):
		"""Sposta il cursore all'ultima carta della pila corrente (tasto END).
		
		Supportato su:
		- Pile base (0-6)
		- Pila scarti (11)
		
		Bloccato su:
		- Pile semi (7-10) - usa SHIFT+(1-4) per accesso rapido
		- Mazzo (12) - non consultabile
		
		Returns:
			str: Messaggio vocale per screen reader
		"""
		self.last_quick_move_pile = None
		col = self.cursor_pos[1]
		pila = self.tavolo.pile[col]
		
		# Pile base e scarti: supportate
		if pila.is_pila_base() or col == 11:
			if pila.is_empty_pile():
				return "La pila è vuota!\n"
			
			self.cursor_pos[0] = len(pila.carte) - 1
			carta = pila.carte[-1]
			
			if col == 11:  # Scarti
				totale = len(pila.carte)
				hint = " Premi CTRL+INVIO per selezionare." if totale > 0 else ""
				return f"{totale} di {totale}: {carta.get_name} Ultima carta.{hint}\n"
			else:  # Pila base
				return f"{len(pila.carte)}: {carta.get_name} Ultima carta.\n"
		
		# Mazzo: non consultabile
		elif col == 12:
			return "Il mazzo non è consultabile.\n"
		
		# Pile semi: suggerisci alternativa
		else:
			return "Pile semi non consultabili. Usa SHIFT+(1-4) per accesso rapido.\n"

	def move_cursor_left(self):
		self.last_quick_move_pile = None  # Reset tracking on manual movement
		pile = self.tavolo.pile
		if self.cursor_pos[1] > 0:
			self.cursor_pos[1] -= 1
			self.validate_cursor_position()
			pila = self.tavolo.pile[self.cursor_pos[1]]
			self.cursor_pos[0] = self.move_cursor_top_card(pila)
			speack = self.get_string_colonna()
			return speack

	def move_cursor_right(self):
		self.last_quick_move_pile = None  # Reset tracking on manual movement
		pile = self.tavolo.pile
		if self.cursor_pos[1] < len(pile) - 1:
			self.cursor_pos[1] += 1
			self.validate_cursor_position()
			pila = self.tavolo.pile[self.cursor_pos[1]]
			self.cursor_pos[0] = self.move_cursor_top_card(pila)
			speack = self.get_string_colonna()
			return speack

	def move_cursor_pile_type(self):
		""" Sposta il cursore di navigazione sulla prima pila di tipo diverso da quello iniziale"""
		self.last_quick_move_pile = None  # Reset tracking on manual movement
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
		""" Sposta il cursore di navigazione in cima alla pila in cui ci si trova durante lo spostamento con le frecce orizzontali"""
		if not pila.is_empty_pile():
			return len(pila.carte) - 1
		return 0  # Ritorna 0 invece di None per pile vuote

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

	def move_cursor_to_pile_with_select(self, pile_index):
		"""
		Movimento rapido su pila con possibilità double-tap.
		
		Comportamento:
		- 1° tap: sposta cursore su pila
		- 2° tap consecutivo: seleziona ultima carta (pile base/semi) o azione speciale (scarti/mazzo)
		
		Args:
			pile_index (int): Indice pila (0-6 base, 7-10 semi, 11 scarti, 12 mazzo)
		
		Returns:
			str: Messaggio vocale per screen reader
		"""
		
		current_pile = self.cursor_pos[1]
		pila = self.tavolo.pile[pile_index]
		
		# --- DOUBLE-TAP DETECTED ---
		if current_pile == pile_index and self.last_quick_move_pile == pile_index:
			
			# CASO SPECIALE: MAZZO (pila 12)
			if pile_index == 12:
				self.last_quick_move_pile = None
				return "Cursore già su mazzo.\n"
			
			# CASO SPECIALE: SCARTI (pila 11)
			if pile_index == 11:
				self.last_quick_move_pile = None
				return "Cursore già su scarti.\n"
			
			# PILE BASE/SEMI: Validazioni per selezione
			if pila.is_empty_pile():
				self.last_quick_move_pile = None
				return "Pila vuota, nessuna carta da selezionare.\n"
			
			# Auto-deseleziona vecchia selezione se presente
			msg_deselect = ""
			if self.selected_card:
				self.cancel_selected_cards()  # Reset interno (non vocalizzare)
				msg_deselect = "Selezione precedente annullata. "
			
			# Sposta cursore sull'ultima carta selezionabile
			self.cursor_pos[0] = self.move_cursor_top_card(pila)
			
			# Tenta selezione
			msg = self.select_card()
			
			# Reset tracking dopo selezione
			self.last_quick_move_pile = None
			
			return msg_deselect + msg
		
		# --- PRIMO TAP: SPOSTA CURSORE ---
		else:
			# Sposta cursore su pila
			self.cursor_pos[1] = pile_index
			self.cursor_pos[0] = self.move_cursor_top_card(pila)
			
			# Aggiorna tracking
			self.last_quick_move_pile = pile_index
			
			# Genera messaggio vocale
			msg = self.get_string_colonna()
			
			# HINT VOCALE: Aggiungi suggerimento appropriato
			if pile_index == 12:
				# MAZZO: hint per pescare
				if not pila.is_empty_pile():
					msg += "Premi INVIO per pescare.\n"
				else:
					msg += "Mazzo vuoto.\n"
			
			elif pile_index == 11:
				# SCARTI: hint per navigare/selezionare
				if not pila.is_empty_pile():
					msg += "Usa frecce per navigare. CTRL+INVIO per selezionare ultima carta.\n"
				else:
					msg += "Scarti vuoti.\n"
			
			elif not pila.is_empty_pile():
				# PILE BASE/SEMI: hint per selezionare
				if pila.is_pila_base():
					tasto = str(pile_index + 1)  # 1-7
					msg += f"Premi ancora {tasto} per selezionare.\n"
				elif pila.is_pila_seme():
					seme_num = pile_index - 6  # 7->1, 8->2, 9->3, 10->4
					msg += f"Premi ancora SHIFT+{seme_num} per selezionare.\n"
			
			return msg


	#@@# sezione metodi per selezionare e deselezionare le carte

	def cancel_selected_cards(self):
		if not self.selected_card :
			return "non hai selezionato nessuna carta!  \n"

		self.selected_card = []
		self.target_card = None
		self.origin_pile = None
		self.dest_pile = None
		self.last_quick_move_pile = None  # Reset tracking on cancel
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

		self.validate_cursor_position()
		row , col = self.cursor_pos
		pile = self.tavolo.pile[col]
		
		# NUOVO: ENTER su mazzo = pesca
		if col == 12:
			return self.pesca()
		
		if pile.is_empty_pile():
			return "la pila è vuota!\n"

		if pile.carte[row].get_covered:
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

	def _genera_messaggio_carte_pescate(self, lista_carte):
		"""Genera il messaggio vocale per le carte pescate."""
		msg = "hai pescato: "
		for c in lista_carte:
			msg += "%s,  \n" % c.get_name
		return msg

	def _esegui_rimescolamento_e_pescata(self):
		"""Rimescola gli scarti nel mazzo e pesca automaticamente."""
		self.tavolo.riordina_scarti(self.shuffle_discards)
		self.conta_rimischiate += 1
		
		# Prepara messaggio rimescolamento
		if self.shuffle_discards:
			msg_rimescola = "Rimescolo gli scarti in modo casuale nel mazzo riserve!  \n"
		else:
			msg_rimescola = "Rimescolo gli scarti in mazzo riserve!  \n"
		
		# Auto-draw: tenta pescata automatica dopo rimescolamento
		livello = int(self.difficulty_level)
		pescata_ok = self.tavolo.pescata(livello)
		
		if not pescata_ok:
			# Mazzo ancora vuoto dopo rimescolamento (edge case)
			return msg_rimescola + "Attenzione: mazzo vuoto, nessuna carta da pescare!  \n"
		
		# Pescata riuscita: ottieni carte e genera messaggio completo
		carte_pescate = self.execute_draw()
		msg_pescata = self._genera_messaggio_carte_pescate(carte_pescate)
		
		return msg_rimescola + "Pescata automatica: " + msg_pescata

	def pesca(self):
		""" pesca le carte dal mazzo riserve """
		livello = int(self.difficulty_level)
		pescata_riuscita = self.tavolo.pescata(livello)
		
		if not pescata_riuscita:
			# Mazzo vuoto: rimescola scarti e pesca automaticamente
			return self._esegui_rimescolamento_e_pescata()

		# Pescata normale andata a buon fine
		carte_pescate = self.execute_draw()
		return self._genera_messaggio_carte_pescate(carte_pescate)

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
				self.aggiorna_statistiche_semi()  # NUOVA LINEA: aggiorna statistiche semi
				ver_win = self.ceck_victory()
				if ver_win:
					string += ver_win

		# CORREZIONE: Aggiorno la posizione del cursore con validazione
		self.cursor_pos[1] = self.dest_pile.id
		if not self.dest_pile.is_empty_pile():
			self.cursor_pos[0] = self.dest_pile.get_last_card_index()
		else:
			self.cursor_pos[0] = 0

		self.reset_data_moving() # resettiamo anche i dati di spostamento
		self.last_quick_move_pile = None  # Reset tracking after move
		return string

	def ceck_victory(self):
		""" verifica se il giocatore ha vinto utilizzando il metodo verifica_vittoria del tavolo """

		if self.tavolo.verifica_vittoria():
			self.winner = True
			return True

		return False

	def ceck_lost_by_time(self):
		""" verifica se il giocatore ha perso controllando se la partita è durata più del tempo impostato """

		tempo_partita = self.get_time()
		time_out = self.max_time_game
		if tempo_partita > time_out:
			self.is_time_over = True
			return True

		return False

	def you_lost_by_time(self):
		""" metodo che viene chiamato quando il giocatore perde per tempo scaduto """
		
		# PRIMA salva le statistiche
		self.stop_game()
		
		# POI genera il messaggio usando le statistiche salvate
		timer = self.max_time_game // 60
		str_lost = f"Hai perso!  \nHai superato il tempo limite di {timer} minuti!  \n\n"
		str_lost += self.get_report_game()
		
		self.create_alert_box(str_lost, "Tempo scaduto")
		self.create_yes_or_no_box("Vuoi giocare ancora?", "Rivincita?")
		if self.answare:
			self.nuova_partita()
		else:
			self.chiudi_partita()

	def you_winner(self):
		""" metodo che viene chiamato quando il giocatore vince """
		
		# PRIMA genera il report (mentre i dati sono ancora disponibili)
		str_win = f"Hai Vinto!  \nComplimenti, vittoria spumeggiante!  \n\n"
		
		# stop_game() salverà le statistiche e poi resetterà i contatori
		self.stop_game()
		
		# Ora usa get_report_game() che leggerà le statistiche salvate
		str_win += self.get_report_game()
		
		self.create_alert_box(str_win, "Congratulazioni")
		self.create_yes_or_no_box("Vuoi giocare ancora?", "Rivincita?")
		if self.answare:
			self.nuova_partita()
		else:
			self.chiudi_partita()



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
