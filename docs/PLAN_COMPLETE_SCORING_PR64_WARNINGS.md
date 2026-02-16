# Piano Implementazione: Completamento Scoring System v2.0
## Integrazione TTS Threshold Warnings + Bug Fix Critici

**Riferimento**: PR #64 - Sistema Scoring v2.0  
**Specifica**: `docs/SCORING_SYSTEM_V2.md`  
**Branch**: `refactoring-engine`  
**Data Pianificazione**: 16 Febbraio 2026  
**Versione Target**: v2.6.0

---

## 📋 Executive Summary

### Obiettivo
Completare l'implementazione del sistema scoring v2.0 con:
1. **Fix bug critici** nell'integrazione gameplay-scoring
2. **Sistema warnings graduati** per soglie penalità (accessibilità TTS)
3. **Retrocompatibilità** con score salvati v1.0

### Scope
- ✅ **Bug Fix CRITICO**: Registrazione eventi `STOCK_DRAW` (sistema penalità rotto)
- ✅ **Bug Fix OPZIONALE**: Tracking eventi `INVALID_MOVE` (statistiche future)
- ✅ **Feature Warnings**: 4 livelli graduati (DISABLED/MINIMAL/BALANCED/COMPLETE)
- ✅ **Retrocompat**: Gestione score legacy senza `victory_quality_multiplier`
- ✅ **Test Coverage**: Integration test end-to-end + unit test parametrici

### Effort Totale Stimato
**4-5 ore** distribuite in 5 fasi:
- Fase 0 (CRITICA): 30 minuti
- Fase 0.5 (OPZIONALE): 20 minuti
- Fasi 1-4 (FEATURE): 3-4 ore

### Priorità
🔴 **FASE 0** (MASSIMA) → Blocca funzionamento scoring v2.0  
🟡 **FASE 0.5** (MEDIA) → Nice-to-have per completezza  
⭐ **FASI 1-4** (ALTA) → Enhancement accessibilità

---

## 🐛 Analisi Bug Critici

### Bug #1: STOCK_DRAW Events Mai Registrati (CRITICO)

#### Problema
**File**: `src/domain/services/game_service.py` (metodo `draw_cards()`)

Il metodo `draw_cards()` incrementa correttamente `self.draw_count` (counter generico per statistiche), ma **NON registra mai** l'evento scoring `ScoreEventType.STOCK_DRAW` necessario per le penalità progressive.

**Codice Attuale** (linee 286-299):
```python
def draw_cards(self, count: int = 1) -> Tuple[bool, str, List[Card]]:
    # ... validazione ...
    
    # Draw cards
    drawn_cards: List[Card] = []
    for _ in range(min(count, stock.get_card_count())):
        card = stock.remove_last_card()
        if card:
            card.set_uncover()
            waste.aggiungi_carta(card)
            drawn_cards.append(card)
            # ❌ MANCA: self.scoring.record_event(ScoreEventType.STOCK_DRAW)
    
    self.draw_count += 1  # Solo statistiche, NON scoring
    return True, f"Pescate {len(drawn_cards)} carte", drawn_cards
```

#### Impact
- ⛔ **Sistema penalità progressive ROTTO**: Soglie 21/41 NON si attivano
- 📈 **Score inflated**: Giocatori che pescano 50+ volte NON ricevono penalità
- 🧪 **Test falsati**: Unit test `ScoringService` passano, integration test mancano
- 🏆 **Leaderboard compromessa**: Score non comparabili tra partite

#### Root Cause
Separazione responsabilità tra `draw_count` (statistiche) e `stock_draw_count` (scoring) senza collegamento nel flusso gameplay.

---

### Bug #2: INVALID_MOVE Events Non Tracciati (MINORE)

#### Problema
**File**: `src/domain/services/game_service.py` (metodo `move_card()`)

Quando una mossa fallisce validazione, il metodo ritorna `False` ma NON traccia l'evento `INVALID_MOVE` per statistiche future.

**Codice Attuale** (linee 149-158):
```python
# Validate move
if is_foundation_target:
    if not self.rules.can_place_on_foundation(card, target_pile):
        # ❌ MANCA: self.scoring.record_event(ScoreEventType.INVALID_MOVE)
        return False, "Mossa non valida per fondazione"
else:
    if not self.rules.can_place_on_tableau(card, target_pile):
        # ❌ MANCA: self.scoring.record_event(ScoreEventType.INVALID_MOVE)
        return False, "Mossa non valida per tableau"
```

#### Impact
- 📊 **Statistiche incomplete**: Impossibile tracciare mosse invalide per analytics
- 🔮 **Feature future bloccate**: v2.1+ potrebbero usare metric "efficienza mosse"
- ✅ **Nessun impact scoring v2.0**: Evento è `0pt`, tracking-only

---

## 🔧 FASE 0: Fix Critical Bug - STOCK_DRAW Event Registration

### Priorità: 🔴 MASSIMA (BLOCCA SCORING V2.0)

### File Modificato
`src/domain/services/game_service.py` - Metodo `draw_cards()`

### Implementazione

