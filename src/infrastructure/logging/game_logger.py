"""
Helper semantici per logging eventi di gioco.

Pattern:
- Funzioni named per evento specifico (chiaro intent)
- Wrappano logger.info/error/warning/debug
- Parametri espliciti (no kwargs magici)

Usage:
    >>> from src.infrastructure.logging import game_logger as log
    >>> log.game_started("draw_three", "medium", True)
    >>> log.card_moved("tableau_3", "foundation_1", "A♠", True)

Version:
    v2.3.0: Initial implementation

Author:
    Nemex81
"""

import logging
from typing import Optional

# Logger dedicati per categorie eventi
_game_logger = logging.getLogger('game')
_ui_logger = logging.getLogger('ui')
_error_logger = logging.getLogger('error')
_timer_logger = logging.getLogger('timer')


# ===== LIFECYCLE APPLICAZIONE =====

def app_started() -> None:
    """Log avvio applicazione."""
    _game_logger.info("Application started - wxPython solitaire v2.3.0")


def app_shutdown() -> None:
    """Log chiusura applicazione."""
    _game_logger.info("Application shutdown requested")


# ===== LIFECYCLE PARTITA =====

def game_started(deck_type: str, difficulty: str, timer_enabled: bool) -> None:
    """
    Log inizio nuova partita.
    
    Args:
        deck_type: "draw_one" | "draw_three"
        difficulty: "easy" | "medium" | "hard" | "expert" | "master"
        timer_enabled: Se timer attivo
    
    Example:
        >>> game_started("draw_three", "medium", True)
        2026-02-14 14:30:12 - INFO - game - New game started - Deck: draw_three, Difficulty: medium, Timer: True
    """
    _game_logger.info(
        f"New game started - Deck: {deck_type}, "
        f"Difficulty: {difficulty}, Timer: {timer_enabled}"
    )


def game_won(elapsed_time: int, moves_count: int, score: int) -> None:
    """
    Log vittoria con statistiche.
    
    Args:
        elapsed_time: Tempo trascorso in secondi
        moves_count: Numero mosse effettuate
        score: Punteggio finale
    """
    _game_logger.info(
        f"Game WON - Time: {elapsed_time}s, "
        f"Moves: {moves_count}, Score: {score}"
    )


def game_abandoned(elapsed_time: int, moves_count: int) -> None:
    """
    Log abbandono partita.
    
    Args:
        elapsed_time: Tempo trascorso in secondi
        moves_count: Numero mosse effettuate prima di abbandonare
    """
    _game_logger.info(
        f"Game ABANDONED - Time: {elapsed_time}s, Moves: {moves_count}"
    )


def game_reset() -> None:
    """Log reset partita (menu → new game senza conferma)."""
    _game_logger.info("Game reset")


# ===== AZIONI GIOCATORE =====

def card_moved(from_pile: str, to_pile: str, card: str, success: bool) -> None:
    """
    Log movimento carta.
    
    Args:
        from_pile: Es. "tableau_3", "waste", "foundation_1"
        to_pile: Destinazione
        card: Rappresentazione carta (es. "A♠")
        success: Se mossa valida
    
    Example:
        >>> card_moved("tableau_3", "foundation_1", "A♠", True)
        2026-02-14 14:30:15 - INFO - game - Move SUCCESS: A♠ from tableau_3 to foundation_1
    """
    level = logging.INFO if success else logging.WARNING
    result = "SUCCESS" if success else "FAILED"
    _game_logger.log(
        level,
        f"Move {result}: {card} from {from_pile} to {to_pile}"
    )


def cards_drawn(count: int) -> None:
    """
    Log pesca da mazzo.
    
    Args:
        count: Numero carte pescate (1 o 3)
    
    Note:
        - Livello DEBUG (noise in production)
    """
    _game_logger.debug(f"Drew {count} card(s) from stock")


def waste_recycled(recycle_count: int) -> None:
    """
    Log riciclo scarti.
    
    Args:
        recycle_count: Numero totale ricicli effettuati
    """
    _game_logger.info(f"Waste recycled (total recycles: {recycle_count})")


def invalid_action(action: str, reason: str) -> None:
    """
    Log azione invalida con ragione.
    
    Args:
        action: Nome azione tentata
        reason: Motivo fallimento
    
    Example:
        >>> invalid_action("move_card", "Cannot place red on red")
        2026-02-14 14:30:20 - WARNING - game - Invalid action 'move_card': Cannot place red on red
    """
    _game_logger.warning(f"Invalid action '{action}': {reason}")


