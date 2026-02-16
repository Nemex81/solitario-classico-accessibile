# Sistema Verbosità Warnings Malus - Piano Implementazione v2.6.0

**Data**: 2026-02-16  
**Versione**: v2.6.0  
**Branch**: `copilot/complete-scoring-system-v2-0`  
**Autore**: Piano tecnico validato su analisi codice esistente  

---

## Executive Summary

Il sistema di scoring v2.0 implementa correttamente i malus progressivi per stock draw e recycle, ma **manca completamente il sistema di avvisi TTS** per informare il giocatore quando supera soglie di penalità.

### Problema Identificato

```python
# ATTUALE: Eventi registrati silenziosamente
if self.scoring:
    self.scoring.record_event(ScoreEventType.STOCK_DRAW)  # Nessun feedback TTS
```

### Soluzione Proposta

```python
# NUOVO: Warning TTS contestuali e configurabili
if self.scoring:
    event = self.scoring.record_event(ScoreEventType.STOCK_DRAW)
    warning = self.scoring.check_threshold_warning(event)
    if warning and settings.score_warning_level >= warning.min_level:
        self.screenreader.speak(warning.message, interrupt=False)
```

### Obiettivi Feature v2.6.0

1. **Opzione Menu**: ComboBox "Avvisi Malus" con 4 livelli (DISABLED, MINIMAL, BALANCED, COMPLETE)
2. **Warning Contestuali**: Avvisi TTS quando giocatore supera soglie stock draw/recycle
3. **Configurabile**: Principianti ricevono guida massima, veterani possono disabilitare
4. **Accessibile**: Messaggi TTS ottimizzati per screen reader, non intrusivi
5. **Architettura Clean**: Domain genera warnings, Application decide vocalizzazione

---

## Architettura del Sistema

### Struttura Layered (Clean Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ScoreFormatter                                        │ │
│  │  + format_threshold_warning(warning) → str (TTS)      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  APPLICATION LAYER                                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  GameEngine                                            │ │
│  │  + _draw_from_stock() → check warnings + TTS          │ │
│  │  + recyclewaste() → check warnings + TTS              │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  OptionsController                                     │ │
│  │  + navigate to option 8 (Avvisi Malus)                │ │
│  │  + cycle_warning_level() → DISABLED/MINIMAL/...       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  DOMAIN LAYER                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  GameSettings                                          │ │
│  │  + score_warning_level: ScoreWarningLevel (BALANCED)  │ │
│  │  + cycle_warning_level() → (bool, str)                │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ScoringService                                        │ │
│  │  + check_threshold_warning(event) → Optional[Warning] │ │
│  │  + _should_emit_warning(threshold_key) → bool         │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Models (scoring.py)                                   │ │
│  │  + ScoreWarningLevel (IntEnum)                         │ │
│  │  + ThresholdWarning (dataclass)                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Flusso di Esecuzione

```
1. Giocatore preme M (pesca dal mazzo)
   ↓
2. GameEngine._draw_from_stock()
   ↓
3. ScoringService.record_event(STOCK_DRAW)
   ├─ Aggiorna stock_draw_count
   ├─ Calcola penalità progressiva
   └─ Ritorna ScoreEvent
   ↓
4. ScoringService.check_threshold_warning(event)
   ├─ Controlla se soglia superata (es. draw 21 = prima penalità)
   ├─ Verifica se warning già emesso per questa soglia
   └─ Ritorna Optional[ThresholdWarning]
   ↓
5. GameEngine: Se warning presente E level >= warning.min_level
   ↓
6. ScoreFormatter.format_threshold_warning(warning)
   └─ Formatta messaggio TTS accessibile
   ↓
7. ScreenReader.speak(message, interrupt=False)
   └─ Annuncio non intrusivo (dopo messaggio mossa)
```

---

## Modelli di Dominio (Fase 1)

### File: `src/domain/models/scoring.py`

#### 1.1 Enum `ScoreWarningLevel` (GIÀ IMPLEMENTATO)

```python
from enum import IntEnum

class ScoreWarningLevel(IntEnum):
    """Livelli di verbosità warnings soglie scoring (v2.6.0)."""
    
    DISABLED = 0   # Nessun warning
    MINIMAL = 1    # Solo transizioni 0pt → penalità
    BALANCED = 2   # Transizioni + escalation (DEFAULT)
    COMPLETE = 3   # Pre-warnings + tutte soglie
```

✅ **Nota**: Questo enum è già presente nel file `scoring.py` alle righe finali.

#### 1.2 Dataclass `ThresholdWarning` (NUOVO)

