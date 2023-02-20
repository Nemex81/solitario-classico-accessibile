import sys, random
from gtts import gTTS
#import pdb

def create_speech_mp3():
	# per avviare inserire  create_speech_mp3()
    text = input("Inserisci la frase da convertire in MP3: ")
    filename = input("Inserisci il nome del file MP3 (senza estensione): ")
    language = input("Inserisci la lingua (es. it per italiano): ")
    tts = gTTS(text, lang=language)
    tts.save(f"{filename}.mp3")
    print(f"File MP3 {filename}.mp3 creato con successo!")


# funzione per ricavare il numero di key totali presenti in un dizionario
def dlen(diz):
	if not diz:
		return 0

	i = 0
	for k in diz:
	    i += 1

	return i


#@@@# Start del modulo
if __name__ != "__main__":
	print("Carico: %s" % __name__)