#### Opzione A: Record Per Carta (RACCOMANDATO)
Coerente con filosofia attuale dove `stock_draw_count` incrementa per ogni carta pescata.

```python
def draw_cards(self, count: int = 1) -> Tuple[bool, str, List[Card]]:
    """Draw cards from stock to waste pile.
    
    Args:
        count: Number of cards to draw (1 or 3)
        
    Returns:
        Tuple of (success, message, drawn_cards)
    """
    stock = self.table.pile_mazzo
    waste = self.table.pile_scarti
    
    if stock is None or waste is None:
        return False, "Pile tallone non inizializzate", []
    
    # Check if can draw
    if not self.rules.can_draw_from_stock(stock):
        if waste.is_empty():
            return False, "Tallone e scarti vuoti - impossibile pescare", []
        else:
            return False, "Tallone vuoto - riciclo automatico fallito", []
    
    # Draw cards
    drawn_cards: List[Card] = []
    for _ in range(min(count, stock.get_card_count())):
        card = stock.remove_last_card()
        if card:
            card.set_uncover()
            waste.aggiungi_carta(card)
            drawn_cards.append(card)
            
            # ✅ FIX v2.6.0: Record scoring event per ogni carta pescata
            if self.scoring:
                self.scoring.record_event(ScoreEventType.STOCK_DRAW)
    
    self.draw_count += 1  # Counter azioni pescata (statistiche legacy)
    return True, f"Pescate {len(drawn_cards)} carte", drawn_cards
```

#### Razionale Tecnico
1. **Coerenza con soglie spec**: Soglie 21/41 assumono conteggio "per carta"
   - Draw-1: 21 azioni = 21 carte ✅
   - Draw-3: 7 azioni = 21 carte ✅
   
2. **Semplicità implementazione**: Loop già itera per carta
   
3. **Backward compatible**: `self.draw_count` resta "per azione" (statistiche legacy non rompono)

### Test Integration (ROBUSTI - AGGIORNATI)

> **⚠️ TEST STRATEGY IMPROVEMENT**  
> I seguenti test usano **setup diretto su `GameService`** anziché `GameEngine.create()`
> per garantire **determinismo completo** ed evitare dipendenze da configurazioni esterne.
> 
> **Benefici**:
> - ✅ Controllo totale su `draw_count` parameter
> - ✅ Nessuna dipendenza da settings globali
> - ✅ Event filtering per test isolation perfetto

#### Test 1: Eventi Registrati Correttamente (DETERMINISTICO)
```python
def test_stock_draw_events_recorded_in_gameplay():
    """CRITICAL: Verify STOCK_DRAW events registered (deterministic setup).
    
    Uses GameService directly to avoid dependency on GameEngine config
    and ensure predictable draw behavior (1 card per call).
    
    This test catches the bug where draw_cards() increments draw_count
    but never calls scoring.record_event(ScoreEventType.STOCK_DRAW).
    """
    # Setup DIRETTO (no engine overhead)
    table = GameTable.create(deck_type="french")
    rules = SolitaireRules()
    scoring = ScoringService(
        deck_type="french",
        difficulty_level=1,
        draw_count=1  # Force 1-card draw for determinism
    )
    service = GameService(table, rules, scoring)
    service.start_game()
    
    # Verify stock has enough cards
    assert service.table.pile_mazzo.get_card_count() >= 25, \
        "Stock must have at least 25 cards for test"
    
    # Draw exactly 25 cards (1 per call)
    for i in range(25):
        success, msg, cards = service.draw_cards(count=1)
        assert success, f"Draw {i+1} failed: {msg}"
        assert len(cards) == 1, f"Expected 1 card, got {len(cards)}"
    
    # VERIFY: Exactly 25 events registered
    assert scoring.stock_draw_count == 25, \
        f"Expected 25 STOCK_DRAW events, got {scoring.stock_draw_count}"
    
    # VERIFY: Correct penalty via EVENT FILTERING (isolation)
    # This approach isolates STOCK_DRAW events from other events
    # like CARD_REVEALED that might affect base_score
    draw_events = [
        e for e in scoring.score_events 
        if e.event_type == ScoreEventType.STOCK_DRAW
    ]
    assert len(draw_events) == 25, "Event count mismatch"
    
    # Draw 1-20: 0pt, Draw 21-25: 5 × -1pt = -5pt
    draw_penalty = sum(e.points for e in draw_events)
    assert draw_penalty == -5, \
        f"Expected -5pt penalty (draw 21-25), got {draw_penalty}pt"
```