```python
@dataclass(frozen=True)
class ThresholdWarning:
    """Warning emesso quando giocatore supera soglia malus (v2.6.0).
    
    Generato dal ScoringService quando:
    - Stock draw count supera 20 (pre-warning) o 21 (penalità) o 41 (escalation)
    - Recycle count supera 2 (pre-warning) o 3 (penalità) o 5 (escalation)
    
    Attributes:
        threshold_key: Chiave unica soglia (es. "stock_draw_21", "recycle_3")
        min_level: Livello minimo per emettere questo warning
        event_type: Tipo evento che ha scatenato warning
        current_count: Conteggio corrente (stock_draw_count o recycle_count)
        penalty_points: Penalità applicata (-1, -2, -10, -20, etc.)
        message_key: Chiave per formatter (es. "stock_first_penalty")
    
    Example:
        >>> warning = ThresholdWarning(
        ...     threshold_key="stock_draw_21",
        ...     min_level=ScoreWarningLevel.MINIMAL,
        ...     event_type=ScoreEventType.STOCK_DRAW,
        ...     current_count=21,
        ...     penalty_points=-1,
        ...     message_key="stock_first_penalty"
        ... )
    """
    
    threshold_key: str
    min_level: ScoreWarningLevel
    event_type: ScoreEventType
    current_count: int
    penalty_points: int
    message_key: str
```

#### Mapping Soglie per Livello

| Threshold Key | Event | Count | Penalty | Min Level | Message Key |
|--------------|-------|-------|---------|-----------|-------------|
| `stock_draw_20` | STOCK_DRAW | 20 | 0 | COMPLETE | `stock_pre_warning` |
| `stock_draw_21` | STOCK_DRAW | 21 | -1 | MINIMAL | `stock_first_penalty` |
| `stock_draw_41` | STOCK_DRAW | 41 | -2 | BALANCED | `stock_escalation` |
| `recycle_3` | RECYCLE_WASTE | 3 | -10 | MINIMAL | `recycle_first_penalty` |
| `recycle_4` | RECYCLE_WASTE | 4 | -20 | BALANCED | `recycle_escalation` |
| `recycle_5` | RECYCLE_WASTE | 5 | -35 | COMPLETE | `recycle_escalation_2` |

---

## ScoringService Extensions (Fase 2)

### File: `src/domain/services/scoring_service.py`

#### 2.1 Aggiungere Tracking Warnings Emessi

```python
class ScoringService:
    def __init__(self, ...):
        # ... existing fields ...
        self.stock_draw_count = 0
        self.recycle_count = 0
        
        # NEW v2.6.0: Track emitted warnings (avoid duplicates)
        self._emitted_warnings: set[str] = set()  # {"stock_draw_21", "recycle_3", ...}
```

#### 2.2 Metodo `check_threshold_warning()` (NUOVO)

```python
def check_threshold_warning(self, event: ScoreEvent) -> Optional[ThresholdWarning]:
    """Check if event triggered a threshold warning (v2.6.0).
    
    Verifica se l'evento appena registrato ha superato una soglia
    di malus e se deve essere emesso un warning TTS.
    
    Args:
        event: Evento appena registrato
        
    Returns:
        ThresholdWarning se soglia superata e warning non già emesso, None altrimenti
        
    Logic:
        - STOCK_DRAW: Controlla stock_draw_count contro soglie 20, 21, 41
        - RECYCLE_WASTE: Controlla recycle_count contro soglie 3, 4, 5
        - Altri eventi: sempre None
        
    Warning Emission:
        - Warning emesso UNA SOLA VOLTA per soglia (tracking in _emitted_warnings)
        - Se warning già emesso per questa soglia, ritorna None
    
    Example:
        >>> event = service.record_event(ScoreEventType.STOCK_DRAW)
        >>> warning = service.check_threshold_warning(event)
        >>> if warning:
        ...     print(f"Soglia superata: {warning.threshold_key}")
    """
    if event.event_type == ScoreEventType.STOCK_DRAW:
        return self._check_stock_draw_warning()
    elif event.event_type == ScoreEventType.RECYCLE_WASTE:
        return self._check_recycle_warning()
    else:
        return None

def _check_stock_draw_warning(self) -> Optional[ThresholdWarning]:
    """Check stock draw thresholds (v2.6.0).
    
    Thresholds:
    - 20: Pre-warning (COMPLETE only) - "Prossima pesca avrà penalità"
    - 21: First penalty (MINIMAL+) - "Attenzione: penalità pesca attiva"
    - 41: Escalation (BALANCED+) - "Penalità pesca aumentata a -2 punti"
    """
    count = self.stock_draw_count
    
    # Threshold 20: Pre-warning (COMPLETE only)
    if count == 20 and "stock_draw_20" not in self._emitted_warnings:
        self._emitted_warnings.add("stock_draw_20")
        return ThresholdWarning(
            threshold_key="stock_draw_20",
            min_level=ScoreWarningLevel.COMPLETE,
            event_type=ScoreEventType.STOCK_DRAW,
            current_count=count,
            penalty_points=0,  # Next draw will be -1
            message_key="stock_pre_warning"
        )
    
    # Threshold 21: First penalty (MINIMAL+)
    elif count == 21 and "stock_draw_21" not in self._emitted_warnings:
        self._emitted_warnings.add("stock_draw_21")
        return ThresholdWarning(
            threshold_key="stock_draw_21",
            min_level=ScoreWarningLevel.MINIMAL,
            event_type=ScoreEventType.STOCK_DRAW,
            current_count=count,
            penalty_points=-1,
            message_key="stock_first_penalty"
        )
    
    # Threshold 41: Escalation (BALANCED+)
    elif count == 41 and "stock_draw_41" not in self._emitted_warnings:
        self._emitted_warnings.add("stock_draw_41")
        return ThresholdWarning(
            threshold_key="stock_draw_41",
            min_level=ScoreWarningLevel.BALANCED,
            event_type=ScoreEventType.STOCK_DRAW,
            current_count=count,
            penalty_points=-2,
            message_key="stock_escalation"
        )
    
    return None

def _check_recycle_warning(self) -> Optional[ThresholdWarning]:
    """Check recycle waste thresholds (v2.6.0).
    
    Thresholds:
    - 3: First penalty (MINIMAL+) - "Attenzione: penalità riciclo -10 punti"
    - 4: Escalation (BALANCED+) - "Penalità riciclo aumentata a -20 punti"
    - 5: Escalation 2 (COMPLETE only) - "Penalità riciclo aumentata a -35 punti"
    """
    count = self.recycle_count
    
    # Threshold 3: First penalty (MINIMAL+)
    if count == 3 and "recycle_3" not in self._emitted_warnings:
        self._emitted_warnings.add("recycle_3")
        return ThresholdWarning(
            threshold_key="recycle_3",
            min_level=ScoreWarningLevel.MINIMAL,
            event_type=ScoreEventType.RECYCLE_WASTE,
            current_count=count,
            penalty_points=-10,
            message_key="recycle_first_penalty"
        )
    
    # Threshold 4: Escalation (BALANCED+)
    elif count == 4 and "recycle_4" not in self._emitted_warnings:
        self._emitted_warnings.add("recycle_4")
        return ThresholdWarning(
            threshold_key="recycle_4",
            min_level=ScoreWarningLevel.BALANCED,
            event_type=ScoreEventType.RECYCLE_WASTE,
            current_count=count,
            penalty_points=-20,
            message_key="recycle_escalation"
        )
    
    # Threshold 5: Escalation 2 (COMPLETE only)
    elif count == 5 and "recycle_5" not in self._emitted_warnings:
        self._emitted_warnings.add("recycle_5")
        return ThresholdWarning(
            threshold_key="recycle_5",
            min_level=ScoreWarningLevel.COMPLETE,
            event_type=ScoreEventType.RECYCLE_WASTE,
            current_count=count,
            penalty_points=-35,
            message_key="recycle_escalation_2"
        )
    
    return None
```

