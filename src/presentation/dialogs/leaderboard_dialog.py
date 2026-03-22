"""
LeaderboardDialog

Dialogo accessibile per la visualizzazione della classifica (leaderboard).
Compatibile con screen reader e navigazione da tastiera.
"""
import wx

class LeaderboardDialog(wx.Dialog):
    def __init__(
        self,
        parent: wx.Window,
        profiles_with_stats: list = None,
        current_profile_id: str = None,
        metric: str = "victories"
    ):
        """
        Dialog accessibile per la visualizzazione della classifica.
        :param parent: finestra genitore
        :param profiles_with_stats: lista di profili/statistiche da mostrare
        :param current_profile_id: profilo attivo (per evidenziare)
        :param metric: metrica di ordinamento (es. "victories")
        """
        super().__init__(parent, title="Classifica", style=wx.DEFAULT_DIALOG_STYLE)
        self.profiles_with_stats = profiles_with_stats or []
        self.current_profile_id = current_profile_id
        self.metric = metric
        self._init_ui()


    def _init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(panel, label=f"Classifica giocatori ({self.metric}):")
        vbox.Add(label, flag=wx.ALL | wx.EXPAND, border=10)

        # Placeholder: elenco classifica (solo stringhe)
        choices = []
        for row in self.profiles_with_stats:
            if isinstance(row, dict):
                name = row.get("profile_name", str(row))
                value = row.get(self.metric, "-")
                line = f"{name}: {value}"
            else:
                line = str(row)
            if self.current_profile_id and isinstance(row, dict) and row.get("profile_id") == self.current_profile_id:
                line = f"* {line}"
            choices.append(line)

        list_box = wx.ListBox(panel, choices=choices)
        vbox.Add(list_box, flag=wx.ALL | wx.EXPAND, border=10, proportion=1)

        btn_ok = wx.Button(panel, wx.ID_OK, label="&OK")
        btn_ok.SetDefault()
        vbox.Add(btn_ok, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        panel.SetSizer(vbox)

        # Sizer principale del dialog che contiene il panel
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(panel, flag=wx.EXPAND | wx.ALL, border=0, proportion=1)
        self.SetSizerAndFit(main_sizer)
        self.CentreOnParent()
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_ok)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        btn_ok.SetFocus()

    def on_close(self, event):
        self.EndModal(wx.ID_OK)
