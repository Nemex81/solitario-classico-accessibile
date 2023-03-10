"""
	Modulo per test vari
"""

# lib
import os, sys, glob, random, math, copy, logging, time, pygame
from enum import Enum
#from pygame.locals import *
# moduli personali
from scr.solitario_accessibile import SolitarioAccessibile
from scr.screen_reader import ScreenReader
from scr.cards import Carta, Mazzo
from scr.pile import Pila, Tavolo
from scr.game_engine import EngineSolitario
from scr.game_play import GamePlay
from my_lib.dialog_box import DialogBox
from my_lib.myglob import *
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger.setLevel(logging.DEBUG)


# test_cards.py
from scr.cards import Carta, Mazzo

# Crea un mazzo di carte e mescola le carte
mazzo = Mazzo()
mazzo.crea()
mazzo.mischia()

# Stampa il numero di carte nel mazzo
print("Numero di carte nel mazzo:", len(mazzo.cards))

# Pesca alcune carte dal mazzo
carta1 = mazzo.pesca()
carta2 = mazzo.pesca()

# Stampa le carte pescate
#print("Carta 1:", carta1.get_name())
#print("Carta 2:", carta2.get_name())
#print("Numero di carte nel mazzo:", len(mazzo.cards))
mazzo.reset()
print("mazzo ripristinato.\nNumero di carte nel mazzo:", len(mazzo.cards))
tavolo = Tavolo()
tavolo.crea_pile_gioco()
tavolo.distribuisci_carte(mazzo)
for p in tavolo.pile:
	print(p.nome)
	print(p.numero_carte())
	carte = p.get_carte()
	for c in carte:
		print(c.nome)


6print("tavolo di gioco allestito.\n Numero di carte nel mazzo:", len(mazzo.cards))
print("Numero di carte nel tavolo:", tavolo.numero_carte())