#### 2.3 Aggiornare `reset()` Method

```python
def reset(self) -> None:
    """Reset scoring state for new game."""
    self.events = []
    self.recycle_count = 0
    self.stock_draw_count = 0
    self._emitted_warnings.clear()  # NEW v2.6.0: Reset warning tracking
```

---

## GameSettings Extensions (Fase 3)

### File: `src/domain/services/game_settings.py`

#### 3.1 Aggiungere Campo `score_warning_level`

```python
class GameSettings:
    def __init__(self):
        # ... existing fields ...
        
        # NEW v2.6.0: Score warning verbosity level
        self.score_warning_level: ScoreWarningLevel = ScoreWarningLevel.BALANCED  # Default
```

#### 3.2 Metodo `cycle_warning_level()` (NUOVO)

```python
def cycle_warning_level(self) -> tuple[bool, str]:
    """Cycle through warning levels: DISABLED → MINIMAL → BALANCED → COMPLETE → DISABLED.
    
    Returns:
        (success, message) - Success flag and TTS confirmation message
        
    Behavior:
        - Cycles through all 4 levels in order
        - Returns localized level name for TTS
        
    Example:
        >>> success, msg = settings.cycle_warning_level()
        >>> print(msg)
        "Avvisi malus: Bilanciato."
    """
    # Cycle through levels
    current_value = self.score_warning_level.value
    next_value = (current_value + 1) % 4  # 0-3 wrap-around
    self.score_warning_level = ScoreWarningLevel(next_value)
    
    # Get display name
    display = self.get_warning_level_display()
    
    return True, f"Avvisi malus: {display}."
```

#### 3.3 Metodo `get_warning_level_display()` (NUOVO)

```python
def get_warning_level_display(self) -> str:
    """Get Italian display name for current warning level.
    
    Returns:
        Localized level name for UI/TTS
        
    Mapping:
        - DISABLED (0) → "Disattivato"
        - MINIMAL (1) → "Minimo"
        - BALANCED (2) → "Bilanciato"
        - COMPLETE (3) → "Completo"
    """
    level_names = {
        ScoreWarningLevel.DISABLED: "Disattivato",
        ScoreWarningLevel.MINIMAL: "Minimo",
        ScoreWarningLevel.BALANCED: "Bilanciato",
        ScoreWarningLevel.COMPLETE: "Completo",
    }
    return level_names.get(self.score_warning_level, "Sconosciuto")
```

---

## OptionsController Extensions (Fase 4)

### File: `src/application/options_controller.py`

#### 4.1 Aggiornare Lista Opzioni (ora 9 opzioni)

