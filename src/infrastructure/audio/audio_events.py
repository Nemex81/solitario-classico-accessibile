"""Audio event definitions for the solitaire audio system.

AudioEvent è il contratto dati immutabile tra i controller del layer Application e l'AudioManager.
I controller creano eventi; l'AudioManager li consuma.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any

class AudioEventType:
    """Costanti stringa per i tipi di evento audio.
    Organizzati per bus/categoria.
    I controller usano queste costanti per creare istanze AudioEvent.
    """
    # Gameplay bus - azioni sulle carte
    CARD_MOVE = "card_move"
    CARD_SELECT = "card_select"
    CARD_DROP = "card_drop"
    FOUNDATION_DROP = "foundation_drop"
    INVALID_MOVE = "invalid_move"
    TABLEAU_BUMPER = "tableau_bumper"
    STOCK_DRAW = "stock_draw"
    WASTE_DROP = "waste_drop"
    # UI bus
    UI_NAVIGATE = "ui_navigate"
    UI_SELECT = "ui_select"
    UI_CANCEL = "ui_cancel"
    MIXER_OPENED = "mixer_opened"
    # Ambient bus
    AMBIENT_LOOP = "ambient_loop"
    # Music bus
    MUSIC_LOOP = "music_loop"
    # Voice bus
    GAME_WON = "game_won"
    # Timer events
    TIMER_WARNING = "timer_warning"
    TIMER_EXPIRED = "timer_expired"

@dataclass(frozen=True)
class AudioEvent:
    """Contratto dati immutabile per eventi del sistema audio.
    Creato dai controller Application, consumato da AudioManager.
    I controller descrivono solo COSA è successo, non COME il suono sarà riprodotto.
    Args:
        event_type: Costante stringa da AudioEventType
        source_pile: Indice 0-12 della pila origine (opzionale, per panning)
        destination_pile: Indice 0-12 della pila destinazione (opzionale, per panning)
        context: Dict opzionale per estensioni future
    Version:
        v3.4.0: Implementazione iniziale
    """
    event_type: str
    source_pile: Optional[int] = None
    destination_pile: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