# ===== NAVIGAZIONE UI =====

def panel_switched(from_panel: str, to_panel: str) -> None:
    """
    Log cambio panel.
    
    Args:
        from_panel: Panel corrente (o "none" se primo switch)
        to_panel: Panel destinazione
    
    Example:
        >>> panel_switched("menu", "gameplay")
        2026-02-14 14:30:25 - INFO - ui - Panel transition: menu → gameplay
    """
    _ui_logger.info(f"Panel transition: {from_panel} → {to_panel}")


def dialog_shown(dialog_type: str, title: str) -> None:
    """
    Log apertura dialog.
    
    Args:
        dialog_type: "yes_no" | "info" | "error"
        title: Titolo dialog
    
    Note:
        - Livello DEBUG (troppo verboso per production)
    """
    _ui_logger.debug(f"Dialog shown: {dialog_type} - '{title}'")


def dialog_closed(dialog_type: str, result: str) -> None:
    """
    Log chiusura dialog con risposta utente.
    
    Args:
        dialog_type: "yes_no" | "info" | "error"
        result: "yes" | "no" | "ok" | "cancel"
    
    Note:
        - Livello DEBUG
    """
    _ui_logger.debug(f"Dialog closed: {dialog_type} - result: {result}")


def keyboard_command(command: str, context: str) -> None:
    """
    Log comando tastiera (solo comandi significativi, no arrow keys).
    
    Args:
        command: Es. "ENTER", "ESC", "CTRL+ENTER", "SHIFT+S"
        context: Panel attivo (es. "gameplay", "menu")
    
    Note:
        - Livello DEBUG per evitare noise
        - Utile per capire pattern di utilizzo utente
    
    Example:
        >>> keyboard_command("CTRL+ENTER", "gameplay")
        2026-02-14 14:30:30 - DEBUG - ui - Key command: CTRL+ENTER in context 'gameplay'
    """
    _ui_logger.debug(f"Key command: {command} in context '{context}'")


# ===== ERRORI E WARNINGS =====

def error_occurred(error_type: str, details: str, exception: Optional[Exception] = None) -> None:
    """
    Log errore con dettagli.
    
    Args:
        error_type: Categoria errore (es. "FileIO", "StateCorruption", "Application")
        details: Descrizione human-readable
        exception: Eccezione originale (se disponibile)
    
    Example:
        >>> try:
        ...     risky_operation()
        ... except ValueError as e:
        ...     error_occurred("Validation", "Invalid card state", e)
        2026-02-14 14:30:35 - ERROR - error - ERROR [Validation]: Invalid card state
        Traceback (most recent call last):
          ...
    
    Note:
        - Se exception fornita, include full traceback
    """
    if exception:
        _error_logger.error(
            f"ERROR [{error_type}]: {details}",
            exc_info=exception
        )
    else:
        _error_logger.error(f"ERROR [{error_type}]: {details}")


def warning_issued(warning_type: str, message: str) -> None:
    """
    Log warning (situazioni anomale ma gestite).
    
    Args:
        warning_type: Categoria warning
        message: Descrizione situazione
    
    Example:
        >>> warning_issued("TTS", "NVDA not available, fallback to silent mode")
        2026-02-14 14:30:40 - WARNING - error - WARNING [TTS]: NVDA not available, fallback to silent mode
    """
    _error_logger.warning(f"WARNING [{warning_type}]: {message}")


# ===== DEBUG HELPERS =====

def debug_state(state_name: str, state_data: dict) -> None:
    """
    Log stato interno (solo durante debug).
    
    Args:
        state_name: Nome stato loggato
        state_data: Dict con dati stato
    
    Example:
        >>> debug_state("game_state", {
        ...     "selected_cards": 2,
        ...     "cursor_pile": "tableau_3",
        ...     "can_recycle": True
        ... })
        2026-02-14 14:30:45 - DEBUG - game - State [game_state]: {'selected_cards': 2, ...}
    
    Note:
        - Usare solo per debug complessi
        - Non chiamare in hot paths
    """
    _game_logger.debug(f"State [{state_name}]: {state_data}")


# ===== SETTINGS CHANGES =====