```python
def _format_current_option(self, include_hint: bool) -> str:
    """Format current option for TTS."""
    option_name = OptionsFormatter.OPTION_NAMES[self.cursor_position]
    
    # Get current value
    value_getters = [
        self.settings.get_deck_type_display,
        self.settings.get_difficulty_display,
        self.settings.get_draw_count_display,
        self.settings.get_timer_display,
        self.settings.get_shuffle_mode_display,
        self.settings.get_command_hints_display,
        self.settings.get_scoring_display,
        self.settings.get_timer_strict_mode_display,
        self.settings.get_warning_level_display,  # NEW option 8
    ]
    
    value = value_getters[self.cursor_position]()
    # ...
```

#### 4.2 Aggiornare `navigate_up()` e `navigate_down()`

```python
def navigate_up(self) -> str:
    """Navigate to previous option (wraparound)."""
    self.cursor_position = (self.cursor_position - 1) % 9  # Was 8, now 9
    return self._format_current_option(include_hint=True)

def navigate_down(self) -> str:
    """Navigate to next option (wraparound)."""
    self.cursor_position = (self.cursor_position + 1) % 9  # Was 8, now 9
    return self._format_current_option(include_hint=True)
```

#### 4.3 Aggiungere Handler Option 8

```python
def modify_current_option(self) -> str:
    """Modify currently selected option (toggle/cycle)."""
    # ...
    
    handlers = [
        self._modify_deck_type,           # 0
        self._modify_difficulty,          # 1
        self._modify_draw_count,          # 2
        self._cycle_timer_preset,         # 3
        self._modify_shuffle_mode,        # 4
        self._modify_command_hints,       # 5
        self._modify_scoring,             # 6
        self._modify_timer_strict_mode,   # 7
        self._modify_warning_level,       # 8 NEW
    ]
    # ...

def _modify_warning_level(self) -> str:
    """Cycle warning level (DISABLED → MINIMAL → BALANCED → COMPLETE → DISABLED)."""
    old_value = self.settings.score_warning_level
    success, msg = self.settings.cycle_warning_level()
    if success:
        new_value = self.settings.score_warning_level
        log.settings_changed("score_warning_level", old_value, new_value)
    return msg
```

#### 4.4 Aggiornare `read_all_settings()`

```python
def read_all_settings(self) -> str:
    """Read complete settings recap (tasto I)."""
    settings_dict = {
        "Tipo mazzo": self.settings.get_deck_type_display(),
        "Difficoltà": self.settings.get_difficulty_display(),
        "Carte Pescate": self.settings.get_draw_count_display(),
        "Timer": self.settings.get_timer_display(),
        "Modalità riciclo scarti": self.settings.get_shuffle_mode_display(),
        "Suggerimenti comandi": self.settings.get_command_hints_display(),
        "Sistema Punti": self.settings.get_scoring_display(),
        "Modalità Timer": self.settings.get_timer_strict_mode_display(),
        "Avvisi Malus": self.settings.get_warning_level_display(),  # NEW
    }
    
    return OptionsFormatter.format_all_settings(settings_dict)
```

#### 4.5 Aggiornare Snapshot Save/Restore

```python
def _save_snapshot(self) -> None:
    """Save current settings snapshot for change tracking."""
    self.original_settings = {
        # ... existing fields ...
        "score_warning_level": self.settings.score_warning_level,  # NEW
    }

def _restore_snapshot(self) -> None:
    """Restore original settings (discard changes)."""
    # ... existing restorations ...
    self.settings.score_warning_level = self.original_settings["score_warning_level"]  # NEW
```

---

## Presentation Layer (Fase 5)

### File: `src/presentation/formatters/score_formatter.py`

#### 5.1 Metodo `format_threshold_warning()` (NUOVO)

```python
@staticmethod
def format_threshold_warning(warning: ThresholdWarning) -> str:
    """Format threshold warning for TTS (v2.6.0).
    
    Genera messaggio TTS ottimizzato per screen reader quando
    giocatore supera soglia malus (stock draw o recycle).
    
    Args:
        warning: ThresholdWarning from ScoringService
        
    Returns:
        Formatted TTS message
        
    Message Templates:
        - stock_pre_warning: "Prossima pesca dal mazzo avrà penalità di 1 punto."
        - stock_first_penalty: "Attenzione: penalità pesca attiva, meno 1 punto per pesca."
        - stock_escalation: "Penalità pesca aumentata: meno 2 punti per pesca."
        - recycle_first_penalty: "Attenzione: penalità riciclo attiva, meno 10 punti."
        - recycle_escalation: "Penalità riciclo aumentata: meno 20 punti."
        - recycle_escalation_2: "Penalità riciclo aumentata: meno 35 punti."
    
    Example:
        >>> warning = ThresholdWarning(..., message_key="stock_first_penalty", ...)
        >>> msg = ScoreFormatter.format_threshold_warning(warning)
        >>> print(msg)
        "Attenzione: penalità pesca attiva, meno 1 punto per pesca."
    """
    # Message templates (Italian, TTS-optimized)
    templates = {
        "stock_pre_warning": (
            "Prossima pesca dal mazzo avrà penalità di 1 punto."
        ),
        "stock_first_penalty": (
            "Attenzione: penalità pesca attiva, meno 1 punto per pesca."
        ),
        "stock_escalation": (
            "Penalità pesca aumentata: meno 2 punti per pesca."
        ),
        "recycle_first_penalty": (
            f"Attenzione: penalità riciclo attiva, meno {abs(warning.penalty_points)} punti."
        ),
        "recycle_escalation": (
            f"Penalità riciclo aumentata: meno {abs(warning.penalty_points)} punti."
        ),
        "recycle_escalation_2": (
            f"Penalità riciclo aumentata: meno {abs(warning.penalty_points)} punti."
        ),
    }
    
    # Get template for message_key
    message = templates.get(
        warning.message_key,
        f"Soglia malus superata: {warning.current_count}."
    )
    
    return message
```

