# 📋 TODO – Scoring System v2.0 Implementation

**Branch**: `refactoring-engine`  
**Tipo**: REFACTOR + FEATURE  
**Priorità**: HIGH  
**Stato**: READY  
**Versione Target**: v2.5.2 → v2.6.0 (MINOR bump, breaking changes documentati)

---

## 📖 Riferimento Documentazione

**⚠️ OBBLIGATORIO**: Prima di iniziare qualsiasi commit, consultare:

📚 **[docs/SCORING_SYSTEM_V2.md](docs/SCORING_SYSTEM_V2.md)** ← Piano completo con formule, invarianti, test strategy

Questo file TODO è solo un cruscotto operativo da consultare e aggiornare durante implementazione.

---

## 🎯 Obiettivo Implementazione

**Cosa**: Reimplementazione completa sistema di punteggio con:
- Formula deterministico (order-independent scoring)
- Config esterna JSON (no hardcoded values)
- Victory bonus composite (35% time, 35% moves, 30% recycles)
- Time/Victory bonus = 0 su abbandono (anti-exploit)
- Rounding policy TRUNCATE + Rule 5 safety
- TTS formatters + threshold warnings

**Perché**: Sistema v1.0 non bilanciato (time bonus dominante), non configurabile, exploitable (abbandoni premiano).

**Impatto**: Breaking change punteggi, leaderboard separata v1/v2, utenti notificati migrazione.

---

## 📊 Implementation Progress

### Phase 1: Core Scoring Logic (6 commits)

#### Commit 1: Extend ScoreEventType + ScoringConfig ✅
**File coinvolti**:
- [x] `src/domain/models/scoring.py` → MODIFY
  - [x] Aggiungi `STOCK_DRAW`, `INVALID_MOVE`, `AUTO_MOVE` a `ScoreEventType` enum
  - [x] Aggiorna `ScoringConfig` dataclass con campi v2.0:
    - [x] `victory_bonus_base: int = 400` (era 500)
    - [x] `victory_weights: dict = {"time": 0.35, "moves": 0.35, "recycles": 0.30}`
    - [x] `stock_draw_thresholds: tuple = (20, 40)`
    - [x] `stock_draw_penalties: tuple = (0, -1, -2)`
    - [x] `recycle_penalties: tuple = (0, 0, -10, -20, -35, -55, -80)`
    - [x] `time_bonus_max_timer_off: int = 1200` (era 2000)
    - [x] `time_bonus_decay_per_minute: int = 40` (era 50)
    - [x] `time_bonus_max_timer_on: int = 1000` (era 1500)
    - [x] `difficulty_multipliers: dict = {1: 1.0, 2: 1.2, 3: 1.4, 4: 1.8, 5: 2.2}`
    - [x] `deck_type_bonuses: dict = {"neapolitan": 100, "french": 50}`
  - [x] Aggiungi `__post_init__` validation:
    - [x] Version check (`startswith("2.")`)
    - [x] Weights sum validation (0.99 ≤ sum ≤ 1.01)
    - [x] Difficulty levels completeness ({1,2,3,4,5})
  - [x] Rendi dataclass `frozen=True` (immutability)

- [x] `tests/domain/models/test_scoring_models.py` → MODIFY
  - [x] `test_score_event_type_new_events()` → STOCK_DRAW, INVALID_MOVE, AUTO_MOVE esistono
  - [x] `test_scoring_config_v2_defaults()` → Defaults corretti (victory_base=400, time_max=1200)
  - [x] `test_scoring_config_validation()` → ValueError su weights invalidi

**Status commit 1**: ✅ DONE (SHA: aaf12c2) - ⚠️ **TEST ESISTENTI DA INTEGRARE**

---

