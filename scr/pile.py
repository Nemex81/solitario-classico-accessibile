"""
	file pile.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr/file pile.py

	Modulo per la gestione delle pile di gioco
"""
#lib
from scr.cards import Carta, Mazzo

class Pila:
	def __init__(self, nome):
		self.nome = nome
		self.carte = []

	def aggiungi_carta(self, carta):
		self.carte.append(carta)

	def rimuovi_carta(self, pos=-1):
		return self.carte.pop(pos)

	def aggiungi_carte(self, carte):
		self.carte += carte

	def rimuovi_carte(self, num_carte):
		if num_carte > len(self.carte):
			raise ValueError("Impossibile rimuovere più carte di quelle presenti nella pila.")
		carte_rimosse = self.carte[-num_carte:]
		self.carte = self.carte[:-num_carte]
		return carte_rimosse

	def is_vuota(self):
		return len(self.carte) == 0

	def get_nome(self):
		return self.nome

	def get_carte(self):
		return self.carte

	def get_cima(self):
		if self.is_vuota():
			return None
		return self.carte[-1]

	def get_dim(self):
		return len(self.carte)

	def reset(self):
		"""Rimuove tutte le carte dalla pila"""
		self._carte = []

	def is_vuota(self):
		"""Restituisce True se la pila è vuota, False altrimenti"""
		return len(self._carte) == 0



class PileGioco:
	def __init__(self):
		self.pile = {}
		self.mazzo = Mazzo()
		self.reset()  # resetta il tavolo di gioco ai valori di nuova partita

	def crea_pile_gioco(self):
		for i in range(1, 8):
			nome_pila = f"pila{i}"
			self.pile[nome_pila] = Pila(nome_pila)
		for seme in Mazzo.SUITES:
			self.pile[seme] = Pila(seme)
		self.pile['scarti'] = Pila('scarti')
		self.pile['mazzo_riserve'] = Pila('mazzo_riserve')

	def get_pila(self, nome):
		return self.pile[nome]

	def pesca(self):
		if len(self.mazzo.carte) == 0:
			carte_scartate = self.pile['scarti'].rimuovi_carte(1)
			self.mazzo.carte = self.mazzo.crea_mazzo(carte_scartate)
			self.pile['scarti'].aggiungi_carte(self.mazzo.carte)
			self.mazzo.carte = []

		carta_pescata = self.mazzo.pesca()
		return carta_pescata

	def reset(self):
		self.pile = {}
		self.crea_pile_gioco()

	def distribuisci_carte(self):
		"""
		Distribuisce le carte sulle 7 pile di gioco.
		La prima pila riceve una carta, la seconda pila riceve 2 carte, la terza pila riceve 3 carte e così via.
		L'ultima carta di ogni pila è scoperta. Tutte le altre carte sono coperte.
		"""
		self.reset() # resetta il tavolo di gioco
		mazzo = self.mazzo.carte[:]
		for i in range(7):
			pila = self.get_pila(f"pila{i+1}")
			carte = mazzo[:i+1]
			pila.aggiungi_carte(carte)
			for carta in carte[:-1]:
				carta.coperta = True

			carte[-1].coperta = False
			mazzo = mazzo[i+1:]



#@@@# start del modulo
if __name__ == "__main__":
	print("compilazione completata di %s" % __name__)
else:
	print("Carico: %s" % __name__)
