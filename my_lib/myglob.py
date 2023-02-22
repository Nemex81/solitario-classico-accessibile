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


#@@@# inizio parte 2
# costanti
M_TITOLO = "Solitario Accessibile"



#@@@# Start del modulo
if __name__ != "__main__":
	print("Carico: %s" % __name__)