#### Commit 2: Implement STOCK_DRAW penalty ✅
**File coinvolti**:
- [x] `src/domain/services/scoring_service.py` → MODIFY
  - [x] Aggiungi `self.stock_draw_count = 0` in `__init__()`
  - [x] Implementa `_calculate_stock_draw_penalty()` progressive:
    ```python
    if self.stock_draw_count <= 20: return 0
    elif self.stock_draw_count <= 40: return -1
    else: return -2
    ```
  - [x] Aggiorna `_calculate_event_points()` per gestire `STOCK_DRAW`:
    ```python
    if event_type == ScoreEventType.STOCK_DRAW:
        self.stock_draw_count += 1
        return self._calculate_stock_draw_penalty()
    ```
  - [x] Aggiungi guard in `_calculate_recycle_penalty()`:
    ```python
    if recycle_count <= 0: return 0
    ```
  - [x] Aggiorna `reset()` per includere `self.stock_draw_count = 0`

- [ ] `tests/domain/services/test_scoring_service.py` → MODIFY
  - [ ] `test_stock_draw_penalty_progressive()` → 20 draw = 0pt, 25 draw = -5pt, 50 draw = -55pt
  - [ ] `test_stock_draw_boundaries()` **CRITICAL**:
    - [ ] `penalty(20) == 0` (last free)
    - [ ] `penalty(21) == -1` (first penalty)
    - [ ] `penalty(40) == -1` (last -1pt tier)
    - [ ] `penalty(41) == -2` (first -2pt tier)
  - [ ] `test_recycle_penalty_guard_zero()` **CRITICAL**:
    - [ ] `penalty(0) == 0`
    - [ ] `penalty(-1) == 0` (safety)

**Status commit 2**: ✅ DONE (SHA: fa524cc) - ⚠️ **TEST DA SCRIVERE**

---

#### Commit 3: Update time bonus (v2.0 values) ✅
**File coinvolti**:
- [x] `src/domain/services/scoring_service.py` → MODIFY
  - [x] Implementa `_safe_truncate(value: float, context: str) -> int`:
    ```python
    if value < 0:
        raise ValueError(f"Truncation safety violated: {value} < 0 (context: {context})")
    return int(value)
    ```
  - [x] Aggiorna `_calculate_time_bonus()` con v2.0 values:
    - [x] Timer OFF: `max(0, 1200 - (elapsed_minutes * 40))`
    - [x] Timer ON: `int(time_remaining_pct * 1000)`
    - [x] Usa `_safe_truncate()` invece di `int()` diretto

- [ ] `tests/domain/services/test_scoring_service.py` → MODIFY
  - [ ] `test_time_bonus_timer_off_v2()`:
    - [ ] 0min → 1200pt
    - [ ] 10min → 800pt
    - [ ] 30min → 0pt
  - [ ] `test_time_bonus_timer_on_v2()`:
    - [ ] 80% remaining → 800pt
    - [ ] 50% remaining → 500pt
  - [ ] `test_time_bonus_float_determinism()` → `bonus(1122.7) == bonus(1122.7)` (same input = same output)
  - [ ] `test_safe_truncate_raises_on_negative()` **CRITICAL**:
    - [ ] `_safe_truncate(-1.5, "test")` raises `ValueError`

**Status commit 3**: ✅ DONE (SHA: 005593c) - ⚠️ **TEST DA SCRIVERE**

---

#### Commit 4: Implement quality factors ✅
**File coinvolti**:
- [x] `src/domain/services/scoring_service.py` → MODIFY
  - [x] Implementa `_calculate_time_quality(elapsed_seconds: float) -> float`:
    - [x] Timer OFF: thresholds 10/20/30/45 min → 1.5/1.2/1.0/0.8/0.7
    - [x] Timer ON: thresholds 80%/50%/25%/0% remaining → 1.5/1.2/1.0/0.8/0.7
  - [x] Implementa `_calculate_move_quality(move_count: int) -> float`:
    - [x] Thresholds 80/120/180/250 → 1.3/1.1/1.0/0.85/0.7
  - [x] Implementa `_calculate_recycle_quality(recycle_count: int) -> float`:
    - [x] Thresholds 0/2/4/7 → 1.2/1.1/1.0/0.8/0.5

- [ ] `tests/domain/services/test_scoring_service.py` → MODIFY
  - [ ] `test_time_quality_timer_off()` → Verifica tutte soglie (5min=1.5, 15min=1.2, ...)
  - [ ] `test_time_quality_timer_on()` → Verifica percentuali (80%=1.5, 50%=1.2, ...)
  - [ ] `test_move_quality_thresholds()` → 75=1.3, 100=1.1, 150=1.0, 200=0.85, 300=0.7
  - [ ] `test_recycle_quality_thresholds()` → 0=1.2, 2=1.1, 4=1.0, 6=0.8, 10=0.5

