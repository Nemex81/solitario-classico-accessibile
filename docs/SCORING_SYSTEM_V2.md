# 📊 Solitario Accessibile - Scoring System v2.0 - Specification

**Version**: 2.0.0  
**Date**: 2026-02-15  
**Status**: 🔒 **Design Locked** - Ready for Implementation  
**Breaking Changes**: Yes (incompatible with v1.0)

---

## 📋 Table of Contents

1. [Design Principles](#design-principles)
2. [Mathematical Model](#mathematical-model)
3. [Events & Penalties](#events--penalties)
4. [Bonuses & Multipliers](#bonuses--multipliers)
5. [Time Bonus System](#time-bonus-system)
6. [Victory Bonus Composite](#victory-bonus-composite)
7. [Final Score Pipeline](#final-score-pipeline)
8. [Numerical Precision Policy](#numerical-precision-policy)
9. [Determinism Guarantees](#determinism-guarantees)
10. [Architecture](#architecture)
11. [Data Persistence](#data-persistence)
12. [TTS Accessibility](#tts-accessibility)
13. [Testing Strategy](#testing-strategy)
14. [Implementation Plan](#implementation-plan)
15. [Migration Guide (v1.0 → v2.0)](#migration-guide)

---

## 🎯 Design Principles

### 1. Skill over Luck
Premio decisioni strategiche del giocatore, non distribuzione casuale delle carte.

### 2. Accessibility First
Velocità non deve dominare (max 35% peso) per non penalizzare latenza TTS/screen reader.

### 3. Transparency
Sistema spiegabile vocalmente, niente matematica "black box".

### 4. Anti-Exploit
Abbandoni non premiano, leaderboard pulita da gaming strategies.

### 5. Evolvability
Config esterna, telemetria-ready (v2.1+), tuning senza recompile.

---

## 🧮 Mathematical Model

### Score Formula
```
FINAL_SCORE = max(0, PROVISIONAL + TIME_BONUS + VICTORY_BONUS)

where:
  PROVISIONAL = (BASE_SCORE + DECK_BONUS + DRAW_BONUS) × DIFFICULTY_MULT
  TIME_BONUS = f(elapsed_time) if is_victory else 0
  VICTORY_BONUS = BASE_VICTORY × quality_multiplier if is_victory else 0
```

### Key Properties
- **Deterministic**: Same input → same output, always
- **Order-independent**: Event sequence doesn't affect final score
- **Non-negative**: Clamped to minimum 0 (never negative)
- **Integer-only**: All final values truncated (no decimals)

---

## 📊 Events & Penalties

### Base Events (Fixed Points)

| Event | Points | Note |
|-------|--------|------|
| `WASTE_TO_FOUNDATION` | +10 | Carta da scarti a fondazioni |
| `TABLEAU_TO_FOUNDATION` | +10 | Carta da tableau a fondazioni |
| `CARD_REVEALED` | +5 | Carta scoperta in tableau |
| `FOUNDATION_TO_TABLEAU` | -15 | Penalità mossa inversa |

### Progressive Events

#### `STOCK_DRAW` (Pescare dal mazzo)
```python
draws_cumulative = 0  # Counter globale partita (mai reset)

def calculate_stock_draw_penalty(draws_cumulative):
    if draws_cumulative <= 20:
        return 0   # Primi 20 draw gratuiti
    elif draws_cumulative <= 40:
        return -1  # Draw 21-40: -1pt cadauno
    else:
        return -2  # Draw 41+: -2pt cadauno
```

**Boundary tests richiesti**:
```python
assert penalty(20) == 0   # Last free draw
assert penalty(21) == -1  # First penalty
assert penalty(40) == -1  # Last -1pt tier
assert penalty(41) == -2  # First -2pt tier
```

**Esempi**:
- 15 draw → 0pt totali
- 35 draw → -15pt totali
- 60 draw → -55pt totali

#### `RECYCLE_WASTE` (Riciclare scarti)
```python
recycle_penalties = [0, 0, -10, -20, -35, -55, -80]

def calculate_recycle_penalty(recycle_count):
    # Guard contro recycle_count <= 0
    if recycle_count <= 0:
        return 0
    
    index = min(recycle_count - 1, 6)  # Clamp max index 6
    return recycle_penalties[index]
```

**Esempi**:
- 1° riciclo → 0pt
- 2° riciclo → 0pt
- 3° riciclo → -10pt
- 5° riciclo → -35pt
- 10° riciclo → -80pt (clamped)

### Tracking-Only Events (No Impact v2.0)

| Event | Punti | Uso Futuro |
|-------|-------|------------|
| `INVALID_MOVE` | 0 | Statistiche + penalty v2.1+ |
| `AUTO_MOVE` | 0 | Neutral (punti già in mosse base) |
| `UNDO_MOVE` | 0 | Riservato v3.0 |
| `HINT_USED` | 0 | Riservato v3.0 |

---

## 🎁 Bonuses & Multipliers

### Deck Type Bonus
```python
deck_bonuses = {
    "neapolitan": 100,  # 40 carte (più difficile)
    "french": 50        # 52 carte (baseline)
}
```

### Draw Count Bonus (livello-dipendente)
```python
def get_draw_bonus(draw_count, difficulty_level):
    if difficulty_level <= 3:
        # Livelli 1-3: bonus pieno
        return {1: 0, 2: 100, 3: 200}[draw_count]
    else:
        # Livelli 4-5: bonus ridotto 50%
        return {1: 0, 2: 50, 3: 100}[draw_count]
```

### Difficulty Multipliers
```python
difficulty_multipliers = {
    1: 1.0,   # Principiante
    2: 1.2,   # Facile
    3: 1.4,   # Normale
    4: 1.8,   # Esperto
    5: 2.2    # Maestro
}
```

**Nota**: Moltiplicatore applicato SOLO a provisional score, NON a time/victory bonus.

---

## ⏱️ Time Bonus System

### Regola Critica
**Time bonus = 0 se `is_victory == False`** (indipendentemente dal tempo).

### Timer OFF (decay lineare)
```python
def calculate_time_bonus_timer_off(elapsed_minutes):
    return max(0, 1200 - (elapsed_minutes * 40))
```

**Tabella riferimento**:
```
Tempo     | Bonus
----------|-------
0-5 min   | +1000-1200pt
10 min    | +800pt
20 min    | +400pt
30 min    | +0pt (zero bonus)
```

### Timer ON (percentuale tempo risparmiato)
```python
def calculate_time_bonus_timer_on(elapsed_seconds, timer_limit_seconds):
    time_remaining_pct = (timer_limit_seconds - elapsed_seconds) / timer_limit_seconds
    return int(time_remaining_pct * 1000)
```

**Tabella riferimento** (60min timer):
```
Tempo usato | Tempo rimasto | Bonus
------------|---------------|-------
12 min      | 80%           | +800pt
30 min      | 50%           | +500pt
45 min      | 25%           | +250pt
59 min      | 2%            | +20pt
```

### Overtime (PERMISSIVE mode)
```python
def calculate_overtime_penalty(overtime_minutes):
    return -100 * overtime_minutes
```

**STRICT mode**: `-500pt` fissi (terminazione forzata partita).

---

## 🏆 Victory Bonus Composite

### Regola Critica
**Victory bonus = 0 se `is_victory == False`**.

### Formula
```python
BASE_VICTORY = 400

# Calcolo quality factors
time_quality = calculate_time_quality(...)      # Range: 0.7 - 1.5
move_quality = calculate_move_quality(...)      # Range: 0.7 - 1.3
recycle_quality = calculate_recycle_quality(...) # Range: 0.5 - 1.2

# Media ponderata (35% time, 35% moves, 30% recycles)
quality_multiplier = (
    time_quality * 0.35 +
    move_quality * 0.35 +
    recycle_quality * 0.30
)

# Victory finale
victory_bonus = int(BASE_VICTORY * quality_multiplier)
```

**Range teorico**: 252pt (worst) - 536pt (perfect)

**Max teorico**:
```
quality_max = 1.5*0.35 + 1.3*0.35 + 1.2*0.30 = 1.34
victory_max = 400 * 1.34 = 536pt
```

### Quality Thresholds

#### Time Quality

**Timer OFF** (minuti assoluti):
```python
if elapsed_minutes <= 10:   return 1.5  # Velocissimo
elif elapsed_minutes <= 20: return 1.2  # Veloce
elif elapsed_minutes <= 30: return 1.0  # Medio
elif elapsed_minutes <= 45: return 0.8  # Lento
else:                       return 0.7  # Molto lento
```

**Timer ON** (percentuale tempo rimasto):
```python
if time_remaining_pct >= 0.80: return 1.5  # 80%+ rimasto
elif time_remaining_pct >= 0.50: return 1.2  # 50%+ rimasto
elif time_remaining_pct >= 0.25: return 1.0  # 25%+ rimasto
elif time_remaining_pct > 0:    return 0.8  # Entro limite
else:                           return 0.7  # Overtime
```

#### Move Quality
```python
if move_count <= 80:    return 1.3  # Ottimale
elif move_count <= 120: return 1.1  # Buono
elif move_count <= 180: return 1.0  # Medio
elif move_count <= 250: return 0.85 # Basso
else:                   return 0.7  # Brute force
```

#### Recycle Quality
```python
if recycle_count == 0:      return 1.2  # Perfetto (zero ricicli)
elif recycle_count <= 2:    return 1.1  # Ottimo
elif recycle_count <= 4:    return 1.0  # Medio
elif recycle_count <= 7:    return 0.8  # Molti
else:                       return 0.5  # Tantissimi
```

---

## 🔢 Final Score Pipeline

```python
# Step 1: Base score (somma eventi)
base_score = sum(event.points for event in events)

# Step 2: Provisional score
provisional = (base_score + deck_bonus + draw_bonus) * difficulty_multiplier

# Step 3: Time & Victory bonuses (SOLO su vittoria)
if is_victory:
    time_bonus = calculate_time_bonus(...)
    victory_bonus, quality_multiplier = calculate_victory_bonus(...)
else:
    time_bonus = 0
    victory_bonus = 0
    quality_multiplier = 0.0  # Explicit zero per abbandono

# Step 4: Final score
final_score = provisional + time_bonus + victory_bonus

# Step 5: Clamp a minimo
final_score = max(0, final_score)

# Step 6: Return FinalScore con quality_multiplier persistito
return FinalScore(
    base_score=base_score,
    provisional_score=provisional,
    time_bonus=time_bonus,
    victory_bonus=victory_bonus,
    victory_quality_multiplier=quality_multiplier,  # 🆕 Persisted
    total_score=final_score,
    ...
)
```

---

## 🔢 Numerical Precision Policy

### Rounding Rules

1. **Intermediate calculations**: Use FLOAT (no premature rounding)
2. **Final conversion**: TRUNCATE (floor) to INT, never round up
3. **Method**: Python `int()` (equivalent to floor for positive numbers)
4. **All scores**: INTEGER only (no decimals in final values)
5. **Safety clause**: All values subject to `int()` MUST be non-negative

### Rule 5 Rationale

Python `int()` behavior differs for negative numbers:
```python
int(1.9)   → 1  (floor)
int(-1.9)  → -1 (NOT floor, truncation toward zero)
```

To guarantee consistent floor behavior, enforce non-negativity:
```python
# CORRECT (safe)
value = max(0, calculated_value)  # Clamp negative to 0 FIRST
final = int(value)  # Then truncate

# INCORRECT (unsafe if future adds negative multipliers)
final = int(calculated_value)  # Behavior undefined for negatives
```

### Enforcement in Code

```python
def _safe_truncate(self, value: float, context: str = "") -> int:
    """Safe truncation with invariant enforcement.
    
    Raises:
        ValueError: If value < 0 (domain invariant violation)
    """
    if value < 0:
        raise ValueError(
            f"Truncation safety violated: {value} < 0 "
            f"(context: {context}). Domain logic bug."
        )
    return int(value)
```

**Nota**: NON usare `assert` per invarianti di dominio (può sparire con `-O` flag).

### Truncation Bias Analysis

TRUNCATE (floor) introduces systematic negative bias:
- Max loss per truncation: **-0.999pt**
- Truncation points: 3 (provisional, time_bonus, victory_bonus)
- Max cumulative loss: **-2.997pt**

**Impact**: On typical score ~1500pt, bias ~0.2% (negligible).

**Justification**:
- Consistent (always negative)
- Bounded (< 3pt loss)
- Predictable (no randomness)
- Conservative (never gifts points)

**Alternative considered**: `round()` (statistically unbiased but feels non-deterministic).  
**Decision**: TRUNCATE chosen for **determinism** over statistical fairness.

---

## ⚙️ Determinism Guarantees

### Principle: Order-Independent Scoring

Final score depends ONLY on aggregated final state, NOT on temporal order of events.

**Example**:
```python
# Sequence A
draw 5 times → recycle → draw 5 times → final_score = X

# Sequence B  
draw 10 times → recycle → final_score = X

# Both produce SAME score (X) because:
# - stock_draw_count = 10 (cumulative)
# - recycle_count = 1
# Order irrelevant, only final counts matter.
```

### Implications

1. **Replay safety**: Reconstructing score from event log produces identical result
2. **Serializability**: Can save/load game state without order-dependent bugs
3. **Debuggability**: Score discrepancies traceable to state differences, not event sequences

### Non-Order-Dependent State

- `stock_draw_count` (cumulative, never resets)
- `recycle_count` (cumulative, never resets)
- `base_score` (sum of event points, associative)
- `move_count` (external counter, order-agnostic)
- `elapsed_seconds` (monotonic timer, order-agnostic)

### Constraint: Associative & Commutative Events

`record_event()` MUST remain associative and commutative:

```python
# Associativity: Grouping doesn't matter
(event_A + event_B) + event_C == event_A + (event_B + event_C)

# Commutativity: Order doesn't matter
event_A + event_B == event_B + event_A
```

**Allowed**:
- Cumulative counters (`stock_draw_count += 1`)
- Additive scores (`base_score += points`)
- State-independent penalties

**Forbidden** (breaks determinism):
- Streak bonuses (depends on consecutive events)
- Time-dependent modifiers
- Order-dependent penalties

**Enforcement**: If future features require order-dependent logic, they MUST be documented as determinism exceptions.

---

## 🏗️ Architecture

### Layer Separation

```
Infrastructure Layer
  ├─ ScoringConfigLoader (JSON → ScoringConfig)
  └─ ScoreStorage (persistence)
       ↓
Application Layer
  ├─ GameEngine (orchestration)
  └─ GameplayController
       ↓
Domain Layer
  ├─ ScoringService (logic pura)
  ├─ ScoringConfig (immutable dataclass)
  └─ FinalScore (result object)
       ↓
Presentation Layer
  └─ ScoreFormatter (TTS output)
```

### Key Principles

1. **Domain never accesses JSON directly** (receives `ScoringConfig` validato)
2. **Config immutable** (`@dataclass(frozen=True)`)
3. **No data reconstruction in UI** (quality_multiplier persisted)
4. **Invariants enforced in domain** (`ValueError`, not `assert`)

### Config Externalization

**Location**: `config/scoring_config.json`

**Structure**:
```json
{
  "version": "2.0.0",
  "event_points": {
    "waste_to_foundation": 10,
    "tableau_to_foundation": 10,
    "card_revealed": 5,
    "foundation_to_tableau": -15
  },
  "stock_draw": {
    "thresholds": [20, 40],
    "penalties": [0, -1, -2]
  },
  "recycle_penalties": [0, 0, -10, -20, -35, -55, -80],
  "deck_bonuses": {
    "neapolitan": 100,
    "french": 50
  },
  "difficulty_multipliers": {
    "1": 1.0,
    "2": 1.2,
    "3": 1.4,
    "4": 1.8,
    "5": 2.2
  },
  "time_bonus": {
    "timer_off_max": 1200,
    "timer_off_decay_per_minute": 40,
    "timer_on_max": 1000,
    "overtime_penalty_per_minute": -100
  },
  "victory_bonus": {
    "base": 400,
    "weights": {
      "time": 0.35,
      "moves": 0.35,
      "recycles": 0.30
    }
  },
  "min_score": 0
}
```

**Loader**:
```python
class ScoringConfigLoader:
    @classmethod
    def load(cls, path: Path = None) -> ScoringConfig:
        """Load config from JSON with validation.
        
        Fallbacks to hardcoded defaults if file missing.
        """
        try:
            with open(path or cls.DEFAULT_PATH, 'r') as f:
                data = json.load(f)
            return cls._parse_and_validate(data)
        except FileNotFoundError:
            return cls.fallback_default()
```

---

## 💾 Data Persistence

### FinalScore Dataclass (v2.0)

```python
@dataclass(frozen=True)
class FinalScore:
    """Final score at game end with complete breakdown."""
    
    # Score components
    base_score: int
    deck_bonus: int
    draw_bonus: int
    difficulty_multiplier: float
    time_bonus: int
    victory_bonus: int
    total_score: int
    
    # Game metadata
    is_victory: bool
    elapsed_seconds: float
    difficulty_level: int
    deck_type: str
    draw_count: int
    recycle_count: int
    move_count: int
    
    # 🆕 NEW v2.0: Persisted quality (not reconstructed in UI)
    victory_quality_multiplier: float  # Range: 0.0 (abbandono) - 1.34 (perfect)
```

### Retrocompatibility (v1.0 → v2.0)

**Legacy scores** senza `victory_quality_multiplier`:

```python
def load_all_scores(self) -> List[FinalScore]:
    """Load scores with legacy handling."""
    for score_dict in raw_scores:
        # Add missing field for legacy
        if "victory_quality_multiplier" not in score_dict:
            score_dict["victory_quality_multiplier"] = -1.0  # Sentinel
        
        yield FinalScore(**score_dict)
```

**Display in UI**:
```python
if final_score.victory_quality_multiplier < 0:
    # Legacy score, hide quality
    text = f"Bonus vittoria: {final_score.victory_bonus} punti (legacy)"
else:
    # v2.0 score, show quality
    text = f"Bonus vittoria: {final_score.victory_bonus} punti, qualità {final_score.victory_quality_multiplier:.2f}"
```

### Versioning scores.json

```json
{
  "version": "2.0.0",
  "scores": [
    {
      "scoring_system_version": "2.0.0",
      "total_score": 1523,
      "victory_quality_multiplier": 1.05,
      ...
    }
  ]
}
```

Se caricato score v1.0, mostra:  
`"⚠️ Punteggio legacy v1.0 (non comparabile con v2.0)"`

---

## 📢 TTS Accessibility

### Riepilogo Sintetico (default, fine partita)

```python
def format_summary(final_score: FinalScore) -> str:
    """Sintetico TTS-friendly."""
    status = "Vittoria" if final_score.is_victory else "Partita abbandonata"
    minutes = int(final_score.elapsed_seconds // 60)
    
    return (
        f"{status} in {minutes} minuti con {final_score.move_count} mosse. "
        f"Punteggio totale: {final_score.total_score} punti."
    )
```

**Output esempio**:  
*"Vittoria in 18 minuti con 142 mosse. Punteggio totale: 1.523 punti."*

### Dettaglio Espanso (tasto `D`)

```python
def format_detailed(final_score: FinalScore) -> str:
    """Breakdown completo TTS."""
    parts = [
        f"Dettaglio punteggio:",
        f"Punteggio base dalle mosse: {final_score.base_score} punti.",
        f"Bonus mazzo {final_score.deck_type}: {final_score.deck_bonus} punti.",
    ]
    
    if final_score.draw_bonus > 0:
        parts.append(f"Bonus pescata {final_score.draw_count} carte: {final_score.draw_bonus} punti.")
    
    parts.append(f"Moltiplicatore difficoltà livello {final_score.difficulty_level}: {final_score.difficulty_multiplier}.")
    
    provisional = int((final_score.base_score + final_score.deck_bonus + final_score.draw_bonus) * final_score.difficulty_multiplier)
    parts.append(f"Punteggio provvisorio: {provisional} punti.")
    
    if final_score.time_bonus != 0:
        parts.append(f"Bonus tempo: {final_score.time_bonus} punti.")
    
    # 🆕 Use persisted quality, not reconstructed
    if final_score.victory_bonus > 0 and final_score.victory_quality_multiplier > 0:
        parts.append(
            f"Bonus vittoria: {final_score.victory_bonus} punti, "
            f"qualità {final_score.victory_quality_multiplier:.2f}."
        )
    
    parts.append(f"Punteggio finale: {final_score.total_score} punti.")
    
    return " ".join(parts)
```

**Output esempio**:  
*"Dettaglio punteggio: Punteggio base dalle mosse: 95 punti. Bonus mazzo napoletano: 100 punti. ..."*

### Notifiche Soglie (configurabili)

**Setting**: `settings.json` → `"score_warnings_enabled": true`

```python
# Quando superi stock_draw threshold
if stock_draw_count == 21:
    tts.speak(
        "Attenzione: superata soglia 20 pescate. "
        "Penalità -1 punto per pescata."
    )

# Quando superi recycle threshold
if recycle_count == 3:
    tts.speak(
        "Attenzione: terzo riciclo. "
        "Dal prossimo riciclo penalità -10 punti."
    )
```

**Timing**: Mai durante selezione carta/esecuzione mossa. Solo post-azione o idle.

---

## 🧪 Testing Strategy

### Coverage Target

**95%+ su**:
- `ScoringService`
- `ScoringConfig`
- `ScoringConfigLoader`
- Calcolo formule (quality factors, bonuses)

### Critical Test Categories

#### 1. Boundary Tests
```python
def test_stock_draw_boundaries():
    """CRITICAL: Exact boundary values."""
    assert penalty(19) == 0
    assert penalty(20) == 0   # 👈 Last free
    assert penalty(21) == -1  # 👈 First penalty
    assert penalty(40) == -1  # 👈 Last -1pt
    assert penalty(41) == -2  # 👈 First -2pt
```

#### 2. Abandonment Protection
```python
def test_abandonment_no_bonuses():
    """CRITICAL: Abandonment receives no time/victory bonus."""
    final = service.calculate_final_score(
        elapsed_seconds=300,  # 5min (would be +1000pt if victory)
        move_count=50,
        is_victory=False  # 👈 Abandonment
    )
    
    assert final.time_bonus == 0      # 👈 CRITICAL
    assert final.victory_bonus == 0   # 👈 CRITICAL
```

#### 3. Determinism (Commutativity)
```python
def test_scoring_commutativity():
    """Verify event order doesn't affect final score."""
    events = [
        (ScoreEventType.STOCK_DRAW, 10),
        (ScoreEventType.RECYCLE_WASTE, 2),
        (ScoreEventType.TABLEAU_TO_FOUNDATION, 5),
    ]
    
    # Try multiple random shuffles
    for _ in range(10):
        service = ScoringService(...)
        shuffled = events.copy()
        random.shuffle(shuffled)
        
        # Record events in shuffled order
        for event_type, count in shuffled:
            for _ in range(count):
                service.record_event(event_type)
        
        # Score must be identical
        assert service.get_base_score() == reference_score
```

#### 4. Truncation Safety
```python
def test_truncation_safety_enforcement():
    """Verify _safe_truncate raises on negative."""
    service = ScoringService(...)
    
    with pytest.raises(ValueError, match="Truncation safety violated"):
        service._safe_truncate(-1.5, "test_context")
```

#### 5. Victory Bonus Max
```python
def test_victory_bonus_max_theoretical():
    """Victory bonus cannot exceed 536pt."""
    service = ScoringService(...)
    
    # Force perfect conditions
    bonus, quality = service._calculate_victory_bonus_with_quality(
        elapsed_seconds=60,   # 1min (time_quality=1.5)
        move_count=50         # (move_quality=1.3)
    )
    # recycle_count=0 → recycle_quality=1.2
    
    assert bonus <= 536  # Hard limit
    assert quality <= 1.34
```

#### 6. Config Validation
```python
def test_config_validation_weights():
    """Config validation catches invalid weights."""
    with pytest.raises(ValueError, match="must sum to 1.0"):
        ScoringConfig(
            victory_weights={"time": 0.5, "moves": 0.3, "recycles": 0.1}
        )
```

---

## 📅 Implementation Plan

### Phase 1: Core Scoring Logic (Commits 1-6)

#### Commit 1: Extend ScoreEventType + update ScoringConfig
- Aggiungi `STOCK_DRAW`, `INVALID_MOVE`, `AUTO_MOVE` a enum
- Aggiorna `ScoringConfig` dataclass con campi v2.0
- Aggiungi `__post_init__` validation
- Test: config defaults, validation

#### Commit 2: Implement STOCK_DRAW penalty
- `_calculate_stock_draw_penalty()` progressive
- `stock_draw_count` cumulative counter
- Guard `recycle_count <= 0` in `_calculate_recycle_penalty()`
- Test: boundary (20→21, 40→41), guard zero

#### Commit 3: Update time bonus (v2.0 values)
- Cambia max 2000→1200 (timer OFF)
- Cambia decay 50→40 per minute
- Cambia max 1500→1000 (timer ON)
- Test: tabelle riferimento, float determinism

#### Commit 4: Implement quality factors
- `_calculate_time_quality()`
- `_calculate_move_quality()`
- `_calculate_recycle_quality()`
- Test: thresholds corretti per ogni factor

#### Commit 5: Implement composite victory bonus
- `_calculate_victory_bonus_with_quality()` return tuple
- Weighted average 35/35/30
- Test: perfect (536pt), average (400pt), poor (~252pt)

#### Commit 6: Update calculate_final_score()
- Azzeramento time/victory su abbandono
- Persist `victory_quality_multiplier` in `FinalScore`
- Test: end-to-end vittoria, abbandono, clamping

**Status post-Commit 6**: Core scoring v2.0 completo (ancora hardcoded config).

---

### Phase 2: Config Externalization (Commits 7-8)

#### Commit 7: Create config JSON + loader
- `config/scoring_config.json` completo
- `ScoringConfigLoader.load()` con validation
- `ScoringConfigLoader.fallback_default()` hardcoded
- Test: load valid, missing file, malformed JSON

#### Commit 8: Integrate loader into GameEngine
- `GameEngine.__init__()` carica config via loader
- `ScoringService` riceve config iniettato
- Test: GameEngine usa config esterno

**Status post-Commit 8**: Config externalization completa.

---

### Phase 3: TTS Transparency (Commit 9)

#### Commit 9: Implement formatters + warnings
- `ScoreFormatter.format_summary()`
- `ScoreFormatter.format_detailed()`
- `ScoreFormatter.format_threshold_warning()`
- Integrazione warnings in `GameEngine` (stock_draw 21, recycle 3)
- Setting `score_warnings_enabled` in `settings.json`
- Test: formatter output, warning triggered

**Status post-Commit 9**: Sistema completo v2.0.

---

### Phase 4: Testing & Documentation

- Run full test suite (target 95%+)
- Update `CHANGELOG.md` (breaking changes)
- Update `README.md` (scoring documentation)
- Playtesting (10-20 partite manuali)

---

## 🔄 Migration Guide (v1.0 → v2.0)

### Breaking Changes

1. **Punteggi non comparabili**: Formule completamente diverse
2. **Config structure**: Era hardcoded, ora JSON esterno
3. **Eventi nuovi**: `STOCK_DRAW` tracciato con penalty progressive
4. **FinalScore dataclass**: Campo `victory_quality_multiplier` aggiunto

### Migration Steps

#### 1. Backup scores esistenti
```bash
cp data/scores.json data/scores_v1_backup.json
```

#### 2. Update scores.json structure
```python
# Aggiungi campo version
{
  "version": "2.0.0",
  "scores": [...]
}
```

#### 3. Handle legacy scores
Scores v1.0 senza `victory_quality_multiplier`:
```python
if "victory_quality_multiplier" not in score_dict:
    score_dict["victory_quality_multiplier"] = -1.0  # Sentinel
    score_dict["scoring_system_version"] = "1.0"
```

#### 4. Display warning
Quando mostri score v1.0:
```
"⚠️ Punteggio calcolato con sistema legacy v1.0 (non comparabile con v2.0)"
```

#### 5. Leaderboard separation (opzionale)
```python
# Separate leaderboards
scores_v1 = [s for s in all_scores if s.get("scoring_system_version") == "1.0"]
scores_v2 = [s for s in all_scores if s.get("scoring_system_version") == "2.0"]
```

---

## 📊 Expected Score Ranges

| Scenario | Range Punti | Composizione |
|----------|-------------|--------------|
| **Vittoria Perfetta** (liv 5, 8min, 75 mosse, 0 ricicli) | **2400-2800pt** | Base 18%, Time 45%, Victory 22%, Provisional 15% |
| **Vittoria Ottima** (liv 4, 18min, 110 mosse, 2 ricicli) | **1600-2000pt** | Base 20%, Time 40%, Victory 25%, Provisional 15% |
| **Vittoria Media** (liv 3, 25min, 160 mosse, 4 ricicli) | **1000-1400pt** | Base 25%, Time 35%, Victory 28%, Provisional 12% |
| **Vittoria Scrausa** (liv 2, 40min, 280 mosse, 8 ricicli) | **400-700pt** | Base 35%, Time 15%, Victory 20%, Provisional 30% |
| **Abbandono** (qualsiasi) | **0-800pt** | Solo provisional (no time/victory) |

---

## ✅ Design Lock Checklist

```
Mathematical Soundness
 ✅ Formula deterministico
 ✅ Rounding policy (TRUNCATE + Rule 5)
 ✅ Bias sistematico documentato
 ✅ Boundary conditions testabili

Architectural Integrity
 ✅ Domain/Infrastructure separation
 ✅ Config externalization (JSON + loader)
 ✅ No data reconstruction in UI
 ✅ Invariant enforcement (ValueError)

Determinism Guarantees
 ✅ Order-independent scoring
 ✅ Associative & commutative constraint
 ✅ Replay-safe from event log

Data Persistence
 ✅ victory_quality_multiplier persisted
 ✅ Legacy retrocompat (sentinel -1.0)
 ✅ FinalScore complete

Accessibility (TTS)
 ✅ Formatters (summary + detailed)
 ✅ Threshold warnings configurabili
 ✅ Null-safe display

Testing Strategy
 ✅ 95% coverage target
 ✅ Boundary tests
 ✅ Commutativity tests
 ✅ Safety invariant tests

Documentation
 ✅ Specifica completa
 ✅ Breaking changes documentati
 ✅ Migration path
```

---

## 📝 Future Enhancements (v2.1+)

1. **Telemetry opt-in**: Raccolta statistiche anonime per calibrazione soglie data-driven
2. **Achievements layer**: Badge "Prima vittoria liv 5", "10 vittorie consecutive"
3. **Personal bests**: Notifica vocale "Nuovo record personale!"
4. **Difficulty auto-adjust**: Suggerimento downgrade se win rate < 20%
5. **Hint/Undo penalties**: Penalità esplicite per suggerimenti/annullamenti

---

## 🔒 Design Status

```
╔═══════════════════════════════════════════════════════════════╗
║  SOLITARIO ACCESSIBILE - SCORING SYSTEM v2.0                 ║
║  Design Phase: COMPLETED & LOCKED                            ║
║  Date: 2026-02-15 17:30 CET                                  ║
║  Status: Ready for Implementation                            ║
╚═══════════════════════════════════════════════════════════════╝

Signed off:
✅ Mathematical Correctness
✅ Architectural Soundness  
✅ Testing Coverage
✅ Accessibility

No ambiguities. No implicit assumptions. No deferred decisions.

Implementation Phase: AUTHORIZED
```

---

**End of Specification**