### File: `src/presentation/options_formatter.py`

#### 5.2 Aggiornare `OPTION_NAMES`

```python
class OptionsFormatter:
    """Formatter for options window messages (v2.6.0)."""
    
    OPTION_NAMES = [
        "Tipo Mazzo",           # 0
        "Difficoltà",           # 1
        "Carte Pescate",        # 2
        "Timer",                # 3
        "Modalità Riciclo",     # 4
        "Suggerimenti Comandi", # 5
        "Sistema Punti",        # 6
        "Modalità Timer",       # 7
        "Avvisi Malus",         # 8 NEW
    ]
```

---

## GameEngine Integration (Fase 5)

### File: `src/application/game_engine.py`

#### 5.1 Aggiornare `_draw_from_stock()` con Warning Check

```python
def _draw_from_stock(self):
    """Draw card(s) from stock with scoring integration (v2.0 + v2.6.0)."""
    # ... existing draw logic ...
    
    # Record scoring event (v2.0)
    if self.scoring:
        event = self.scoring.record_event(ScoreEventType.STOCK_DRAW)
        
        # NEW v2.6.0: Check for threshold warning
        warning = self.scoring.check_threshold_warning(event)
        if warning and self.settings.score_warning_level >= warning.min_level:
            # Format warning message
            from src.presentation.formatters.score_formatter import ScoreFormatter
            warning_msg = ScoreFormatter.format_threshold_warning(warning)
            
            # Announce after main message (non-intrusive)
            pygame.time.wait(300)  # Brief pause
            self.screenreader.speak(warning_msg, interrupt=False)
```

#### 5.2 Aggiornare `recyclewaste()` con Warning Check

```python
def recyclewaste(self):
    """Recycle waste pile with scoring integration (v2.0 + v2.6.0)."""
    # ... existing recycle logic ...
    
    # Record scoring event (v2.0)
    if self.scoring:
        event = self.scoring.record_event(ScoreEventType.RECYCLE_WASTE)
        
        # NEW v2.6.0: Check for threshold warning
        warning = self.scoring.check_threshold_warning(event)
        if warning and self.settings.score_warning_level >= warning.min_level:
            # Format warning message
            from src.presentation.formatters.score_formatter import ScoreFormatter
            warning_msg = ScoreFormatter.format_threshold_warning(warning)
            
            # Announce after main message (non-intrusive)
            pygame.time.wait(300)  # Brief pause
            self.screenreader.speak(warning_msg, interrupt=False)
```

---

## Testing Strategy

### Unit Tests (Target: 95% coverage)

#### Test Suite 1: Domain Models

**File**: `tests/unit/domain/models/test_scoring_warnings.py`

```python
def test_threshold_warning_immutability():
    """ThresholdWarning dataclass is frozen."""
    warning = ThresholdWarning(...)
    with pytest.raises(FrozenInstanceError):
        warning.penalty_points = -10

def test_score_warning_level_values():
    """ScoreWarningLevel enum has correct values."""
    assert ScoreWarningLevel.DISABLED == 0
    assert ScoreWarningLevel.MINIMAL == 1
    assert ScoreWarningLevel.BALANCED == 2
    assert ScoreWarningLevel.COMPLETE == 3

def test_score_warning_level_comparison():
    """ScoreWarningLevel supports comparison operators."""
    assert ScoreWarningLevel.BALANCED >= ScoreWarningLevel.MINIMAL
    assert ScoreWarningLevel.COMPLETE > ScoreWarningLevel.DISABLED
```

#### Test Suite 2: ScoringService Warnings

**File**: `tests/unit/domain/services/test_scoring_service_warnings.py`

