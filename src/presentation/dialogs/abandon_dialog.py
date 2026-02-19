"""Abandon dialog with game statistics.

Shows abandon/defeat message with game progress and profile impact.
NVDA-optimized with proper focus management and TTS announcements.
"""

import wx
from typing import Dict, Any

from src.domain.models.profile import SessionOutcome
from src.domain.models.game_end import EndReason
from src.presentation.formatters.stats_formatter import StatsFormatter


class AbandonDialog(wx.Dialog):
    """Abandon/defeat end game dialog.
    
    Shows:
    - Abandon/defeat message with reason
    - Time played, moves made
    - Progress (cards in foundations)
    - Profile stats impact (winrate, streak broken)
    
    Keyboard:
    - ENTER: New game
    - ESC: Main menu
    """
    
    def __init__(self, parent, outcome: SessionOutcome, profile_summary: Dict[str, Any], 
                 show_rematch_option: bool = False):
        """Initialize abandon dialog.
        
        Args:
            parent: Parent window
            outcome: SessionOutcome with game results
            profile_summary: Dict with updated profile stats
            show_rematch_option: If True, show rematch/stats/menu buttons (for timeout).
                                If False, show standard new game/menu buttons (default).
        """
        super().__init__(
            parent,
            title="Partita Abbandonata",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        
        self.outcome = outcome
        self.profile_summary = profile_summary
        self.show_rematch_option = show_rematch_option
        self.formatter = StatsFormatter()
        
        self._create_ui()
        self._set_focus()
    
    def _create_ui(self) -> None:
        """Create dialog UI elements."""
        # Main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header
        header = wx.StaticText(self, label="═" * 45)
        header_title = wx.StaticText(self, label="      PARTITA ABBANDONATA")
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
            size=(500, 250)
        )
        self.stats_text.SetName("Statistiche abbandono")
        sizer.Add(self.stats_text, 1, wx.ALL | wx.EXPAND, 10)
        
        # Buttons (timeout vs normal abandon)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        if self.show_rematch_option:
            # Timeout scenario: 3 buttons (Rematch / Stats / Menu)
            self.btn_rematch = wx.Button(self, wx.ID_YES, "Rivincita")
            self.btn_stats = wx.Button(self, wx.ID_MORE, "Statistiche Dettagliate")
            self.btn_menu = wx.Button(self, wx.ID_NO, "Torna al Menu (ESC)")
            
            # Bind event handlers (v3.1.3 fix)
            self.btn_rematch.Bind(wx.EVT_BUTTON, self._on_rematch)
            self.btn_stats.Bind(wx.EVT_BUTTON, self._on_stats)
            self.btn_menu.Bind(wx.EVT_BUTTON, self._on_menu_timeout)
            
            btn_sizer.Add(self.btn_rematch, 0, wx.ALL, 5)
            btn_sizer.Add(self.btn_stats, 0, wx.ALL, 5)
            btn_sizer.Add(self.btn_menu, 0, wx.ALL, 5)
        else:
            # Normal abandon: 2 buttons (New Game / Menu)
            self.btn_new_game = wx.Button(self, wx.ID_OK, "Nuova Partita (INVIO)")
            self.btn_menu = wx.Button(self, wx.ID_CANCEL, "Menu Principale (ESC)")
            
            btn_sizer.Add(self.btn_new_game, 0, wx.ALL, 5)
            btn_sizer.Add(self.btn_menu, 0, wx.ALL, 5)
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 10)
        
        self.SetSizer(sizer)
        self.Fit()
    
    def _build_content_text(self) -> str:
        """Build abandon stats content text."""
        lines = []
        
        # Reason
        reason_text = self.formatter.format_end_reason(self.outcome.end_reason)
        lines.append(f"Motivo: {reason_text}")
        lines.append("")
        
        # Time and moves
        lines.append(f"Tempo giocato: {self.formatter.format_duration(self.outcome.elapsed_time)}")
        lines.append(f"Mosse: {self.outcome.move_count}")
        lines.append("")
        
        # Progress (cards in foundations)
        # Note: This would need to be added to SessionOutcome or calculated
        # For now, using a placeholder
        cards_placed = self.profile_summary.get('cards_placed', 0)
        progress = (cards_placed / 52) * 100 if cards_placed > 0 else 0
        lines.append(f"Progressione: {cards_placed}/52 carte ({progress:.1f}%)")
        lines.append("")
        
        # Profile stats impact
        lines.append("[STATISTICHE PROFILO - Aggiornate]")
        lines.append(f"Sconfitte totali: {self.profile_summary.get('total_defeats', 0)}")
        winrate = self.profile_summary.get('winrate', 0)
        lines.append(f"Winrate: {self.formatter.format_percentage(winrate)}")
        
        if self.profile_summary.get('streak_broken'):
            lines.append("")
            lines.append(f"⚠ Streak interrotto: era {self.profile_summary.get('previous_streak', 0)} vittorie")
        
        return "\n".join(lines)
    
    def _set_focus(self) -> None:
        """Set initial focus and TTS announcement."""
        self.stats_text.SetFocus()
        
        # TTS announcement
        reason = self.formatter.format_end_reason(self.outcome.end_reason)
        elapsed = self.formatter.format_duration(self.outcome.elapsed_time)
        
        announcement = (
            f"Partita abbandonata. Motivo: {reason}. "
            f"Tempo giocato: {elapsed}. Mosse: {self.outcome.move_count}."
        )
        
        self.SetTitle(announcement)

    # ========================================
    # BUTTON EVENT HANDLERS (v3.1.3 - Bug Fix)
    # ========================================

    def _on_rematch(self, event):
        """Handler for Rematch button (timeout scenario).

        Closes dialog with wx.ID_YES to signal rematch request.
        GameEngine will start new game.
        """
        self.EndModal(wx.ID_YES)

    def _on_stats(self, event):
        """Handler for Detailed Stats button (timeout scenario).

        Closes dialog with wx.ID_MORE to signal stats request.
        GameEngine will open DetailedStatsDialog.
        """
        self.EndModal(wx.ID_MORE)

    def _on_menu_timeout(self, event):
        """Handler for Main Menu button (timeout scenario).

        Closes dialog with wx.ID_NO to signal menu return.
        GameEngine will return control to main menu.
        """
        self.EndModal(wx.ID_NO)

    def _on_new_game(self, event):
        """Handler for New Game button (normal abandon scenario).

        Closes dialog with wx.ID_OK to signal new game request.
        GameEngine will start new game.
        """
        self.EndModal(wx.ID_OK)

    def _on_menu_normal(self, event):
        """Handler for Main Menu button (normal abandon scenario).

        Closes dialog with wx.ID_CANCEL to signal menu return.
        GameEngine will return control to main menu.
        """
        self.EndModal(wx.ID_CANCEL)
