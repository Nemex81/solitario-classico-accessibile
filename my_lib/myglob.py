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

# costanti per la bussola
class COMPASS(Enum):
	NORD = 0
	NORDEST = 45
	EST = 90
	SUDEST = 135
	SUD = 180
	SUDOVEST = 225
	OVEST = 270
	NORDOVEST = 315

# versione vecchia con costanti standard, da eliminare appena finito di integrare la classe enum sopra
NORD = 0
NORDEST = 45
EST = 90
SUDEST = 135
SUD = 180
SUDOVEST = 225
OVEST = 270
NORDOVEST = 315

# costanti per le direzioni
DIRECTION = {
	NORD : "nord",
	NORDEST : "nord-est",
	EST : "est",
	SUDEST : "sud-est",
	SUD : "sud",
	SUDOVEST : "sud-ovest",
	OVEST : "ovest",
	NORDOVEST : "nord-ovest",
}

# liste tipi diterreno
class TYPE_TYLES(Enum):
	VUOTO_COSMICO = 0
	ASFALTO = 1
	TERRA_ROSSA = 2
	GHIAIA = 3
	ACCIAIO_ARRUGGINITO = 4
	CEMENTO_FRANTUMATO = 5
	SCORIE_RADIOATTIVE = 6
	ACQUA_BASSA = 7
	ACQUA_ALTA = 8
	ACQUA_INQUINATA = 9
	FERRO_LAMIERE = 10
	TERRA_BRULLA = 11
	ERBA = 12
	VEGETAZIONE_SELVAGGIA = 13
	ARIA = 14
	PAVIMENTO_FLUTTUANTE = 15
	PAVIMENTO_ROBOTICO = 16
	PAVIMENTO_ENERGETICO = 17
	PAVIMENTO_ANTIGRAVITA = 18
	TERRA_BATTUTA = 19
	TERRA_UMIDA = 20
	NEVE = 21
	GHIACCIO = 22
	ROCCIA = 23
	SABBIA = 24
	FOGLIAME = 25
	TERRA_BATTUTA_UMIDA = 26
	LAVA = 27
	DESERTO = 28
	TERRA_GHIACCIATA = 29
	MONTAGNA = 30
	SUPERFICE_LUNARE = 31
	SUPERFICE_MARZIANA = 32
	SPAZIO_APERTO = 33
	GAS_TOSSICO = 34
	FOGNA = 35
	COLLINA = 36
	CAMPAGNA = 37
	CEMENTO = 38
	PARETE = 39
	CONFINE_MAPPA = 40

TYLES_LOCKED = [
	TYPE_TYLES.PARETE.value,
	TYPE_TYLES.CONFINE_MAPPA.value,
	TYPE_TYLES.ACQUA_ALTA.value
]

ECHO_TYPE_TYLES = {
	TYPE_TYLES.VUOTO_COSMICO.value: "VUOTO COSMICO",
	TYPE_TYLES.ASFALTO.value: "Asfalto",
	TYPE_TYLES.TERRA_ROSSA.value: "Terra rossa",
	TYPE_TYLES.GHIAIA.value: "Ghiaia",
	TYPE_TYLES.ACCIAIO_ARRUGGINITO.value: "Acciaio arrugginito",
	TYPE_TYLES.CEMENTO_FRANTUMATO.value: "Cemento frantumato",
	TYPE_TYLES.SCORIE_RADIOATTIVE.value: "Scorie radioattive",
	TYPE_TYLES.ACQUA_BASSA.value: "Acqua bassa",
	TYPE_TYLES.ACQUA_ALTA.value: "Acqua alta",
	TYPE_TYLES.ACQUA_INQUINATA.value: "Acqua inquinata",
	TYPE_TYLES.FERRO_LAMIERE.value: "Ferro lamiere",
	TYPE_TYLES.TERRA_BRULLA.value: "Terra brulla",
	TYPE_TYLES.ERBA.value: "Erba",
	TYPE_TYLES.VEGETAZIONE_SELVAGGIA.value: "Vegetazione selvaggia",
	TYPE_TYLES.ARIA.value: "Aria",
	TYPE_TYLES.PAVIMENTO_FLUTTUANTE.value: "Pavimento fluttuante",
	TYPE_TYLES.PAVIMENTO_ROBOTICO.value: "Pavimento robotico",
	TYPE_TYLES.PAVIMENTO_ENERGETICO.value: "Pavimento energetico",
	TYPE_TYLES.PAVIMENTO_ANTIGRAVITA.value: "Pavimento antigravità",
	TYPE_TYLES.TERRA_BATTUTA.value: "Terra battuta",
	TYPE_TYLES.TERRA_UMIDA.value: "Terra umida",
	TYPE_TYLES.NEVE.value: "Neve",
	TYPE_TYLES.GHIACCIO.value: "Ghiaccio",
	TYPE_TYLES.ROCCIA.value: "Roccia",
	TYPE_TYLES.SABBIA.value: "Sabbia",
	TYPE_TYLES.FOGLIAME.value: "Fogliame",
	TYPE_TYLES.TERRA_BATTUTA_UMIDA.value: "Terra battuta umida",
	TYPE_TYLES.LAVA.value: "Lava",
	TYPE_TYLES.DESERTO.value: "Deserto",
	TYPE_TYLES.TERRA_GHIACCIATA.value: "Terra ghiacciata",
	TYPE_TYLES.MONTAGNA.value: "Montagna",
	TYPE_TYLES.SUPERFICE_LUNARE .value: "superfice lunare",
	TYPE_TYLES.SUPERFICE_MARZIANA.value: "superfice marziana",
	TYPE_TYLES.SPAZIO_APERTO.value: "spazio aperto",
	TYPE_TYLES.GAS_TOSSICO.value: "gas tossico",
	TYPE_TYLES.FOGNA.value: "fogna",
	TYPE_TYLES.COLLINA.value: "collina",
	TYPE_TYLES.CAMPAGNA.value: "campagna",
	TYPE_TYLES.CEMENTO.value: "CEMENTO",
	TYPE_TYLES.PARETE.value: "parete",
	TYPE_TYLES.CONFINE_MAPPA.value: "confine mappa",
}

