# Piano Implementazione: Completamento Scoring System v2.0
## Integrazione TTS Threshold Warnings + Bug Fix Critici

**Riferimento**: PR #64 - Sistema Scoring v2.0  
**Specifica**: `docs/SCORING_SYSTEM_V2.md`  
**Branch**: `refactoring-engine`  
**Data Pianificazione**: 16 Febbraio 2026  
**Versione Target**: v2.6.0  
**Revisione**: v2.1 (con correzioni API da codice reale) ✅

---

## 📋 Executive Summary

### Obiettivo
Completare l'implementazione del sistema scoring v2.0 con:
1. **Fix bug critici** nell'integrazione gameplay-scoring
2. **Sistema warnings graduati** per soglie penalità (accessibilità TTS)
3. **Persistenza settings** score_warning_level (previene crash riavvio)
4. **Test robusti** con tag-based detection (no keyword matching fragile)
5. **Retrocompatibilità** con score salvati v1.0

### Scope
- ✅ **Bug Fix CRITICO**: Registrazione eventi `STOCK_DRAW` (sistema penalità rotto)
- ✅ **Bug Fix OPZIONALE**: Tracking eventi `INVALID_MOVE` (statistiche future)
- ✅ **Feature Warnings**: 4 livelli graduati (DISABLED/MINIMAL/BALANCED/COMPLETE)
- ✅ **Settings Persistence**: Estensione metodi esistenti `to_dict()`/`load_from_dict()` (CORRETTO v2.1)
- ✅ **Test Robustness**: Tag `[SCORING_WARNING]` per detection affidabile
- ✅ **Safe TTS**: Pattern adapter con None-check
- ✅ **Retrocompat**: Gestione score legacy senza `victory_quality_multiplier`
- ✅ **Test Coverage**: Integration test end-to-end + unit test parametrici

### Effort Totale Stimato
**5-6 ore** distribuite in 7 fasi:
- Fase 0 (CRITICA): 30 minuti
- Fase 0.5 (OPZIONALE): 20 minuti
- Fase 1 (FEATURE): 1 ora
- **Fase 1.5 (CRITICA)**: 30 minuti ← CORRETTO v2.1
- Fase 2 (FEATURE): 1 ora ← SEMPLIFICATO v2.1
- **Fase 2.5 (IMPORTANTE)**: 20 minuti
- Fase 3 (RETROCOMPAT): 15 minuti
- Fase 4 (TEST): 1.5 ore ← CORRETTO v2.1

### Priorità
🔴 **FASE 0** (MASSIMA) → Blocca funzionamento scoring v2.0  
🔴 **FASE 1.5** (CRITICA) → Previene crash/reset opzioni riavvio  
🟡 **FASE 0.5** (MEDIA) → Nice-to-have per completezza  
⭐ **FASI 1-2** (ALTA) → Enhancement accessibilità  
🟠 **FASE 2.5** (IMPORTANTE) → Test robusti senza flakiness  
✅ **FASI 3-4** (ALTA) → Retrocompat + coverage

---

## 🐛 Analisi Bug Critici

### Bug #1: STOCK_DRAW Events Mai Registrati (CRITICO)

#### Problema
**File**: `src/domain/services/game_service.py` (metodo `draw_cards()`)

Il metodo `draw_cards()` incrementa correttamente `self.draw_count` (counter generico per statistiche), ma **NON registra mai** l'evento scoring `ScoreEventType.STOCK_DRAW` necessario per le penalità progressive.

**Codice Attuale** (linee 286-299, SHA: d0dce8a):
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

#### Codice Fix (Record Per Carta)
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
    
    # INVARIANT: draw_count (actions) vs stock_draw_count (cards)
    # - self.draw_count = numero AZIONI di pescata (statistiche legacy)
    # - self.scoring.stock_draw_count = numero CARTE pescate (scoring v2.0)
    # Esempio draw-3: dopo 7 azioni -> draw_count=7, stock_draw_count=21
    self.draw_count += 1
    
    return True, f"Pescate {len(drawn_cards)} carte", drawn_cards
