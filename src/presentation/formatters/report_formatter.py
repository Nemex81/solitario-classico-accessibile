"""Format final game reports for TTS and dialog display.

This module provides static formatting methods for generating
Italian-language game reports optimized for screen reader output.

All output follows TTS best practices:
- Short sentences (max 10-12 words)
- Clear punctuation (periods for natural pauses)
- No symbols (use words: "completo!" not "✅")
- Natural number format ("3 minuti" not "3m")
"""

from typing import Dict, Any, Optional, List


class ReportFormatter:
    """Format final game reports for TTS and dialog display.
    
    All methods are static (stateless formatting).
    Output optimized for Italian screen readers (NVDA, JAWS).
    
    Example:
        >>> stats = service.get_final_statistics()
        >>> report = ReportFormatter.format_final_report(
        ...     stats=stats,
        ...     final_score=score,
        ...     is_victory=True,
        ...     deck_type="french"
        ... )
        >>> print(report)
        Hai Vinto!
        
        Tempo trascorso: 3 minuti e 45 secondi.
        Spostamenti totali: 85.
        ...
    """
    
    @staticmethod
    def format_final_report(
        stats: Dict[str, Any],
        final_score: Optional['FinalScore'] = None,
        is_victory: bool = False,
        deck_type: str = "french"
    ) -> str:
        """Generate complete final report.
        
        Args:
            stats: From GameService.get_final_statistics()
            final_score: Optional scoring data (if scoring enabled)
            is_victory: Whether game was won (all 4 suits complete)
            deck_type: "french" or "neapolitan" for suit names
            
        Returns:
            Multi-line Italian report string formatted for TTS
            
        Example output:
            ```
            Hai Vinto!
            
            Tempo trascorso: 3 minuti e 45 secondi.
            Spostamenti totali: 85.
            Rimischiate: 3.
            
            --- Statistiche Pile Semi ---
            Cuori: 13 carte (completo!).
            Quadri: 13 carte (completo!).
            Fiori: 10 carte.
            Picche: 8 carte.
            
            Semi completati: 2 su 4.
            Completamento totale: 44 su 52 carte (84.6%).
            
            Punteggio finale: 1523 punti.
            ```
        """
        lines = []
        
        # ═══════════════════════════════════════════════════════════
        # HEADER: Victory/defeat announcement
        # ═══════════════════════════════════════════════════════════
        if is_victory:
            lines.append("Hai Vinto!")
            lines.append("Complimenti, vittoria spumeggiante!")
        else:
            lines.append("Partita terminata.")
        
        lines.append("")  # Blank line for TTS pause
        
        # ═══════════════════════════════════════════════════════════
        # TIME & MOVES: Basic statistics
        # ═══════════════════════════════════════════════════════════
        elapsed = int(stats['elapsed_time'])
        minutes = elapsed // 60
        seconds = elapsed % 60
        lines.append(f"Tempo trascorso: {minutes} minuti e {seconds} secondi.")
        lines.append(f"Spostamenti totali: {stats['move_count']}.")
        
        # Reshuffles (if any)
        if 'recycle_count' in stats and stats['recycle_count'] > 0:
            lines.append(f"Rimischiate: {stats['recycle_count']}.")
        
        lines.append("")  # Blank line
        
        # ═══════════════════════════════════════════════════════════
        # SUIT STATISTICS: Per-suit breakdown
        # ═══════════════════════════════════════════════════════════
        lines.append("--- Statistiche Pile Semi ---")
        suit_names = ReportFormatter._get_suit_names(deck_type)
        max_cards = 13 if deck_type == "french" else 10
        
        for i, suit_name in enumerate(suit_names):
            count = stats['carte_per_seme'][i]
            
            if count == max_cards:
                lines.append(f"{suit_name}: {count} carte (completo!).")
            elif count > 0:
                lines.append(f"{suit_name}: {count} carte.")
            else:
                lines.append(f"{suit_name}: 0 carte.")
        
        lines.append("")  # Blank line
        
        # ═══════════════════════════════════════════════════════════
        # COMPLETION SUMMARY: Overall progress
        # ═══════════════════════════════════════════════════════════
        lines.append(
            f"Semi completati: {stats['semi_completati']} su 4."
        )
        
        total_cards = 52 if deck_type == "french" else 40
        lines.append(
            f"Completamento totale: {stats['total_foundation_cards']} "
            f"su {total_cards} carte "
            f"({stats['completion_percentage']:.1f}%)."
        )
        
        # ═══════════════════════════════════════════════════════════
        # SCORING: Final score (if enabled)
        # ═══════════════════════════════════════════════════════════
        if final_score:
            lines.append("")  # Blank line
            lines.append(f"Punteggio finale: {final_score.total_score} punti.")
        
        return "\n".join(lines)
    
    @staticmethod
    def _get_suit_names(deck_type: str) -> List[str]:
        """Get localized suit names for deck type.
        
        Args:
            deck_type: "french" or "neapolitan"
            
        Returns:
            List of 4 Italian suit names in foundation order
            
        Example:
            >>> ReportFormatter._get_suit_names("french")
            ['Cuori', 'Quadri', 'Fiori', 'Picche']
            
            >>> ReportFormatter._get_suit_names("neapolitan")
            ['Coppe', 'Denari', 'Bastoni', 'Spade']
        """
        if deck_type == "neapolitan":
            return ["Coppe", "Denari", "Bastoni", "Spade"]
        else:  # french (default)
            return ["Cuori", "Quadri", "Fiori", "Picche"]