```python
def test_stock_draw_warning_at_21(scoring_service):
    """Stock draw 21 triggers first penalty warning (MINIMAL+)."""
    # Draw 20 times (no warning)
    for _ in range(20):
        event = scoring_service.record_event(ScoreEventType.STOCK_DRAW)
        warning = scoring_service.check_threshold_warning(event)
        assert warning is None
    
    # Draw 21st time (triggers warning)
    event = scoring_service.record_event(ScoreEventType.STOCK_DRAW)
    warning = scoring_service.check_threshold_warning(event)
    
    assert warning is not None
    assert warning.threshold_key == "stock_draw_21"
    assert warning.min_level == ScoreWarningLevel.MINIMAL
    assert warning.penalty_points == -1
    assert warning.message_key == "stock_first_penalty"

def test_stock_draw_warning_at_41(scoring_service):
    """Stock draw 41 triggers escalation warning (BALANCED+)."""
    # Draw 40 times
    for _ in range(40):
        scoring_service.record_event(ScoreEventType.STOCK_DRAW)
    
    # Draw 41st time
    event = scoring_service.record_event(ScoreEventType.STOCK_DRAW)
    warning = scoring_service.check_threshold_warning(event)
    
    assert warning is not None
    assert warning.threshold_key == "stock_draw_41"
    assert warning.penalty_points == -2

def test_warning_emitted_once_per_threshold(scoring_service):
    """Warning emitted only once per threshold (no duplicates)."""
    # Draw to threshold 21
    for _ in range(21):
        scoring_service.record_event(ScoreEventType.STOCK_DRAW)
    
    # Reset and draw again to 21
    scoring_service.reset()
    for _ in range(20):
        event = scoring_service.record_event(ScoreEventType.STOCK_DRAW)
        warning = scoring_service.check_threshold_warning(event)
    
    # First time at 21 after reset: warning present
    event = scoring_service.record_event(ScoreEventType.STOCK_DRAW)
    warning = scoring_service.check_threshold_warning(event)
    assert warning is not None
    
    # Second event at same count (shouldn't happen but test safety)
    # Warning should NOT be emitted again
    event = scoring_service.record_event(ScoreEventType.STOCK_DRAW)  # 22nd
    warning = scoring_service.check_threshold_warning(event)
    assert warning is None  # No warning at 22

def test_recycle_warning_at_3(scoring_service):
    """Recycle 3 triggers first penalty warning (MINIMAL+)."""
    # Recycle twice (no warning)
    for _ in range(2):
        event = scoring_service.record_event(ScoreEventType.RECYCLE_WASTE)
        warning = scoring_service.check_threshold_warning(event)
        assert warning is None
    
    # Recycle 3rd time
    event = scoring_service.record_event(ScoreEventType.RECYCLE_WASTE)
    warning = scoring_service.check_threshold_warning(event)
    
    assert warning is not None
    assert warning.threshold_key == "recycle_3"
    assert warning.penalty_points == -10
```

#### Test Suite 3: GameSettings Warning Level

**File**: `tests/unit/domain/services/test_game_settings_warnings.py`

```python
def test_default_warning_level_balanced(settings):
    """Default warning level is BALANCED."""
    assert settings.score_warning_level == ScoreWarningLevel.BALANCED

def test_cycle_warning_level(settings):
    """Cycle warning level through all 4 levels."""
    # Start at BALANCED (2)
    assert settings.score_warning_level == ScoreWarningLevel.BALANCED
    
    # Cycle to COMPLETE (3)
    success, msg = settings.cycle_warning_level()
    assert success
    assert settings.score_warning_level == ScoreWarningLevel.COMPLETE
    assert "Completo" in msg
    
    # Cycle to DISABLED (0)
    success, msg = settings.cycle_warning_level()
    assert settings.score_warning_level == ScoreWarningLevel.DISABLED
    assert "Disattivato" in msg
    
    # Cycle to MINIMAL (1)
    success, msg = settings.cycle_warning_level()
    assert settings.score_warning_level == ScoreWarningLevel.MINIMAL
    assert "Minimo" in msg
    
    # Cycle back to BALANCED (2)
    success, msg = settings.cycle_warning_level()
    assert settings.score_warning_level == ScoreWarningLevel.BALANCED
    assert "Bilanciato" in msg

def test_get_warning_level_display(settings):
    """Display names are correct for all levels."""
    settings.score_warning_level = ScoreWarningLevel.DISABLED
    assert settings.get_warning_level_display() == "Disattivato"
    
    settings.score_warning_level = ScoreWarningLevel.MINIMAL
    assert settings.get_warning_level_display() == "Minimo"
    
    settings.score_warning_level = ScoreWarningLevel.BALANCED
    assert settings.get_warning_level_display() == "Bilanciato"
    
    settings.score_warning_level = ScoreWarningLevel.COMPLETE
    assert settings.get_warning_level_display() == "Completo"
```

#### Test Suite 4: Presentation Formatters

**File**: `tests/unit/presentation/test_score_formatter_warnings.py`

```python
def test_format_stock_first_penalty():
    """Format stock draw first penalty warning."""
    warning = ThresholdWarning(
        threshold_key="stock_draw_21",
        min_level=ScoreWarningLevel.MINIMAL,
        event_type=ScoreEventType.STOCK_DRAW,
        current_count=21,
        penalty_points=-1,
        message_key="stock_first_penalty"
    )
    
    msg = ScoreFormatter.format_threshold_warning(warning)
    assert "Attenzione" in msg
    assert "penalità pesca" in msg
    assert "meno 1 punto" in msg

def test_format_recycle_escalation():
    """Format recycle escalation warning."""
    warning = ThresholdWarning(
        threshold_key="recycle_4",
        min_level=ScoreWarningLevel.BALANCED,
        event_type=ScoreEventType.RECYCLE_WASTE,
        current_count=4,
        penalty_points=-20,
        message_key="recycle_escalation"
    )
    
    msg = ScoreFormatter.format_threshold_warning(warning)
    assert "Penalità riciclo aumentata" in msg
    assert "meno 20 punti" in msg
```