#### Test 2: Penalità Progressive (CON EVENT FILTERING)
```python
def test_stock_draw_penalties_progression():
    """Verify progressive penalties: 1-20 free, 21-40 = -1pt, 41+ = -2pt.
    
    Uses event filtering for robust assertion that doesn't depend
    on other scoring events that might occur during gameplay.
    """
    # Setup diretto
    table = GameTable.create(deck_type="french")
    rules = SolitaireRules()
    scoring = ScoringService(
        deck_type="french",
        difficulty_level=1,
        draw_count=1  # Deterministic: 1 card per call
    )
    service = GameService(table, rules, scoring)
    service.start_game()
    
    # Verify stock has enough cards
    assert service.table.pile_mazzo.get_card_count() >= 45
    
    # Draw 45 cards (1 per call)
    for i in range(45):
        success, msg, cards = service.draw_cards(count=1)
        assert success, f"Draw {i+1} failed: {msg}"
        assert len(cards) == 1
    
    # VERIFY: Event filtering (robust, isolated from other events)
    draw_events = [
        e for e in scoring.score_events
        if e.event_type == ScoreEventType.STOCK_DRAW
    ]
    assert len(draw_events) == 45, \
        f"Expected 45 STOCK_DRAW events, got {len(draw_events)}"
    
    # Expected penalties:
    # - Draw 1-20: 0pt (20 cards)
    # - Draw 21-40: -1pt × 20 = -20pt
    # - Draw 41-45: -2pt × 5 = -10pt
    # Total: -30pt
    total_penalty = sum(e.points for e in draw_events)
    assert total_penalty == -30, \
        f"Expected -30pt total penalty, got {total_penalty}pt"
```

#### Test 3: Draw-3 Coerenza (Conteggio Per Carta)
```python
def test_stock_draw_penalties_with_draw3():
    """Verify penalties count per-card, not per-action with draw-3."""
    # Setup con draw-3
    table = GameTable.create(deck_type="french")
    rules = SolitaireRules()
    scoring = ScoringService(
        deck_type="french",
        difficulty_level=1,
        draw_count=3  # Draw-3 mode
    )
    service = GameService(table, rules, scoring)
    service.start_game()
    
    # Draw 7 actions × 3 cards = 21 cards total
    for _ in range(7):
        service.draw_cards(count=3)
    
    # VERIFY: Exactly 21 events (not 7 actions)
    assert scoring.stock_draw_count == 21, \
        f"Expected 21 events (per-card), got {scoring.stock_draw_count}"
    
    # VERIFY: Penalties start at card 21 (not action 21)
    draw_events = [
        e for e in scoring.score_events
        if e.event_type == ScoreEventType.STOCK_DRAW
    ]
    
    # Only 21st card has penalty (not cards 1-20)
    penalties = [e.points for e in draw_events]
    assert penalties[:20] == [0] * 20, "First 20 draws should be free"
    assert penalties[20] == -1, "21st draw should have -1pt penalty"
```

### Effort: 30 minuti
- Codice: 5 minuti (1 linea + guard)
- Test: 20 minuti (3 test robusti)
- Review: 5 minuti

---

## 🔍 FASE 0.5: Track INVALID_MOVE Events

### Priorità: 🟡 MEDIA (NICE-TO-HAVE)

### File Modificato
`src/domain/services/game_service.py` - Metodo `move_card()`

### Implementazione

Aggiungi tracking in **3 punti di validazione**:

#### 1. Foundation Validation Failure
```python
# Validate move
if is_foundation_target:
    if not self.rules.can_place_on_foundation(card, target_pile):
        # ✅ NEW v2.6.0: Track invalid moves per statistiche
        if self.scoring:
            self.scoring.record_event(ScoreEventType.INVALID_MOVE)
        return False, "Mossa non valida per fondazione"
```

#### 2. Tableau Validation Failure
```python
else:
    if not self.rules.can_place_on_tableau(card, target_pile):
        # ✅ NEW v2.6.0: Track invalid moves per statistiche
        if self.scoring:
            self.scoring.record_event(ScoreEventType.INVALID_MOVE)
        return False, "Mossa non valida per tableau"
```

#### 3. Sequence Validation Failure
```python
# Validate sequence move
if not self.rules.can_move_sequence(cards, target_pile):
    # ✅ NEW v2.6.0: Track invalid sequence move
    if self.scoring:
        self.scoring.record_event(ScoreEventType.INVALID_MOVE)
    return False, "Sequenza non può essere spostata"
```

### Test
```python
def test_invalid_moves_tracked():
    """Verify INVALID_MOVE events tracked for future statistics."""
    # Setup
    engine = GameEngine.create(scoring_enabled=True)
    engine.new_game()
    
    # Force invalid move scenario
    # (Implementation details depend on table setup)
    source = engine.service.table.pile_base[0]
    target = engine.service.table.pile_semi[0]
    
    # Attempt invalid move
    success, msg = engine.service.move_card(source, target, is_foundation_target=True)
    assert not success, "Move should fail validation"
    
    # VERIFY: Event tracked
    events = engine.service.scoring.score_events
    invalid_events = [e for e in events if e.event_type == ScoreEventType.INVALID_MOVE]
    assert len(invalid_events) >= 1, "INVALID_MOVE event not tracked"
```

### Effort: 20 minuti
- Codice: 5 minuti (3 righe)
- Test: 10 minuti (1 test)
- Review: 5 minuti

---

## ⭐ FASE 1: Extend GameSettings - Livelli Warnings Graduati

### Priorità: ⭐ ALTA (FEATURE CORE)

### File Modificati
1. `src/domain/models/scoring.py` (nuovo enum)
2. `src/domain/services/game_settings.py` (campo + metodi)

