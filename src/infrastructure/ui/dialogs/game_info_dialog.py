"""Game info dialog for current game state (I key during gameplay).

Shows current game progress without ending the game.
NVDA-optimized read-only information dialog.
"""

import wx
from typing import Dict, Any

from src.presentation.formatters.stats_formatter import StatsFormatter


class GameInfoDialog(wx.Dialog):
    """Current game information dialog (triggered by I key).
    
    Shows:
    - Time elapsed
    - Timer remaining (if enabled)
    - Moves count
    - Foundation breakdown by suit
    - Provisional score (if scoring enabled)
    
    Keyboard:
    - ESC: Close and return to game
    """
    
    def __init__(self, parent, game_state: Dict[str, Any]):
        """Initialize game info dialog.
        
        Args:
            parent: Parent window
            game_state: Dict with current game state
                - elapsed_time: float
                - timer_enabled: bool
                - timer_remaining: float (if timer_enabled)
                - move_count: int
                - foundations: Dict[str, int] (suit -> card count)
                - provisional_score: int (if scoring_enabled)
                - scoring_enabled: bool
        """
        super().__init__(
            parent,
            title="Info Partita Corrente",
            style=wx.DEFAULT_DIALOG_STYLE
        )
        
        self.game_state = game_state
        self.formatter = StatsFormatter()
        
        self._create_ui()
        self._set_focus()
    
    def _create_ui(self) -> None:
        """Create dialog UI elements."""
        # Main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header
        header = wx.StaticText(self, label="═" * 45)
        header_title = wx.StaticText(self, label="      INFO PARTITA CORRENTE")
        header_bottom = wx.StaticText(self, label="═" * 45)
        
        sizer.Add(header, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(header_title, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(header_bottom, 0, wx.ALL | wx.EXPAND, 5)
        
        # Info content (TextCtrl readonly)
        content = self._build_content_text()
        self.info_text = wx.TextCtrl(
            self,
            value=content,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            size=(450, 250)
        )
        self.info_text.SetName("Informazioni partita")
        sizer.Add(self.info_text, 1, wx.ALL | wx.EXPAND, 10)
        
        # Close button
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_close = wx.Button(self, wx.ID_CANCEL, "Chiudi (ESC)")
        btn_sizer.Add(self.btn_close, 0, wx.ALL, 5)
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 10)
        
        self.SetSizer(sizer)
        self.Fit()
    
    def _build_content_text(self) -> str:
        """Build game info content text."""
        lines = []
        
        # Time info
        elapsed = self.game_state.get('elapsed_time', 0)
        lines.append(f"Tempo trascorso: {self.formatter.format_duration(elapsed)}")
        
        if self.game_state.get('timer_enabled', False):
            remaining = self.game_state.get('timer_remaining', 0)
            if remaining > 0:
                lines.append(f"Tempo rimanente: {self.formatter.format_duration(remaining)}")
            else:
                lines.append("⚠ Timer scaduto (modalità PERMISSIVE attiva)")
        
        lines.append("")
        
        # Moves and draws
        lines.append(f"Mosse: {self.game_state.get('move_count', 0)}")
        lines.append("")
        
        # Foundations breakdown
        lines.append("FONDAZIONI:")
        foundations = self.game_state.get('foundations', {})
        total_cards = sum(foundations.values())
        lines.append(f"Totale: {total_cards}/52 carte ({(total_cards/52*100):.1f}%)")
        
        # Per-suit breakdown
        suits = ['Cuori', 'Quadri', 'Fiori', 'Picche']
        suit_keys = ['hearts', 'diamonds', 'clubs', 'spades']
        for suit_name, suit_key in zip(suits, suit_keys):
            count = foundations.get(suit_key, 0)
            lines.append(f"  {suit_name}: {count}/13")
        
        lines.append("")
        
        # Provisional score
        if self.game_state.get('scoring_enabled', False):
            score = self.game_state.get('provisional_score', 0)
            lines.append(f"Punteggio provvisorio: {self.formatter.format_number(score)} punti")
        
        return "\n".join(lines)
    
    def _set_focus(self) -> None:
        """Set initial focus and TTS announcement."""
        self.info_text.SetFocus()
        
        # TTS announcement
        elapsed = self.formatter.format_duration(self.game_state.get('elapsed_time', 0))
        moves = self.game_state.get('move_count', 0)
        foundations = self.game_state.get('foundations', {})
        total_cards = sum(foundations.values())
        
        announcement = (
            f"Info partita corrente. Tempo: {elapsed}. "
            f"Mosse: {moves}. Carte in fondazione: {total_cards} su 52."
        )
        
        self.SetTitle(announcement)
