"""Formatter for profile statistics presentation (TTS-friendly)."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from src.domain.models.profile import SessionOutcome, EndReason
from src.domain.models.statistics import (
    GlobalStats, TimerStats, DifficultyStats, ScoringStats
)


class StatsFormatter:
    """Format profile statistics for screen-reader friendly presentation.
    
    All methods return multi-line strings optimized for NVDA reading.
    Includes proper Italian formatting (thousands separator, plurals).
    """
    
    # ========================================
    # TIME FORMATTING
    # ========================================
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in Italian (human-readable).
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Human-readable Italian duration string
            
        Examples:
            42 sec -> "42 secondi"
            90 sec -> "1 minuto e 30 secondi"
            3665 sec -> "1 ora, 1 minuto e 5 secondi"
        """
        if seconds < 60:
            return f"{int(seconds)} secondi"
        
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        
        if minutes < 60:
            if secs == 0:
                return f"{minutes} minuti" if minutes > 1 else "1 minuto"
            min_str = f"{minutes} minuti" if minutes > 1 else "1 minuto"
            return f"{min_str} e {secs} secondi"
        
        hours = minutes // 60
        mins = minutes % 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours} ora" if hours == 1 else f"{hours} ore")
        if mins > 0:
            parts.append(f"{mins} minuti" if mins > 1 else f"{mins} minuto")
        if secs > 0:
            parts.append(f"{secs} secondi")
        
        if len(parts) == 0:
            return "0 secondi"
        elif len(parts) == 1:
            return parts[0]
        else:
            return ", ".join(parts[:-1]) + " e " + parts[-1]
    
    @staticmethod
    def format_time_mm_ss(seconds: float) -> str:
        """Format time as MM:SS.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            MM:SS formatted string
            
        Examples:
            42 -> "0:42"
            325 -> "5:25"
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    # ========================================
    # NUMBER FORMATTING
    # ========================================
    
    @staticmethod
    def format_number(value: int) -> str:
        """Format number with thousands separator.
        
        Args:
            value: Integer to format
            
        Returns:
            Formatted string with Italian thousands separator (.)
            
        Examples:
            1250 -> "1.250"
            450 -> "450"
        """
        return f"{value:,}".replace(",", ".")
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """Format percentage.
        
        Args:
            value: Percentage value (0.0-1.0)
            decimals: Number of decimal places
            
        Returns:
            Formatted percentage string with Italian decimal separator (,)
            
        Examples:
            0.6742 -> "67,4%"
            0.5 -> "50,0%"
        """
        return f"{value * 100:.{decimals}f}%".replace(".", ",")
    
    # ========================================
    # END REASON FORMATTING
    # ========================================
    
    @staticmethod
    def format_end_reason(reason: EndReason) -> str:
        """Format EndReason as Italian label.
        
        Args:
            reason: EndReason enum value
            
        Returns:
            Human-readable Italian label for TTS
        """
        labels = {
            EndReason.VICTORY: "Vittoria",
            EndReason.VICTORY_OVERTIME: "Vittoria (oltre tempo)",
            EndReason.ABANDON_NEW_GAME: "Abbandono (nuova partita)",
            EndReason.ABANDON_EXIT: "Abbandono volontario",
            EndReason.ABANDON_APP_CLOSE: "Chiusura app durante partita",
            EndReason.TIMEOUT_STRICT: "Tempo scaduto"
        }
        return labels.get(reason, reason.value)
    
    # ========================================
    # GLOBAL STATS FORMATTING
    # ========================================
    
    def format_global_stats_summary(self, stats: GlobalStats) -> str:
        """Format global stats summary (for victory dialog footer).
        
        Args:
            stats: GlobalStats instance with aggregated statistics
            
        Returns:
            2-3 line summary with victories, winrate
        """
        victories = self.format_number(stats.total_victories)
        winrate = self.format_percentage(stats.winrate)
        
        return (
            f"Vittorie totali: {victories}\n"
            f"Winrate: {winrate}"
        )
    
    def format_global_stats_detailed(self, stats: GlobalStats, profile_name: str) -> str:
        """Format full global stats page (Page 1 of detailed stats).
        
        Args:
            stats: GlobalStats instance
            profile_name: Profile display name for header
            
        Returns:
            Multi-line formatted text for 3-page stats dialog (Page 1/3)
        """
        header = f"{'=' * 56}\n"
        header += f"    STATISTICHE PROFILO: {profile_name}\n"
        header += f"{'=' * 56}\n\n"
        
        performance = "PERFORMANCE GLOBALE\n"
        performance += f"Partite totali: {stats.total_games}\n"
        performance += f"Vittorie: {stats.total_victories} ({self.format_percentage(stats.winrate)})\n"
        
        defeats = stats.total_games - stats.total_victories
        defeat_rate = 1 - stats.winrate if stats.total_games > 0 else 0
        performance += f"Sconfitte: {defeats} ({self.format_percentage(defeat_rate)})\n\n"
        
        streak = "STREAK\n"
        streak += f"Streak corrente: {stats.current_streak} vittorie\n"
        streak += f"Streak massimo: {stats.longest_streak} vittorie consecutive\n\n"
        
        time_stats = "TEMPO\n"
        time_stats += f"Tempo totale giocato: {self.format_duration(stats.total_playtime)}\n"
        avg_time = stats.total_playtime / stats.total_games if stats.total_games > 0 else 0
        time_stats += f"Tempo medio per partita: {self.format_duration(avg_time)}\n\n"
        
        records = "RECORD PERSONALI\n"
        if stats.fastest_victory < float('inf'):
            records += f"🏆 Vittoria più veloce: {self.format_duration(stats.fastest_victory)}\n"
        if stats.slowest_victory > 0:
            records += f"🏆 Vittoria più lenta: {self.format_duration(stats.slowest_victory)}\n"
        if stats.highest_score > 0:
            records += f"🏆 Punteggio massimo: {self.format_number(stats.highest_score)} punti\n"
        
        footer = f"\n{'─' * 56}\n"
        footer += "Pagina 1/3\n"
        footer += "PAGE DOWN - Pagina successiva\n"
        footer += "ESC - Torna a Gestione Profili"
        
        return header + performance + streak + time_stats + records + footer