### Implementazione

#### 1. Crea Enum Livelli Warning
**File**: `src/domain/models/scoring.py` (dopo classe `FinalScore`)

```python
from enum import IntEnum

class ScoreWarningLevel(IntEnum):
    """Livelli di verbosità warnings soglie scoring.
    
    Controlla quanti avvisi TTS vengono emessi quando il giocatore
    supera soglie di penalità (stock draw, recycle).
    
    I livelli progressivi permettono a principianti di ricevere
    guida completa e a veterani di minimizzare interruzioni.
    
    Attributes:
        DISABLED: Nessun warning (0)
        MINIMAL: Solo transizioni 0pt → penalità (1)
        BALANCED: Transizioni + escalation significative (2, default)
        COMPLETE: Pre-warnings + tutte le transizioni (3)
    
    Example:
        >>> settings.score_warning_level = ScoreWarningLevel.BALANCED
        >>> settings.is_warning_enabled_for(21)  # True (soglia critica)
    
    Version: v2.6.0
    """
    DISABLED = 0      # Nessun warning
    MINIMAL = 1       # Solo transizioni 0pt → penalità
    BALANCED = 2      # Transizioni + escalation (DEFAULT)
    COMPLETE = 3      # Pre-warnings + tutte transizioni
```

#### 2. Aggiungi Campo in GameSettings
**File**: `src/domain/services/game_settings.py` (nel `__init__`)

```python
from src.domain.models.scoring import ScoreWarningLevel

def __init__(self, game_state=None):
    # ... campi esistenti ...
    
    # Feature v2.6.0: Score warning level (graduated)
    self.score_warning_level = ScoreWarningLevel.BALANCED  # Default
```

#### 3. Metodo Cycle Livelli
**File**: `src/domain/services/game_settings.py`

```python
def cycle_score_warning_level(self) -> Tuple[bool, str]:
    """Cycle through score warning levels.
    
    Sequence: DISABLED → MINIMAL → BALANCED → COMPLETE → DISABLED
    
    Levels:
    - DISABLED: Nessun warning (silenzioso)
    - MINIMAL: Solo transizioni 0pt→penalità (veterani)
    - BALANCED: Transizioni + escalation (default, casual)
    - COMPLETE: Pre-warnings + tutte soglie (principianti)
    
    Cannot be changed during active game for consistency.
    
    Returns:
        Tuple[bool, str]: (success, message with level description)
        
    Examples:
        >>> settings.score_warning_level = ScoreWarningLevel.BALANCED
        >>> settings.cycle_score_warning_level()
        (True, "Avvisi soglie punteggio: Completi (principianti).")
    
    Version: v2.6.0
    """
    if not self.validate_not_running():
        return (False, "Non puoi modificare questa opzione durante una partita!")
    
    # Store old value for logging
    old_value = self.score_warning_level
    
    # Cycle: 0 → 1 → 2 → 3 → 0
    self.score_warning_level = ScoreWarningLevel((self.score_warning_level + 1) % 4)
    
    # Log change
    log.settings_changed(
        "score_warning_level",
        old_value.name,
        self.score_warning_level.name
    )
    
    # Human-readable message for TTS
    level_names = {
        ScoreWarningLevel.DISABLED: "Disattivati",
        ScoreWarningLevel.MINIMAL: "Minimi (veterani)",
        ScoreWarningLevel.BALANCED: "Equilibrati (default)",
        ScoreWarningLevel.COMPLETE: "Completi (principianti)"
    }
    
    level_name = level_names[self.score_warning_level]
    return (True, f"Avvisi soglie punteggio: {level_name}.")
```

#### 4. Display Method
```python
def get_score_warning_level_display(self) -> str:
    """Get human-readable warning level for options display.
    
    Returns:
        Short description of current level
        
    Examples:
        >>> settings.score_warning_level = ScoreWarningLevel.BALANCED
        >>> settings.get_score_warning_level_display()
        "Equilibrati"
    """
    level_names = {
        ScoreWarningLevel.DISABLED: "Disattivati",
        ScoreWarningLevel.MINIMAL: "Minimi",
        ScoreWarningLevel.BALANCED: "Equilibrati",
        ScoreWarningLevel.COMPLETE: "Completi"
    }
    return level_names.get(self.score_warning_level, "Sconosciuto")
```

### Mapping Soglie per Livello

| Livello | Draw 20 | Draw 21 | Draw 41 | Recycle 3 | Recycle 4 | Recycle 5 |
|---------|---------|---------|---------|-----------|-----------|-----------|
| **DISABLED** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **MINIMAL** | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **BALANCED** | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **COMPLETE** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Effort: 1 ora
- Enum: 10 minuti
- Campo + metodi: 30 minuti
- Docstring: 20 minuti

---

## 🎯 FASE 2: Integrate Warnings in GameEngine

### Priorità: ⭐ ALTA (FEATURE CORE)

### File Modificato
`src/application/game_engine.py` - Metodi `draw_from_stock()` e `recycle_waste()`

### Implementazione

