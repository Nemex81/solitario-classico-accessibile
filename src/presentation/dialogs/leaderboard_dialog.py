"""Global leaderboard dialog.

Shows rankings across all profiles for various metrics.
NVDA-optimized with keyboard navigation.
"""

import wx
from typing import List, Dict, Any

from src.presentation.formatters.stats_formatter import StatsFormatter


class LeaderboardDialog(wx.Dialog):
    """Global leaderboard dialog with multiple ranking views.
    
    Rankings:
    - Winrate (minimum 10 games)
    - Total victories
    - Fastest victory time
    - Highest score
    - Longest streak
    
    Keyboard:
    - Arrow keys: Scroll
    - ESC: Close dialog
    """
    
    def __init__(
        self,
        parent,
        all_profiles: List[Dict[str, Any]],
        current_profile_id: str,
        metric: str = "victories"
    ):
        """Initialize leaderboard dialog.
        
        Args:
            parent: Parent window
            all_profiles: List of all profile dicts with stats
            current_profile_id: ID of current profile (to highlight)
            metric: Ranking metric (winrate/victories/fastest_time/highest_score/streak)
        """
        super().__init__(
            parent,
            title="Classifica Globale",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        
        self.all_profiles = all_profiles
        self.current_profile_id = current_profile_id
        self.metric = metric
        self.formatter = StatsFormatter()
        
        self._create_ui()
        self._set_focus()
    
    def _create_ui(self) -> None:
        """Create dialog UI elements."""
        # Main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Leaderboard content
        content = self._build_leaderboard_text()
        self.leaderboard_text = wx.TextCtrl(
            self,
            value=content,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            size=(550, 450)
        )
        self.leaderboard_text.SetName("Classifica globale")
        sizer.Add(self.leaderboard_text, 1, wx.ALL | wx.EXPAND, 10)
        
        # Close button
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_close = wx.Button(self, wx.ID_CANCEL, "Chiudi (ESC)")
        btn_sizer.Add(self.btn_close, 0, wx.ALL, 5)
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 10)
        
        self.SetSizer(sizer)
        self.Fit()
    
    def _build_leaderboard_text(self) -> str:
        """Build leaderboard content text."""
        lines = []
        
        # Header
        lines.append("=" * 60)
        
        metric_titles = {
            "winrate": "CLASSIFICA WINRATE",
            "victories": "CLASSIFICA VITTORIE TOTALI",
            "fastest_time": "CLASSIFICA RECORD TEMPO",
            "highest_score": "CLASSIFICA RECORD PUNTEGGIO",
            "streak": "CLASSIFICA STREAK MASSIMO"
        }
        
        title = metric_titles.get(self.metric, "CLASSIFICA")
        lines.append(f"    {title}")
        lines.append("=" * 60)
        lines.append("")
        
        # Calculate ranking
        ranking = self._calculate_ranking()
        
        if not ranking:
            lines.append("Nessun dato disponibile per questa classifica.")
            return "\n".join(lines)
        
        # Display top 10
        for idx, entry in enumerate(ranking[:10], 1):
            profile_id = entry['profile_id']
            profile_name = entry['profile_name']
            value = entry['value']
            
            # Format value based on metric
            if self.metric == "winrate":
                value_str = self.formatter.format_percentage(value)
                games = entry.get('total_games', 0)
                value_str += f" ({games} partite)"
            elif self.metric == "victories":
                value_str = f"{value} vittorie"
            elif self.metric == "fastest_time":
                value_str = self.formatter.format_duration(value)
            elif self.metric == "highest_score":
                value_str = f"{self.formatter.format_number(value)} punti"
            elif self.metric == "streak":
                value_str = f"{value} vittorie consecutive"
            else:
                value_str = str(value)
            
            # Highlight current profile
            marker = " ← TU" if profile_id == self.current_profile_id else ""
            
            lines.append(f"{idx:2}. {profile_name:<20} {value_str}{marker}")
        
        lines.append("")
        lines.append("─" * 60)
        lines.append("ESC - Chiudi")
        
        return "\n".join(lines)
    
    def _calculate_ranking(self) -> List[Dict[str, Any]]:
        """Calculate ranking for current metric.
        
        Returns:
            Sorted list of profile entries with ranking value
        """
        ranking = []
        
        for profile in self.all_profiles:
            # Skip guest profile
            if profile.get('is_guest', False):
                continue
            
            profile_id = profile.get('profile_id')
            profile_name = profile.get('profile_name', 'Unknown')
            global_stats = profile.get('global_stats', {})
            
            # Extract value based on metric
            if self.metric == "winrate":
                total_games = global_stats.get('total_games', 0)
                if total_games < 10:  # Minimum games requirement
                    continue
                value = global_stats.get('winrate', 0)
                ranking.append({
                    'profile_id': profile_id,
                    'profile_name': profile_name,
                    'value': value,
                    'total_games': total_games
                })
            
            elif self.metric == "victories":
                value = global_stats.get('total_victories', 0)
                if value == 0:
                    continue
                ranking.append({
                    'profile_id': profile_id,
                    'profile_name': profile_name,
                    'value': value
                })
            
            elif self.metric == "fastest_time":
                value = global_stats.get('fastest_victory', float('inf'))
                if value == float('inf'):
                    continue
                ranking.append({
                    'profile_id': profile_id,
                    'profile_name': profile_name,
                    'value': value
                })
            
            elif self.metric == "highest_score":
                value = global_stats.get('highest_score', 0)
                if value == 0:
                    continue
                ranking.append({
                    'profile_id': profile_id,
                    'profile_name': profile_name,
                    'value': value
                })
            
            elif self.metric == "streak":
                value = global_stats.get('longest_streak', 0)
                if value == 0:
                    continue
                ranking.append({
                    'profile_id': profile_id,
                    'profile_name': profile_name,
                    'value': value
                })
        
        # Sort ranking (descending for most metrics, ascending for fastest_time)
        reverse = self.metric != "fastest_time"
        ranking.sort(key=lambda x: x['value'], reverse=reverse)
        
        return ranking
    
    def _set_focus(self) -> None:
        """Set initial focus and TTS announcement."""
        self.leaderboard_text.SetFocus()
        
        metric_names = {
            "winrate": "Winrate",
            "victories": "Vittorie totali",
            "fastest_time": "Record tempo",
            "highest_score": "Record punteggio",
            "streak": "Streak massimo"
        }
        
        metric_name = metric_names.get(self.metric, "Classifica")
        announcement = f"Classifica globale: {metric_name}"
        self.SetTitle(announcement)
