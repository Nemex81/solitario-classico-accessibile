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
    CARD_FLIP = "card_flip"  # carta scoperta
    CARD_SHUFFLE = "card_shuffle"  # new game / mischia mazzo
    CARD_SHUFFLE_WASTE = "card_shuffle_waste"  # rimischia scarti
    FOUNDATION_DROP = "foundation_drop"
    INVALID_MOVE = "invalid_move"
    TABLEAU_BUMPER = "tableau_bumper"
    TABLEAU_DROP = "tableau_drop"  # drop singolo su pila di gioco
    STOCK_DRAW = "stock_draw"
    WASTE_DROP = "waste_drop"
    CARDS_EXHAUSTED = "cards_exhausted"
    MULTI_CARD_MOVE = "multi_card_move"
    # UI bus - navigazione
    UI_NAVIGATE = "ui_navigate"
    UI_NAVIGATE_FRAME = "ui_navigate_frame"
    UI_NAVIGATE_PILE = "ui_navigate_pile"
    UI_SELECT = "ui_select"
    UI_CANCEL = "ui_cancel"
    UI_CONFIRM = "ui_confirm"
    UI_TOGGLE = "ui_toggle"
    UI_FOCUS_CHANGE = "ui_focus_change"
    UI_BOUNDARY_HIT = "ui_boundary_hit"
    UI_NOTIFICATION = "ui_notification"
    UI_ERROR = "ui_error"
    # UI bus - menu e pulsanti
    UI_MENU_OPEN = "ui_menu_open"
    UI_MENU_CLOSE = "ui_menu_close"
    UI_BUTTON_CLICK = "ui_button_click"
    UI_BUTTON_HOVER = "ui_button_hover"
    MIXER_OPENED = "mixer_opened"
    # Settings bus
    SETTING_SAVED = "setting_saved"
    SETTING_CHANGED = "setting_changed"
    SETTING_LEVEL_CHANGED = "setting_level_changed"
    SETTING_VOLUME_CHANGED = "setting_volume_changed"
    SETTING_MUSIC_CHANGED = "setting_music_changed"
    SETTING_SWITCH_ON = "setting_switch_on"
    SETTING_SWITCH_OFF = "setting_switch_off"
    # Ambient bus
    AMBIENT_LOOP = "ambient_loop"
    # Music bus
    MUSIC_LOOP = "music_loop"
    # Voice bus
    GAME_WON = "game_won"
    WELCOME_MESSAGE = "welcome_message"
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
