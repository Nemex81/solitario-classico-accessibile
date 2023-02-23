"""
	file wx_dialog_box.py
	percorso: https://github.com/Nemex81/solitario-classico-accessibile/blob/main/my_lib/wx_dialog_box.py

	Modulo per la gestione delle dialog box
"""
#lib
import wx

# Classe che rappresenta la logica di modello per la dialog box
class CreateBoxDialogModel:
	def __init__(self):
		self.answare = ""
		self.question = ""

# Classe che rappresenta la logica di presentazione per la dialog box
class CreateBoxDialogView(wx.Dialog):
	def __init__(self, parent, title, model):
		super().__init__(parent, title=title)
		self.model = model
		sizer = wx.BoxSizer(wx.VERTICAL)
		label = wx.StaticText(self, label=self.model.question)
		sizer.Add(label, 0, wx.ALL, 5)

		self.text_ctrl = wx.TextCtrl(self)
		sizer.Add(self.text_ctrl, 0, wx.ALL | wx.EXPAND, 5)

		buttons_sizer = wx.StdDialogButtonSizer()

		ok_button = wx.Button(self, wx.ID_OK)
		ok_button.SetDefault()
		buttons_sizer.AddButton(ok_button)

		cancel_button = wx.Button(self, wx.ID_CANCEL)
		buttons_sizer.AddButton(cancel_button)

		buttons_sizer.Realize()
		sizer.Add(buttons_sizer, 0, wx.ALL | wx.EXPAND, 5)

		self.Bind(wx.EVT_BUTTON, self.on_ok, ok_button)

		self.SetSizer(sizer)
		sizer.Fit(self)

	def on_ok(self, event):
		self.model.answare = self.text_ctrl.GetValue()
		self.EndModal(wx.ID_OK)

#@@# end del modulo

class CreateBoxPresenter:
	def __init__(self, view):
		self.view = view

	def on_ok(self, event):
		self.view.answare = self.view.text_ctrl.GetValue()
		self.view.EndModal(wx.ID_OK)


class CreateBoxDialog(wx.Dialog):
	def __init__(self, parent, title):
		super().__init__(parent, title=title)
		self.answare = ""
		self.question = ""
		sizer = wx.BoxSizer(wx.VERTICAL)
		label = wx.StaticText(self, label=self.question)
		sizer.Add(label, 0, wx.ALL, 5)

		self.text_ctrl = wx.TextCtrl(self)
		sizer.Add(self.text_ctrl, 0, wx.ALL | wx.EXPAND, 5)

		buttons_sizer = wx.StdDialogButtonSizer()

		ok_button = wx.Button(self, wx.ID_OK)
		ok_button.SetDefault()
		buttons_sizer.AddButton(ok_button)

		cancel_button = wx.Button(self, wx.ID_CANCEL)
		buttons_sizer.AddButton(cancel_button)

		buttons_sizer.Realize()
		sizer.Add(buttons_sizer, 0, wx.ALL | wx.EXPAND, 5)

		self.presenter = CreateBoxPresenter(self)
		self.Bind(wx.EVT_BUTTON, self.presenter.on_ok, ok_button)

		self.SetSizer(sizer)
		sizer.Fit(self)


class WxDialogBox:
	def __init__(self):
		self.answare = ""
		self.question = ""
		self.title = ""

	def create_dialog_box(self, question):
		self.clean_answare()
		app = wx.App()
		dialog = CreateBoxDialog(None, question)
		result = dialog.ShowModal()
		if result == wx.ID_OK:
			self.answare = dialog.answare
			return self.answare

		dialog.Destroy()
		wx.Yield()

	def create_question_box(self, question):
		self.clean_answare()
		app = wx.App()
		dlg = wx.MessageDialog(None, question, "Conferma", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
		result = dlg.ShowModal()
		if result == wx.ID_OK:
			self.answare = True
		else:
			self.answare = False

		dlg.Destroy()
		wx.Yield()

	def create_yes_or_no_box(self, question, title):
		self.clean_answare()
		app = wx.App()
		dialog = wx.MessageDialog(None, question, title, style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		result = dialog.ShowModal() == wx.ID_YES
		dialog.Destroy()
		self.answare = result

	def create_alert_box(self, message, title):
		self.clean_answare()
		app = wx.App()
		dlg = wx.MessageDialog(None, message, title, wx.OK|wx.ICON_EXCLAMATION)
		dlg.ShowModal()
		dlg.Destroy()
		wx.Yield()

	def create_input_box(self, question, title):
		self.clean_answare()
		app = wx.App()
		dlg = wx.TextEntryDialog(None, question, title, value="")
		if dlg.ShowModal() == wx.ID_OK:
			answare = dlg.GetValue()
			self.save_input(answare)

		# distruzione della dialog box
		dlg.Destroy()
		wx.Yield()

	def create_duble_input_box(self, lbl1, lbl2):
		self.clean_answare()
		app = wx.App()
		dlg = wx.Dialog(None, title=self.question, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		dlg.CenterOnScreen()
		
		# Aggiungiamo una sizer verticale al dialog
		sizer = wx.BoxSizer(wx.VERTICAL)

		# Aggiungiamo la casella di testo per l'input della coordinata x
		x_text = wx.StaticText(dlg, label=lbl1)
		sizer.Add(x_text, 0, wx.ALL, 5)
		x_input = wx.TextCtrl(dlg, style=wx.TE_PROCESS_ENTER)
		sizer.Add(x_input, 0, wx.ALL | wx.EXPAND, 5)

		# Aggiungiamo la casella di testo per l'input della coordinata y
		y_text = wx.StaticText(dlg, label=lbl2)
		sizer.Add(y_text, 0, wx.ALL, 5)
		y_input = wx.TextCtrl(dlg, style=wx.TE_PROCESS_ENTER)
		sizer.Add(y_input, 0, wx.ALL | wx.EXPAND, 5)

		# Aggiungiamo i pulsanti per OK e Annulla
		btn_sizer = dlg.CreateButtonSizer(wx.OK | wx.CANCEL)
		sizer.Add(btn_sizer, 0, wx.ALL | wx.EXPAND, 5)

		# Assegnamo il sizer al dialog
		dlg.SetSizer(sizer)
		sizer.Fit(dlg)

		# Mostriamo il dialog e attendiamo che l'utente prema un pulsante
		if dlg.ShowModal() == wx.ID_OK:
			x_value = x_input.GetValue()
			y_value = y_input.GetValue()
			result = (x_value, y_value)
			self.save_input(result)

		# distruzione della dialog box
		dlg.Destroy()
		wx.Yield()

	def save_input(self, string):
		self.answare = string

	def show_user_input(self):
		string = "input salvato: %s!  " % self.answare
		self.Vocalizza(string)

	def clean_question(self):
		self.question = ""

	def clean_answare(self):
		self.answare = ""

#@@@# Start del modulo
if __name__ == "__main__":
	print("Complilazione eseguita con successo!\n")

else:
	print("Carico: %s" % __name__)