def settings_changed(setting_name: str, old_value, new_value) -> None:
    """
    Log configuration change.
    
    Args:
        setting_name: Name of setting (e.g. "difficulty", "timer_enabled")
        old_value: Previous value
        new_value: New value
    
    Example:
        >>> settings_changed("difficulty", "medium", "hard")
        2026-02-14 15:00:00 - INFO - game - Setting changed: difficulty = medium → hard
    """
    _game_logger.info(
        f"Setting changed: {setting_name} = {old_value} → {new_value}"
    )


# ===== TIMER LIFECYCLE =====

def timer_started(duration: int) -> None:
    """Log timer start with max duration.
    
    Args:
        duration: Maximum timer duration in seconds
    
    Example:
        >>> timer_started(600)
        2026-02-14 15:00:00 - INFO - timer - Timer started - Duration: 600s
    """
    _timer_logger.info(f"Timer started - Duration: {duration}s")


def timer_expired() -> None:
    """Log timer expiration (game over event).
    
    Example:
        >>> timer_expired()
        2026-02-14 15:10:00 - WARNING - timer - Timer EXPIRED - Game auto-abandoned
    """
    _timer_logger.warning("Timer EXPIRED - Game auto-abandoned")


def timer_paused(remaining: int) -> None:
    """Log timer pause (if pause feature exists).
    
    Args:
        remaining: Remaining time in seconds
    
    Note:
        Optional feature - only log if pause functionality is implemented
    """
    _timer_logger.debug(f"Timer paused - Remaining: {remaining}s")


# ===== NAVIGATION TRACKING (DEBUG LEVEL) =====

def cursor_moved(from_position: str, to_position: str) -> None:
    """
    Log cursor movement (DEBUG level - verbose).
    
    Args:
        from_position: Previous cursor position (e.g. "tableau_3[5]")
        to_position: New cursor position
    
    Note:
        DEBUG level to avoid noise in INFO logs.
        Useful for UX heatmap analytics (which piles/cards focused most).
    
    Example:
        >>> cursor_moved("tableau_3[5]", "tableau_3[4]")
        2026-02-14 15:05:00 - DEBUG - game - Cursor: tableau_3[5] → tableau_3[4]
    """
    _game_logger.debug(f"Cursor: {from_position} → {to_position}")


def pile_jumped(from_pile: str, to_pile: str) -> None:
    """
    Log direct pile jump (1-7 keys, SHIFT+1-4, etc.).
    
    Args:
        from_pile: Previous pile (e.g. "tableau_1")
        to_pile: Target pile (e.g. "foundation_2")
    
    Example:
        >>> pile_jumped("tableau_1", "foundation_2")
        2026-02-14 15:05:05 - DEBUG - game - Pile jump: tableau_1 → foundation_2
    """
    _game_logger.debug(f"Pile jump: {from_pile} → {to_pile}")


# ===== QUERY COMMANDS TRACKING =====

def info_query_requested(query_type: str, context: str = "") -> None:
    """
    Log information query command.
    
    Args:
        query_type: Type of info requested (e.g. "table_info", "cursor_position")
        context: Optional context (e.g. current pile)
    
    Note:
        INFO level - questi comandi sono meno frequenti delle navigation keys.
        Utile per capire quali info users cercano più spesso.
    
    Example:
        >>> info_query_requested("table_info", "during_gameplay")
        2026-02-14 15:10:00 - INFO - game - Info query: table_info (during_gameplay)
    """
    if context:
        _game_logger.info(f"Info query: {query_type} ({context})")
    else:
        _game_logger.info(f"Info query: {query_type}")


# ===== TTS FEEDBACK TRACKING (OPTIONAL) =====

def tts_spoken(message: str, interrupt: bool) -> None:
    """
    Log TTS vocalization (DEBUG level).
    
    Args:
        message: Text vocalized
        interrupt: Whether previous speech interrupted
    
    Note:
        DEBUG level - molto verboso (ogni azione genera TTS).
        Utile per accessibility audits e TTS testing.
    
    Example:
        >>> tts_spoken("7 di cuori su 8 di picche", True)
        2026-02-14 15:15:00 - DEBUG - ui - TTS: "7 di cuori su 8 di picche" (interrupt=True)
    """
    _ui_logger.debug(f'TTS: "{message}" (interrupt={interrupt})')
