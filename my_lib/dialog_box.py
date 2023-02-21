"""
	file dialog_box.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/my_lib

	Modulo per la gestione delle dialog box
"""
#lib
import wx
#from my_lib.pygame_dialog_box import PygameDialogBox
from my_lib.wx_dialog_box import WxDialogBox

class DialogBox(WxDialogBox):
	def __init__(self):
		super().__init__()

	#def create_question_box(self, question):
		#pass

	#def create_alert_box(self, message, title):
		#pass

	#def create_input_box(self, question, title):
		#pass

	#def create_duble_input_box(self):
		#pass

#@@@# Start del modulo
if __name__ == "__main__":
	print("Complilazione eseguita con successo!\n")

else:
	print("Carico: %s" % __name__)