**Status commit 4**: ✅ DONE (SHA: 5919715) - ⚠️ **TEST DA SCRIVERE**

---

#### Commit 5: Implement composite victory bonus ✅
**File coinvolti**:
- [x] `src/domain/services/scoring_service.py` → MODIFY
  - [x] Rinomina `_calculate_victory_bonus()` → `_calculate_victory_bonus_with_quality()`
  - [x] Return type: `tuple[int, float]` (bonus, quality_multiplier)
  - [x] Formula:
    ```python
    quality_multiplier = (
        time_quality * 0.35 +
        move_quality * 0.35 +
        recycle_quality * 0.30
    )
    victory_bonus = self._safe_truncate(
        config.victory_bonus_base * quality_multiplier,
        "victory_bonus"
    )
    return victory_bonus, quality_multiplier
    ```
  - [x] Log breakdown (time/move/recycle quality + multiplier finale)

- [ ] `tests/domain/services/test_scoring_service.py` → MODIFY
  - [ ] `test_victory_bonus_perfect()` → 5min, 75 mosse, 0 ricicli → 536pt (max teorico)
  - [ ] `test_victory_bonus_average()` → 25min, 160 mosse, 4 ricicli → 400pt
  - [ ] `test_victory_bonus_poor()` → 50min, 300 mosse, 10 ricicli → ~252pt
  - [ ] `test_victory_bonus_max_theoretical()` **CRITICAL**:
    - [ ] `bonus <= 536` (hard limit)
    - [ ] `quality <= 1.34` (max multiplier)

**Status commit 5**: ✅ DONE (SHA: 20aad2c) - ⚠️ **TEST DA SCRIVERE**

---

#### Commit 6: Update calculate_final_score() ✅
**File coinvolti**:
- [x] `src/domain/models/scoring.py` → MODIFY
  - [x] Aggiungi campo a `FinalScore` dataclass:
    ```python
    victory_quality_multiplier: float  # NEW v2.0
    ```

- [x] `src/domain/services/scoring_service.py` → MODIFY
  - [x] Aggiorna `calculate_final_score()`:
    - [x] Se `is_victory == False`:
      ```python
      time_bonus = 0
      victory_bonus = 0
      quality_multiplier = 0.0  # Explicit zero
      ```
    - [x] Se `is_victory == True`:
      ```python
      time_bonus = self._calculate_time_bonus(...)
      victory_bonus, quality_multiplier = self._calculate_victory_bonus_with_quality(...)
      ```
    - [x] Return `FinalScore` con `victory_quality_multiplier=quality_multiplier` persistito
    - [x] Usa `_safe_truncate()` per `provisional_score`

- [ ] `tests/domain/services/test_scoring_service.py` → MODIFY
  - [ ] `test_final_score_victory_complete()` → End-to-end vittoria (10 mosse, 5 reveal, 30 draw, 2 recycle)
  - [ ] `test_final_score_abandonment_no_bonuses()` **CRITICAL**:
    - [ ] `is_victory=False` → `time_bonus == 0` AND `victory_bonus == 0`
  - [ ] `test_final_score_clamping()` → Score negativo clamped a 0
  - [ ] `test_final_score_persists_quality_multiplier()` **CRITICAL**:
    - [ ] `final_score.victory_quality_multiplier` field exists
    - [ ] Range 0.6-1.34 per vittoria, 0.0 per abbandono

- [ ] `tests/domain/services/test_scoring_determinism.py` → CREATE
  - [ ] `test_scoring_commutativity()` **CRITICAL**:
    - [ ] Shuffle 10 volte eventi random → stesso punteggio finale
  - [ ] `test_truncation_bias_bounded()` **CRITICAL**:
    - [ ] Bias < 3pt su punteggio tipico ~1500pt

**Status commit 6**: ✅ DONE (SHA: 92ab3de) - ⚠️ **TEST DA SCRIVERE**