#### A. Warnings in `draw_from_stock()`
**Posizione**: Dopo `self.service.draw_cards(count)`, prima del `return`

```python
def draw_from_stock(self, count: int = None) -> Tuple[bool, str]:
    """Draw cards from stock to waste.
    
    Args:
        count: Number of cards (None = use settings draw_count)
        
    Returns:
        Tuple of (success, message)
    """
    # ... codice esistente ...
    
    success, generic_msg, cards = self.service.draw_cards(count)
    
    if not success:
        return success, generic_msg
    
    # ✅ NEW v2.6.0: TTS threshold warnings (graduated)
    if self.settings and self.settings.scoring_enabled and self.service.scoring:
        self._announce_draw_threshold_warning()
    
    # ... resto codice (auto-draw, etc) ...
    
    return success, message

def _announce_draw_threshold_warning(self) -> None:
    """Announce threshold warning for stock draw based on warning level.
    
    Called after successful draw to check if a scoring threshold
    has been crossed and announce warning to user via TTS.
    
    Warnings depend on score_warning_level setting:
    - DISABLED: No warnings
    - MINIMAL: Warning at 21 (first penalty)
    - BALANCED: Warning at 21 and 41 (escalation)
    - COMPLETE: Warning at 20 (pre), 21, and 41
    
    Version: v2.6.0
    """
    level = self.settings.score_warning_level
    
    # Early exit if disabled
    if level == ScoreWarningLevel.DISABLED:
        return
    
    draw_count = self.service.scoring.stock_draw_count
    warning = None
    
    # COMPLETE level: Pre-warning at 20 (last free draw)
    if level == ScoreWarningLevel.COMPLETE and draw_count == 20:
        warning = (
            "Ultima pescata gratuita. "
            "Dal prossimo draw penalità -1 punto per pescata."
        )
    
    # ALL levels (MINIMAL, BALANCED, COMPLETE): Warning at 21 (first penalty)
    elif draw_count == 21:
        from src.presentation.formatters.score_formatter import ScoreFormatter
        warning = ScoreFormatter.format_threshold_warning(
            "stock_draw", 21, 20, -1
        )
    
    # BALANCED and COMPLETE: Warning at 41 (penalty doubles)
    elif level >= ScoreWarningLevel.BALANCED and draw_count == 41:
        from src.presentation.formatters.score_formatter import ScoreFormatter
        warning = ScoreFormatter.format_threshold_warning(
            "stock_draw", 41, 40, -2
        )
    
    # Announce warning if any
    if warning and self.screen_reader:
        self.screen_reader.tts.speak(warning, interrupt=False)
```

#### B. Warnings in `recycle_waste()`
**Posizione**: Dopo `self.service.recycle_waste(shuffle)`, prima dell'auto-draw

```python
def recycle_waste(self, shuffle: bool = None) -> Tuple[bool, str]:
    """Recycle waste pile back to stock.
    
    Args:
        shuffle: Override shuffle mode (None = use settings)
        
    Returns:
        Tuple of (success, message)
    """
    # ... codice esistente ...
    
    success, message = self.service.recycle_waste(shuffle_mode)
    
    if not success:
        return success, message
    
    # ✅ NEW v2.6.0: TTS threshold warning for recycle
    if self.settings and self.settings.scoring_enabled and self.service.scoring:
        self._announce_recycle_threshold_warning()
    
    # ... resto codice (auto-draw) ...
    
    return success, message

def _announce_recycle_threshold_warning(self) -> None:
    """Announce threshold warning for waste recycle based on warning level.
    
    Called after successful recycle to check if a scoring threshold
    has been crossed and announce warning to user via TTS.
    
    Warnings depend on score_warning_level setting:
    - DISABLED: No warnings
    - MINIMAL: Warning at 3rd recycle (first penalty)
    - BALANCED: Warning at 3rd recycle
    - COMPLETE: Warning at 3rd, 4th, and 5th recycle
    
    Version: v2.6.0
    """
    level = self.settings.score_warning_level
    
    # Early exit if disabled
    if level == ScoreWarningLevel.DISABLED:
        return
    
    recycle_count = self.service.scoring.recycle_count
    warning = None
    
    # ALL levels: Warning at 3rd recycle (first penalty)
    if recycle_count == 3:
        from src.presentation.formatters.score_formatter import ScoreFormatter
        warning = ScoreFormatter.format_threshold_warning(
            "recycle", 3, 2, -10
        )
    
    # COMPLETE level: Warning at 4th recycle (penalty doubles)
    elif level == ScoreWarningLevel.COMPLETE and recycle_count == 4:
        warning = "Attenzione: quarto riciclo. Penalità totale -20 punti."
    
    # COMPLETE level: Warning at 5th recycle (acceleration)
    elif level == ScoreWarningLevel.COMPLETE and recycle_count == 5:
        warning = (
            "Attenzione: quinto riciclo. "
            "Penalità totale -35 punti. Crescita rapida."
        )
    
    # Announce warning if any
    if warning and self.screen_reader:
        self.screen_reader.tts.speak(warning, interrupt=False)
```

