"""Last game summary dialog (read-only).

Shows summary of the most recently completed game session.
NVDA-optimized with proper focus management and TTS announcements.
"""

import wx
from datetime import datetime
from typing import Optional

from src.domain.models.profile import SessionOutcome
from src.presentation.formatters.stats_formatter import StatsFormatter
from src.infrastructure.logging import game_logger as log


class LastGameDialog(wx.Dialog):
    """Show summary of last completed game.
    
    Read-only dialog with:
    - Game date/time
    - Outcome (vittoria/abbandono/timeout)
    - Time played, moves, score
    - Game config (difficulty, deck, timer)
    
    Keyboard:
    - ESC: Close
    """
    
    def __init__(self, parent, outcome: SessionOutcome):
        """Initialize last game dialog.
        
        Args:
            parent: Parent window
            outcome: SessionOutcome with last game data
        """
        super().__init__(
            parent,
            title="Ultima Partita Giocata",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        
        self.outcome = outcome
        self.formatter = StatsFormatter()
        
        log.dialog_shown("last_game_dialog", "Ultima Partita")
        
        self._create_ui()
        self._set_focus()
    
    def _create_ui(self) -> None:
        """Create dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header
        header = wx.StaticText(self, label="RIEPILOGO ULTIMA PARTITA")
        font = header.GetFont()
        font.PointSize += 1
        font = font.Bold()
        header.SetFont(font)
        sizer.Add(header, 0, wx.ALL | wx.CENTER, 10)
        
        # Content
        content = self._build_content_text()
        self.text_ctrl = wx.TextCtrl(
            self,
            value=content,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            size=(450, 250)
        )
        self.text_ctrl.SetName("Riepilogo ultima partita")
        sizer.Add(self.text_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        
        # Close button
        btn_close = wx.Button(self, wx.ID_CANCEL, "Chiudi (ESC)")
        sizer.Add(btn_close, 0, wx.ALL | wx.CENTER, 10)
        
        self.SetSizer(sizer)
        self.Fit()
    
    def _build_content_text(self) -> str:
        """Build summary content."""
        lines = []
        
        # Date/time
        try:
            dt = datetime.fromisoformat(self.outcome.session_date)
            lines.append(f"Data: {dt.strftime('%d/%m/%Y alle %H:%M')}")
        except (ValueError, AttributeError):
            lines.append(f"Data: Non disponibile")
        lines.append("")
        
        # Outcome
        outcome_label = "VITTORIA" if self.outcome.is_victory else "SCONFITTA"
        lines.append(f"Esito: {outcome_label}")
        if not self.outcome.is_victory:
            reason = self.formatter.format_end_reason(self.outcome.end_reason)
            lines.append(f"Motivo: {reason}")
        lines.append("")
        
        # Stats
        lines.append(f"Tempo giocato: {self.formatter.format_duration(self.outcome.elapsed_time)}")
        lines.append(f"Mosse: {self.outcome.move_count}")
        
        if self.outcome.is_victory and self.outcome.scoring_enabled and self.outcome.final_score > 0:
            lines.append(f"Punteggio: {self.formatter.format_number(self.outcome.final_score)} punti")
        lines.append("")
        
        # Config
        lines.append("[CONFIGURAZIONE]")
        lines.append(f"Difficoltà: Livello {self.outcome.difficulty_level}")
        
        # Deck count from deck_type (rough approximation - default to 1)
        deck_count = 1  # Default, could be enhanced later
        deck_label = "1 mazzo" if deck_count == 1 else f"{deck_count} mazzi"
        deck_type_label = "francese" if self.outcome.deck_type == "french" else "napoletano"
        lines.append(f"Mazzo: {deck_type_label}")
        
        if self.outcome.timer_enabled:
            timer_limit = self.formatter.format_time_mm_ss(self.outcome.timer_limit)
            lines.append(f"Timer: {timer_limit} ({self.outcome.timer_mode})")
        else:
            lines.append("Timer: Disabilitato")
        
        return "\n".join(lines)
    
    def _set_focus(self) -> None:
        """Set initial focus and TTS announcement."""
        self.text_ctrl.SetFocus()
        
        # TTS announcement
        outcome_label = "Vittoria" if self.outcome.is_victory else "Sconfitta"
        elapsed = self.formatter.format_duration(self.outcome.elapsed_time)
        announcement = f"Ultima partita: {outcome_label}. Tempo: {elapsed}."
        self.SetTitle(announcement)
    
    def Destroy(self):
        """Override Destroy to log dialog closure."""
        log.dialog_closed("last_game_dialog", "closed")
        return super().Destroy()
