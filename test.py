# lib
import os, sys, glob, random, math, copy, logging, time, pygame
from enum import Enum
#from pygame.locals import *
# moduli personali
from solitario_accessibile import SolitarioAccessibile
from scr.game_engine import EngineSolitario
from scr.game_play import GamePlay
from my_lib.dialog_box import DialogBox
from my_lib.myglob import *
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger.setLevel(logging.DEBUG)



class NewEngineSolitario(EngineSolitario):
	def __init__(self):
		super().__init__()


class NewGamePlay(GamePlay):
	def __init__(self):
		super().__init__()


class Test(SolitarioAccessibile):
	def __init__(self):
		super().__init__()
		self.is_working = True
		self.is_betatesting = True




#@@@# start del modulo
Test().run()