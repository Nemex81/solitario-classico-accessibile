"""Victory dialog with integrated statistics.

Shows victory message with game stats and updated profile statistics.
NVDA-optimized with proper focus management and TTS announcements.
"""

import wx
from typing import Dict, Any

from src.domain.models.profile import SessionOutcome
from src.domain.models.game_end import EndReason
from src.presentation.formatters.stats_formatter import StatsFormatter


class VictoryDialog(wx.Dialog):
    """Victory end game dialog with stats summary.
    
    Shows:
    - Victory message
    - Time, moves, score (if enabled)
    - Timer info (if enabled + overtime warning)
    - Profile stats update (victories, winrate)
    - Record notifications
    
    Keyboard:
    - ENTER: New game
    - ESC: Main menu
    """
    
    def __init__(self, parent, outcome: SessionOutcome, profile_summary: Dict[str, Any]):
        """Initialize victory dialog.
        
        Args:
            parent: Parent window
            outcome: SessionOutcome with game results
            profile_summary: Dict with updated profile stats
        """
        super().__init__(
            parent,
            title="Vittoria!",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        
        self.outcome = outcome
        self.profile_summary = profile_summary
        self.formatter = StatsFormatter()
        
        self._create_ui()
        self._set_focus()
    
    def _create_ui(self) -> None:
        """Create dialog UI elements."""
        # Main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Victory header
        header = wx.StaticText(self, label="═" * 45)
        header_title = wx.StaticText(self, label="           VITTORIA!")
        header_bottom = wx.StaticText(self, label="═" * 45)
        
        font_header = header_title.GetFont()
        font_header.PointSize += 2
        font_header = font_header.Bold()
        header_title.SetFont(font_header)
        
        sizer.Add(header, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(header_title, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(header_bottom, 0, wx.ALL | wx.EXPAND, 5)
        
        # Stats content (TextCtrl readonly)
        content = self._build_content_text()
        self.stats_text = wx.TextCtrl(
            self,
            value=content,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            size=(500, 300)
        )
        self.stats_text.SetName("Statistiche vittoria")
        sizer.Add(self.stats_text, 1, wx.ALL | wx.EXPAND, 10)
        
        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_new_game = wx.Button(self, wx.ID_OK, "Nuova Partita (INVIO)")
        self.btn_menu = wx.Button(self, wx.ID_CANCEL, "Menu Principale (ESC)")
        
        btn_sizer.Add(self.btn_new_game, 0, wx.ALL, 5)
        btn_sizer.Add(self.btn_menu, 0, wx.ALL, 5)
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 10)
        
        self.SetSizer(sizer)
        self.Fit()
    
    def _build_content_text(self) -> str:
        """Build victory stats content text."""
        lines = []
        
        # Time and moves
        lines.append(f"Tempo: {self.formatter.format_duration(self.outcome.elapsed_time)}")
        lines.append(f"Mosse: {self.outcome.move_count}")
        lines.append("")
        
        # Timer info
        if self.outcome.timer_enabled:
            if self.outcome.end_reason == EndReason.VICTORY_OVERTIME:
                overtime = self.outcome.elapsed_time - self.outcome.timer_limit
                lines.append(f"⚠ Overtime: +{self.formatter.format_duration(overtime)}")
            else:
                lines.append(f"✓ Completato entro il limite ({self.formatter.format_time_mm_ss(self.outcome.timer_limit)})")
            lines.append("")
        
        # Scoring
        if self.outcome.scoring_enabled and self.outcome.final_score > 0:
            lines.append(f"Punteggio: {self.formatter.format_number(self.outcome.final_score)} punti")
            lines.append("")
        
        # Profile stats
        lines.append("[STATISTICHE PROFILO - Aggiornate]")
        lines.append(f"Vittorie totali: {self.profile_summary.get('total_victories', 0)}")
        winrate = self.profile_summary.get('winrate', 0)
        lines.append(f"Winrate: {self.formatter.format_percentage(winrate)}")
        lines.append("")
        
        # Record notification
        if self.profile_summary.get('new_record'):
            lines.append("🏆 NUOVO RECORD: Vittoria più veloce!")
            if 'previous_record' in self.profile_summary:
                prev = self.formatter.format_duration(self.profile_summary['previous_record'])
                lines.append(f"  Precedente: {prev}")
        
        return "\n".join(lines)
    
    def _set_focus(self) -> None:
        """Set initial focus and TTS announcement."""
        self.stats_text.SetFocus()
        
        # TTS announcement (via accessible name)
        elapsed = self.formatter.format_duration(self.outcome.elapsed_time)
        score_part = ""
        if self.outcome.scoring_enabled and self.outcome.final_score > 0:
            score_part = f" Punteggio: {self.outcome.final_score} punti."
        
        announcement = (
            f"Vittoria! Completato in {elapsed} con {self.outcome.move_count} mosse."
            f"{score_part} Vittorie totali: {self.profile_summary.get('total_victories', 0)}."
        )
        
        if self.profile_summary.get('new_record'):
            announcement += " Nuovo record personale: vittoria più veloce!"
        
        self.SetTitle(announcement)
