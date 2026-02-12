"""Abstract interface for modal dialog operations.

This module defines the contract for dialog providers, allowing
different implementations (wxPython, GTK, Qt, terminal, web, mock)
without coupling domain/application layers to specific UI frameworks.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class DialogProvider(ABC):
    """Abstract interface for modal dialog operations.
    
    Implementations must provide platform-specific dialog boxes
    that are accessible to screen readers and support keyboard navigation.
    
    Thread-safety:
        All methods must be called from main thread (UI thread).
        wxPython enforces this via wx.CallAfter if needed.
    
    Accessibility requirements:
        - All dialogs must be navigable via keyboard only
        - All text must be exposed to screen readers (NVDA, JAWS, Orca)
        - Focus must return to main window after dialog closes
    
    Example:
        >>> provider = WxDialogProvider()
        >>> provider.show_alert("Hai vinto!", "Congratulazioni")
        >>> if provider.show_yes_no("Vuoi giocare ancora?", "Rivincita?"):
        ...     start_new_game()
    """
    
    @abstractmethod
    def show_alert(self, message: str, title: str) -> None:
        """Show informational alert dialog (OK button only).
        
        Args:
            message: Main content (can be multi-line)
            title: Dialog window title
            
        Blocks until user dismisses dialog.
        Screen reader announces title + message when dialog opens.
        
        Example:
            >>> provider.show_alert(
            ...     "Hai vinto!\\nMosse: 85\\nTempo: 3:45",
            ...     "Partita Terminata"
            ... )
        """
        pass
    
    @abstractmethod
    def show_yes_no(self, question: str, title: str) -> bool:
        """Show Yes/No question dialog.
        
        Args:
            question: Question text
            title: Dialog window title
            
        Returns:
            True if Yes clicked, False if No or dialog closed (ESC)
            
        Default button is NO to prevent accidental confirmations.
        
        Example:
            >>> if provider.show_yes_no("Vuoi giocare ancora?", "Rivincita?"):
            ...     start_new_game()
            ... else:
            ...     return_to_menu()
        """
        pass
    
    @abstractmethod
    def show_input(
        self,
        question: str,
        title: str,
        default: str = ""
    ) -> Optional[str]:
        """Show text input dialog.
        
        Args:
            question: Prompt text
            title: Dialog window title
            default: Pre-filled value
            
        Returns:
            User input string, or None if cancelled (ESC or Cancel button)
            
        Example:
            >>> name = provider.show_input(
            ...     "Inserisci il tuo nome:",
            ...     "Configurazione",
            ...     default="Giocatore 1"
            ... )
            >>> if name:
            ...     save_player_name(name)
        """
        pass
    
    @abstractmethod
    def show_statistics_report(
        self,
        stats: Dict[str, Any],
        final_score: Optional[Dict[str, Any]],
        is_victory: bool,
        deck_type: str
    ) -> None:
        """Show structured statistics report dialog.
        
        Displays game completion statistics in a dedicated dialog
        optimized for screen readers and structured data presentation.
        
        Args:
            stats: Final statistics dictionary with keys:
                - elapsed_time: float (seconds)
                - move_count: int
                - recycle_count: int
                - carte_per_seme: List[int] (cards per suit)
                - semi_completati: int (completed suits)
                - completion_percentage: float
            final_score: Optional score breakdown with keys:
                - base_points: int
                - time_bonus: int
                - move_bonus: int
                - difficulty_bonus: int
                - deck_bonus: int
                - penalties: int
                - final_score: int
            is_victory: True if game won (all 4 suits completed)
            deck_type: "french" or "neapolitan" for suit name formatting
        
        Display features:
            - Multiline read-only TextCtrl with formatted report
            - Auto-focused for immediate NVDA announcement
            - OK button to close
            - Title: "Congratulazioni!" (victory) or "Partita Terminata" (defeat)
            
        Example:
            >>> provider.show_statistics_report(
            ...     stats={'elapsed_time': 125.5, 'move_count': 87, ...},
            ...     final_score={'final_score': 1250, ...},
            ...     is_victory=True,
            ...     deck_type="french"
            ... )
            # Shows dialog with formatted report
            # NVDA reads: "Congratulazioni! Hai Vinto! Tempo: 2 minuti 5 secondi..."
        """
        pass