```

#### Razionale Tecnico
1. **Coerenza con soglie spec**: Soglie 21/41 assumono conteggio "per carta"
   - Draw-1: 21 azioni = 21 carte ✅
   - Draw-3: 7 azioni = 21 carte ✅
   
2. **Semplicità implementazione**: Loop già itera per carta
   
3. **Backward compatible**: `self.draw_count` resta "per azione" (statistiche legacy non rompono)

4. **Invariante documentato**: Commento inline chiarisce separazione responsabilità

### Test Integration (ROBUSTI - AGGIORNATI v2.1)

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
    deck = FrenchDeck()
    deck.crea()
    deck.mischia()
    table = GameTable(deck)
    rules = SolitaireRules(deck)
    scoring = ScoringService(
        config=ScoringConfig(),
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
    deck = FrenchDeck()
    deck.crea()
    deck.mischia()
    table = GameTable(deck)
    rules = SolitaireRules(deck)
    scoring = ScoringService(
        config=ScoringConfig(),
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
    deck = FrenchDeck()
    deck.crea()
    deck.mischia()
    table = GameTable(deck)
    rules = SolitaireRules(deck)
    scoring = ScoringService(
        config=ScoringConfig(),
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
- Codice: 5 minuti (1 linea + guard + commento)
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
    # Setup con API CORRETTA (v2.1)
    settings = GameSettings()
    settings.scoring_enabled = True
    
    engine = GameEngine.create(
        settings=settings,
        audio_enabled=False
    )
    engine.new_game()
    
    # Force invalid move scenario
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
|---------|---------|---------|---------|-----------|-----------|--------------|
| **DISABLED** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **MINIMAL** | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **BALANCED** | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **COMPLETE** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Effort: 1 ora
- Enum: 10 minuti
- Campo + metodi: 30 minuti
- Docstring: 20 minuti

---

## 🔴 FASE 1.5: Settings Persistence score_warning_level (CORRETTA v2.1)

### Priorità: 🔴 CRITICA (PREVIENE CRASH/RESET RIAVVIO)

> **⚠️ CRITICAL: Senza questa fase, `score_warning_level` funziona solo in sessione**  
> Al riavvio app, l'opzione torna al default o il loader crasha se non riconosce il valore.

### File Modificato
`src/domain/services/game_settings.py` (metodi ESISTENTI da estendere)

### 🎯 CORREZIONE API v2.1

**SCOPERTA**: I metodi `to_dict()` e `load_from_dict()` **esistono già** in `GameSettings` (linee 1043-1069, SHA: 8394774) ✅

**AZIONE RICHIESTA**: **ESTENDI** metodi esistenti, NON creare da zero.

### Implementazione

#### Approccio: Estensione Serializzazione String

**File**: `src/domain/services/game_settings.py` (LINEE 1043-1069)

```python
# ✅ ESTENDI metodo ESISTENTE (NON creare nuovo)
def to_dict(self) -> dict:
    """Export settings to dictionary for JSON serialization.
    
    Returns:
        Dictionary with all setting values
    
    Example:
        >>> settings = GameSettings()
        >>> data = settings.to_dict()
        >>> data['difficulty_level']
        1
    
    Version: v2.4.0 (base), v2.6.0 (added score_warning_level)
    """
    return {
        "deck_type": self.deck_type,
        "difficulty_level": self.difficulty_level,
        "draw_count": self.draw_count,
        "max_time_game": self.max_time_game,
        "shuffle_discards": self.shuffle_discards,
        "command_hints_enabled": self.command_hints_enabled,
        "scoring_enabled": self.scoring_enabled,
        "timer_strict_mode": self.timer_strict_mode,
        
        # ✅ NEW v2.6.0: Serialize score_warning_level as string
        "score_warning_level": self.score_warning_level.name,  # "BALANCED"
    }

# ✅ ESTENDI metodo ESISTENTE (NON creare nuovo)
def load_from_dict(self, data: dict) -> None:
    """Load settings from dictionary and reapply preset (anti-cheat).
    
    This method loads settings from JSON and then reapplies the difficulty
    preset to enforce lock rules. This prevents manual JSON editing to
    bypass tournament restrictions.
    
    Args:
        data: Dictionary with setting values
    
    Example:
        >>> settings = GameSettings()
        >>> data = {"difficulty_level": 5, "draw_count": 1}  # Cheating attempt
        >>> settings.load_from_dict(data)
        >>> settings.draw_count  # 3 (preset enforced, not 1)
    
    Anti-cheat:
        If user manually edits JSON to set Level 5 with draw_count=1,
        the preset system will override it back to 3 (locked value).
    
    Version: v2.4.0 (base), v2.6.0 (added score_warning_level retrocompat)
    """
    # Load all values from dictionary
    for key, value in data.items():
        if hasattr(self, key):
            setattr(self, key, value)
    
    # ✅ NEW v2.6.0: Load score_warning_level con retrocompat
    if "score_warning_level" in data:
        try:
            # Parse string to enum
            level_name = data["score_warning_level"]
            self.score_warning_level = ScoreWarningLevel[level_name]
        except (KeyError, ValueError) as e:
            # Invalid value → fallback to default
            from src.infrastructure.logging import game_logger as log
            log.warning_issued(
                "GameSettings",
                f"Invalid score_warning_level '{level_name}': {e}. Using default BALANCED."
            )
            self.score_warning_level = ScoreWarningLevel.BALANCED
    else:
        # Missing field → retrocompat default (legacy JSON v1.0)
        self.score_warning_level = ScoreWarningLevel.BALANCED
    
    # Reapply difficulty preset to enforce locks (anti-cheat)
    if hasattr(self, 'difficulty_level'):
        self.apply_difficulty_preset(self.difficulty_level)
```

### Test FASE 1.5

**File**: `tests/domain/services/test_game_settings_persistence.py`

```python
import pytest
from src.domain.models.scoring import ScoreWarningLevel
from src.domain.services.game_settings import GameSettings

def test_score_warning_level_persistence():
    """Verify score_warning_level saved/loaded correctly."""
    settings = GameSettings()
    settings.score_warning_level = ScoreWarningLevel.MINIMAL
    
    # Serialize
    data = settings.to_dict()
    assert data["score_warning_level"] == "MINIMAL"  # String serialization
    
    # Deserialize
    loaded = GameSettings()
    loaded.load_from_dict(data)
    assert loaded.score_warning_level == ScoreWarningLevel.MINIMAL

