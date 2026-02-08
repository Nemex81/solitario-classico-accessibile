"""Game state formatter for text-to-speech output.

Formats domain objects into accessible Italian text following
screen reader best practices.

All methods are pure functions that take domain models as input
and return formatted strings. No side effects.
"""

from typing import Optional, List
from src.domain.models.card import Card
from src.domain.models.pile import Pile
from src.domain.models.deck import ProtoDeck


class GameFormatter:
    """Formats game state for accessible output.
    
    Provides pure formatting functions that convert domain models
    into Italian text optimized for screen reader pronunciation.
    
    All methods are static - no internal state.
    
    Design Principles:
    1. Italian language conventions
    2. Screen reader friendly (avoid symbols/abbreviations)
    3. Concise but complete information
    4. Natural pronunciation flow
    
    Example:
        >>> card = Card("7", "cuori")
        >>> GameFormatter.format_card(card)
        "Sette di cuori, scoperta"
    """
    
    # ===== ORIGINAL FORMATTERS (unchanged) =====
    
    @staticmethod
    def format_card(
        card: Card,
        include_status: bool = True
    ) -> str:
        """Format card for speech.
        
        Args:
            card: Card to format
            include_status: Include covered/uncovered status
        
        Returns:
            Italian text: "Sette di cuori, scoperta"
        
        Example:
            >>> card = Card("Asso", "picche")
            >>> card.set_uncover()
            >>> GameFormatter.format_card(card)
            "Asso di picche, scoperta"
        """
        # Base: "Sette di cuori"
        text = f"{card.get_name} di {card.get_suit}"
        
        if include_status:
            status = "scoperta" if not card.get_covered else "coperta"
            text += f", {status}"
        
        return text
    
    @staticmethod
    def format_pile_summary(
        pile: Pile,
        include_top_card: bool = True
    ) -> str:
        """Format pile summary for speech.
        
        Args:
            pile: Pile to format
            include_top_card: Include top card description
        
        Returns:
            Italian text describing pile state
        
        Examples:
            >>> # Empty pile
            "Pila base 1: vuota"
            
            >>> # Pile with cards
            "Pila base 3: 5 carte, ultima Regina di quadri scoperta"
        """
        pile_name = pile.get_name()
        card_count = pile.get_len()
        
        if card_count == 0:
            return f"{pile_name}: vuota"
        
        # Count + plural
        count_text = f"{card_count} carta" if card_count == 1 else f"{card_count} carte"
        
        text = f"{pile_name}: {count_text}"
        
        if include_top_card:
            top_card = pile.get_top_card()
            if top_card:
                card_text = GameFormatter.format_card(top_card, include_status=True)
                text += f", ultima {card_text}"
        
        return text
    
    @staticmethod
    def format_pile_detailed(
        pile: Pile,
        max_cards: int = 5
    ) -> str:
        """Format detailed pile information.
        
        Lists all visible cards (up to max_cards).
        
        Args:
            pile: Pile to format
            max_cards: Maximum cards to list
        
        Returns:
            Detailed Italian description
        
        Example:
            "Pila base 2: 3 carte visibili. Dall'alto: Regina di cuori, Fante di picche, 10 di cuori."
        """
        pile_name = pile.get_name()
        card_count = pile.get_len()
        
        if card_count == 0:
            return f"{pile_name}: vuota"
        
        # Count visible (uncovered) cards
        visible_cards = [c for c in pile.get_cards() if not c.get_covered]
        visible_count = len(visible_cards)
        
        if visible_count == 0:
            return f"{pile_name}: {card_count} carte coperte"
        
        # Base text
        count_text = f"{visible_count} carta visibile" if visible_count == 1 else f"{visible_count} carte visibili"
        text = f"{pile_name}: {count_text}"
        
        # List cards (top to bottom, up to max_cards)
        cards_to_list = visible_cards[-max_cards:]  # Last N cards (top of pile)
        cards_to_list.reverse()  # Top to bottom order
        
        if cards_to_list:
            card_names = [GameFormatter.format_card(c, include_status=False) for c in cards_to_list]
            text += f". Dall'alto: {', '.join(card_names)}"
        
        return text
    
    @staticmethod
    def format_move_result(
        success: bool,
        message: str
    ) -> str:
        """Format move result message.
        
        Args:
            success: Whether move succeeded
            message: Move description
        
        Returns:
            Formatted message with prefix
        
        Example:
            >>> GameFormatter.format_move_result(True, "Fante su Pila base 2")
            "Mossa eseguita: Fante su Pila base 2"
        """
        prefix = "Mossa eseguita" if success else "Mossa non valida"
        return f"{prefix}: {message}"
    
    @staticmethod
    def format_statistics(
        moves: int,
        time_seconds: int,
        deck_type: str
    ) -> str:
        """Format game statistics.
        
        Args:
            moves: Number of moves made
            time_seconds: Elapsed time in seconds
            deck_type: "french" or "neapolitan"
        
        Returns:
            Statistics summary in Italian
        
        Example:
            "Statistiche: 42 mosse, 3 minuti e 25 secondi, mazzo francese"
        """
        # Format time
        minutes = time_seconds // 60
        seconds = time_seconds % 60
        
        if minutes > 0:
            time_text = f"{minutes} minut" + ("o" if minutes == 1 else "i")
            if seconds > 0:
                time_text += f" e {seconds} second" + ("o" if seconds == 1 else "i")
        else:
            time_text = f"{seconds} second" + ("o" if seconds == 1 else "i")
        
        # Format moves
        moves_text = f"{moves} mossa" if moves == 1 else f"{moves} mosse"
        
        # Format deck type
        deck_text = "mazzo francese" if deck_type == "french" else "mazzo napoletano"
        
        return f"Statistiche: {moves_text}, {time_text}, {deck_text}"
    
    @staticmethod
    def format_victory(
        moves: int,
        time_seconds: int
    ) -> str:
        """Format victory announcement.
        
        Args:
            moves: Number of moves made
            time_seconds: Time to complete
        
        Returns:
            Victory message in Italian
        
        Example:
            "Vittoria! Completato in 3 minuti e 25 secondi con 42 mosse."
        """
        # Format time
        minutes = time_seconds // 60
        seconds = time_seconds % 60
        
        if minutes > 0:
            time_text = f"{minutes} minut" + ("o" if minutes == 1 else "i")
            if seconds > 0:
                time_text += f" e {seconds} second" + ("o" if seconds == 1 else "i")
        else:
            time_text = f"{seconds} second" + ("o" if seconds == 1 else "i")
        
        return f"Vittoria! Completato in {time_text} con {moves} mosse."
    
    @staticmethod
    def format_help_summary() -> str:
        """Generate help text summary.
        
        Returns:
            Brief help text listing main commands
        """
        return (
            "Comandi principali: "
            "Frecce per navigare. "
            "INVIO per selezionare. "
            "Tasti 1-7 per pile base. "
            "SHIFT più 1-4 per fondazioni. "
            "A per auto-mossa. "
            "N per nuova partita. "
            "ESC per menu. "
            "H per aiuto completo."
        )
    
    @staticmethod
    def format_help_detailed() -> str:
        """Generate detailed help text.
        
        Returns:
            Complete help text with all commands
        """
        return (
            "Comandi di gioco. "
            "Navigazione: Frecce per muovere cursore. "
            "INVIO per selezionare carta. "
            "CANC per annullare selezione. "
            "Accesso rapido: Tasti da 1 a 7 per pile base. "
            "SHIFT più tasti da 1 a 4 per pile fondazione. "
            "SHIFT più S per scarti. "
            "SHIFT più M per mazzo. "
            "Azioni: A per auto-mossa alle fondazioni. "
            "Gestione: N per nuova partita. "
            "S per statistiche. "
            "ESC per tornare al menu. "
            "Impostazioni: F1 per cambiare mazzo. "
            "F2 per attivare timer. "
            "F3 e F4 per regolare timer. "
            "F5 per mescolamento automatico."
        )
    
    @staticmethod
    def format_timer_warning(minutes_left: int) -> str:
        """Format timer warning message.
        
        Args:
            minutes_left: Minutes remaining
        
        Returns:
            Warning message in Italian
        
        Example:
            "Attenzione! Restano 5 minuti."
        """
        if minutes_left == 1:
            return "Attenzione! Resta 1 minuto."
        return f"Attenzione! Restano {minutes_left} minuti."
    
    @staticmethod
    def format_timer_expired() -> str:
        """Format timer expiration message.
        
        Returns:
            Expiration message
        """
        return "Tempo scaduto! Partita terminata."
    
    @staticmethod
    def format_deck_switched(deck_type: str) -> str:
        """Format deck switch announcement.
        
        Args:
            deck_type: "french" or "neapolitan"
        
        Returns:
            Switch announcement in Italian
        """
        deck_text = "francese" if deck_type == "french" else "napoletano"
        return f"Mazzo cambiato in: {deck_text}. Nuova partita avviata."
    
    @staticmethod
    def format_setting_changed(
        setting_name: str,
        new_value: str
    ) -> str:
        """Format setting change announcement.
        
        Args:
            setting_name: Name of setting
            new_value: New value description
        
        Returns:
            Change announcement
        
        Example:
            "Timer: attivato, 10 minuti"
        """
        return f"{setting_name}: {new_value}"
    
    # ===== NEW DETAILED FEEDBACK FORMATTERS (Commit #16) =====
    
    @staticmethod
    def format_drawn_cards(cards: List[Card]) -> str:
        """Format detailed card draw announcement.
        
        Announces all drawn cards by their full names, matching
        legacy scr/game_engine.py behavior exactly.
        
        Args:
            cards: List of cards drawn from stock
        
        Returns:
            Formatted announcement in Italian
        
        Examples:
            >>> cards = [Card("7", "cuori"), Card("Regina", "quadri")]
            >>> GameFormatter.format_drawn_cards(cards)
            "Hai pescato: 7 di Cuori, Regina di Quadri."
            
            >>> GameFormatter.format_drawn_cards([])
            "Nessuna carta pescata."
        
        Reference:
            Legacy: scr/game_engine.py lines 758-762
        """
        if not cards:
            return "Nessuna carta pescata."
        
        msg = "Hai pescato: "
        card_names = [card.get_display_name() for card in cards]
        msg += ", ".join(card_names) + ".  \n"
        
        return msg
    
    @staticmethod
    def format_move_report(
        moved_cards: List[Card],
        origin_pile: Pile,
        dest_pile: Pile,
        card_under: Optional[Card] = None,
        revealed_card: Optional[Card] = None
    ) -> str:
        """Format complete move narration with all details.
        
        Provides comprehensive move feedback matching legacy behavior:
        - Cards moved (with count if more than 2)
        - Origin pile name
        - Destination pile name
        - Card underneath (if not King)
        - Revealed card in origin pile (if any)
        
        Args:
            moved_cards: Cards that were moved
            origin_pile: Source pile
            dest_pile: Destination pile
            card_under: Card in destination that moved cards sit on (optional)
            revealed_card: Card revealed in origin after move (optional)
        
        Returns:
            Complete move narration in Italian
        
        Examples:
            >>> # Single card move
            "Sposti: Asso di Cuori. Da: Pila base 1. A: Pila semi Cuori. 
             Sopra alla carta: Re di Cuori. Hai scoperto: 5 di Picche in: Pila base 1."
            
            >>> # Multiple cards
            "Sposti: 7 di Fiori e altre 3 carte. Da: Pila base 2. A: Pila base 3."
        
        Reference:
            Legacy: scr/game_engine.py lines 526-556
        """
        if not moved_cards:
            return "Nessuna carta spostata."
        
        msg = "Sposti: "
        
        # Format cards: if >2 show only first + count
        tot_cards = len(moved_cards)
        if tot_cards > 2:
            msg += f"{moved_cards[0].get_display_name()} e altre {tot_cards - 1} carte.  \n"
        else:
            card_names = [card.get_display_name() for card in moved_cards]
            for name in card_names:
                msg += f"{name}.  \n"
        
        # Origin and destination
        msg += f"Da: {origin_pile.get_name()}.  \n"
        msg += f"A: {dest_pile.get_name()}.  \n"
        
        # Card under (only if not King and not None)
        if card_under and card_under.get_value != 13:
            msg += f"Sopra alla carta: {card_under.get_display_name()}.  \n"
        
        # Revealed card in origin pile
        if revealed_card:
            msg += f"Hai scoperto: {revealed_card.get_display_name()} in: {origin_pile.get_name()}.  \n"
        
        return msg
    
    @staticmethod
    def format_reshuffle_message(
        shuffle_mode: str,
        auto_drawn_cards: Optional[List[Card]] = None
    ) -> str:
        """Format reshuffle announcement with auto-draw.
        
        Announces waste pile recycling mode and any automatically
        drawn cards after the reshuffle.
        
        Args:
            shuffle_mode: "shuffle" (random) or "reverse" (simple inversion)
            auto_drawn_cards: Cards automatically drawn after reshuffle (optional)
        
        Returns:
            Complete reshuffle + draw announcement in Italian
        
        Examples:
            >>> # Random shuffle with auto-draw
            "Rimescolo gli scarti in modo casuale nel mazzo riserve!
             Pescata automatica: Hai pescato: 9 di Quadri, Asso di Fiori."
            
            >>> # Reverse without auto-draw (empty deck)
            "Rimescolo gli scarti in mazzo riserve!
             Attenzione: mazzo vuoto, nessuna carta da pescare!"
        
        Reference:
            Legacy: scr/game_engine.py lines 779-803
        """
        # Announce shuffle mode
        if shuffle_mode == "shuffle":
            msg = "Rimescolo gli scarti in modo casuale nel mazzo riserve!  \n"
        else:
            msg = "Rimescolo gli scarti in mazzo riserve!  \n"
        
        # Auto-draw announcement
        if auto_drawn_cards:
            msg += "Pescata automatica: "
            msg += GameFormatter.format_drawn_cards(auto_drawn_cards)
        else:
            msg += "Attenzione: mazzo vuoto, nessuna carta da pescare!  \n"
        
        return msg