### Integration Tests

**File**: `tests/integration/test_warning_system_integration.py`

```python
def test_stock_draw_warning_vocalizes_when_enabled(game_engine, mock_screenreader):
    """Stock draw warning vocalizes when level >= MINIMAL."""
    # Set warning level to MINIMAL
    game_engine.settings.score_warning_level = ScoreWarningLevel.MINIMAL
    
    # Draw 21 times
    for _ in range(21):
        game_engine._draw_from_stock()
    
    # Verify warning was spoken
    calls = mock_screenreader.speak.call_args_list
    warning_call = [c for c in calls if "penalità pesca" in str(c)]
    assert len(warning_call) > 0

def test_stock_draw_warning_silent_when_disabled(game_engine, mock_screenreader):
    """Stock draw warning NOT vocalized when level == DISABLED."""
    # Set warning level to DISABLED
    game_engine.settings.score_warning_level = ScoreWarningLevel.DISABLED
    
    # Draw 21 times
    for _ in range(21):
        game_engine._draw_from_stock()
    
    # Verify NO warning was spoken
    calls = mock_screenreader.speak.call_args_list
    warning_call = [c for c in calls if "penalità" in str(c)]
    assert len(warning_call) == 0
```

---

## Implementation Roadmap

### Commit Strategy (5 atomic commits)

#### Commit 1: Domain Models (Fase 1)

```bash
feat(domain): Add ThresholdWarning model and ScoreWarningLevel enum v2.6.0

- Add ThresholdWarning dataclass (frozen)
- ScoreWarningLevel enum already present (validate)
- Define threshold mapping table
- Add comprehensive docstrings

Files modified:
- src/domain/models/scoring.py (+60 lines)

Tests added:
- tests/unit/domain/models/test_scoring_warnings.py (8 tests)

Coverage: 100% on new code
```

#### Commit 2: ScoringService Warning Logic (Fase 2)

```bash
feat(domain): Implement threshold warning detection in ScoringService v2.6.0

- Add check_threshold_warning() method
- Implement _check_stock_draw_warning()
- Implement _check_recycle_warning()
- Add _emitted_warnings tracking (avoid duplicates)
- Update reset() to clear warning history

Files modified:
- src/domain/services/scoring_service.py (+120 lines)

Tests added:
- tests/unit/domain/services/test_scoring_service_warnings.py (12 tests)

Coverage: 95% on new code (boundary cases tested)
```

#### Commit 3: GameSettings Warning Level (Fase 3)

```bash
feat(domain): Add score warning level setting to GameSettings v2.6.0

- Add score_warning_level field (default BALANCED)
- Implement cycle_warning_level() method
- Implement get_warning_level_display() method
- Add Italian localization for level names

Files modified:
- src/domain/services/game_settings.py (+45 lines)

Tests added:
- tests/unit/domain/services/test_game_settings_warnings.py (8 tests)

Coverage: 100% on new code
```

#### Commit 4: Options Menu Integration (Fase 4)

```bash
feat(application): Add option 8 "Avvisi Malus" to options menu v2.6.0

- Update OptionsController for 9 options (was 8)
- Add _modify_warning_level() handler
- Update navigation (arrows, jump-to)
- Update read_all_settings() to include warning level
- Update snapshot save/restore
- Add OPTION_NAMES entry "Avvisi Malus"

Files modified:
- src/application/options_controller.py (+25 lines)
- src/presentation/options_formatter.py (+5 lines)

Tests added:
- tests/unit/application/test_options_controller_warnings.py (6 tests)

Coverage: 95% on modified code
```

#### Commit 5: GameEngine Integration + Formatters (Fase 5)

```bash
feat(application): Integrate threshold warnings into gameplay with TTS v2.6.0

- Update _draw_from_stock() with warning check + vocalization
- Update recyclewaste() with warning check + vocalization
- Add format_threshold_warning() to ScoreFormatter
- Add Italian message templates (6 templates)
- Use 300ms pause before warning (non-intrusive)

Files modified:
- src/application/game_engine.py (+30 lines)
- src/presentation/formatters/score_formatter.py (+55 lines)

Tests added:
- tests/unit/presentation/test_score_formatter_warnings.py (6 tests)
- tests/integration/test_warning_system_integration.py (8 tests)

Coverage: 90% on integration code (includes end-to-end flow)
```

### Timeline Estimate (Copilot Agent)

