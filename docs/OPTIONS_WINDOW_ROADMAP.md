# 🗺️ ROADMAP: FINESTRA VIRTUALE OPZIONI

> **Feature**: Virtual Options Window (HYBRID design)
> **Commits**: #17-20
> **Branch**: `refactoring-engine`
> **Version**: v1.5.0
> **Design**: HYBRID (frecce + numeri + hint concisi)

---

## 📋 INDICE

1. [Panoramica Feature](#panoramica)
2. [Design Approvato](#design)
3. [Commit #17: Domain Layer](#commit-17)
4. [Commit #18: Presentation Layer](#commit-18)
5. [Commit #19: Application Layer](#commit-19)
6. [Commit #20: Integrazione Gameplay](#commit-20)
7. [Testing Completo](#testing)
8. [Esempi Flusso Utente](#examples)

---

## 🎯 PANORAMICA FEATURE {#panoramica}

### Obiettivo

Creare finestra virtuale opzioni accessibile per non vedenti con navigazione HYBRID:
- **Frecce ↑/↓**: Navigazione sequenziale (intuitiva)
- **Numeri 1-5**: Accesso rapido diretto (efficiente)
- **Hint vocali**: Feedback conciso contestuale
- **Conferma salvataggio**: Dialog prima di chiudere se modifiche presenti

### Funzionalità Implementate

✅ Navigazione ibrida (frecce + numeri)
✅ 5 opzioni configurabili (mazzo, difficoltà, timer, riciclo, futuro)
✅ Gestione timer dedicata (T toggle, +/- regola)
✅ Conferma salvataggio modifiche
✅ Help contestuale (tasto H)
✅ Recap impostazioni (tasto I)
✅ Blocco durante partita attiva
✅ Snapshot settings (save/discard)

### Tasti Implementati

```
O          → Apri/chiudi finestra (conferma se modifiche)
↑/↓        → Naviga opzioni (wraparound)
1-5        → Salta a opzione N
INVIO/SPAZ → Modifica opzione corrente
+/-        → Incrementa/decrementa timer (solo se Timer selezionato)
T          → Toggle timer ON(5min)/OFF (solo se Timer selezionato)
I          → Recap tutte le impostazioni
H          → Help completo finestra
ESC        → Chiudi con conferma
```

### Tasti Eliminati (Legacy)

```
❌ F1       → Sostituito da navigazione finestra
❌ F2       → Sostituito da navigazione finestra
❌ F3       → Sostituito da tasto -
❌ F4       → Sostituito da tasto +
❌ F5       → Sostituito da navigazione finestra
❌ CTRL+F3  → Sostituito da tasto T
```

---

## 🎨 DESIGN APPROVATO {#design}

### User Feedback (Risposte Utente)

**1. Design Preferito**: HYBRID (Proposta 3)
- Frecce per navigazione intuitiva
- Numeri per accesso rapido
- Meglio di entrambi i mondi

**2. Feedback Vocale**: Conciso con hint
- Hint vocali durante navigazione
- Esempio: "Premi INVIO per modificare"
- Nessun suono/beep aggiuntivo

**3. Gestione Timer**:
- Tasti +/-/T solo se Timer selezionato
- Step incremento: 5 minuti
- Tasto T dedicato: OFF ↔ 5min
- Decremento fino a 0 = disattivato

**4. Accesso Rapido**: Opzione A
- "3 di 5: Timer, Disattivato." (conciso)

**5. Help**: Completo
- Legge tutti i comandi della finestra

**6. Comportamento ESC**: Opzione B
- Chiede conferma: "Salvare modifiche?"
- Opzioni: S (salva), N (scarta), ESC (annulla)

### Mapping Tasti Completo

```
┌─────────────────┬──────────────────────────────────────────────────┐
│ TASTO           │ AZIONE                                           │
├─────────────────┼──────────────────────────────────────────────────┤
│ O               │ Apri/Chiudi (conferma se modifiche)              │
│ ↑               │ Opzione precedente (wraparound 0→4)              │
│ ↓               │ Opzione successiva (wraparound 4→0)              │
│ 1-5             │ Salta a opzione N                                │
│ INVIO/SPAZIO    │ Modifica opzione corrente                        │
│ + (solo timer)  │ Incrementa timer +5min                           │
│ - (solo timer)  │ Decrementa timer -5min (0=OFF)                   │
│ T (solo timer)  │ Toggle timer OFF↔5min                            │
│ I               │ Leggi tutte le impostazioni                      │
│ H               │ Help completo finestra                           │
│ ESC             │ Chiudi con conferma                              │
└─────────────────┴──────────────────────────────────────────────────┘
```

### Struttura Opzioni (indice 0-4)

```
┌───┬──────────────────────┬─────────────┬────────────────────────┐
│ # │ Nome Opzione         │ Tipo        │ Metodo GameSettings    │
├───┼──────────────────────┼─────────────┼────────────────────────┤
│ 0 │ Tipo Mazzo           │ Toggle      │ toggle_deck_type()     │
│ 1 │ Difficoltà           │ Ciclo       │ cycle_difficulty()     │
│ 2 │ Timer                │ Range+Toggle│ toggle_timer() (NUOVO) │
│   │                      │             │ increment_timer()      │
│   │                      │             │ decrement_timer()      │
│ 3 │ Modalità Riciclo     │ Toggle      │ toggle_shuffle_mode()  │
│ 4 │ (Futuro) Verbosità   │ -           │ Non implementato       │
└───┴──────────────────────┴─────────────┴────────────────────────┘
```

### Stati Finestra

```
1. CLOSED      → Gameplay normale (finestra non attiva)
2. OPEN_CLEAN  → Finestra aperta, nessuna modifica
3. OPEN_DIRTY  → Finestra aperta, modifiche presenti (richiede conferma)

Transizioni:
CLOSED  ──[O]──→  OPEN_CLEAN
OPEN_CLEAN  ──[Modifica]──→  OPEN_DIRTY
OPEN_CLEAN  ──[O/ESC]──→  CLOSED (diretto)
OPEN_DIRTY  ──[O/ESC]──→  Dialog conferma → CLOSED o OPEN_DIRTY
```

---

## 📦 COMMIT #17: DOMAIN LAYER {#commit-17}

### Obiettivo

Aggiungere metodo `toggle_timer()` a GameSettings per supportare tasto T dedicato.

### File Modificato

**`src/domain/services/game_settings.py`**

### Implementazione

```python
from typing import Tuple

class GameSettings:
    """Game settings management (domain service)."""
    
    # ... metodi esistenti ...
    
    def toggle_timer(self) -> Tuple[bool, str]:
        """Toggle timer ON/OFF con default 5 minuti.
        
        Logica:
        - Se OFF (max_time_game <= 0): Attiva a 5 minuti (300 secondi)
        - Se ON (max_time_game > 0): Disattiva (max_time_game = -1)
        
        Validazioni:
        - Richiede is_game_running=False
        - Blocca durante partita attiva
        
        Returns:
            Tuple[bool, str]: (success, message)
        
        Examples:
            >>> settings.max_time_game = -1  # OFF
            >>> settings.toggle_timer()
            (True, "Timer attivato a: 5 minuti.")
            
            >>> settings.max_time_game = 600  # 10 min
            >>> settings.toggle_timer()
            (True, "Timer disattivato.")
        
        Reference:
            User requirement: Tasto T per toggle rapido OFF ↔ 5min
        """
        # Validazione: blocca se partita attiva
        if not self.validate_not_running():
            return (False, "Non puoi modificare il timer durante una partita!")
        
        # Toggle logic
        if self.max_time_game <= 0:
            # OFF → ON (default 5 minuti)
            self.max_time_game = 300  # 5 minuti in secondi
            return (True, "Timer attivato a: 5 minuti.")
        else:
            # ON → OFF
            self.max_time_game = -1
            return (True, "Timer disattivato.")
```

### Test Unitari

```python
# test_game_settings.py

def test_toggle_timer_off_to_on():
    """Test toggle timer da OFF a ON."""
    settings = GameSettings(game_state)
    settings.max_time_game = -1
    
    success, msg = settings.toggle_timer()
    
    assert success is True
    assert settings.max_time_game == 300
    assert "attivato a: 5 minuti" in msg

def test_toggle_timer_on_to_off():
    """Test toggle timer da ON a OFF."""
    settings = GameSettings(game_state)
    settings.max_time_game = 600  # 10 minuti
    
    success, msg = settings.toggle_timer()
    
    assert success is True
    assert settings.max_time_game == -1
    assert "disattivato" in msg

def test_toggle_timer_blocked_during_game():
    """Test blocco toggle durante partita."""
    settings = GameSettings(game_state)
    game_state.is_running = True
    
    success, msg = settings.toggle_timer()
    
    assert success is False
    assert "durante una partita" in msg
```

### Commit Message

```
feat(domain): Add toggle_timer() to GameSettings

Implement dedicated timer toggle method for options window.

Features:
- Toggle OFF → ON (default 5 minutes)
- Toggle ON → OFF
- Validation: blocked during active game
- Returns (success, message) tuple

Supports tasto T in options window (user requirement).

Ref: OPTIONS_WINDOW_ROADMAP.md Commit #17
```

---

## 🎨 COMMIT #18: PRESENTATION LAYER {#commit-18}

### Obiettivo

Creare formatter dedicato per messaggi TTS della finestra opzioni.

### File Nuovo

**`src/presentation/options_formatter.py`**

### Implementazione Completa

```python
"""Options window formatter for TTS output.

Formats all option-related messages for screen reader accessibility.
Follows Italian language conventions with concise, clear feedback.

All methods are pure static functions - no side effects.
"""

from typing import Dict, Optional


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
        "Timer",
        "Modalità riciclo scarti",
        "(Opzione futura)"
    ]
    
    @staticmethod
    def format_open_message(first_option_value: str) -> str:
        """Format window opening message.
        
        Args:
            first_option_value: Current value of first option (Tipo mazzo)
        
        Returns:
            "Finestra opzioni. 1 di 5: Tipo mazzo, Carte Francesi. Premi H per aiuto."
        """
        return (
            f"Finestra opzioni. "
            f"1 di 5: Tipo mazzo, {first_option_value}. "
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
            index: Option position (0-4)
            name: Option name
            value: Current value
            include_hint: Add navigation hint (default True)
        
        Returns:
            Concise format: "3 di 5: Timer, Disattivato."
            With hint: "3 di 5: Timer, Disattivato. Premi INVIO per modificare."
        
        Examples:
            >>> format_option_item(0, "Tipo mazzo", "Carte Francesi", True)
            "1 di 5: Tipo mazzo, Carte Francesi. Premi INVIO per modificare."
            
            >>> format_option_item(2, "Timer", "10 minuti", False)
            "3 di 5: Timer, 10 minuti."
        """
        position = index + 1
        msg = f"{position} di 5: {name}, {value}."
        
        if include_hint:
            # Special hint for Timer (has extra keys)
            if index == 2:  # Timer option
                if "Disattivato" in value:
                    msg += " Premi T per attivare."
                else:
                    msg += " Premi T per disattivare o + e - per regolare."
            # Special message for future option
            elif index == 4:
                msg += " Opzione non ancora implementata."
            # Standard hint for other options
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
```

### Test Output TTS

```python
# test_options_formatter.py

def test_format_open_message():
    msg = OptionsFormatter.format_open_message("Carte Francesi")
    assert "Finestra opzioni" in msg
    assert "1 di 5" in msg
    assert "Premi H per aiuto" in msg

def test_format_option_item_with_hint():
    msg = OptionsFormatter.format_option_item(2, "Timer", "Disattivato", True)
    assert "3 di 5" in msg
    assert "Timer, Disattivato" in msg
    assert "Premi T per attivare" in msg

def test_format_option_changed():
    msg = OptionsFormatter.format_option_changed("Timer", "10 minuti")
    assert "Timer impostato a: 10 minuti" in msg

def test_format_help_text():
    msg = OptionsFormatter.format_help_text()
    assert "Frecce su e giù" in msg
    assert "1 a 5" in msg
    assert "INVIO" in msg
```

### Commit Message

```
feat(presentation): Create OptionsFormatter for TTS

Add dedicated formatter for options window messages.

Features:
- format_option_item(): Navigation messages with hints
- format_option_changed(): Modification confirmations
- format_all_settings(): Complete recap (tasto I)
- format_help_text(): Full command list (tasto H)
- format_save_dialog(): Confirmation dialog
- Contextual hints based on option type
- Italian gender agreement
- Timer-specific messages (+/-/T hints)

All methods pure static functions (no side effects).

Ref: OPTIONS_WINDOW_ROADMAP.md Commit #18
```

---

## 🎮 COMMIT #19: APPLICATION LAYER {#commit-19}

### Obiettivo

Creare controller per gestire logica completa della finestra opzioni.

### File Nuovo

**`src/application/options_controller.py`**

### Implementazione Completa

```python
"""Options window controller for virtual modal dialog.

Manages all options window logic including:
- Navigation (arrows, numbers)
- Modifications (toggle/cycle settings)
- State management (CLOSED/OPEN_CLEAN/OPEN_DIRTY)
- Save/discard confirmation
- Input routing and validation

Architecture: Application Layer (Clean Architecture)
Depends on: Domain (GameSettings), Presentation (OptionsFormatter)
"""

from typing import Dict, Optional, Tuple
from src.domain.services.game_settings import GameSettings
from src.presentation.options_formatter import OptionsFormatter


class OptionsWindowController:
    """Controller for virtual options window.
    
    Manages modal window state and user interactions.
    Uses HYBRID navigation (arrows + numbers) with accessibility focus.
    
    States:
    - CLOSED: Window not active (gameplay normal)
    - OPEN_CLEAN: Window open, no modifications
    - OPEN_DIRTY: Window open, modifications made (requires confirmation)
    
    Attributes:
        settings: Reference to GameSettings (domain service)
        cursor_position: Current option index (0-4)
        is_open: Window state flag
        state: Current state ("CLOSED"/"OPEN_CLEAN"/"OPEN_DIRTY")
        original_settings: Snapshot of settings at window open
        current_settings: Dict tracking current values
    """
    
    def __init__(self, settings: GameSettings):
        """Initialize options controller.
        
        Args:
            settings: Game settings service (domain layer)
        """
        self.settings = settings
        self.cursor_position = 0  # Current option (0-4)
        self.is_open = False
        self.state = "CLOSED"
        
        # Snapshot for change tracking
        self.original_settings: Dict[str, any] = {}
        self.current_settings: Dict[str, any] = {}
    
    # ===== WINDOW LIFECYCLE =====
    
    def open_window(self) -> str:
        """Open options window and save settings snapshot.
        
        Returns:
            TTS message for window opening
        
        State transition: CLOSED → OPEN_CLEAN
        """
        self.is_open = True
        self.state = "OPEN_CLEAN"
        self.cursor_position = 0
        
        # Save snapshot for change tracking
        self._save_snapshot()
        
        # Get first option current value
        deck_type = self._get_deck_type_display()
        
        return OptionsFormatter.format_open_message(deck_type)
    
    def close_window(self) -> str:
        """Close window with confirmation if modifications present.
        
        Returns:
            TTS message (direct close or dialog prompt)
        
        State transitions:
        - OPEN_CLEAN → CLOSED (direct)
        - OPEN_DIRTY → Show save dialog (stays OPEN_DIRTY until confirmed)
        """
        if self.state == "OPEN_DIRTY":
            # Show confirmation dialog (handled externally)
            return OptionsFormatter.format_save_dialog()
        else:
            # No changes, close directly
            self._reset_state()
            return OptionsFormatter.format_close_message()
    
    def save_and_close(self) -> str:
        """Save modifications and close window.
        
        Returns:
            TTS confirmation message
        
        State transition: OPEN_DIRTY → CLOSED
        """
        # Modifications already applied live, just update snapshot
        self._save_snapshot()
        self._reset_state()
        return OptionsFormatter.format_save_confirmed()
    
    def discard_and_close(self) -> str:
        """Discard modifications and close window.
        
        Returns:
            TTS confirmation message
        
        State transition: OPEN_DIRTY → CLOSED
        """
        # Restore original settings
        self._restore_snapshot()
        self._reset_state()
        return OptionsFormatter.format_save_discarded()
    
    def cancel_close(self) -> str:
        """Cancel close operation (stay in window).
        
        Returns:
            TTS message
        
        State: Stays OPEN_DIRTY
        """
        return OptionsFormatter.format_save_cancelled()
    
    # ===== NAVIGATION =====
    
    def navigate_up(self) -> str:
        """Navigate to previous option (wraparound).
        
        Returns:
            TTS message with option name, value, and hint
        """
        self.cursor_position = (self.cursor_position - 1) % 5
        return self._format_current_option(include_hint=True)
    
    def navigate_down(self) -> str:
        """Navigate to next option (wraparound).
        
        Returns:
            TTS message with option name, value, and hint
        """
        self.cursor_position = (self.cursor_position + 1) % 5
        return self._format_current_option(include_hint=True)
    
    def jump_to_option(self, index: int) -> str:
        """Jump directly to option by number (1-5).
        
        Args:
            index: Option index (0-4)
        
        Returns:
            TTS message (concise, no hint)
        
        Example:
            >>> controller.jump_to_option(2)
            "3 di 5: Timer, Disattivato."
        """
        if 0 <= index <= 4:
            self.cursor_position = index
            return self._format_current_option(include_hint=False)
        else:
            return "Opzione non valida."
    
    # ===== MODIFICATIONS =====
    
    def modify_current_option(self) -> str:
        """Modify currently selected option (toggle/cycle).
        
        Returns:
            TTS confirmation message or error
        
        State transition: OPEN_CLEAN → OPEN_DIRTY (on first modification)
        """
        # Block if game running
        if self.settings.game_state.is_running:
            return OptionsFormatter.format_blocked_during_game()
        
        # Block future option (index 4)
        if self.cursor_position == 4:
            return OptionsFormatter.format_future_option_blocked()
        
        # Route to appropriate handler
        handlers = [
            self._modify_deck_type,      # 0: Tipo Mazzo
            self._modify_difficulty,     # 1: Difficoltà
            self._cycle_timer_preset,    # 2: Timer (INVIO = cycle presets)
            self._modify_shuffle_mode,   # 3: Riciclo Scarti
        ]
        
        msg = handlers[self.cursor_position]()
        
        # Mark as dirty on successful modification
        if "impostato" in msg or "impostata" in msg or "disattivato" in msg:
            self.state = "OPEN_DIRTY"
        
        return msg
    
    def increment_timer(self) -> str:
        """Increment timer by 5 minutes (tasto +).
        
        Returns:
            TTS message or error
        
        Only works if cursor_position == 2 (Timer selected)
        """
        if self.cursor_position != 2:
            return OptionsFormatter.format_timer_error()
        
        if self.settings.game_state.is_running:
            return OptionsFormatter.format_blocked_during_game()
        
        success, msg = self.settings.increment_timer_validated()
        
        if success:
            self.state = "OPEN_DIRTY"
        
        return msg
    
    def decrement_timer(self) -> str:
        """Decrement timer by 5 minutes (tasto -).
        
        Returns:
            TTS message or error
        
        Only works if cursor_position == 2 (Timer selected)
        """
        if self.cursor_position != 2:
            return OptionsFormatter.format_timer_error()
        
        if self.settings.game_state.is_running:
            return OptionsFormatter.format_blocked_during_game()
        
        success, msg = self.settings.decrement_timer_validated()
        
        if success:
            self.state = "OPEN_DIRTY"
        
        return msg
    
    def toggle_timer(self) -> str:
        """Toggle timer ON(5min)/OFF (tasto T).
        
        Returns:
            TTS message or error
        
        Only works if cursor_position == 2 (Timer selected)
        """
        if self.cursor_position != 2:
            return OptionsFormatter.format_timer_error()
        
        if self.settings.game_state.is_running:
            return OptionsFormatter.format_blocked_during_game()
        
        success, msg = self.settings.toggle_timer()
        
        if success:
            self.state = "OPEN_DIRTY"
        
        return msg
    
    # ===== INFORMATION =====
    
    def read_all_settings(self) -> str:
        """Read complete settings recap (tasto I).
        
        Returns:
            TTS message with all current settings
        """
        settings_dict = {
            "Tipo mazzo": self._get_deck_type_display(),
            "Difficoltà": f"Livello {self.settings.difficulty_level}",
            "Timer": self._get_timer_display(),
            "Modalità riciclo scarti": self._get_shuffle_mode_display()
        }
        
        return OptionsFormatter.format_all_settings(settings_dict)
    
    def show_help(self) -> str:
        """Show complete help text (tasto H).
        
        Returns:
            TTS message with all commands
        """
        return OptionsFormatter.format_help_text()
    
    # ===== INTERNAL HELPERS =====
    
    def _format_current_option(self, include_hint: bool) -> str:
        """Format current option for TTS.
        
        Args:
            include_hint: Add navigation hint
        
        Returns:
            Formatted TTS message
        """
        option_name = OptionsFormatter.OPTION_NAMES[self.cursor_position]
        
        # Get current value
        value_getters = [
            self._get_deck_type_display,
            self._get_difficulty_display,
            self._get_timer_display,
            self._get_shuffle_mode_display,
            lambda: "Non implementata"
        ]
        
        value = value_getters[self.cursor_position]()
        
        return OptionsFormatter.format_option_item(
            self.cursor_position,
            option_name,
            value,
            include_hint
        )
    
    def _modify_deck_type(self) -> str:
        """Toggle deck type (French ↔ Neapolitan)."""
        success, msg = self.settings.toggle_deck_type()
        return msg
    
    def _modify_difficulty(self) -> str:
        """Cycle difficulty (1 → 2 → 3 → 1)."""
        success, msg = self.settings.cycle_difficulty()
        return msg
    
    def _cycle_timer_preset(self) -> str:
        """Cycle timer through presets (OFF → 10 → 20 → 30 → OFF).
        
        INVIO on Timer option cycles through common presets.
        For fine control, use +/- keys.
        """
        current = self.settings.max_time_game
        
        # Preset cycle: OFF → 10 → 20 → 30 → OFF
        if current <= 0:
            new_value = 600  # 10 minutes
        elif current == 600:
            new_value = 1200  # 20 minutes
        elif current == 1200:
            new_value = 1800  # 30 minutes
        else:
            new_value = -1  # OFF
        
        self.settings.max_time_game = new_value
        display = self._get_timer_display()
        
        return OptionsFormatter.format_option_changed("Timer", display)
    
    def _modify_shuffle_mode(self) -> str:
        """Toggle shuffle mode (Inversione ↔ Mescolata)."""
        success, msg = self.settings.toggle_shuffle_mode()
        return msg
    
    # ===== DISPLAY HELPERS =====
    
    def _get_deck_type_display(self) -> str:
        """Get human-readable deck type."""
        return (
            "Carte Francesi" if self.settings.deck_type == "french"
            else "Carte Napoletane"
        )
    
    def _get_difficulty_display(self) -> str:
        """Get human-readable difficulty."""
        return f"Livello {self.settings.difficulty_level}"
    
    def _get_timer_display(self) -> str:
        """Get human-readable timer value."""
        if self.settings.max_time_game <= 0:
            return "Disattivato"
        else:
            minutes = self.settings.max_time_game // 60
            return f"{minutes} minuti"
    
    def _get_shuffle_mode_display(self) -> str:
        """Get human-readable shuffle mode."""
        return (
            "Mescolata Casuale" if self.settings.shuffle_discards
            else "Inversione Semplice"
        )
    
    # ===== STATE MANAGEMENT =====
    
    def _save_snapshot(self) -> None:
        """Save current settings snapshot for change tracking."""
        self.original_settings = {
            "deck_type": self.settings.deck_type,
            "difficulty": self.settings.difficulty_level,
            "timer": self.settings.max_time_game,
            "shuffle": self.settings.shuffle_discards
        }
        self.current_settings = self.original_settings.copy()
    
    def _restore_snapshot(self) -> None:
        """Restore original settings (discard changes)."""
        self.settings.deck_type = self.original_settings["deck_type"]
        self.settings.difficulty_level = self.original_settings["difficulty"]
        self.settings.max_time_game = self.original_settings["timer"]
        self.settings.shuffle_discards = self.original_settings["shuffle"]
    
    def _reset_state(self) -> None:
        """Reset controller state (close window)."""
        self.is_open = False
        self.state = "CLOSED"
        self.cursor_position = 0
        self.original_settings.clear()
        self.current_settings.clear()
```

### Commit Message

```
feat(application): Create OptionsWindowController

Implement complete options window controller with HYBRID navigation.

Features:
- Window lifecycle (open/close with confirmation)
- Navigation (arrows wraparound, number jump)
- Modifications (toggle/cycle all options)
- Timer management (+/-/T keys with validation)
- State machine (CLOSED/OPEN_CLEAN/OPEN_DIRTY)
- Snapshot tracking (save/discard changes)
- Information (recap, help)
- Validation (block during game, timer key check)

Architecture:
- Application Layer (Clean Architecture)
- Depends on GameSettings (domain)
- Depends on OptionsFormatter (presentation)
- No pygame/UI dependencies

Supports user-approved HYBRID design (arrows + numbers + hints).

Ref: OPTIONS_WINDOW_ROADMAP.md Commit #19
```

---

## 🔌 COMMIT #20: INTEGRAZIONE GAMEPLAY {#commit-20}

### Obiettivo

Integrare controller opzioni in GameplayController con routing prioritario.

### File Modificato

**`src/application/gameplay_controller.py`**

### Modifiche Implementate

#### 1. Importazione e Inizializzazione

```python
# Aggiungi import
from src.application.options_controller import OptionsWindowController

class GameplayController:
    def __init__(self, engine, settings, accessibility):
        # ... init esistente ...
        
        # NUOVO: Controller finestra opzioni
        self.options_controller = OptionsWindowController(settings)
        
        # DEPRECATO: Rimuovi flag change_settings (gestito dal controller)
        # self.change_settings = False  # ← Rimuovi questa linea
```

#### 2. Routing Prioritario Input

```python
def handle_keyboard_events(self, event):
    """Handle keyboard input with priority routing.
    
    Priority:
    1. Options window (if open) - HIGHEST
    2. Normal gameplay
    
    Args:
        event: pygame keyboard event
    """
    # PRIORITY 1: Options window open
    if self.options_controller.is_open:
        self._handle_options_events(event)
        return
    
    # PRIORITY 2: Normal gameplay
    # ... codice esistente per gameplay ...
```

#### 3. Handler Opzioni Dedicato

```python
def _handle_options_events(self, event):
    """Handle keyboard input when options window is open.
    
    All gameplay keys are blocked when options window is active.
    
    Args:
        event: pygame keyboard event
    """
    import pygame
    
    # Special handling for save dialog state
    if self.options_controller.state == "OPEN_DIRTY" and hasattr(self, '_awaiting_save_response'):
        if self._awaiting_save_response:
            self._handle_save_dialog(event)
            return
    
    # Normal options navigation
    key_map = {
        pygame.K_o: lambda: self._handle_options_close(),
        pygame.K_UP: self.options_controller.navigate_up,
        pygame.K_DOWN: self.options_controller.navigate_down,
        pygame.K_RETURN: self.options_controller.modify_current_option,
        pygame.K_SPACE: self.options_controller.modify_current_option,
        pygame.K_ESCAPE: lambda: self._handle_options_close(),
        pygame.K_1: lambda: self.options_controller.jump_to_option(0),
        pygame.K_2: lambda: self.options_controller.jump_to_option(1),
        pygame.K_3: lambda: self.options_controller.jump_to_option(2),
        pygame.K_4: lambda: self.options_controller.jump_to_option(3),
        pygame.K_5: lambda: self.options_controller.jump_to_option(4),
        pygame.K_PLUS: self.options_controller.increment_timer,
        pygame.K_EQUALS: self.options_controller.increment_timer,  # + without SHIFT
        pygame.K_MINUS: self.options_controller.decrement_timer,
        pygame.K_t: self.options_controller.toggle_timer,
        pygame.K_i: self.options_controller.read_all_settings,
        pygame.K_h: self.options_controller.show_help,
    }
    
    if event.key in key_map:
        msg = key_map[event.key]()
        self.speak(msg)

def _handle_options_close(self) -> str:
    """Handle options window close (O or ESC).
    
    If modifications present, show save dialog.
    Otherwise close directly.
    
    Returns:
        TTS message
    """
    msg = self.options_controller.close_window()
    
    # Check if save dialog was triggered
    if "modifiche non salvate" in msg:
        self._awaiting_save_response = True
    
    return msg

def _handle_save_dialog(self, event):
    """Handle save confirmation dialog response.
    
    Args:
        event: pygame keyboard event
    """
    import pygame
    
    if event.key == pygame.K_s:
        # Save changes
        msg = self.options_controller.save_and_close()
        self._awaiting_save_response = False
        self.speak(msg)
    
    elif event.key == pygame.K_n:
        # Discard changes
        msg = self.options_controller.discard_and_close()
        self._awaiting_save_response = False
        self.speak(msg)
    
    elif event.key == pygame.K_ESCAPE:
        # Cancel close (stay in options)
        msg = self.options_controller.cancel_close()
        self._awaiting_save_response = False
        self.speak(msg)
```

#### 4. Handler Tasto O (Gameplay)

```python
def _handle_o_key(self):
    """Open options window (tasto O durante gameplay).
    
    Blocca se partita attiva.
    """
    if self.game_service.is_game_running():
        msg = "Non puoi aprire le opzioni durante una partita! Termina prima la partita."
    else:
        msg = self.options_controller.open_window()
    
    self.speak(msg)
```

#### 5. Rimozione Tasti Legacy (DEPRECATI)

```python
# RIMUOVI questi handler (sostituiti dalla finestra opzioni):
# - _handle_f1_key()  → Cambio mazzo
# - _handle_f2_key()  → Difficoltà
# - _handle_f3_key()  → Timer -
# - _handle_f4_key()  → Timer +
# - _handle_f5_key()  → Shuffle mode
# - _handle_ctrl_f3() → Timer OFF

# RIMUOVI dal callback_dict:
self.callback_dict = {
    # ... altri tasti ...
    # pygame.K_F1: self._handle_f1_key,  # ← RIMUOVI
    # pygame.K_F2: self._handle_f2_key,  # ← RIMUOVI
    # pygame.K_F3: self._handle_f3_key,  # ← RIMUOVI
    # pygame.K_F4: self._handle_f4_key,  # ← RIMUOVI
    # pygame.K_F5: self._handle_f5_key,  # ← RIMUOVI
}
```

### Commit Message

```
feat(application): Integrate OptionsWindowController in gameplay

Replace legacy F1-F5 hotkeys with full options window.

Changes:
- Add OptionsWindowController instance
- Priority input routing (options > gameplay)
- Dedicated _handle_options_events() handler
- Save dialog support (_handle_save_dialog)
- Open window with tasto O (gameplay)
- Remove deprecated F1-F5 handlers
- Remove deprecated CTRL+F3 handler

Features:
- Full HYBRID navigation (arrows + numbers)
- Confirmation dialog for unsaved changes
- Complete options control in modal window
- Block all gameplay keys when window open

Breaking change:
- F1-F5 keys no longer function
- Users must use tasto O to access options
- Help text updated to reflect new commands

Ref: OPTIONS_WINDOW_ROADMAP.md Commit #20
```

---

## ✅ TESTING COMPLETO {#testing}

### Test Manuali Critici

#### Navigazione
- [ ] Tasto O apre finestra (solo se no partita)
- [ ] Freccia ↑ naviga opzioni (wraparound 0→4)
- [ ] Freccia ↓ naviga opzioni (wraparound 4→0)
- [ ] Tasti 1-5 saltano a opzione N
- [ ] Feedback TTS conciso con hint

#### Modifiche Opzioni
- [ ] Opzione 0: Toggle Mazzo (French ↔ Napoletano)
- [ ] Opzione 1: Ciclo Difficoltà (1→2→3→1)
- [ ] Opzione 2: INVIO cicla timer presets (OFF→10→20→30→OFF)
- [ ] Opzione 3: Toggle Riciclo (Inversione ↔ Mescolata)
- [ ] Opzione 4: Blocco "non implementata"

#### Timer Dedicato (solo se cursor_position=2)
- [ ] Tasto T: Toggle OFF↔5min
- [ ] Tasto +: Incrementa +5min (max 60)
- [ ] Tasto -: Decrementa -5min (min 0=OFF)
- [ ] Limite massimo: "già al massimo: 60 minuti"
- [ ] Limite minimo: "già disattivato"
- [ ] Errore se +/-/T premuti con cursor_position≠2

#### Conferma Salvataggio
- [ ] ESC con modifiche: Dialog "Salvare modifiche?"
- [ ] Tasto S: Salva e chiudi
- [ ] Tasto N: Scarta e chiudi
- [ ] Tasto ESC in dialog: Annulla (rimani in opzioni)
- [ ] ESC senza modifiche: Chiudi diretto
- [ ] Tasto O con modifiche: Stesso comportamento ESC

#### Informazioni
- [ ] Tasto I: Recap completo tutte impostazioni
- [ ] Tasto H: Help completo comandi finestra
- [ ] Help non cambia cursor_position
- [ ] Recap non cambia cursor_position

#### Validazioni
- [ ] Blocco modifiche durante partita attiva
- [ ] TTS: "Non puoi modificare durante partita"
- [ ] Tasti +/-/T bloccati se cursor_position≠2
- [ ] Opzione 4 bloccata (non implementata)
- [ ] Snapshot settings salvato all'apertura
- [ ] Snapshot ripristinato se discard

#### Edge Cases
- [ ] Apertura durante partita: bloccata
- [ ] Wraparound navigazione: 0↔4
- [ ] Timer già al massimo: messaggio limite
- [ ] Timer già disattivato: messaggio limite
- [ ] Chiusura senza modifiche: no dialog
- [ ] Multiple modifiche: state OPEN_DIRTY corretto

#### Integrazione Gameplay
- [ ] Tasti gameplay bloccati quando finestra aperta
- [ ] Routing prioritario funziona
- [ ] Tasti F1-F5 non funzionano più (deprecati)
- [ ] CTRL+F3 non funziona più (deprecato)
- [ ] Tasto O apre finestra da gameplay

---

## 📚 ESEMPI FLUSSO UTENTE {#examples}

### Scenario 1: Modifica Timer Semplice

```
UTENTE                          TTS
────────────────────────────────────────────────────────────────
[Menu] Preme O                  "Finestra opzioni. 1 di 5: Tipo mazzo, 
                                 Carte Francesi. Premi H per aiuto."

Preme 3                         "3 di 5: Timer, Disattivato."

Preme T                         "Timer attivato a: 5 minuti."

Preme + + +                     "Timer impostato a: 10 minuti."
                                "Timer impostato a: 15 minuti."
                                "Timer impostato a: 20 minuti."

Preme ESC                       "Hai modifiche non salvate. Salvare le 
                                 modifiche? Premi S per salvare, N per scartare."

Preme S                         "Modifiche salvate. Torno al gioco."
```

### Scenario 2: Navigazione con Frecce

```
UTENTE                          TTS
────────────────────────────────────────────────────────────────
Preme O                         "Finestra opzioni. 1 di 5..."

Preme ↓                         "2 di 5: Difficoltà, Livello 1. 
                                 Premi INVIO per modificare."

Preme INVIO                     "Difficoltà impostata a: Livello 2."

Preme ↓                         "3 di 5: Timer, Disattivato. 
                                 Premi T per attivare."

Preme ↓                         "4 di 5: Modalità riciclo scarti, 
                                 Inversione Semplice. Premi INVIO per modificare."

Preme INVIO                     "Modalità riciclo: Mescolata Casuale."

Preme I                         "Impostazioni correnti: 
                                 Tipo mazzo: Carte Francesi. 
                                 Difficoltà: Livello 2. 
                                 Timer: Disattivato. 
                                 Modalità riciclo scarti: Mescolata Casuale."

Preme ESC                       "Hai modifiche non salvate..."

Preme S                         "Modifiche salvate. Torno al gioco."
```

### Scenario 3: Scarta Modifiche

```
UTENTE                          TTS
────────────────────────────────────────────────────────────────
Preme O                         "Finestra opzioni..."

Preme 1                         "2 di 5: Difficoltà, Livello 1."

Preme INVIO INVIO               "Difficoltà impostata a: Livello 2."
                                "Difficoltà impostata a: Livello 3."

Preme ESC                       "Hai modifiche non salvate..."

Preme N                         "Modifiche scartate. Torno al gioco."
                                [Difficoltà ripristinata a Livello 1]
```

### Scenario 4: Help e Recap

```
UTENTE                          TTS
────────────────────────────────────────────────────────────────
Preme O                         "Finestra opzioni..."

Preme H                         "Comandi finestra opzioni: 
                                 Frecce su e giù per navigare. 
                                 Tasti da 1 a 5 per accesso rapido. 
                                 INVIO o SPAZIO per modificare opzione. 
                                 Se Timer selezionato: T per attivare o disattivare, 
                                 + e - per regolare. 
                                 I per leggere tutte le impostazioni. 
                                 ESC per chiudere e tornare al gioco."

Preme I                         "Impostazioni correnti: 
                                 Tipo mazzo: Carte Francesi. 
                                 Difficoltà: Livello 1. 
                                 Timer: Disattivato. 
                                 Modalità riciclo scarti: Inversione Semplice."

Preme ESC                       "Opzioni chiuse. Torno al gioco."
                                [Nessuna modifica, chiude diretto]
```

### Scenario 5: Errori e Validazioni

```
UTENTE                          TTS
────────────────────────────────────────────────────────────────
Preme O                         "Finestra opzioni..."

Preme 1                         "2 di 5: Difficoltà, Livello 1."

Preme T                         "Seleziona prima il Timer con il tasto 3."
                                [Errore: T funziona solo su Timer]

Preme +                         "Seleziona prima il Timer con il tasto 3."
                                [Errore: + funziona solo su Timer]

Preme 3                         "3 di 5: Timer, Disattivato."

Preme +                         "Timer impostato a: 5 minuti."
                                [OK: Timer selezionato]

Preme + (x11)                   [Incrementa fino a 60 minuti]
                                "Timer già al massimo: 60 minuti."
                                [Limite raggiunto]

Preme -                         "Timer impostato a: 55 minuti."
                                [Decremento OK]

Preme 5                         "5 di 5: Opzione non ancora implementata."

Preme INVIO                     "Opzione non ancora implementata. 
                                 Sarà disponibile in un prossimo aggiornamento."
```

---

## 📊 STATISTICHE IMPLEMENTAZIONE

**Commits totali**: 4 (#17-20)

**File creati**: 2
- `src/application/options_controller.py`
- `src/presentation/options_formatter.py`

**File modificati**: 2
- `src/domain/services/game_settings.py`
- `src/application/gameplay_controller.py`

**Linee codice totali**: ~800
- Domain Layer: ~30 linee
- Presentation Layer: ~150 linee
- Application Layer: ~500 linee
- Integration: ~120 linee

**Metodi aggiunti**: ~25
- GameSettings: 1 (toggle_timer)
- OptionsFormatter: 14 (static)
- OptionsWindowController: 20+ (instance)
- GameplayController: 3 (handlers)

**Test cases da eseguire**: ~40

**Tasti eliminati**: 6 (F1, F2, F3, F4, F5, CTRL+F3)

**Tasti aggiunti**: 11 (O, ↑, ↓, 1-5, INVIO, +, -, T, I, H, ESC)

---

## ✅ CHECKLIST COMMIT-PER-COMMIT

### Commit #17: Domain Layer
- [ ] Aggiungi `toggle_timer()` a GameSettings
- [ ] Test unitari toggle_timer()
- [ ] Commit con messaggio descrittivo

### Commit #18: Presentation Layer
- [ ] Crea `options_formatter.py`
- [ ] Implementa tutti i metodi format_*()
- [ ] Test output TTS
- [ ] Commit con messaggio descrittivo

### Commit #19: Application Layer
- [ ] Crea `options_controller.py`
- [ ] Implementa classe completa OptionsWindowController
- [ ] Test logica navigazione
- [ ] Test logica modifiche
- [ ] Test state machine
- [ ] Commit con messaggio descrittivo

### Commit #20: Integrazione
- [ ] Aggiungi OptionsWindowController in GameplayController
- [ ] Implementa routing prioritario
- [ ] Implementa _handle_options_events()
- [ ] Implementa _handle_save_dialog()
- [ ] Rimuovi handler F1-F5 deprecati
- [ ] Test integrazione completa
- [ ] Commit con messaggio descrittivo

---

🗺️ **ROADMAP FINESTRA OPZIONI COMPLETATO**

**Next**: Esegui testing completo e documenta eventuali issue trovati.