---

### Phase 2: Config Externalization (2 commits)

#### Commit 7: Create config JSON + loader ✅ / ❌
**File coinvolti**:
- [ ] `config/scoring_config.json` → CREATE
  - [ ] Struttura completa JSON con tutti parametri v2.0 (vedi spec)
  - [ ] `"version": "2.0.0"`
  - [ ] Event points, stock_draw thresholds, recycle penalties
  - [ ] Deck bonuses, draw bonuses, difficulty multipliers
  - [ ] Time bonus params, victory bonus params

- [ ] `src/infrastructure/config/scoring_config_loader.py` → CREATE
  - [ ] `ScoringConfigLoader.load(path: Path = None) -> ScoringConfig`
    - [ ] Carica JSON, parse, valida schema
    - [ ] Fallback a `fallback_default()` se file missing
    - [ ] Raise `ValueError` se JSON malformed
  - [ ] `ScoringConfigLoader.fallback_default() -> ScoringConfig`
    - [ ] Return hardcoded v2.0 defaults
  - [ ] `ScoringConfigLoader._parse_and_validate(data: dict) -> ScoringConfig`
    - [ ] Version check
    - [ ] Convert difficulty_multipliers keys (JSON string → int)
    - [ ] Validation via `ScoringConfig.__post_init__`

- [ ] `tests/infrastructure/config/test_scoring_config_loader.py` → CREATE
  - [ ] `test_config_loader_valid_json()` → Load config, verify version=2.0.0
  - [ ] `test_config_loader_missing_file()` → Fallback to defaults
  - [ ] `test_config_loader_malformed_json()` → Raise ValueError

**Status commit 7**: ❌ NOT STARTED

---

#### Commit 8: Integrate loader into GameEngine ✅ / ❌
**File coinvolti**:
- [ ] `src/application/game_engine.py` → MODIFY
  - [ ] `__init__()`:
    ```python
    from src.infrastructure.config.scoring_config_loader import ScoringConfigLoader
    
    self.scoring_config = ScoringConfigLoader.load()
    self.scoring_service = ScoringService(
        config=self.scoring_config,  # Injected from JSON
        ...
    )
    ```

- [ ] `tests/application/test_game_engine.py` → MODIFY
  - [ ] `test_game_engine_uses_external_config()` → Verify engine loads config v2.0 from JSON

**Status commit 8**: ❌ NOT STARTED

---

### Phase 3: TTS Transparency (1 commit)

#### Commit 9: Implement formatters + warnings ✅ / ❌
**File coinvolti**:
- [ ] `src/presentation/formatters/score_formatter.py` → CREATE/MODIFY
  - [ ] `format_summary(final_score: FinalScore) -> str`:
    - [ ] Output: "Vittoria in X minuti con Y mosse. Punteggio totale: Z punti."
  - [ ] `format_detailed(final_score: FinalScore) -> str`:
    - [ ] Breakdown completo (base, deck, draw, multiplier, provisional, time, victory con quality)
    - [ ] Null-safe: se `victory_quality_multiplier < 0` → "(legacy)" invece di qualità
  - [ ] `format_threshold_warning(event_type: str, current: int, threshold: int, penalty: int) -> str`:
    - [ ] Stock draw: "Attenzione: superata soglia 20 pescate. Penalità -1 punto per pescata."
    - [ ] Recycle: "Attenzione: terzo riciclo. Dal prossimo riciclo penalità -10 punti."

- [ ] `src/application/game_engine.py` → MODIFY
  - [ ] Integra warnings in `draw_from_stock()`:
    ```python
    if self.settings.score_warnings_enabled and stock_draw_count == 21:
        warning = ScoreFormatter.format_threshold_warning("stock_draw", 21, 20, -1)
        self.tts.speak(warning)
    ```
  - [ ] Integra warnings in `recycle_waste()`:
    ```python
    if self.settings.score_warnings_enabled and recycle_count == 3:
        warning = ScoreFormatter.format_threshold_warning("recycle", 3, 2, -10)
        self.tts.speak(warning)
    ```

- [ ] `src/domain/services/game_settings.py` → MODIFY
  - [ ] Aggiungi setting: `score_warnings_enabled: bool = True`