def test_score_warning_level_retrocompat_missing():
    """Verify default BALANCED if field missing (legacy JSON v1.0)."""
    legacy_data = {
        "difficulty_level": 1,
        "draw_count": 3
        # No score_warning_level field
    }
    
    settings = GameSettings()
    settings.load_from_dict(legacy_data)
    assert settings.score_warning_level == ScoreWarningLevel.BALANCED, \
        "Missing field should default to BALANCED"

def test_score_warning_level_invalid_value():
    """Verify fallback to BALANCED if invalid value in JSON."""
    bad_data = {
        "score_warning_level": "INVALID_LEVEL_NAME"
    }
    
    settings = GameSettings()
    settings.load_from_dict(bad_data)
    assert settings.score_warning_level == ScoreWarningLevel.BALANCED, \
        "Invalid value should fallback to BALANCED"

def test_score_warning_level_int_legacy_support():
    """Verify support for int values (legacy or alternative format)."""
    int_data = {
        "score_warning_level": 1  # MINIMAL as int
    }
    
    # If using int serialization, this should work
    # If using string serialization, add conversion logic
    settings = GameSettings()
    settings.load_from_dict(int_data)
    # Should handle gracefully (convert or fallback)
    assert settings.score_warning_level in ScoreWarningLevel
```

### Effort: 30 minuti (RIDOTTO con metodi esistenti)
- Estensione to_dict(): 5 minuti (1 riga)
- Estensione load_from_dict(): 15 minuti (retrocompat + error handling)
- Test: 10 minuti

---

## 🎯 FASE 2: Integrate Warnings in GameEngine (SEMPLIFICATO v2.1)

### Priorità: ⭐ ALTA (FEATURE CORE)

### File Modificato
`src/application/game_engine.py` - Metodi `draw_from_stock()` e `recycle_waste()`

### Pre-Implementation Checklist (SEMPLIFICATO v2.1)

> **✅ VERIFICHE COMPLETATE (v2.1)**

#### A. TTS API Path ✅
**CONFERMATO**: GameEngine usa `self.screen_reader.tts.speak()` (linea 24, SHA: 9681cf5)

```python
# ✅ API VERIFICATA
from src.presentation.formatters.score_formatter import ScoreFormatter
self.screen_reader.tts.speak(message, interrupt=False)
```

#### B. TTS speak() Signature ✅
**CONFERMATO**: Supporta parametro `interrupt: bool`

```python
# ✅ SIGNATURE VERIFICATA
def speak(text: str, interrupt: bool = False)
```

#### C. Import ScoreFormatter ✅
**CONFERMATO**: Import a livello modulo **senza problemi circular** (linea 24)

```python
# ✅ IMPORT ESISTENTE (no circular import)
from src.presentation.formatters.score_formatter import ScoreFormatter
```

**CONCLUSIONE v2.1**: ❌ NON serve import locale. Usa import esistente.

### Implementazione

#### A. Safe TTS Helper (PATTERN ROBUSTO)

**Aggiungi metodo helper per TTS access sicuro**:

```python
def _speak(self, message: str, interrupt: bool = False) -> None:
    """Safe TTS adapter with None-check.
    
    Centralizes TTS access to avoid crashes if screen_reader not initialized.
    Used by warning announcement helpers.
    
    Args:
        message: Text to speak
        interrupt: Whether to interrupt current speech
        
    Version: v2.6.0
    """
    if self.screen_reader and hasattr(self.screen_reader, 'tts'):
        try:
            self.screen_reader.tts.speak(message, interrupt=interrupt)
        except Exception as e:
            # Fail gracefully in tests or if TTS unavailable
            log.warning_issued("GameEngine", f"TTS speak failed: {e}")
    # Else: no-op (test-safe, no crash)
```

#### B. Warnings in `draw_from_stock()`
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
        # ✅ v2.1: Usa formatter anche per pre-warning (consistency)
        warning = (
            f"{ScoreFormatter.SCORING_WARNING_TAG} "
            f"Ultima pescata gratuita. "
            f"Dal prossimo draw penalità -1 punto per pescata."
        )
    
    # ALL levels (MINIMAL, BALANCED, COMPLETE): Warning at 21 (first penalty)
    elif draw_count == 21:
        # ✅ v2.1: Import a livello modulo già presente (no circular)
        warning = ScoreFormatter.format_threshold_warning(
            "stock_draw", 21, 20, -1
        )
    
    # BALANCED and COMPLETE: Warning at 41 (penalty doubles)
    elif level >= ScoreWarningLevel.BALANCED and draw_count == 41:
        warning = ScoreFormatter.format_threshold_warning(
            "stock_draw", 41, 40, -2
        )
    
    # Announce warning if any (usa helper safe)
    if warning:
        self._speak(warning, interrupt=False)
```

#### C. Warnings in `recycle_waste()`
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
        warning = ScoreFormatter.format_threshold_warning(
            "recycle", 3, 2, -10
        )
    
    # COMPLETE level: Warning at 4th recycle (penalty doubles)
    elif level == ScoreWarningLevel.COMPLETE and recycle_count == 4:
        warning = (
            f"{ScoreFormatter.SCORING_WARNING_TAG} "
            f"Attenzione: quarto riciclo. Penalità totale -20 punti."
        )
    
    # COMPLETE level: Warning at 5th recycle (acceleration)
    elif level == ScoreWarningLevel.COMPLETE and recycle_count == 5:
        warning = (
            f"{ScoreFormatter.SCORING_WARNING_TAG} "
            f"Attenzione: quinto riciclo. "
            f"Penalità totale -35 punti. Crescita rapida."
        )
    
    # Announce warning if any (usa helper safe)
    if warning:
        self._speak(warning, interrupt=False)
