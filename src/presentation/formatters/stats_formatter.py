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
            
        Version:
            v3.1.0: Initial implementation
            v3.1.2: Added edge case handling for 0-game profiles
        """
        # ========== v3.1.2: Handle empty profile (0 games) ==========
        if stats.total_games == 0:
            return f"""{'=' * 56}
    STATISTICHE PROFILO: {profile_name}
{'=' * 56}

Nessuna statistica disponibile.
Gioca la tua prima partita per iniziare a tracciare le statistiche!

{'─' * 56}
Pagina 1/3
PAGE DOWN - Pagina successiva
ESC - Torna a Gestione Profili"""
        
        # ========== Normal formatting (existing code) ==========
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
        # v3.1.2: Defensive programming for None/infinite values
        if stats.fastest_victory and stats.fastest_victory < float('inf'):
            records += f"🏆 Vittoria più veloce: {self.format_duration(stats.fastest_victory)}\n"
        else:
            records += "🏆 Vittoria più veloce: N/D\n"
        
        if stats.slowest_victory and stats.slowest_victory > 0:
            records += f"🏆 Vittoria più lenta: {self.format_duration(stats.slowest_victory)}\n"
        else:
            records += "🏆 Vittoria più lenta: N/D\n"
        
        if stats.highest_score > 0:
            records += f"🏆 Punteggio massimo: {self.format_number(stats.highest_score)} punti\n"
        else:
            records += "🏆 Punteggio massimo: N/D\n"
        
        footer = f"\n{'─' * 56}\n"
        footer += "Pagina 1/3\n"
        footer += "PAGE DOWN - Pagina successiva\n"
        footer += "ESC - Torna a Gestione Profili"
        
        return header + performance + streak + time_stats + records + footer
    
    # ========================================
    # TIMER STATS FORMATTING
    # ========================================
    
    def format_timer_stats_detailed(self, stats: TimerStats, global_stats: GlobalStats) -> str:
        """Format timer stats page (Page 2 of detailed stats).
        
        Args:
            stats: TimerStats instance with timer-specific data
            global_stats: GlobalStats instance for cross-stat calculations
            
        Returns:
            Multi-line formatted text for timer performance (Page 2/3)
            
        Note:
            v3.1.1: Now requires global_stats parameter for games_without_timer
            calculation and complete timer mode breakdown display.
            
        Version:
            v3.1.1: Added global_stats parameter for cross-stat support
        """
        header = f"{'=' * 56}\n"
        header += f"    STATISTICHE TIMER\n"
        header += f"{'=' * 56}\n\n"
        
        # Calculate games_without_timer from GlobalStats (defensive: handle corruption)
        games_without_timer = max(0, global_stats.total_games - stats.games_with_timer)
        
        # Timer usage
        timer_section = "UTILIZZO TIMER\n"
        timer_section += f"Partite con timer attivo: {stats.games_with_timer}\n"
        timer_section += f"Partite senza timer: {games_without_timer}\n\n"
        
        if stats.games_with_timer > 0:
            # Performance breakdown
            perf_section = "PERFORMANCE TEMPORALE\n"
            perf_section += f"Entro il limite: {stats.victories_within_time}\n"
            perf_section += f"Overtime: {stats.victories_overtime}\n"
            perf_section += f"Timeout (sconfitte): {stats.defeats_timeout}\n"
            
            # Calculate success rate
            within_rate = stats.victories_within_time / stats.games_with_timer
            perf_section += f"Tasso completamento in tempo: {self.format_percentage(within_rate)}\n\n"
            
            # Overtime analytics
            overtime_section = "ANALISI OVERTIME\n"
            if stats.victories_overtime > 0:
                overtime_section += f"Overtime medio: {self.format_duration(stats.average_overtime)}\n"
                overtime_section += f"Overtime massimo: {self.format_duration(stats.max_overtime)}\n\n"
            else:
                overtime_section += "Nessuna partita in overtime\n\n"
            
            # Mode breakdown (now tracked in TimerStats v3.1.1!)
            mode_section = "PER MODALITÀ\n"
            mode_section += f"STRICT: {stats.strict_mode_games} partite\n"
            mode_section += f"PERMISSIVE: {stats.permissive_mode_games} partite\n"
            
            content = timer_section + perf_section + overtime_section + mode_section
        else:
            content = timer_section + "\nNessuna partita con timer giocata.\n"
        
        footer = f"\n{'─' * 56}\n"
        footer += "Pagina 2/3\n"
        footer += "PAGE UP - Pagina precedente | PAGE DOWN - Pagina successiva\n"
        footer += "ESC - Torna a Gestione Profili"
        
        return header + content + footer
    
    # ========================================
    # SCORING + DIFFICULTY STATS FORMATTING
    # ========================================
    
    def format_scoring_difficulty_stats(
        self,
        scoring_stats: ScoringStats,
        difficulty_stats: DifficultyStats
    ) -> str:
        """Format scoring and difficulty stats (Page 3 of detailed stats).
        
        Args:
            scoring_stats: ScoringStats instance
            difficulty_stats: DifficultyStats instance
            
        Returns:
            Multi-line formatted text for scoring/difficulty (Page 3/3)
        """
        header = f"{'=' * 56}\n"
        header += f"    PUNTEGGIO & DIFFICOLTÀ\n"
        header += f"{'=' * 56}\n\n"
        
        # Scoring analytics
        scoring_section = "PUNTEGGIO\n"
        if scoring_stats.games_with_scoring > 0:
            scoring_section += f"Partite con punteggio: {scoring_stats.games_with_scoring}\n"
            scoring_section += f"Punteggio medio: {self.format_number(int(scoring_stats.average_score))} punti\n"
            scoring_section += f"Punteggio massimo: {self.format_number(scoring_stats.highest_score)} punti\n\n"
        else:
            scoring_section += "Nessuna partita con punteggio abilitato\n\n"
        
        # Difficulty breakdown
        diff_section = "PERFORMANCE PER DIFFICOLTÀ\n"
        diff_section += f"{'─' * 56}\n"
        
        # Difficulty levels: 1=molto facile, 2=facile, 3=medio, 4=difficile, 5=molto difficile
        diff_labels = {
            1: "Molto Facile",
            2: "Facile",
            3: "Medio",
            4: "Difficile",
            5: "Molto Difficile"
        }
        
        for level in range(1, 6):
            games_at_level = difficulty_stats.games_per_level.get(level, 0)
            if games_at_level > 0:
                victories = difficulty_stats.victories_per_level.get(level, 0)
                winrate = victories / games_at_level if games_at_level > 0 else 0
                avg_score = difficulty_stats.avg_score_per_level.get(level, 0)
                
                diff_section += f"\n{diff_labels[level]} (Livello {level}):\n"
                diff_section += f"  Partite: {games_at_level}\n"
                diff_section += f"  Vittorie: {victories} ({self.format_percentage(winrate)})\n"
                if avg_score > 0:
                    diff_section += f"  Punteggio medio: {self.format_number(int(avg_score))} punti\n"
        
        footer = f"\n{'─' * 56}\n"
        footer += "Pagina 3/3\n"
        footer += "PAGE UP - Pagina precedente\n"
        footer += "ESC - Torna a Gestione Profili"
        
        return header + scoring_section + diff_section + footer
