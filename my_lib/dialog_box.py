"""
	file dialog_box.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/my_lib/dialog_box.py

	Modulo per la gestione delle dialog box
"""
#lib
import wx
#from my_lib.pygame_dialog_box import PygameDialogBox
from my_lib.wx_dialog_box import WxDialogBox

class DialogBox:
	def __init__(self):
		super().__init__()
		self.dialog_box = WxDialogBox()  # gestore dialog box
		self.question = ""
		self.answare = ""

	def create_question_box(self, question):
		self.dialog_box.create_question_box(question)
		self.answare = self.dialog_box.answare

	def create_yes_or_no_box(self, question, title):
		self.dialog_box.create_yes_or_no_box(question, title)
		self.answare = self.dialog_box.answare

	def create_alert_box(self, message, title):
		self.dialog_box.create_alert_box(message, title)

	def create_input_box(self, question, title):
		answare = self.dialog_box.create_input_box(question, title)
		self.answare = self.dialog_box.answare

	def create_duble_input_box(self):
		answare = self.dialog_box.create_duble_input_box()
		self.answare = self.dialog_box.answare



#@@@# Start del modulo
if __name__ == "__main__":
	print("Complilazione eseguita con successo!\n")

else:
	print("Carico: %s" % __name__)
