"""
	file my_glob.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/my_lib
""""
from enum import Enum
#import pdb

# colori rgb
from enum import Enum

class Colors(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 255)

# costanti
M_TAV = 7  # numero di tavoli nel gioco
M_RIS = 4  # numero di riserve nel gioco
M_CRX = 13  # numero massimo di carte per tavolo
M_MSG = 40  # lunghezza massima messaggio in console
M_AZZ = M_TAV * M_CRX + M_RIS * 13 + 1  # numero di carte nel mazzo
M_SEMI = ["Quadri", "Fiori", "Cuori", "Picche"]
M_VALORI = ["Asso", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Regina", "Re"]
M_SX = 50  # posizione x del tavolo da gioco
M_SY = 50  # posizione y del tavolo da gioco
M_DX = 125  # spostamento orizzontale tra le carte sul tavolo
M_DY = 25  # spostamento verticale tra le carte sul tavolo

# var globali
debug_mode = False
tavolo = [[] for i in range(M_TAV)]
riserva = [[] for i in range(M_RIS)]
mazzo = []
dialog_box = DialogBox()

#@@@# inizio parte 2
# costanti
M_TITOLO = "Solitario Accessibile"

#@@# end parte 2

#@@@# Start del modulo
if __name__ != "__main__":
	print("Carico: %s" % __name__)