# classi per i menù builder
class BTN_MENU_BUILDER(Enum):
	""" enum per le voci del menu builder """
	NEW_MAP = 0
	SAVE_MAP = 1
	SAVE_MAP_AS = 2
	RESET_MAP = 3
	DELETE_MAP = 4
	LOAD_MAP = 5
	POP_MAP = 6
	EDIT_TYLE = 7
	CLOSE_BUILDER_MENU = 8

LIST_BTN_MENU = [
	"carica mappa di default",
	"salva mappa",
	"salva mappa con nome",
	"resetta mappa a vuoto cosmico",
	"elimina mappa",
	"carica mappa salvata",
	"popola mappa in random mod",
	"modifica casella attuale",
	"chiudi il menù",
]

# classi per la gestione degli stati del personaggio
class ChPosition(Enum):
	REGLINING = 0
	SITTING = 1
	STANDING = 2
	FLOATING = 3

ECHO_POSITION = {
	ChPosition.REGLINING : "sdraiato",
	ChPosition.	SITTING : "seduto",
	ChPosition.STANDING : "in piedi",
	ChPosition.FLOATING : "in volo",
}

class ChStatus(Enum):
	CREAZIONE = -2
	MORTO = -1
	INATTIVO = 0
	FERMO = 1
	MOVIMENTO = 2

ECHO_Status = {
	ChStatus.CREAZIONE : "creazione del personaggio",
	ChStatus.MORTO : "morto",
	ChStatus.INATTIVO : "inattivo",
	ChStatus.FERMO : "fermo",
	ChStatus.MOVIMENTO : "in movimento",
}

class ChMoveStatus(Enum):
	FERMO = 1
	AVANTI = 2
	INDIETRO = 3
	PASSO_LATERALE_SINISTRA = 4
	PASSO_LATERALE_DESTRA = 5

ECHO_MoveStatus = {
	ChMoveStatus.FERMO : "fermo",
	ChMoveStatus.	AVANTI : "in avanti",
	ChMoveStatus.INDIETRO : "indietro",
	ChMoveStatus.PASSO_LATERALE_SINISTRA : "passo laterale a sinistra",
	ChMoveStatus.PASSO_LATERALE_DESTRA : "passo laterale a destra",
}

class ChRotation(Enum):
	FERMO = 1
	ROTAZIONE_SINISTRA = 2
	ROTAZIONE_DESTRA = 3
	INVERSIONE = 4

ECHO_Rotation = {
	ChRotation.FERMO : "fermo",
	ChRotation.ROTAZIONE_SINISTRA : "rotazione a sinistra",
	ChRotation.ROTAZIONE_DESTRA : "rotazione a destra",
	ChRotation.INVERSIONE : "inversione di marcia",
}

class ChMoveType(Enum):
	WALKING = 0
	SEMIRUNNING = 1
	RUNNING = 2

ECHO_move_TYPE = {
	ChMoveType.WALKING : "camminata",
	ChMoveType.RUNNING : "corsa",
	ChMoveType.SEMIRUNNING : "corsetta"
}

ECHO_SPEED = {
	ChMoveType.WALKING : 5.0,
	ChMoveType.SEMIRUNNING : 12,
	ChMoveType.RUNNING : 25.0
}

#@@@# Start del modulo
if __name__ != "__main__":
	print("Carico: %s" % __name__)