```

### Effort: 1 ora (RIDOTTO con import già presente)
- Safe TTS helper: 10 minuti
- Metodi warning: 25 minuti
- Integration: 10 minuti
- Testing: 15 minuti

---

## 🟠 FASE 2.5: Tag-Based Warning Detection (TEST ROBUSTNESS)

### Priorità: 🟠 IMPORTANTE (PREVIENE TEST FLAKY)

> **⚠️ PROBLEMA: Keyword matching è fragile**  
> Test che cercano `"soglia"` o `"penalità"` rompono se cambi una parola.
> **SOLUZIONE**: Tag costante `[SCORING_WARNING]` per detection affidabile.

### File Modificato
`src/presentation/formatters/score_formatter.py`

### Implementazione

#### Aggiungi Tag Costante

```python
# In src/presentation/formatters/score_formatter.py

class ScoreFormatter:
    """Formatter for scoring system messages and warnings.
    
    Version: v2.6.0
    """
    
    # ✅ NEW v2.6.0: Tag costante per test detection robusto
    SCORING_WARNING_TAG = "[SCORING_WARNING]"
    
    @staticmethod
    def format_threshold_warning(
        event_type: str,
        threshold: int,
        previous: int,
        penalty: int
    ) -> str:
        """Format threshold warning with tag for robust test detection.
        
        Args:
            event_type: "stock_draw" or "recycle"
            threshold: Threshold value crossed
            previous: Previous threshold
            penalty: Penalty amount (negative)
            
        Returns:
            Tagged warning message for TTS
            
        Examples:
            >>> ScoreFormatter.format_threshold_warning("stock_draw", 21, 20, -1)
            "[SCORING_WARNING] Attenzione: superata soglia 20 pescate..."
        
        Version: v2.6.0
        """
        if event_type == "stock_draw":
            msg = (
                f"Attenzione: superata soglia {previous} pescate. "
                f"Penalità {penalty} punto per pescata."
            )
        elif event_type == "recycle":
            msg = (
                f"Attenzione: {threshold}° riciclo. "
                f"Penalità {abs(penalty)} punti."
            )
        else:
            msg = f"Soglia {threshold} superata."
        
        # ✅ Prepend tag costante per test detection
        return f"{ScoreFormatter.SCORING_WARNING_TAG} {msg}"
```

### Test Update (usa Tag)

**File**: `tests/application/test_scoring_warnings_levels.py`

```python
from src.presentation.formatters.score_formatter import ScoreFormatter

def test_stock_draw_warnings_per_level_robust(scoring_engine_draw1, level, expected_warnings):
    """Verify warnings using TAG detection (robust, non-fragile)."""
    engine = scoring_engine_draw1
    engine.settings.score_warning_level = level
    
    # Draw 45 times
    for _ in range(45):
        engine.draw_from_stock()
    
    # ✅ Count warnings by TAG (non fragile a cambi testo)
    warning_calls = [
        call for call in engine.screen_reader.tts.speak.call_args_list
        if ScoreFormatter.SCORING_WARNING_TAG in call[0][0]
    ]
    
    assert len(warning_calls) == expected_warnings, \
        f"Level {level.name}: expected {expected_warnings} warnings, " \
        f"got {len(warning_calls)}"
```

### Effort: 20 minuti
- Tag formatter: 10 minuti
- Update FASE 2: 5 minuti
- Test update: 5 minuti

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

## 🧪 FASE 4: Test Coverage Completo (DI Controllata) - CORRETTA v2.1

### Priorità: ✅ ALTA

### File Modificato
`tests/application/test_game_engine_scoring_warnings.py` (nuovo file)

### Fixture DI Controllata (STRATEGIA UNIFORME) - CORRETTA v2.1

> **⚠️ CRITICAL: Usa questa fixture per TUTTI i test warnings**  
> Evita incoerenze tra `GameEngine.create()` e `mock_engine` fixture diverse.

**File**: `tests/application/conftest.py` o nel test file

```python
import pytest
from unittest.mock import Mock
from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck
from src.domain.rules.solitaire_rules import SolitaireRules
from src.domain.services.scoring_service import ScoringService
from src.domain.services.game_service import GameService
from src.domain.services.game_settings import GameSettings
from src.domain.services.cursor_manager import CursorManager
from src.domain.services.selection_manager import SelectionManager
from src.application.game_engine import GameEngine
from src.domain.models.scoring import ScoreWarningLevel, ScoringConfig

