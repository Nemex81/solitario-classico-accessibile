"""Score formatter for TTS-optimized scoring messages in Italian.

Provides formatting for:
- Provisional scores (during gameplay)
- Final scores (at game end)
- Individual score events
- Scoring disabled messages

All messages are TTS-optimized (no special characters, clear pronunciation).
"""

from src.domain.models.scoring import ProvisionalScore, FinalScore, ScoreEvent, ScoreEventType


class ScoreFormatter:
    """Formatter for scoring messages optimized for screen readers.
    
    All methods are static - no internal state.
    Messages in Italian for accessibility.
    """
    
    # Event type translations (Italian TTS-friendly)
    EVENT_NAMES = {
        ScoreEventType.WASTE_TO_FOUNDATION: "Scarto a fondazione",
        ScoreEventType.TABLEAU_TO_FOUNDATION: "Tableau a fondazione",
        ScoreEventType.CARD_REVEALED: "Carta scoperta",
        ScoreEventType.FOUNDATION_TO_TABLEAU: "Fondazione a tableau",
        ScoreEventType.RECYCLE_WASTE: "Riciclo scarti",
        ScoreEventType.UNDO_MOVE: "Annulla mossa",
        ScoreEventType.HINT_USED: "Suggerimento usato"
    }
    
    @staticmethod
    def format_provisional_score(score: ProvisionalScore) -> str:
        """Format provisional score with complete breakdown.
        
        Shows current score during gameplay without victory bonus.
        
        Args:
            score: ProvisionalScore with current game state
            
        Returns:
            TTS message with score breakdown
            
        Example:
            "Punteggio provvisorio: 160 punti. Punteggio base: 10 punti.
             Bonus mazzo: 150 punti. Moltiplicatore difficoltà: 1 punto 0."
        """
        parts = [f"Punteggio provvisorio: {score.total_score} punti."]
        
        # Base score
        parts.append(f"Punteggio base: {score.base_score} punti.")
        
        # Deck bonus (if any)
        if score.deck_bonus > 0:
            parts.append(f"Bonus mazzo: {score.deck_bonus} punti.")
        
        # Draw bonus (if any)
        if score.draw_bonus > 0:
            parts.append(f"Bonus carte pescate: {score.draw_bonus} punti.")
        
        # Difficulty multiplier
        # Format as "1 punto 5" instead of "1.5" for better TTS
        mult_str = str(score.difficulty_multiplier).replace('.', ' punto ')
        parts.append(f"Moltiplicatore difficoltà: {mult_str}.")
        
        return " ".join(parts)
    
    @staticmethod
    def format_final_score(score: FinalScore) -> str:
        """Format final score with victory status and complete breakdown.
        
        Shows all components including time and victory bonuses.
        
        Args:
            score: FinalScore with complete game results
            
        Returns:
            TTS message with victory status and full breakdown
            
        Example:
            "Vittoria! Punteggio finale: 1015 punti. Punteggio base: 85 punti.
             Bonus mazzo: 150 punti. Bonus tempo: 345 punti. Bonus vittoria: 500 punti."
        """
        # Victory status
        if score.is_victory:
            intro = "Vittoria!"
        else:
            intro = "Partita terminata."
        
        parts = [
            f"{intro} Punteggio finale: {score.total_score} punti.",
            f"Punteggio base: {score.base_score} punti."
        ]
        
        # Deck bonus (if any)
        if score.deck_bonus > 0:
            parts.append(f"Bonus mazzo: {score.deck_bonus} punti.")
        
        # Draw bonus (if any)
        if score.draw_bonus > 0:
            parts.append(f"Bonus carte pescate: {score.draw_bonus} punti.")
        
        # Difficulty multiplier
        mult_str = str(score.difficulty_multiplier).replace('.', ' punto ')
        parts.append(f"Moltiplicatore difficoltà: {mult_str}.")
        
        # Time bonus (if any)
        if score.time_bonus != 0:
            if score.time_bonus > 0:
                parts.append(f"Bonus tempo: {score.time_bonus} punti.")
            else:
                # Negative time bonus (timer expired)
                parts.append(f"Penalità tempo: {abs(score.time_bonus)} punti.")
        
        # Victory bonus (if any)
        if score.victory_bonus > 0:
            parts.append(f"Bonus vittoria: {score.victory_bonus} punti.")
        
        # Game statistics
        elapsed_minutes = int(score.elapsed_seconds / 60)
        elapsed_seconds = int(score.elapsed_seconds % 60)
        parts.append(
            f"Tempo impiegato: {elapsed_minutes} minuti e {elapsed_seconds} secondi. "
            f"Mosse: {score.move_count}. Ricicli: {score.recycle_count}."
        )
        
        return " ".join(parts)
    
    @staticmethod
    def format_score_event(event: ScoreEvent) -> str:
        """Format a single score event for TTS announcement.
        
        Used for showing recent events or event history.
        
        Args:
            event: ScoreEvent to format
            
        Returns:
            TTS message describing the event and points
            
        Example:
            "Scarto a fondazione: più 10 punti."
            "Riciclo scarti: meno 20 punti."
        """
        event_name = ScoreFormatter.EVENT_NAMES.get(
            event.event_type,
            event.event_type.value
        )
        
        # Format points with "più" or "meno" for clarity
        if event.points > 0:
            points_str = f"più {event.points} punti"
        elif event.points < 0:
            points_str = f"meno {abs(event.points)} punti"
        else:
            points_str = "nessun punto"
        
        # Add context if available
        if event.context:
            return f"{event_name}, {event.context}: {points_str}."
        else:
            return f"{event_name}: {points_str}."
    
    @staticmethod
    def format_scoring_disabled() -> str:
        """Format message when scoring is disabled.
        
        Returns:
            TTS message explaining scoring is off
            
        Example:
            "Sistema di punteggio disattivato. Attivalo nelle opzioni per tracciare il punteggio."
        """
        return (
            "Sistema di punteggio disattivato. "
            "Attivalo nelle opzioni per tracciare il punteggio."
        )
    
    @staticmethod
    def format_best_score(score_dict: dict) -> str:
        """Format best score information.
        
        Used for displaying high scores and statistics.
        
        Args:
            score_dict: Dictionary with score data (total_score, is_victory, etc.)
            
        Returns:
            TTS message with best score info
            
        Example:
            "Miglior punteggio: 1250 punti. Vittoria: Sì. Difficoltà: Esperto."
        """
        if not score_dict:
            return "Nessun punteggio registrato."
        
        total = score_dict.get('total_score', 0)
        victory = "Sì" if score_dict.get('is_victory', False) else "No"
        difficulty = score_dict.get('difficulty_level', 1)
        
        # Difficulty names
        difficulty_names = {
            1: "Facile",
            2: "Medio",
            3: "Difficile",
            4: "Esperto",
            5: "Maestro"
        }
        difficulty_name = difficulty_names.get(difficulty, f"Livello {difficulty}")
        
        return (
            f"Miglior punteggio: {total} punti. "
            f"Vittoria: {victory}. "
            f"Difficoltà: {difficulty_name}."
        )
    
    # ========================================
    # V2.0 NEW FORMATTERS
    # ========================================
    
    @staticmethod
    def format_summary(final_score: FinalScore) -> str:
        """Format concise summary for TTS (v2.0).
        
        Optimized for screen readers - minimal, essential info only.
        
        Args:
            final_score: Complete score with all components
            
        Returns:
            Concise TTS message with status, time, moves, and total score
            
        Example:
            "Vittoria in 18 minuti con 142 mosse. Punteggio totale: 1523 punti."
            "Partita abbandonata in 10 minuti con 85 mosse. Punteggio totale: 244 punti."
        """
        # Status
        status = "Vittoria" if final_score.is_victory else "Partita abbandonata"
        
        # Time
        minutes = int(final_score.elapsed_seconds // 60)
        
        # Score
        return (
            f"{status} in {minutes} minuti con {final_score.move_count} mosse. "
            f"Punteggio totale: {final_score.total_score} punti."
        )
    
    @staticmethod
    def format_detailed(final_score: FinalScore) -> str:
        """Format detailed breakdown for TTS (v2.0).
        
        Complete score breakdown with all components.
        Handles legacy scores (victory_quality_multiplier < 0).
        
        Args:
            final_score: Complete score with all components
            
        Returns:
            Detailed TTS message with full breakdown
            
        Example:
            "Dettaglio punteggio: Punteggio base dalle mosse: 95 punti.
             Bonus mazzo napoletano: 100 punti. Bonus pescata 3 carte: 100 punti.
             Moltiplicatore difficoltà livello 4: 1 punto 8.
             Punteggio provvisorio: 531 punti.
             Bonus tempo: 480 punti.
             Bonus vittoria: 454 punti, qualità 1 punto 14.
             Punteggio finale: 1465 punti."
        """
        parts = ["Dettaglio punteggio:"]
        
        # Base score
        parts.append(f"Punteggio base dalle mosse: {final_score.base_score} punti.")
        
        # Deck bonus
        deck_name = "napoletano" if final_score.deck_type == "neapolitan" else "francese"
        parts.append(f"Bonus mazzo {deck_name}: {final_score.deck_bonus} punti.")
        
        # Draw bonus (if any)
        if final_score.draw_bonus > 0:
            parts.append(
                f"Bonus pescata {final_score.draw_count} carte: "
                f"{final_score.draw_bonus} punti."
            )
        
        # Difficulty multiplier (format for TTS: "1.8" → "1 punto 8")
        mult_str = str(final_score.difficulty_multiplier).replace('.', ' punto ')
        parts.append(
            f"Moltiplicatore difficoltà livello {final_score.difficulty_level}: "
            f"{mult_str}."
        )
        
        # Provisional score calculation
        provisional = int(
            (final_score.base_score + final_score.deck_bonus + final_score.draw_bonus) *
            final_score.difficulty_multiplier
        )
        parts.append(f"Punteggio provvisorio: {provisional} punti.")
        
        # Time bonus (if any)
        if final_score.time_bonus != 0:
            parts.append(f"Bonus tempo: {final_score.time_bonus} punti.")
        
        # Victory bonus with quality (v2.0 feature)
        if final_score.victory_bonus > 0:
            # Check if quality is available (v2.0) or legacy (v1.0)
            if hasattr(final_score, 'victory_quality_multiplier') and \
               final_score.victory_quality_multiplier > 0:
                # v2.0: Show quality multiplier
                quality_str = str(final_score.victory_quality_multiplier).replace('.', ' punto ')
                parts.append(
                    f"Bonus vittoria: {final_score.victory_bonus} punti, "
                    f"qualità {quality_str}."
                )
            else:
                # v1.0 legacy: No quality info
                parts.append(f"Bonus vittoria: {final_score.victory_bonus} punti (legacy).")
        
        # Final score
        parts.append(f"Punteggio finale: {final_score.total_score} punti.")
        
        return " ".join(parts)
    
    @staticmethod
    def format_threshold_warning(
        event_type: str,
        current: int,
        threshold: int,
        penalty: int
    ) -> str:
        """Format threshold warning for TTS (v2.0).
        
        Warns player when crossing scoring thresholds.
        
        Args:
            event_type: Type of event ("stock_draw" or "recycle")
            current: Current count
            threshold: Threshold just crossed
            penalty: Penalty per event after threshold
            
        Returns:
            TTS warning message
            
        Examples:
            "Attenzione: superata soglia 20 pescate. Penalità -1 punto per pescata."
            "Attenzione: terzo riciclo. Dal prossimo riciclo penalità -10 punti."
        """
        if event_type == "stock_draw":
            return (
                f"Attenzione: superata soglia {threshold} pescate. "
                f"Penalità {penalty} punto per pescata."
            )
        elif event_type == "recycle":
            if current == 3:
                return (
                    f"Attenzione: terzo riciclo. "
                    f"Dal prossimo riciclo penalità {penalty} punti."
                )
            else:
                return (
                    f"Attenzione: {current} ricicli. "
                    f"Penalità in aumento."
                )
        else:
            return f"Attenzione: soglia {threshold} superata."
