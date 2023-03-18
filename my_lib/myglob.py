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
    COPPE = "coppe"
    DENARI = "denari"
    BASTONI = "bastoni"
    SPADE = "spade"

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

class GamePiles(Enum):
	BASE1 = 0
	BASE2 = 1
	BASE3 = 2
	BASE4 = 3
	BASE5 = 4
	BASE6 = 5
	BASE7 = 6
	CUORI = 7
	QUADRI = 8
	FIORI = 9
	PICCHE = 10
	SCARTI = 11
	RISERVE = 12



#@@@# Start del modulo
if __name__ != "__main__":
	print("Carico: %s" % __name__)
