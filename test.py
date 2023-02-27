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
from scr.game_engine import EngineSolitario
from scr.game_play import GamePlay
from my_lib.dialog_box import DialogBox
from my_lib.myglob import *
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger.setLevel(logging.DEBUG)


solitario = EngineSolitario()
carte = solitario.mazzo.crea_mazzo()
#for carta in carte:
	#carta.set_name()
	#nome = carta.get_name()
	#print(nome)

solitario.mazzo.mischia_carte(carte)
#for c in range(10):
	#carta = solitario.mazzo.pesca(carte)
	#carta.set_name()
	#string = f"{carta.nome}, vale {carta.valore_numerico} punti."
	#print(string)

solitario.distribuisci_carte()