### Effort: 1 ora
- Metodi helper: 30 minuti
- Integration: 20 minuti
- Testing: 10 minuti

---

## ✅ FASE 3: Retrocompatibilità ScoreStorage

### Priorità: ✅ MEDIA

### File Modificato
`src/infrastructure/storage/score_storage.py` - Metodo `load_all_scores()`

### Implementazione

```python
def load_all_scores(self) -> List[Dict[str, Any]]:
    """Load all scores from storage.
    
    Returns:
        List of score dictionaries, empty list if file doesn't exist
        
    v2.6.0: Added backward compatibility for v1.0 scores.
    """
    try:
        if not self.storage_path.exists():
            log.warning_issued(
                "ScoreStorage",
                f"File not found: {self.storage_path}, returning empty list"
            )
            return []
        
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            scores = json.load(f)
        
        # ✅ NEW v2.6.0: Backward compatibility for legacy scores
        # Old v1.0 scores don't have victory_quality_multiplier
        if isinstance(scores, list):
            for score_dict in scores:
                # Sentinel value -1.0 indicates legacy score
                score_dict.setdefault("victory_quality_multiplier", -1.0)
                score_dict.setdefault("scoring_system_version", "1.0")
        
        # Log successful load
        log.info_query_requested(
            "score_load",
            f"Statistics loaded from {self.storage_path}"
        )
        
        return scores if isinstance(scores, list) else []
    
    except json.JSONDecodeError as e:
        log.error_occurred(
            "ScoreStorage",
            f"Corrupted file: {self.storage_path}",
            e
        )
        return []
    
    except Exception as e:
        log.error_occurred(
            "ScoreStorage",
            f"Unexpected error loading {self.storage_path}",
            e
        )
        return []
```

### Effort: 15 minuti

---

## 🧪 FASE 4: Test Coverage Completo

### Priorità: ✅ ALTA

### File Modificato
`tests/application/test_game_engine.py`

### Test Suite

> **⚠️ CRITICAL: Deterministic Test Setup**  
> I seguenti test parametrici **devono forzare `draw_count=1`** nel setup per garantire
> threshold crossing prevedibile. Con draw-3, le soglie si raggiungono a conteggi azione
> non deterministici (es: 7 azioni = 21 carte, ma warnings potrebbero emettere a momenti diversi).
> 
> **Best Practice**: Usa sempre `draw_count=1` nei test warnings per reprodicibilità.

#### Test 1: Warnings per Livello (Parametrico, DETERMINISTICO)
```python
import pytest
from src.domain.models.scoring import ScoreWarningLevel

@pytest.mark.parametrize("level,expected_warnings", [
    (ScoreWarningLevel.DISABLED, 0),
    (ScoreWarningLevel.MINIMAL, 1),    # Solo draw 21
    (ScoreWarningLevel.BALANCED, 2),   # Draw 21 + 41
    (ScoreWarningLevel.COMPLETE, 3),   # Draw 20 + 21 + 41
])
def test_stock_draw_warnings_per_level(level, expected_warnings):
    """Verify correct warnings per level (deterministic setup).
    
    CRITICAL: Uses draw_count=1 to ensure predictable threshold crossing.
    With draw-3, thresholds occur at unpredictable action counts.
    """
    # Setup con draw_count=1 FORZATO per determinismo
    engine = GameEngine.create(
        scoring_enabled=True,
        draw_count=1  # 👈 CRITICO: 1 azione = 1 carta = soglie prevedibili
    )
    engine.new_game()
    engine.settings.score_warning_level = level
    
    # Draw esattamente 45 volte (azioni = carte con draw-1)
    for _ in range(45):
        engine.draw_from_stock()
    
    # Count warnings (robust filtering)
    warning_calls = [
        call for call in engine.screen_reader.tts.speak.call_args_list
        if any(kw in call[0][0].lower() 
               for kw in ["soglia", "penalità", "ultima pescata", "gratuita"])
    ]
    
    assert len(warning_calls) == expected_warnings, \
        f"Level {level.name}: expected {expected_warnings} warnings, " \
        f"got {len(warning_calls)}"
```

#### Test 2: Recycle Warnings per Livello
```python
@pytest.mark.parametrize("level,expected_warnings", [
    (ScoreWarningLevel.DISABLED, 0),
    (ScoreWarningLevel.MINIMAL, 1),    # Solo recycle 3
    (ScoreWarningLevel.BALANCED, 1),   # Solo recycle 3
    (ScoreWarningLevel.COMPLETE, 3),   # Recycle 3 + 4 + 5
])
def test_recycle_warnings_per_level(mock_engine, level, expected_warnings):
    """Verify correct number of warnings per level during 6 recycles."""
    # Setup
    mock_engine.settings.score_warning_level = level
    mock_engine.settings.scoring_enabled = True
    
    # Simula 6 ricicli
    for _ in range(6):
        mock_engine.recycle_waste()
    
    # Count warnings
    warning_calls = [
        call for call in mock_engine.screen_reader.tts.speak.call_args_list
        if "riciclo" in call[0][0].lower()
    ]
    
    assert len(warning_calls) == expected_warnings, \
        f"Level {level.name}: expected {expected_warnings} warnings, " \
        f"got {len(warning_calls)}"
```