| Phase | Description | Files | LOC | Tests | Time Estimate |
|-------|-------------|-------|-----|-------|---------------|
| 1 | Domain Models | 1 | +60 | 8 | 30 min |
| 2 | ScoringService Logic | 1 | +120 | 12 | 60 min |
| 3 | GameSettings | 1 | +45 | 8 | 30 min |
| 4 | Options Menu | 2 | +30 | 6 | 45 min |
| 5 | GameEngine + Formatters | 2 | +85 | 14 | 75 min |
| **Total** | | **7 files** | **+340 LOC** | **48 tests** | **4.0 hours** |

### Testing Coverage Target

- **Unit tests**: 95% coverage su nuovo codice
- **Integration tests**: 85% coverage su flussi end-to-end
- **Total test count**: 48 test (35 unit + 13 integration)

---

## Acceptance Criteria

### Feature Funzionale

- [ ] Opzione 8 "Avvisi Malus" presente nel menu opzioni
- [ ] Ciclo attraverso 4 livelli: DISABLED → MINIMAL → BALANCED → COMPLETE
- [ ] Default BALANCED all'avvio per utenti nuovi
- [ ] Warning vocalizati in modo non intrusivo (300ms pause dopo messaggio mossa)
- [ ] Warning emessi UNA SOLA VOLTA per soglia (no duplicati)
- [ ] Livello DISABLED = nessun warning (silenzioso)
- [ ] Livello MINIMAL = solo prime penalità (draw 21, recycle 3)
- [ ] Livello BALANCED = prime penalità + escalation (draw 21, 41, recycle 3, 4)
- [ ] Livello COMPLETE = pre-warnings + tutte soglie (6 warnings totali)

### Testing e Qualità

- [ ] 48 test implementati (35 unit + 13 integration)
- [ ] Coverage ≥95% su domain layer
- [ ] Coverage ≥85% su application layer
- [ ] Zero breaking changes (backward compatible)
- [ ] Type hints completi su tutto nuovo codice
- [ ] Docstrings complete su tutti metodi pubblici

### Architettura

- [ ] Clean Architecture rispettata (Domain → Application → Presentation)
- [ ] Domain layer zero dipendenze esterne (scoring_service.py puro)
- [ ] Application layer controlla vocalization (game_engine.py)
- [ ] Presentation layer formatta messaggi (score_formatter.py)
- [ ] Nessuna violazione Dependency Rule

### Documentazione

- [ ] Questo piano implementativo completo salvato in `docs/`
- [ ] CHANGELOG.md aggiornato con sezione v2.6.0
- [ ] README.md aggiornato (se necessario) con descrizione feature
- [ ] Commit messages descrittivi con prefix `feat(layer):`
- [ ] Docstrings con esempi di utilizzo

---

## Breaking Changes

**Nessuno**. Feature completamente backward compatible:

- Default `ScoreWarningLevel.BALANCED` fornisce esperienza ragionevole
- Se utente non modifica opzione, warnings vocalizati come da default
- Livello DISABLED disponibile per veterani che non vogliono warnings
- Nessuna modifica a API esistenti (solo estensioni)

---

## Future Enhancements (v2.7+)

1. **Persistenza Livello Warning** in `settings.json`
2. **Configurazione Custom Soglie** (per utenti esperti)
3. **Warning Audio Cues** (suoni non verbali + TTS)
4. **Warning History Panel** (ultimi 10 warnings in finestra info)
5. **Per-Difficulty Soglie** (soglie diverse per livelli 1-5)

---

## Riferimenti Tecnici

### File da Modificare

1. `src/domain/models/scoring.py` - Aggiungere `ThresholdWarning` dataclass
2. `src/domain/services/scoring_service.py` - Implementare logica detection warnings
3. `src/domain/services/game_settings.py` - Aggiungere campo + metodi warning level
4. `src/application/options_controller.py` - Estendere a 9 opzioni + handler
5. `src/application/game_engine.py` - Integrare warning checks in draw/recycle
6. `src/presentation/formatters/score_formatter.py` - Aggiungere formatter warnings
7. `src/presentation/options_formatter.py` - Aggiungere "Avvisi Malus" a lista

### Dipendenze

- **Nessuna dipendenza esterna aggiunta**
- Usa solo librerie standard (enum, dataclasses, typing)
- Compatible con Python 3.10+

### Performance

- **Zero overhead quando DISABLED**: Solo check boolean `settings.score_warning_level`
- **O(1) warning detection**: Check diretto su count con hash set lookup
- **No memory leaks**: `_emitted_warnings` cleared on `reset()`

---

## Conclusione

Questo piano implementa il sistema di verbosità warnings malus mancante, completando il sistema di scoring v2.0 con feedback accessibile e configurabile per utenti non vedenti.

La feature è progettata con:
- **Clean Architecture** rigorosa
- **Test coverage** >90%
- **Backward compatibility** totale
- **Accessibilità** come priorità primaria
- **5 commit atomici** per tracciabilità

**Effort stimato**: 4 ore con Copilot Agent  
**Priorità**: ALTA (feature pianificata mancante)  
**Rischio**: BASSO (architettura consolidata, no breaking changes)

---

**Fine Piano Implementazione v2.6.0**