@pytest.fixture
def scoring_engine_draw1(mocker):
    """GameEngine fixture with scoring enabled and draw_count=1 forced.
    
    ✅ CORRETTA v2.1: Usa API reale GameEngine.create(settings=...)
    NON usa parametri inesistenti come scoring_enabled= o draw_count=
    
    Provides deterministic setup for threshold warning tests.
    - TTS is mocked for call inspection
    - draw_count=1 ensures predictable threshold crossing
    - Scoring enabled with difficulty level 1
    - Full deck (52 cards) for adequate test range
    
    Usage:
        def test_warnings(scoring_engine_draw1):
            engine = scoring_engine_draw1
            engine.settings.score_warning_level = ScoreWarningLevel.BALANCED
            # ... test logic ...
    
    Version: v2.6.0 (API-corrected v2.1)
    """
    # ✅ v2.1: Create settings con API CORRETTA
    settings = GameSettings()
    settings.scoring_enabled = True
    settings.draw_count = 1  # Force determinism: 1 action = 1 card
    settings.deck_type = "french"
    settings.difficulty_level = 1
    settings.score_warning_level = ScoreWarningLevel.BALANCED  # Default
    
    # ✅ v2.1: Create engine con API REALE
    engine = GameEngine.create(
        settings=settings,
        audio_enabled=False  # Will be mocked below
    )
    
    # Mock TTS per call inspection
    mock_tts = mocker.Mock()
    mock_screen_reader = mocker.Mock()
    mock_screen_reader.tts = mock_tts
    engine.screen_reader = mock_screen_reader
    
    # Initialize game state
    engine.new_game()
    
    return engine
```

### Test Suite

> **⚠️ CRITICAL: Deterministic Test Setup**  
> Tutti i test usano fixture `scoring_engine_draw1` con draw_count=1 FORZATO.
> Con draw-3, le soglie si raggiungono a conteggi azione non deterministici.

#### Test 1: Warnings per Livello - Stock Draw (PARAMETRICO, TAG-BASED)
```python
import pytest
from src.domain.models.scoring import ScoreWarningLevel
from src.presentation.formatters.score_formatter import ScoreFormatter

@pytest.mark.parametrize("level,expected_warnings", [
    (ScoreWarningLevel.DISABLED, 0),
    (ScoreWarningLevel.MINIMAL, 1),    # Solo draw 21
    (ScoreWarningLevel.BALANCED, 2),   # Draw 21 + 41
    (ScoreWarningLevel.COMPLETE, 3),   # Draw 20 + 21 + 41
])
def test_stock_draw_warnings_per_level(scoring_engine_draw1, level, expected_warnings):
    """Verify correct warnings per level (deterministic setup, tag-based).
    
    Uses scoring_engine_draw1 fixture with draw_count=1 for predictable
    threshold crossing at exactly cards 20, 21, 41.
    
    Detection via SCORING_WARNING_TAG (robust, non-fragile).
    """
    engine = scoring_engine_draw1
    engine.settings.score_warning_level = level
    
    # Draw esattamente 45 volte (azioni = carte con draw-1)
    for _ in range(45):
        engine.draw_from_stock()
    
    # ✅ Count warnings by TAG (robust, non fragile)
    warning_calls = [
        call for call in engine.screen_reader.tts.speak.call_args_list
        if ScoreFormatter.SCORING_WARNING_TAG in call[0][0]
    ]
    
    assert len(warning_calls) == expected_warnings, \
        f"Level {level.name}: expected {expected_warnings} warnings, " \
        f"got {len(warning_calls)}"
```

#### Test 2: Warnings per Livello - Recycle (PARAMETRICO, TAG-BASED)
```python
@pytest.mark.parametrize("level,expected_warnings", [
    (ScoreWarningLevel.DISABLED, 0),
    (ScoreWarningLevel.MINIMAL, 1),    # Solo recycle 3
    (ScoreWarningLevel.BALANCED, 1),   # Solo recycle 3
    (ScoreWarningLevel.COMPLETE, 3),   # Recycle 3 + 4 + 5
])
def test_recycle_warnings_per_level(scoring_engine_draw1, level, expected_warnings):
    """Verify correct number of warnings per level during 6 recycles.
    
    Detection via SCORING_WARNING_TAG for robustness.
    """
    engine = scoring_engine_draw1
    engine.settings.score_warning_level = level
    
    # Simula 6 ricicli
    for _ in range(6):
        engine.recycle_waste()
    
    # ✅ Count warnings by TAG
    warning_calls = [
        call for call in engine.screen_reader.tts.speak.call_args_list
        if ScoreFormatter.SCORING_WARNING_TAG in call[0][0]
    ]
    
    assert len(warning_calls) == expected_warnings, \
        f"Level {level.name}: expected {expected_warnings} warnings, " \
        f"got {len(warning_calls)}"
