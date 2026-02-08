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
