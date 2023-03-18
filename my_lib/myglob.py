"""
	file myglob.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/my_lib/myglob.py
"""
from enum import Enum
#import pdb

# colori rgb
class Colors(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

class Suit(Enum):
    CUORI = "cuori"
    QUADRI = "quadri"
    FIORI = "fiori"
    PICCHE = "picche"

class Color(Enum):
    ROSSO = "rosso"
    BLU = "blu"

class CardValue(Enum):
    ASSO = 1
    DUE = 2
    TRE = 3
    QUATTRO = 4
    CINQUE = 5
    SEI = 6
    SETTE = 7
    OTTO = 8
    NOVE = 9
    DIECI = 10
    JACK = 11
    REGINA = 12
    RE = 13

#@@@# Start del modulo
if __name__ != "__main__":
	print("Carico: %s" % __name__)