- [ ] `src/infrastructure/storage/score_storage.py` → MODIFY
  - [ ] `load_all_scores()`:
    - [ ] Aggiungi retrocompat sentinel:
      ```python
      if "victory_quality_multiplier" not in score_dict:
          score_dict["victory_quality_multiplier"] = -1.0  # Legacy
          score_dict["scoring_system_version"] = "1.0"
      ```

- [ ] `tests/presentation/formatters/test_score_formatter.py` → CREATE
  - [ ] `test_format_summary()` → Output contiene "Vittoria", minuti, mosse, punteggio
  - [ ] `test_format_detailed()` → Breakdown completo, null-safe legacy
  - [ ] `test_format_threshold_warning()` → Warning stock_draw 21, recycle 3

- [ ] `tests/application/test_game_engine.py` → MODIFY
  - [ ] `test_threshold_warning_stock_draw()` → Warning triggered at draw 21
  - [ ] `test_threshold_warning_recycle()` → Warning triggered at recycle 3

**Status commit 9**: ❌ NOT STARTED

---

## ✅ Criteri di Completamento

L'implementazione è completa quando:

- [ ] Tutti 9 commit completati e testati
- [ ] Test coverage ≥ 95% su `ScoringService`, `ScoringConfig`, `ScoringConfigLoader`
- [ ] Tutti test esistenti passano (nessuna regressione)
- [ ] Test deterministici (commutativity, bias) passano
- [ ] `CHANGELOG.md` aggiornato con breaking changes
- [ ] `README.md` aggiornato con nuova sezione scoring
- [ ] Versione bumped a v2.6.0 (MINOR con breaking changes documentati)
- [ ] Commit messages seguono conventional commits
- [ ] Branch `refactoring-engine` pronto per merge

---

## 📝 Aggiornamenti Documentazione (Post-Implementation)

- [ ] `CHANGELOG.md` → Sezione v2.6.0:
  - [ ] 🚨 BREAKING CHANGE: Scoring system v2.0 (punteggi non comparabili con v1.0)
  - [ ] ✨ Victory bonus composite (35/35/30 weights)
  - [ ] ✨ Config esterna `config/scoring_config.json`
  - [ ] 🐛 FIX: Abbandoni non ricevono time/victory bonus
  - [ ] 🐛 FIX: STOCK_DRAW penalty progressive
  - [ ] 🚀 TTS: Threshold warnings configurabili
  - [ ] 📚 Migration guide v1.0 → v2.0

- [ ] `README.md` → Nuova sezione:
  ```markdown
  ## Sistema di Punteggio v2.0
  
  Il gioco utilizza un sistema di punteggio deterministico che premia:
  - Efficienza nelle mosse (35% peso)
  - Velocità di completamento (35% peso)
  - Minimizzazione ricicli (30% peso)
  
  **Nota**: I punteggi v2.0 non sono comparabili con versioni precedenti.
  Consulta [docs/SCORING_SYSTEM_V2.md](docs/SCORING_SYSTEM_V2.md) per dettagli.
  ```

- [ ] Version bump:
  - [ ] `src/__init__.py` → `__version__ = "2.6.0"`
  - [ ] Commit: `chore: bump version to v2.6.0`

---

## 📌 Note Operative Rapide

### Ordine Implementazione Raccomandato
1. Commit 1-6 (Core logic) → Testare progressivamente
2. Commit 7-8 (Config) → Verificare fallback funziona
3. Commit 9 (TTS) → Test manuale accessibilità
4. Full test suite run
5. Playtesting manuale (5-10 partite)
6. Documentation update
7. Version bump + merge

### Test Command
```bash
pytest tests/ -v --cov=src/domain/services/scoring_service --cov-report=term-missing
```

### Commit Message Convention
```
feat(scoring): [descrizione]
fix(scoring): [descrizione]
test(scoring): [descrizione]
refactor(scoring): [descrizione]
docs(scoring): [descrizione]
```

---

**Fine TODO Operativo**

Consultare sempre `docs/SCORING_SYSTEM_V2.md` per dettagli tecnici completi.