#### Test 3: Warning Disabilitati Quando Scoring OFF
```python
def test_no_warnings_when_scoring_disabled(mock_engine):
    """Verify no warnings announced when scoring system is disabled."""
    # Setup
    mock_engine.settings.score_warning_level = ScoreWarningLevel.COMPLETE
    mock_engine.settings.scoring_enabled = False  # 👈 Scoring OFF
    
    # Simula 45 draw (supererebbe soglie se scoring attivo)
    for _ in range(45):
        mock_engine.draw_from_stock()
    
    # Verify NESSUN warning
    warning_calls = [
        call for call in mock_engine.screen_reader.tts.speak.call_args_list
        if "soglia" in call[0][0].lower()
    ]
    
    assert len(warning_calls) == 0, \
        "No warnings should be announced when scoring is disabled"
```

#### Test 4: Cycle Score Warning Level
```python
def test_cycle_score_warning_level():
    """Verify cycling through all warning levels."""
    settings = GameSettings()
    
    # Default is BALANCED
    assert settings.score_warning_level == ScoreWarningLevel.BALANCED
    
    # Cycle: BALANCED → COMPLETE
    success, msg = settings.cycle_score_warning_level()
    assert success
    assert settings.score_warning_level == ScoreWarningLevel.COMPLETE
    assert "Completi" in msg
    
    # Cycle: COMPLETE → DISABLED
    success, msg = settings.cycle_score_warning_level()
    assert success
    assert settings.score_warning_level == ScoreWarningLevel.DISABLED
    assert "Disattivati" in msg
    
    # Cycle: DISABLED → MINIMAL
    success, msg = settings.cycle_score_warning_level()
    assert success
    assert settings.score_warning_level == ScoreWarningLevel.MINIMAL
    
    # Cycle: MINIMAL → BALANCED (loop completo)
    success, msg = settings.cycle_score_warning_level()
    assert success
    assert settings.score_warning_level == ScoreWarningLevel.BALANCED
```

### Effort: 1 ora

---

## 📚 Test Strategy Best Practices

### Rationale: Direct GameService Setup

**Problema**: Test su `GameEngine.create()` possono avere:
- Dipendenze da configurazioni esterne (settings globali)
- Comportamento draw-3 non deterministico
- Side-effects da componenti non coinvolte

**Soluzione**: Setup diretto su `GameService`:
```python
# ✅ ROBUSTO
table = GameTable.create(deck_type="french")
rules = SolitaireRules()
scoring = ScoringService(deck_type="french", difficulty_level=1, draw_count=1)
service = GameService(table, rules, scoring)
```

**Benefici**:
- ✅ Controllo totale su `draw_count`
- ✅ Zero dipendenze esterne
- ✅ Reprodicibilità 100%

---

### Rationale: Event Filtering per Assertions

**Problema**: `provisional.base_score` include TUTTI gli eventi:
```python
# ⚠️ FRAGILE: altri eventi contaminano assertion
assert provisional.base_score == -5  # Cosa se CARD_REVEALED aggiunge punti?
```

**Soluzione**: Filtra eventi specifici:
```python
# ✅ ROBUSTO: isolation completo
draw_events = [e for e in scoring.score_events if e.event_type == ScoreEventType.STOCK_DRAW]
draw_penalty = sum(e.points for e in draw_events)
assert draw_penalty == -5
```

**Benefici**:
- ✅ Test isolation perfetto
- ✅ No false positives/negatives
- ✅ Verifica doppia (count + sum)

---

### Rationale: Forzare draw_count=1 nei Test Warnings

**Problema**: Con draw-3, le soglie si raggiungono a conteggi azione variabili:
```python
# ⚠️ NON DETERMINISTICO con draw-3
for _ in range(7):  # 7 azioni × 3 carte = 21 carte
    engine.draw_from_stock()  # Warning potrebbe emettere a iterazione 7 o prima
```

**Soluzione**: Forzare draw-1 nei test:
```python
# ✅ DETERMINISTICO
engine = GameEngine.create(draw_count=1)  # 1 azione = 1 carta
for _ in range(45):  # Soglia 21 esattamente a iterazione 21
    engine.draw_from_stock()
```

**Benefici**:
- ✅ Threshold crossing prevedibile
- ✅ Warning count esatto
- ✅ Reprodicibilità garantita

---

## ✅ Success Criteria

### Acceptance Criteria

#### Bug Fixes (Fase 0 + 0.5)
- [ ] `STOCK_DRAW` eventi registrati correttamente durante gameplay
- [ ] Penalità progressive 21/41 si applicano come da spec
- [ ] Test integration end-to-end passano al 100%
- [ ] `INVALID_MOVE` eventi tracciati in tutti i punti validazione

