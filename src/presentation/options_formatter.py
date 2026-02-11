"""Options window formatter for TTS output.

Formats all option-related messages for screen reader accessibility.
Follows Italian language conventions with concise, clear feedback.

All methods are pure static functions - no side effects.
"""

from typing import Dict


class OptionsFormatter:
    """Formats options window messages for accessible TTS output.
    
    Design principles:
    1. Concise but complete information
    2. Italian language natural flow
    3. Contextual hints for navigation
    4. Screen reader optimized (no symbols)
    
    All methods are static - no internal state.
    """
    
    # Options metadata (index → name mapping)
    OPTION_NAMES = [
        "Tipo mazzo",
        "Difficoltà",
        "Carte Pescate",
        "Timer",
        "Modalità riciclo scarti",
        "Suggerimenti Comandi",
        "Sistema Punti",
        "Modalità Timer"
    ]
    
    @staticmethod
    def format_open_message(first_option_value: str) -> str:
        """Format window opening message.
        
        Args:
            first_option_value: Current value of first option (Tipo mazzo)
        
        Returns:
            "Finestra opzioni. 1 di 8: Tipo mazzo, Carte Francesi. Premi H per aiuto."
        """
        return (
            f"Finestra opzioni. "
            f"1 di 8: Tipo mazzo, {first_option_value}. "
            f"Premi H per aiuto."
        )
    
    @staticmethod
    def format_close_message() -> str:
        """Format window closing message."""
        return "Opzioni chiuse. Torno al gioco."
    
    @staticmethod
    def format_option_item(
        index: int,
        name: str,
        value: str,
        include_hint: bool = True
    ) -> str:
        """Format single option for navigation (arrows/numbers).
        
        Args:
            index: Option position (0-7)
            name: Option name
            value: Current value
            include_hint: Add navigation hint (default True)
        
        Returns:
            Concise format: "4 di 8: Timer, Disattivato."
            With hint: "4 di 8: Timer, Disattivato. Premi INVIO per modificare."
        
        Examples:
            >>> format_option_item(0, "Tipo mazzo", "Carte Francesi", True)
            "1 di 8: Tipo mazzo, Carte Francesi. Premi INVIO per modificare."
            
            >>> format_option_item(3, "Timer", "10 minuti", False)
            "4 di 8: Timer, 10 minuti."
        """
        position = index + 1
        msg = f"{position} di 8: {name}, {value}."
        
        if include_hint:
            # Special hint for Timer (has extra keys) - v1.5.1 updated (now at index 3)
            if index == 3:  # Timer option
                if "Disattivato" in value:
                    msg += " Premi T o INVIO per attivare a 5 minuti, o + e - per regolare."
                else:
                    msg += " Premi INVIO per incrementare, T per disattivare, o + e - per regolare."
            # Standard hint for all other options
            else:
                msg += " Premi INVIO per modificare."
        
        return msg
    
    @staticmethod
    def format_option_changed(name: str, new_value: str) -> str:
        """Format option change confirmation.
        
        Args:
            name: Option name
            new_value: New value set
        
        Returns:
            "Timer impostato a: 10 minuti."
            "Difficoltà impostata a: Livello 2."
        
        Examples:
            >>> format_option_changed("Timer", "10 minuti")
            "Timer impostato a: 10 minuti."
            
            >>> format_option_changed("Tipo mazzo", "Carte Napoletane")
            "Tipo mazzo impostato a: Carte Napoletane."
        """
        # Gender agreement for Italian
        if name in ["Difficoltà", "Modalità riciclo scarti"]:
            return f"{name} impostata a: {new_value}."
        else:
            return f"{name} impostato a: {new_value}."
    
    @staticmethod
    def format_timer_limit_reached(limit_type: str) -> str:
        """Format timer limit warning.
        
        Args:
            limit_type: "max" or "min"
        
        Returns:
            "Timer già al massimo: 60 minuti."
            "Timer già disattivato."
        """
        if limit_type == "max":
            return "Timer già al massimo: 60 minuti."
        else:
            return "Timer già disattivato."
    
    @staticmethod
    def format_timer_error() -> str:
        """Format timer key error (pressed +/-/T when timer not selected)."""
        return "Seleziona prima il Timer con il tasto 3."
    
    @staticmethod
    def format_blocked_during_game() -> str:
        """Format error when trying to modify options during active game."""
        return "Non puoi modificare le opzioni durante una partita! Premi N per nuova partita."
    
    @staticmethod
    def format_all_settings(settings: Dict[str, str]) -> str:
        """Format complete settings recap (tasto I).
        
        Args:
            settings: Dict with option names as keys and current values
        
        Returns:
            Multi-line recap of all settings
        
        Example:
            >>> settings = {
            ...     "Tipo mazzo": "Carte Francesi",
            ...     "Difficoltà": "Livello 1",
            ...     "Timer": "Disattivato",
            ...     "Modalità riciclo": "Inversione Semplice"
            ... }
            >>> format_all_settings(settings)
            "Impostazioni correnti:
             Tipo mazzo: Carte Francesi.
             Difficoltà: Livello 1.
             Timer: Disattivato.
             Modalità riciclo scarti: Inversione Semplice."
        """
        msg = "Impostazioni correnti:  \n"
        
        for name, value in settings.items():
            msg += f"{name}: {value}.  \n"
        
        return msg
    
    @staticmethod
    def format_help_text() -> str:
        """Format complete help text for options window (tasto H).
        
        Returns:
            Complete list of commands with descriptions
        """
        return (
            "Comandi finestra opzioni:  \n"
            "Frecce su e giù per navigare.  \n"
            "Tasti da 1 a 5 per accesso rapido.  \n"
            "INVIO o SPAZIO per modificare opzione.  \n"
            "Se Timer selezionato: T per attivare o disattivare, + e - per regolare.  \n"
            "I per leggere tutte le impostazioni.  \n"
            "ESC per chiudere e tornare al gioco."
        )
    
    @staticmethod
    def format_save_dialog() -> str:
        """Format save confirmation dialog.
        
        Returns:
            "Hai modifiche non salvate. Salvare le modifiche? Premi S per salvare, N per scartare."
        """
        return (
            "Hai modifiche non salvate. "
            "Salvare le modifiche? "
            "Premi S per salvare, N per scartare."
        )
    
    @staticmethod
    def format_save_confirmed() -> str:
        """Format save confirmation message."""
        return "Modifiche salvate. Torno al gioco."
    
    @staticmethod
    def format_save_discarded() -> str:
        """Format discard confirmation message."""
        return "Modifiche scartate. Torno al gioco."
    
    @staticmethod
    def format_save_cancelled() -> str:
        """Format cancel save dialog message."""
        return "Annullato. Rimango nelle opzioni."
    
    @staticmethod
    def format_future_option_blocked() -> str:
        """Format message for non-implemented option."""
        return "Opzione non ancora implementata. Sarà disponibile in un prossimo aggiornamento."
    
    # ========================================
    # COMMAND HINTS OPTION (v1.5.0)
    # ========================================
    
    @staticmethod
    def format_command_hints_item(value: str, is_current: bool) -> str:
        """Format command hints option for navigation (v1.5.0).
        
        Args:
            value: Current value ("Attivi" or "Disattivati")
            is_current: True if this is the currently selected option
        
        Returns:
            Formatted option with position and modification hint
        
        Examples:
            >>> format_command_hints_item("Attivi", True)
            "5 di 5: Suggerimenti Comandi, Attivi. Premi INVIO per modificare."
            
            >>> format_command_hints_item("Disattivati", False)
            "5 di 5: Suggerimenti Comandi, Disattivati."
        """
        position = "5 di 5" if is_current else "5 di 5"
        msg = f"{position}: Suggerimenti Comandi, {value}."
        
        if is_current:
            msg += " Premi INVIO per modificare."
        
        return msg
    
    @staticmethod
    def format_command_hints_changed(new_value: str) -> str:
        """Format command hints toggle confirmation (v1.5.0).
        
        Args:
            new_value: New value ("Attivi" or "Disattivati")
        
        Returns:
            Confirmation message
        
        Examples:
            >>> format_command_hints_changed("Attivi")
            "Suggerimenti comandi attivi."
            
            >>> format_command_hints_changed("Disattivati")
            "Suggerimenti comandi disattivati."
        """
        return f"Suggerimenti comandi {new_value.lower()}."