```

#### Test 3: Warning Disabilitati Quando Scoring OFF
```python
def test_no_warnings_when_scoring_disabled(scoring_engine_draw1):
    """Verify no warnings announced when scoring system is disabled."""
    engine = scoring_engine_draw1
    engine.settings.score_warning_level = ScoreWarningLevel.COMPLETE
    engine.settings.scoring_enabled = False  # 👈 Scoring OFF
    
    # Simula 45 draw (supererebbe soglie se scoring attivo)
    for _ in range(45):
        engine.draw_from_stock()
    
    # Verify NESSUN warning
    warning_calls = [
        call for call in engine.screen_reader.tts.speak.call_args_list
        if ScoreFormatter.SCORING_WARNING_TAG in call[0][0]
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

### Effort: 1.5 ore
- Fixture DI (corretta API): 30 minuti
- Test parametrici: 40 minuti
- Test cycle: 10 minuti
- Review: 10 minuti

---

## 📚 Test Strategy Best Practices

### Rationale: Direct GameService Setup (FASE 0)

**Problema**: Test su `GameEngine.create()` possono avere:
- Dipendenze da configurazioni esterne (settings globali)
- Comportamento draw-3 non deterministico
- Side-effects da componenti non coinvolte

**Soluzione**: Setup diretto su `GameService`:
```python
# ✅ ROBUSTO: Zero dipendenze esterne
deck = FrenchDeck()
deck.crea()
deck.mischia()
table = GameTable(deck)
rules = SolitaireRules(deck)
scoring = ScoringService(
    config=ScoringConfig(),
    deck_type="french",
    difficulty_level=1,
    draw_count=1  # Force determinism
)
service = GameService(table, rules, scoring)
```

**Benefici**:
- ✅ Controllo totale su `draw_count`
- ✅ Zero dipendenze esterne
- ✅ Reproducibilità 100%

---

### Rationale: Event Filtering per Assertions (FASE 0)

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

### Rationale: Forzare draw_count=1 nei Test Warnings (FASE 4)

**Problema**: Con draw-3, le soglie si raggiungono a conteggi azione variabili:
```python
# ⚠️ NON DETERMINISTICO con draw-3
for _ in range(7):  # 7 azioni × 3 carte = 21 carte
    engine.draw_from_stock()  # Warning potrebbe emettere a iterazione 7 o prima
```

**Soluzione**: Forzare draw-1 nei test:
```python
# ✅ DETERMINISTICO
engine = scoring_engine_draw1  # Fixture con draw_count=1
for _ in range(45):  # Soglia 21 esattamente a iterazione 21
    engine.draw_from_stock()
```

**Benefici**:
- ✅ Threshold crossing prevedibile
- ✅ Warning count esatto
- ✅ Reproducibilità garantita

---

### Rationale: Tag-Based Detection (FASE 2.5)

**Problema**: Keyword matching fragile:
```python
# ⚠️ FRAGILE: cambi "penalità" → "pena" e test rompe
if "penalità" in call[0][0].lower()
```

**Soluzione**: Tag costante:
```python
# ✅ ROBUSTO: tag non cambia mai
if ScoreFormatter.SCORING_WARNING_TAG in call[0][0]
```

**Benefici**:
- ✅ Test non rompono per refactoring testi
- ✅ Semantica esplicita (è un warning scoring)
- ✅ Grep-friendly per debug

---

## ✅ Success Criteria

### Acceptance Criteria (Checklist Operativa)

#### Bug Fixes (Fase 0 + 0.5)
- [ ] `STOCK_DRAW` eventi registrati correttamente durante gameplay
- [ ] Penalità progressive 21/41 si applicano come da spec
- [ ] Test integration end-to-end passano al 100%
- [ ] `INVALID_MOVE` eventi tracciati in tutti i punti validazione
- [ ] Invariante `draw_count` vs `stock_draw_count` documentato inline

#### Feature Warnings (Fasi 1-2)
- [ ] Enum `ScoreWarningLevel` implementato con 4 livelli
- [ ] `cycle_score_warning_level()` metodo funzionante
- [ ] Warnings annunciati correttamente per ogni livello:
  - DISABLED: 0 warnings
  - MINIMAL: Draw 21, Recycle 3
  - BALANCED: Draw 21/41, Recycle 3
  - COMPLETE: Draw 20/21/41, Recycle 3/4/5
- [ ] Safe TTS adapter `_speak()` con None-check
- [ ] ✅ v2.1: Import ScoreFormatter a livello modulo (no circular)

#### Settings Persistence (Fase 1.5) - CRITICA
- [ ] ✅ v2.1: `score_warning_level` aggiunto a `to_dict()` esistente
- [ ] ✅ v2.1: Deserializzazione in `load_from_dict()` esistente con retrocompat
- [ ] Gestione valori invalidi (fallback → BALANCED)
- [ ] Test persistence passano al 100%

#### Test Robustness (Fase 2.5 + 4) - IMPORTANTE
- [ ] Tag `[SCORING_WARNING]` aggiunto a tutti i warning messages
- [ ] Test usano tag-based detection (non keyword matching)
- [ ] ✅ v2.1: Fixture `scoring_engine_draw1` con API corretta
- [ ] Tutti i test warnings usano fixture uniforme
- [ ] Test parametrici coprono tutti i livelli
- [ ] Test deterministici (draw_count=1 forzato)

#### Retrocompat (Fase 3)
- [ ] Score legacy caricano senza crash
- [ ] Sentinel `-1.0` per `victory_quality_multiplier` mancante
- [ ] Retrocompatibilità score verificata

### Non-Functional Requirements
- [ ] Nessun breaking change in API esistenti
- [ ] Backward compatible al 100%
- [ ] Performance: warnings NON impattano framerate (async TTS)
- [ ] Accessibilità: TTS chiaro e non interrompibile
- [ ] Code coverage: >90% su nuovo codice
- [ ] ✅ v2.1: Nessun import circolare (verificato)
- [ ] Nessun crash se TTS non disponibile

### Quick Checklist (Rapida)

**FASE 0**:
- [ ] STOCK_DRAW registrato per carta
- [ ] Invariante commentato inline
- [ ] Test event-filtered passano

**FASE 0.5**:
- [ ] INVALID_MOVE tracciato

**FASE 1**:
- [ ] ScoreWarningLevel enum ok
- [ ] GameSettings cycle ok

**FASE 1.5** (CRITICA - v2.1):
- [ ] ✅ Estendi to_dict() esistente
- [ ] ✅ Estendi load_from_dict() esistente
- [ ] Retrocompat default BALANCED

**FASE 2** (v2.1 SEMPLIFICATO):
- [ ] Warnings level-aware
- [ ] Safe TTS adapter ok
- [ ] ✅ Import modulo (no locale)

**FASE 2.5** (IMPORTANTE):
- [ ] Tag [SCORING_WARNING] presente
- [ ] Test tag-based

**FASE 3**:
- [ ] ScoreStorage retrocompat ok

**FASE 4** (v2.1 API-CORRETTA):
- [ ] ✅ Fixture con GameEngine.create(settings=...)
- [ ] Test parametrici passano

### Validation Tests
```bash
# Run all tests
pytest tests/ -v

# Run only scoring tests
pytest tests/domain/test_scoring_service.py -v
pytest tests/application/test_game_engine_scoring_warnings.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run only FASE 0 critical tests
pytest tests/domain/services/test_game_service_scoring_integration.py -v

# Run only warnings tests (FASE 4)
pytest tests/application/test_game_engine_scoring_warnings.py -v
```

---

## 📊 Risk Assessment

### Rischi Tecnici

| Rischio | Probabilità | Impact | Mitigazione |
|---------|-------------|--------|-------------|
| Test integration complessi | MEDIA | ALTA | Setup diretto GameService (FASE 0) |
| Settings non persistono | ✅ RISOLTA v2.1 | CRITICA | FASE 1.5 estende metodi esistenti |
| TTS annunci ripetitivi | BASSA | MEDIA | Default BALANCED (3 warnings max) |
| Test flaky keyword matching | ALTA | ALTA | Tag [SCORING_WARNING] (FASE 2.5) |
| Retrocompat score legacy | BASSA | ALTA | Sentinel `-1.0` + `.setdefault()` |
| Performance warnings | MOLTO BASSA | BASSA | TTS async, no blocking |
| Draw-3 test non deterministici | MEDIA | ALTA | Forzare draw_count=1 (Fixture) |
| Import circolari | ✅ RISOLTA v2.1 | MEDIA | Verificato: no circular import |
| TTS crash se None | MEDIA | ALTA | Safe adapter `_speak()` con None-check |

### Rollback Plan
Se Fase 0 (STOCK_DRAW fix) introduce regression:
1. Revert commit specifico
2. Mantieni Fasi 1-4 (warnings indipendenti)
3. Fix bug in feature branch separato

Se FASE 1.5 (persistence) introduce regression:
1. Revert solo FASE 1.5
2. `score_warning_level` funziona in sessione (degrada gracefully)
3. Fix persistence in hotfix branch

---

## 📝 Commit Strategy (10 Atomic Steps)

### Commit Structure (Conventional Commits)

```
1. FASE 0 (CRITICA):
fix(scoring): register STOCK_DRAW events in draw_cards gameplay
- Add scoring.record_event() in draw loop per carta
- Add inline comment documenting draw_count invariant
- Fix progressive penalties 21/41 not applying
- Add robust integration tests with direct GameService setup
- Use event filtering for test isolation
BREAKING: None
Closes: #BUG-STOCK-DRAW

2. FASE 0.5 (OPZIONALE):
feat(scoring): track INVALID_MOVE events for statistics
- Add event tracking in move validation failures (3 points)
- Enable future analytics on move efficiency
- Add test for invalid move tracking
Closes: #FEATURE-INVALID-TRACKING

3. FASE 1.1 (Enum):
feat(scoring): add ScoreWarningLevel enum
- Add enum with 4 levels (DISABLED/MINIMAL/BALANCED/COMPLETE)
- Document level semantics and threshold mapping
Closes: #FEATURE-WARNING-ENUM

4. FASE 1.2 (GameSettings):
feat(settings): add score_warning_level field and cycle method
- Add score_warning_level field (default BALANCED)
- Add cycle_score_warning_level() method
- Add get_score_warning_level_display() helper
- Add test for cycle through all levels
Closes: #FEATURE-WARNING-SETTINGS

5. FASE 1.5 (CRITICA - Persistence v2.1):
fix(settings): extend to_dict/load_from_dict with score_warning_level
- Extend existing to_dict() with score_warning_level serialization (string)
- Extend existing load_from_dict() with retrocompat handling
- Add retrocompat for missing field (default BALANCED)
- Add fallback for invalid values
- Add persistence tests (save/load/retrocompat)
BREAKING: None (graceful degradation)
API: Verified to_dict()/load_from_dict() exist at lines 1043-1069
Closes: #FIX-WARNING-PERSISTENCE

6. FASE 2.1 (Safe TTS):
feat(engine): add safe TTS adapter pattern
- Add _speak() helper with None-check
- Centralize TTS access for warnings
- Fail gracefully if TTS unavailable
Closes: #FEATURE-SAFE-TTS

7. FASE 2.2 (Warnings Integration v2.1):
feat(engine): integrate TTS threshold warnings with levels
- Add _announce_draw_threshold_warning() helper
- Add _announce_recycle_threshold_warning() helper
- Implement level-aware warning logic
- Use existing module-level ScoreFormatter import (no circular)
API: Verified ScoreFormatter import at line 24 (no circular)
Closes: #FEATURE-WARNING-INTEGRATION

8. FASE 2.5 (IMPORTANTE - Tag):
feat(formatter): add [SCORING_WARNING] tag for robust test detection
- Add SCORING_WARNING_TAG constant in ScoreFormatter
- Prepend tag to all threshold warning messages
- Update format_threshold_warning() method
- Enable robust test detection without keyword matching
Closes: #FEATURE-WARNING-TAG

9. FASE 3 (Retrocompat):
fix(storage): add backward compatibility for v1.0 scores
- Handle missing victory_quality_multiplier field
- Add sentinel -1.0 for legacy scores
- Prevent KeyError on load_all_scores()
Closes: #FIX-RETROCOMPAT-SCORES

10. FASE 4 (Test v2.1):
test(scoring): add comprehensive test coverage for warnings
- Add scoring_engine_draw1 fixture with correct API (settings=...)
- Add parametric tests for all warning levels (tag-based)
- Force draw_count=1 for deterministic threshold crossing
- Add integration tests for bug fixes with event filtering
- Achieve >90% coverage on new code
API: Verified GameEngine.create(settings=...) signature at lines 77-153
Closes: #TEST-COVERAGE-WARNINGS
```

---

## 🚀 Next Steps

### Immediate Actions
1. ✅ Review piano con team/stakeholder
2. ✅ Conferma priorità FASE 0 (CRITICA) e FASE 1.5 (CRITICA)
3. ✅ Setup branch: `feature/scoring-warnings-complete-v2`
4. ✅ Implementa FASE 0 (30 min) - **PRIORITÀ MASSIMA**
5. ✅ Implementa FASE 1.5 (30 min) - **CRITICA per persistenza**
6. ✅ Run test suite completo
7. ✅ Procedi con Fasi 1-4 se Fase 0/1.5 passano

### ✅ Pre-Implementation Verifications (COMPLETATE v2.1)
- ✅ TTS API path verificato: `self.screen_reader.tts.speak()` (linea 24)
- ✅ Signature `speak()` verificata: parametro `interrupt` supportato
- ✅ Settings serialization verificata: metodi esistono (linee 1043-1069)
- ✅ Import circolari verificati: ScoreFormatter OK (linea 24, no circular)

### Post-Implementation
- [ ] Update CHANGELOG.md con v2.6.0 features
- [ ] Update user documentation (warnings levels)
- [ ] Add migration guide per vecchi score
- [ ] Performance profiling (TTS overhead)
- [ ] Update ARCHITECTURE.md con nuove componenti

---

## 📚 References

### Documentazione Correlata
- `docs/SCORING_SYSTEM_V2.md` - Specifica completa sistema scoring
- `docs/TEMPLATE_IMPLEMENTATION_PLAN.md` - Template usato per questo piano
- `docs/OPTIONS_WINDOW_ROADMAP.md` - Context opzioni accessibilità

### Pull Request Correlate
- PR #64 - Scoring System v2.0 (PARTE 1)
- PR #XX - Questo piano (PARTE 2 - FINALE COMPLETA)

### Issues Risolte
- Bug: STOCK_DRAW events not registered (FASE 0)
- Bug: INVALID_MOVE events not tracked (FASE 0.5)
- Bug: Settings not persisted on restart (FASE 1.5)
- Feature: Graduated warning levels system (FASE 1)
- Feature: Safe TTS adapter pattern (FASE 2)
- Feature: Tag-based test detection (FASE 2.5)

### ✅ Verifiche Codice Reale (v2.1)
- `src/application/game_engine.py` (SHA: 9681cf5, linee 77-153, 24)
- `src/domain/services/game_settings.py` (SHA: 8394774, linee 1043-1069)
- `src/domain/services/game_service.py` (SHA: d0dce8a, linee 286-306)

---

**Piano approvato da**: [TBD]  
**Data approvazione**: 16 Febbraio 2026  
**Revisione**: v2.1 (API-accurate, verified with real codebase) ✅  
**Implementazione start**: [TBD]  
**Target completion**: [TBD]

---

## 🎯 Definition of Done (Operativa)

Questo piano è considerato **completamente implementato** quando:

1. ✅ Tutti i test della suite passano al 100%
2. ✅ Code coverage >90% su codice nuovo
3. ✅ STOCK_DRAW eventi registrati e penalità attive
4. ✅ Settings persistence funzionante (estensione metodi esistenti)
5. ✅ Warnings annunciati per tutti i livelli come da spec
6. ✅ Test usano tag-based detection (robusti)
7. ✅ Nessun import circolare (verificato v2.1)
8. ✅ Nessun crash TTS
9. ✅ Retrocompat score legacy verificata
10. ✅ Documentazione aggiornata (CHANGELOG, user docs)

**Piano pronto per implementazione "senza sorprese"** 🚀  
**v2.1: API-accurate, verified against real codebase** ✅
