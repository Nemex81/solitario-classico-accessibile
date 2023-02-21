"""
	file screen_reader.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/scr
	Modulo per la Classe ScreenReader per la gestione delle sintesi vocali.

	Questa classe si occupa della gestione degli screen reader, utilizzati per vocalizzare messaggi all'utente.

	Metodi:
		- __init__(): metodo di inizializzazione della classe.
		- Vocalizza(string): vocalizza il messaggio passato come argomento.
		- SayLog(): legge la voce selezionata nel log degli eventi.
		- SayLastLog(): legge l'ultima voce salvata nel log degli eventi.
		- NextLog(): scorrimento in avanti della lista log eventi e vocalizzazione.
		- PriorLog(): scorrimento in indietro della lista log eventi e vocalizzazione.
		- MoveToFirstLog(): sposta il cursore al primo log eventi e vocalizza.
		- MoveToLastLog(): sposta il cursore all'ultimo log eventi e vocalizza.
		- AddLogToList(testo): aggiunge un nuovo messaggio di sistema al dizionario di log degli eventi.
		- SaveLogToFile(): salva su file il log degli eventi di gioco.

"""

# lib
import os, sys, random, time, pygame
from enum import Enum
import accessible_output2.outputs.auto
import  my_lib.myutyls as mu
#import pdb

# inizializzo l'engine per la vocalizzazione
engine = accessible_output2.outputs.auto.Auto()

#@@@# classe per la gestione dell'interfaccia utente
class ScreenReader:

	def __init__(self):
		# costanti
		self.syspath = "./" # pat di sistema per la directory del gioco
		self.listlog = {} # dizionario per la lista degli eventi da vocalizzare
		self.idlog = 0
		self.lastidlog = 0
		self.modlog = True # interruttore per la modalità log degli eventi
		self.is_working = False # su tru abilita la progressione automatica della versione ad ogni compilazione

	#@@# sezione metodi di classe

	def validate_log_string(self, string):
		lista = list(string.strip("\n"))
		num_tyles = len(lista)
		num = 0
		fineriga = 0
		nuova = []
		for i in lista:
			num += 1
			if i == "\n":
				fineriga += 1

		stat = f"caratteri nella stringa: {num}, carattteri di acapo rilevati: {fineriga}."
		return stat

	def vocalizza(self, string):
		"""
		Questo metodo vocalizza il testo passato come parametro utilizzando il motore di sintesi vocale.
		Inoltre, aggiunge il testo passato alla lista dei messaggi di log e lo salva su file, se la modalità log è attiva.

		Args:
			string (str): Il testo da vocalizzare.

		Returns:
			None

		"""

		# verifichiamo la validità di string
		new_string = str(self.validate_log_string(string))
		if string:
			self.AddLogToList(string)
			engine.speak(string, interrupt=True)

	#@@# sezione creazione e gestione log degli eventi 

	def SayLog(self):
		""" 
		legge l'attuale voce selezionata nel log degli eventi 

		Descrizione:
			Il metodo legge l'evento corrente selezionato nel log degli eventi e lo vocalizza utilizzando l'engine di sintesi vocale specificato.
			Viene composto un messaggio vocale concatenando l'indice dell'evento corrente e il relativo contenuto. 
			Se il messaggio vocale è stato composto correttamente, l'engine di sintesi vocale viene utilizzato per riprodurre il messaggio vocalmente.

		"""

		lastlog = self.listlog[self.idlog]
		testo = "%s: %s" % (self.idlog, lastlog)
		if testo:
			engine.speak(testo, interrupt=True)

	def SayLastLog(self):
		""" 
		legge l'ultima voce salvata nel log degli eventi 

		Descrizione:
			Il metodo permette di leggere ad alta voce l'ultima voce salvata nel log degli eventi. 
			In particolare, il metodo determina l'ultima voce salvata nel log degli eventi e costruisce una stringa di testo contenente l'ID della voce e il suo contenuto, in modo simile al metodo  `SayLog`.
			Successivamente, il metodo utilizza il motore di sintesi vocale per leggere la stringa di testo ad alta voce.

		"""

		lastidlog = mu.dlen(self.listlog)
		lastlog = self.listlog[lastidlog]
		self.idlog = lastidlog 
		testo = "%s: %s.  " % (self.idlog, lastlog)
		self.engine.speak(testo, interrupt=True)

	def NextLog(self):
		""" scorrimento in avanti della lista log eventi e vocalizzazione"""

		lastidlog = mu.dlen(self.listlog)
		if self.idlog < lastidlog:
			self.idlog += 1
			self.SayLog()

		else:
			self.idlog = lastidlog


	def PriorLog(self):
		""" scorrimento in indietro della lista log eventi e vocalizzazione"""

		lastidlog = mu.dlen(self.listlog)
		if self.idlog > 1:
			self.idlog -= 1
			self.SayLog()

		elif self.idlog <= 1:
			self.idlog = 1


	def MoveToFirstLog(self):

		self.idlog = 1
		testo = "%s: %s.  " % (self.idlog, self.listlog[self.idlog])
		self.SayLog()


	def MoveToLastLog(self):

		lastidlog = mu.dlen(self.listlog)
		self.idlog = lastidlog
		testo = "%s: %s.  " % (self.idlog, self.listlog[self.idlog])
		self.SayLog()


	def AddLogToList(self, testo):
		"""
		Aggiunge il nuovo messaggio di sistema al dizionario log degli eventi.

		Args:
			testo (str): Il testo del messaggio da aggiungere al log degli eventi.

		Descrizione:
			Questo metodo è utilizzato per aggiungere un nuovo messaggio di sistema al dizionario del log degli eventi. 
			Il parametro è una stringa che rappresenta il testo del messaggio da aggiungere al log.`testo`
			Il metodo inizialmente controlla se non è una stringa vuota. In caso affermativo, determina la chiave del nuovo elemento del dizionario, incrementando il numero totale di elementi del dizionario e aggiungendo 1. 
			Quindi, viene utilizzato il metodo per aggiungere il nuovo messaggio al dizionario.`testo``setdefault()`
			Infine, se la modalità di log è abilitata, viene chiamato il metodo per salvare il log su file.

		"""

		if testo:
			newkey = mu.dlen(self.listlog) + 1
			self.listlog.setdefault(newkey, testo)
			if not self.modlog:
				return

			#self.SaveLogToFile()


	def SaveLogToFile(self):
		"""
		Salva il log degli eventi di gioco su un file.

		Descrizione:
			Il file viene salvato nella directory del gioco con il nome 'gamelog.txt'.
			Ogni voce del log è composta da un numero identificativo e la corrispondente voce.
			Il numero e la voce sono separati da uno spazio e ogni voce è separata da una nuova riga.

		"""

		listlog = self.listlog
		path = self.syspath
		nomefile = "gamelog.txt"
		writefile = "%s%s" % (path, nomefile)
		with open(writefile, "w") as document:
			for k in listlog:
				value = listlog[k]
				string = "%s %s\n" % (k, value)
				document.write(string)

			document.close()



#@@@# Start del modulo
if __name__ == "__main__":
	print("compilazione di %s completata." % __name__)

else:
	print("Carico: %s" % __name__)
