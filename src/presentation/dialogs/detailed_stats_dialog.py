"""Detailed stats dialog with 3-page navigation.

Shows comprehensive profile statistics across multiple pages.
NVDA-optimized with keyboard navigation.
"""

import wx
from typing import List

from src.domain.models.statistics import (
    GlobalStats, TimerStats, DifficultyStats, ScoringStats
)
from src.presentation.formatters.stats_formatter import StatsFormatter


class DetailedStatsDialog(wx.Dialog):
    """Detailed statistics dialog with 3-page navigation.
    
    Pages:
    1. Global stats (performance, streak, time, records)
    2. Timer stats (performance, overtime, mode breakdown)
    3. Scoring + Difficulty stats
    
    Keyboard:
    - Arrow keys: Scroll within page
    - Page Down: Next page
    - Page Up: Previous page
    - ESC: Close dialog
    """
    
    def __init__(
        self,
        parent,
        profile_name: str,
        global_stats: GlobalStats,
        timer_stats: TimerStats,
        difficulty_stats: DifficultyStats,
        scoring_stats: ScoringStats
    ):
        """Initialize detailed stats dialog.
        
        Args:
            parent: Parent window
            profile_name: Profile display name
            global_stats: GlobalStats instance
            timer_stats: TimerStats instance
            difficulty_stats: DifficultyStats instance
            scoring_stats: ScoringStats instance
        """
        super().__init__(
            parent,
            title="Statistiche Dettagliate",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        
        self.profile_name = profile_name
        self.formatter = StatsFormatter()
        self.current_page = 0
        
        # Build all 3 pages
        self.pages: List[str] = [
            self.formatter.format_global_stats_detailed(global_stats, profile_name),
            self.formatter.format_timer_stats_detailed(timer_stats, global_stats),  # Pass global_stats (v3.1.1)
            self.formatter.format_scoring_difficulty_stats(scoring_stats, difficulty_stats)
        ]
        
        self._create_ui()
        self._set_focus()
        
        # Bind page navigation
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key_press)
    
    def _create_ui(self) -> None:
        """Create dialog UI elements."""
        # Main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Stats content (TextCtrl readonly with scroll)
        self.stats_text = wx.TextCtrl(
            self,
            value=self.pages[0],
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            size=(600, 500)
        )
        self.stats_text.SetName(f"Statistiche dettagliate - Pagina 1 di 3")
        sizer.Add(self.stats_text, 1, wx.ALL | wx.EXPAND, 10)
        
        # Close button
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_close = wx.Button(self, wx.ID_CANCEL, "Chiudi (ESC)")
        btn_sizer.Add(self.btn_close, 0, wx.ALL, 5)
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 10)
        
        self.SetSizer(sizer)
        self.Fit()
    
    def _on_key_press(self, event):
        """Handle keyboard navigation."""
        keycode = event.GetKeyCode()
        
        if keycode == wx.WXK_PAGEDOWN:
            # Next page
            if self.current_page < len(self.pages) - 1:
                self.current_page += 1
                self._update_page()
        elif keycode == wx.WXK_PAGEUP:
            # Previous page
            if self.current_page > 0:
                self.current_page -= 1
                self._update_page()
        else:
            # Let other keys pass through (arrow keys for scrolling, ESC for close)
            event.Skip()
    
    def _update_page(self) -> None:
        """Update displayed page content."""
        self.stats_text.SetValue(self.pages[self.current_page])
        self.stats_text.SetName(f"Statistiche dettagliate - Pagina {self.current_page + 1} di 3")
        
        # Announce page change via TTS
        announcement = f"Pagina {self.current_page + 1} di 3"
        self.SetTitle(announcement)
        
        # Reset scroll position
        self.stats_text.SetInsertionPoint(0)
    
    def _set_focus(self) -> None:
        """Set initial focus and TTS announcement."""
        self.stats_text.SetFocus()
        
        announcement = f"Statistiche dettagliate di {self.profile_name}. Pagina 1 di 3."
        self.SetTitle(announcement)