#### Feature Warnings (Fasi 1-4)
- [ ] Enum `ScoreWarningLevel` implementato con 4 livelli
- [ ] `cycle_score_warning_level()` metodo funzionante
- [ ] Warnings annunciati correttamente per ogni livello:
  - DISABLED: 0 warnings
  - MINIMAL: Draw 21, Recycle 3
  - BALANCED: Draw 21/41, Recycle 3
  - COMPLETE: Draw 20/21/41, Recycle 3/4/5
- [ ] Test parametrici coprono tutti i livelli
- [ ] Retrocompatibilità score legacy verificata

### Non-Functional Requirements
- [ ] Nessun breaking change in API esistenti
- [ ] Backward compatible al 100%
- [ ] Performance: warnings NON impattano framerate (async TTS)
- [ ] Accessibilità: TTS chiaro e non interrompibile
- [ ] Code coverage: >90% su nuovo codice

### Validation Tests
```bash
# Run all tests
pytest tests/ -v

# Run only scoring tests
pytest tests/domain/test_scoring_service.py -v
pytest tests/application/test_game_engine.py::test_stock_draw -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

---

## 📊 Risk Assessment

### Rischi Tecnici

| Rischio | Probabilità | Impact | Mitigazione |
|---------|-------------|--------|-------------|
| Test integration complessi | MEDIA | ALTA | Setup diretto GameService (FASE 0) |
| TTS annunci ripetitivi | BASSA | MEDIA | Default BALANCED (3 warnings max) |
| Retrocompat score legacy | BASSA | ALTA | Sentinel `-1.0` + `.setdefault()` |
| Performance warnings | MOLTO BASSA | BASSA | TTS async, no blocking |
| Draw-3 test non deterministici | MEDIA | ALTA | Forzare draw_count=1 (FASE 4) |

### Rollback Plan
Se Fase 0 (STOCK_DRAW fix) introduce regression:
1. Revert commit specifico
2. Mantieni Fasi 1-4 (warnings indipendenti)
3. Fix bug in feature branch separato

---

## 📝 Commit Strategy

### Commit Structure (Conventional Commits)

```
FASE 0:
fix(scoring): register STOCK_DRAW events in draw_cards gameplay
- Add scoring.record_event() in draw loop
- Fix progressive penalties 21/41 not applying
- Add robust integration tests with direct GameService setup
- Use event filtering for test isolation
BREAKING: None
Closes: #BUG-STOCK-DRAW

FASE 0.5:
feat(scoring): track INVALID_MOVE events for statistics
- Add event tracking in move validation failures
- Enable future analytics on move efficiency
- Add test for invalid move tracking
Closes: #FEATURE-INVALID-TRACKING

FASE 1:
feat(settings): add graduated score warning levels system
- Add ScoreWarningLevel enum (DISABLED/MINIMAL/BALANCED/COMPLETE)
- Add cycle_score_warning_level() method
- Update GameSettings with new field
Closes: #FEATURE-WARNING-LEVELS

FASE 2:
feat(engine): integrate TTS threshold warnings with levels
- Add _announce_draw_threshold_warning() helper
- Add _announce_recycle_threshold_warning() helper
- Implement level-aware warning logic
Closes: #FEATURE-WARNING-INTEGRATION

FASE 3:
fix(storage): add backward compatibility for v1.0 scores
- Handle missing victory_quality_multiplier field
- Add sentinel -1.0 for legacy scores
- Prevent KeyError on load_all_scores()
Closes: #FIX-RETROCOMPAT

FASE 4:
test(scoring): add comprehensive test coverage for warnings
- Add parametric tests for all warning levels
- Force draw_count=1 for deterministic threshold crossing
- Add integration tests for bug fixes with event filtering
- Achieve >90% coverage on new code
Closes: #TEST-COVERAGE
```

---

## 🚀 Next Steps

### Immediate Actions
1. ✅ Review piano con team/stakeholder
2. ✅ Conferma priorità Fase 0 (CRITICA)
3. ✅ Setup branch: `feature/scoring-warnings-complete`
4. ✅ Implementa Fase 0 (30 min)
5. ✅ Run test suite completo
6. ✅ Procedi con Fasi 1-4 se Fase 0 passa

### Post-Implementation
- [ ] Update CHANGELOG.md con v2.6.0 features
- [ ] Update user documentation (warnings levels)
- [ ] Add migration guide per vecchi score
- [ ] Performance profiling (TTS overhead)

---

## 📚 References

### Documentazione Correlata
- `docs/SCORING_SYSTEM_V2.md` - Specifica completa sistema scoring
- `docs/TEMPLATE_IMPLEMENTATION_PLAN.md` - Template usato per questo piano
- `docs/OPTIONS_WINDOW_ROADMAP.md` - Context opzioni accessibilità

### Pull Request Correlate
- PR #64 - Scoring System v2.0 (PARTE 1)
- PR #XX - Questo piano (PARTE 2 - FINALE)

### Issues Risolte
- Bug: STOCK_DRAW events not registered
- Bug: INVALID_MOVE events not tracked
- Feature: Graduated warning levels system

---

**Piano approvato da**: [TBD]  
**Data approvazione**: 16 Febbraio 2026  
**Implementazione start**: [TBD]  
**Target completion**: [TBD]
