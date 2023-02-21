"""
	file pygame_menu.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/pygame_menu.py

"""
class PyMenu:
	def __init__(self, items, callback, screen_reader):
		self.items = items
		self.selected_item = 0
		self.callback = callback
		self.speack = screen_reader

	def build_commands_list(self):
		#@@# sezione dizionari per la gestione del comandi di gioco

		# quando il tasto viene premuto
		self.EVENTS_DN = {
			pygame.K_ESCAPE: self.esc_press,
		}

		# quando il tasto viene rilasciato
		self.EVENTS_UP = {}

	def handle_keyboard_EVENTS(self):
		""" metodo per la gestione degli eventi da tastiera """
		for event in pygame.event.get():
			# processa gli eventi in coda
			pygame.event.pump()
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

			elif event.type == KEYDOWN:
				if self.EVENTS_DN.get(event.key):
					self.EVENTS_DN[event.key]()

			elif event.type == KEYUP:
				if self.EVENTS_UP.get(event.key):
					self.EVENTS_UP[event.key]()
				else:
					self.vocalizza("Comando non supportato!\n")

	def next_item(self):
		self.selected_item = (self.selected_item + 1) % len(self.items)
		self.speack.vocalizza(self.items[self.selected_item])

	def prev_item(self):
		self.selected_item = (self.selected_item - 1) % len(self.items)
		self.speack.vocalizza(self.items[self.selected_item])

	def execute(self):
		self.callback(self.selected_item)
