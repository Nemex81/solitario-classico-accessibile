"""
	file acs.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/acs.py

	Solitario Accessibile con pygame
"""

# lib
import pygame
from pygame.locals import *
from scr.solitario_accessibile import SolitarioAccessibile

# inizializzo pygame
pygame.init()
pygame.font.init()

class ACS(SolitarioAccessibile):
	def __init__(self):
		super().__init__()


 
#@@@# avvio del modulo
if __name__ == '__main__':
	print("compilazione di %s completata." % __name__)
	ACS().run()
