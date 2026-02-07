"""Screen reader service for audio feedback and TTS.

Provides accessible audio feedback for game actions using text-to-speech.
Supports multiple TTS engines through TtsProvider abstraction.
"""

from typing import Protocol
from src.domain.models.card import Card
from src.infrastructure.audio.tts_provider import TtsProvider


class ScreenReader:
    """Screen reader service for game audio feedback.
    
    Orchestrates TTS announcements for game events, card descriptions,
    and user feedback. Formats messages for optimal accessibility.
    
    The service can be enabled/disabled and supports different verbosity
    levels for customizing the amount of information provided.
    
    Attributes:
        tts: TTS provider instance for speech output
        enabled: Whether screen reader is active
        verbose: Verbosity level (0=minimal, 1=normal, 2=detailed)
    """
    
    def __init__(
        self,
        tts: TtsProvider,
        enabled: bool = True,
        verbose: int = 1
    ) -> None:
        """Initialize screen reader.
        
        Args:
            tts: TTS provider (SAPI5, NVDA, etc.) for speech output
            enabled: Enable/disable screen reader functionality
            verbose: Verbosity level (0=minimal, 1=normal, 2=detailed)
        """
        self.tts = tts
        self.enabled = enabled
        self.verbose = max(0, min(2, verbose))  # Clamp to 0-2
    
    def announce_move(
        self,
        success: bool,
        message: str,
        interrupt: bool = False
    ) -> None:
        """Announce move result with appropriate prefix.
        
        Formats the move result with a success or failure prefix
        to provide clear feedback to the user.
        
        Args:
            success: Whether move succeeded
            message: Move description
            interrupt: Interrupt current speech if True
        """
        if not self.enabled:
            return
        
        prefix = "Mossa eseguita: " if success else "Mossa non valida: "
        self.tts.speak(prefix + message, interrupt=interrupt)
    
    def announce_card(self, card: Card) -> None:
        """Announce card details in Italian.
        
        Provides a complete description of the card including its name,
        suit, and whether it's face-up or face-down. Format follows
        Italian conventions for accessibility.
        
        Args:
            card: Card to describe
        """
        if not self.enabled:
            return
        
        # Format: "Sette di cuori, coperta" or "Asso di picche, scoperta"
        status = "coperta" if card.get_covered else "scoperta"
        text = f"{card.get_name} di {card.get_suit}, {status}"
        self.tts.speak(text, interrupt=False)
    
    def announce_victory(self, moves: int, time: int) -> None:
        """Announce game victory with statistics.
        
        Provides completion feedback including time elapsed and
        number of moves made. Interrupts any ongoing speech to
        ensure the victory message is heard immediately.
        
        Args:
            moves: Number of moves made
            time: Time elapsed in seconds
        """
        if not self.enabled:
            return
        
        text = f"Vittoria! Completato in {time} secondi con {moves} mosse."
        self.tts.speak(text, interrupt=True)
    
    def announce_error(self, error: str) -> None:
        """Announce error message.
        
        Error messages always interrupt ongoing speech to ensure
        immediate feedback about problems.
        
        Args:
            error: Error description
        """
        if not self.enabled:
            return
        
        self.tts.speak(f"Errore: {error}", interrupt=True)
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable screen reader.
        
        When disabled, all announce methods become no-ops.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.enabled = enabled
    
    def set_verbose(self, level: int) -> None:
        """Set verbosity level.
        
        Controls the amount of detail provided in announcements.
        Values are clamped to valid range 0-2.
        
        Args:
            level: Verbosity level (0=minimal, 1=normal, 2=detailed)
        """
        self.verbose = max(0, min(2, level))
