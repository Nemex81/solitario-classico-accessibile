# TODO: Integrazione Punteggio nel Report Partita (Comando R)

**Data creazione**: 11 Febbraio 2026, 02:05 CET  
**Versione target**: v1.5.2  
**Branch**: `copilot/implement-scoring-system-v2`  
**Stato**: 🟡 PIANIFICATO

---

## 🎯 Obiettivo

Integrare le informazioni del **punteggio provvisorio** nel report di partita (comando **R**), posizionandole tra **tempo trascorso** e **statistiche carte**.

### Motivazione

L'utente ha richiesto di includere il punteggio nel report partita per avere un feedback completo sullo stato del gioco in un'unica lettura TTS, senza dover premere comandi separati (P).

---

## 📋 Stato Attuale vs Desiderato

### **Output Attuale** (comando R)

```
Report partita.
Mosse: 42.
Tempo trascorso: 5:30.
Carte nelle pile semi: 28.
```

### **Output Desiderato** (con scoring abilitato)

```
Report partita.
Mosse: 42.
Tempo trascorso: 5:30.
Punteggio provvisorio: 350 punti (Base: 200 | Moltiplicatore 1.5x | Bonus mazzo: 150).
Carte nelle pile semi: 28.
```

### **Output Desiderato** (con scoring disabilitato)

```
Report partita.
Mosse: 42.
Tempo trascorso: 5:30.
Sistema punti disattivato.
Carte nelle pile semi: 28.
```

---

## 🏗️ Piano Implementazione

### Step 1: Domain Layer - Extend `get_game_report()` ✅

**File**: `src/domain/services/game_service.py`  
**Linee modificate**: ~10 (LOC produzione)  
**Complessità**: BASSA

#### Modifiche Codice

**Posizione**: Metodo `get_game_report()` (attualmente linee ~450-470)

**Codice da sostituire**:

```python
def get_game_report(self) -> Tuple[str, Optional[str]]:
    """Get complete game report (no hint - report is complete).
    
    Returns:
        Tuple[str, Optional[str]]: (message, None)
        - message: Complete game statistics
        - hint: None (report is self-contained)
    """
    stats = self.get_statistics()
    elapsed = int(stats['elapsed_time'])
    minutes = elapsed // 60
    seconds = elapsed % 60
    time_str = f"{minutes}:{seconds:02d}"
    
    report = "Report partita.\n"
    report += f"Mosse: {stats['move_count']}.\n"
    report += f"Tempo trascorso: {time_str}.\n"
    report += f"Carte nelle pile semi: {stats['total_foundation_cards']}.\n"
    
    return (report, None)
```

**Codice nuovo**:

```python
def get_game_report(self) -> Tuple[str, Optional[str]]:
    """Get complete game report with optional scoring info (v1.5.2).
    
    Returns:
        Tuple[str, Optional[str]]: (message, None)
        - message: Complete game statistics including provisional score if enabled
        - hint: None (report is self-contained)
    
    Examples:
        >>> # With scoring enabled
        >>> message, hint = service.get_game_report()
        >>> # "Report partita.\nMosse: 42.\nTempo trascorso: 5:30.\nPunteggio provvisorio: 350 punti..."
        
        >>> # With scoring disabled
        >>> message, hint = service.get_game_report()
        >>> # "Report partita.\nMosse: 42.\nTempo trascorso: 5:30.\nSistema punti disattivato.\n..."
    """
    stats = self.get_statistics()
    elapsed = int(stats['elapsed_time'])
    minutes = elapsed // 60
    seconds = elapsed % 60
    time_str = f"{minutes}:{seconds:02d}"
    
    report = "Report partita.\n"
    report += f"Mosse: {stats['move_count']}.\n"
    report += f"Tempo trascorso: {time_str}.\n"
    
    # ✅ NUOVO (v1.5.2): Aggiungi info punteggio se scoring abilitato
    if self.scoring:
        provisional = self.scoring.calculate_provisional_score()
        report += f"Punteggio provvisorio: {provisional.total_score} punti "
        report += f"(Base: {provisional.base_score} | "
        report += f"Moltiplicatore {provisional.difficulty_multiplier}x | "
        report += f"Bonus mazzo: {provisional.deck_bonus}).\n"
    else:
        report += "Sistema punti disattivato.\n"
    
    report += f"Carte nelle pile semi: {stats['total_foundation_cards']}.\n"
    
    return (report, None)
```

#### Logica Implementata

1. **Check scoring service**: `if self.scoring:` determina se scoring è abilitato
2. **Calcolo provvisorio**: Chiama `calculate_provisional_score()` per ottenere punteggio corrente
3. **Formatting compatto**: Una singola riga con breakdown (base + multiplier + bonus mazzo)
4. **Fallback**: Se scoring OFF → messaggio "Sistema punti disattivato"

#### Vantaggi Architetturali

- ✅ **Domain layer puro**: Nessuna dipendenza da Presentation layer
- ✅ **Backward compatible**: Se `scoring=None` → funziona come v1.5.1
- ✅ **Self-contained**: Report completo senza hint necessari
- ✅ **TTS-friendly**: Formato chiaro per screen reader

---

### Step 2: Testing - Validazione Completa ✅

**File nuovo**: `tests/unit/src/domain/services/test_game_service_report_scoring.py`  
**Linee totali**: ~80 (LOC test)  
**Test da implementare**: 5

#### Test Suite Completa

```python
"""Unit tests for GameService.get_game_report() with scoring integration (v1.5.2).

Tests verify:
- Provisional score included when scoring enabled
- "Disattivato" message when scoring OFF
- Correct report structure order
- Zero score edge case
"""

import pytest
from src.domain.services.game_service import GameService
from src.domain.services.scoring_service import ScoringService
from src.domain.models.scoring import ScoringConfig, ScoreEventType


class TestGameReportWithScoring:
    """Test get_game_report() integration with scoring system (v1.5.2)."""
    
    def test_report_includes_provisional_score_when_enabled(self, game_service_with_scoring):
        """Report includes provisional score breakdown when scoring enabled.
        
        Given: Scoring service is enabled
        And: Some scoring events have been recorded
        When: get_game_report() is called
        Then: Report includes provisional score with breakdown
        And: Breakdown shows base score, multiplier, and deck bonus
        """
        # Setup: Record some scoring events
        game_service_with_scoring.scoring.record_event(
            ScoreEventType.TABLEAU_TO_FOUNDATION, "3 di Cuori"
        )
        game_service_with_scoring.scoring.record_event(
            ScoreEventType.CARD_REVEALED, "Asso di Quadri"
        )
        
        # Execute
        message, hint = game_service_with_scoring.get_game_report()
        
        # Verify scoring info included
        assert "Punteggio provvisorio:" in message
        assert "punti" in message
        assert "Base:" in message
        assert "Moltiplicatore" in message
        assert "Bonus mazzo:" in message
        
        # Verify no hint (report is complete)
        assert hint is None
    
    def test_report_shows_disabled_when_scoring_off(self, game_service_without_scoring):
        """Report shows 'Sistema punti disattivato' when scoring OFF.
        
        Given: Scoring service is None (disabled)
        When: get_game_report() is called
        Then: Report includes "Sistema punti disattivato" message
        And: No score breakdown is shown
        """
        # Execute
        message, hint = game_service_without_scoring.get_game_report()
        
        # Verify disabled message
        assert "Sistema punti disattivato" in message
        
        # Verify no score info
        assert "Punteggio" not in message
        assert "Base:" not in message
        assert "Moltiplicatore" not in message
        
        # Verify no hint
        assert hint is None
    
    def test_report_structure_order_with_scoring(self, game_service_with_scoring):
        """Report follows correct line order: mosse → tempo → score → carte.
        
        Given: Scoring is enabled
        When: get_game_report() is called
        Then: Report lines are in expected order:
            1. "Report partita."
            2. "Mosse: X."
            3. "Tempo trascorso: X:XX."
            4. "Punteggio provvisorio: X punti..."
            5. "Carte nelle pile semi: X."
        """
        # Execute
        message, _ = game_service_with_scoring.get_game_report()
        
        # Parse lines
        lines = message.strip().split("\n")
        
        # Verify structure
        assert len(lines) == 5
        assert "Report partita" in lines[0]
        assert lines[1].startswith("Mosse:")
        assert lines[2].startswith("Tempo trascorso:")
        assert lines[3].startswith("Punteggio provvisorio:")
        assert lines[4].startswith("Carte nelle pile semi:")
    
    def test_report_structure_order_without_scoring(self, game_service_without_scoring):
        """Report follows correct line order when scoring OFF.
        
        Given: Scoring is disabled (None)
        When: get_game_report() is called
        Then: Report lines are in expected order:
            1. "Report partita."
            2. "Mosse: X."
            3. "Tempo trascorso: X:XX."
            4. "Sistema punti disattivato."
            5. "Carte nelle pile semi: X."
        """
        # Execute
        message, _ = game_service_without_scoring.get_game_report()
        
        # Parse lines
        lines = message.strip().split("\n")
        
        # Verify structure
        assert len(lines) == 5
        assert "Report partita" in lines[0]
        assert lines[1].startswith("Mosse:")
        assert lines[2].startswith("Tempo trascorso:")
        assert lines[3].startswith("Sistema punti disattivato")
        assert lines[4].startswith("Carte nelle pile semi:")
    
    def test_report_shows_zero_score_when_no_events(self, game_service_with_scoring):
        """Report correctly shows 0 points when no scoring events recorded.
        
        Given: Scoring is enabled
        And: No scoring events have been recorded
        When: get_game_report() is called
        Then: Report shows "Punteggio provvisorio: 0 punti"
        And: Base score is 0
        """
        # Execute (no events recorded)
        message, _ = game_service_with_scoring.get_game_report()
        
        # Verify zero score
        assert "Punteggio provvisorio: 0 punti" in message or "Punteggio provvisorio: 150 punti" in message  # 150 = deck bonus only
        assert "Base: 0" in message


# ========================================
# FIXTURES
# ========================================

@pytest.fixture
def game_service_with_scoring(french_deck, game_table, solitaire_rules):
    """GameService instance with scoring enabled (medium difficulty).
    
    Returns:
        GameService with ScoringService configured for level 2 (1.25x multiplier)
    """
    config = ScoringConfig(difficulty_level=2)  # Medium difficulty
    scoring = ScoringService(config)
    service = GameService(game_table, solitaire_rules, scoring=scoring)
    service.start_game()
    return service


@pytest.fixture
def game_service_without_scoring(french_deck, game_table, solitaire_rules):
    """GameService instance with scoring disabled (None).
    
    Returns:
        GameService without scoring service (free-play mode)
    """
    service = GameService(game_table, solitaire_rules, scoring=None)
    service.start_game()
    return service
```

#### Test Coverage

| Test | Copertura | Verifica |
|------|-----------|----------|
| `test_report_includes_provisional_score_when_enabled` | Scoring ON | Presenza breakdown completo |
| `test_report_shows_disabled_when_scoring_off` | Scoring OFF | Messaggio "disattivato" |
| `test_report_structure_order_with_scoring` | Ordine linee | Sequenza corretta (con score) |
| `test_report_structure_order_without_scoring` | Ordine linee | Sequenza corretta (senza score) |
| `test_report_shows_zero_score_when_no_events` | Edge case | Punteggio zero gestito |

**Coverage target**: ≥95% del metodo `get_game_report()`

---

## ✅ Checklist Implementazione

### 📝 Domain Layer

- [ ] **Task 1.1**: Aprire file `src/domain/services/game_service.py`
- [ ] **Task 1.2**: Localizzare metodo `get_game_report()` (~linea 450)
- [ ] **Task 1.3**: Aggiungere check `if self.scoring:`
- [ ] **Task 1.4**: Chiamare `self.scoring.calculate_provisional_score()`
- [ ] **Task 1.5**: Formattare breakdown compatto (1 riga)
- [ ] **Task 1.6**: Aggiungere else branch per scoring OFF
- [ ] **Task 1.7**: Aggiornare docstring con esempi v1.5.2
- [ ] **Task 1.8**: Verificare indentazione e formatting

### 🧪 Testing

- [ ] **Task 2.1**: Creare file `tests/unit/src/domain/services/test_game_service_report_scoring.py`
- [ ] **Task 2.2**: Implementare fixture `game_service_with_scoring`
- [ ] **Task 2.3**: Implementare fixture `game_service_without_scoring`
- [ ] **Task 2.4**: Implementare `test_report_includes_provisional_score_when_enabled`
- [ ] **Task 2.5**: Implementare `test_report_shows_disabled_when_scoring_off`
- [ ] **Task 2.6**: Implementare `test_report_structure_order_with_scoring`
- [ ] **Task 2.7**: Implementare `test_report_structure_order_without_scoring`
- [ ] **Task 2.8**: Implementare `test_report_shows_zero_score_when_no_events`
- [ ] **Task 2.9**: Run test suite: `pytest tests/unit/src/domain/services/test_game_service_report_scoring.py -v`
- [ ] **Task 2.10**: Verificare 5/5 test PASSED

### 🔍 Validation

- [ ] **Task 3.1**: Run full test suite: `pytest tests/unit/src/domain/services/ -v`
- [ ] **Task 3.2**: Verificare nessuna regressione su test esistenti
- [ ] **Task 3.3**: Test manuale: Comando R durante partita (scoring ON)
- [ ] **Task 3.4**: Test manuale: Comando R durante partita (scoring OFF)
- [ ] **Task 3.5**: Verificare TTS clarity con screen reader
- [ ] **Task 3.6**: Verificare ordine linee report corretto
- [ ] **Task 3.7**: Test edge case: punteggio zero (nessun evento)
- [ ] **Task 3.8**: Test edge case: punteggio alto (molti eventi)

### 📝 Documentazione

- [ ] **Task 4.1**: Aggiornare `CHANGELOG.md` v1.5.2 con questa modifica
- [ ] **Task 4.2**: Aggiungere sotto sezione "🎮 UX Improvements" in v1.5.2
- [ ] **Task 4.3**: Documentare comando R enhanced con scoring info
- [ ] **Task 4.4**: Aggiornare contatore modifiche tecniche (+1 file modificato)
- [ ] **Task 4.5**: Committare con message: `feat(domain): Add provisional score to game report (command R)`

---

## 📊 Metriche Implementazione

| Metrica | Valore |
|---------|--------|
| **File modificati** | 1 (game_service.py) |
| **File nuovi** | 1 (test file) |
| **LOC produzione** | ~10 |
| **LOC test** | ~80 |
| **Totale LOC** | ~90 |
| **Test implementati** | 5 |
| **Coverage target** | ≥95% |
| **Complessità** | BASSA |
| **Tempo stimato** | 30-45 minuti |
| **Breaking changes** | NESSUNO |
| **Backward compatibility** | 100% |

---

## 🚀 Benefici UX

### Prima (v1.5.1)

```
Report partita.
Mosse: 42.
Tempo trascorso: 5:30.
Carte nelle pile semi: 28.
```

**Problemi**:
- ❌ Nessuna info punteggio nel report
- ❌ Serve comando P separato per vedere score
- ❌ Feedback non completo in un'unica lettura

### Dopo (v1.5.2 con scoring ON)

```
Report partita.
Mosse: 42.
Tempo trascorso: 5:30.
Punteggio provvisorio: 350 punti (Base: 200 | Moltiplicatore 1.5x | Bonus mazzo: 150).
Carte nelle pile semi: 28.
```

**Vantaggi**:
- ✅ Info punteggio inclusa nel report standard
- ✅ Breakdown compatto e chiaro
- ✅ Report completo con una sola lettura TTS
- ✅ Comando P ancora disponibile per dettagli estesi

### Dopo (v1.5.2 con scoring OFF)

```
Report partita.
Mosse: 42.
Tempo trascorso: 5:30.
Sistema punti disattivato.
Carte nelle pile semi: 28.
```

**Vantaggi**:
- ✅ Messaggio chiaro quando free-play mode attivo
- ✅ Nessuna confusione per utenti che disabilitano scoring

---

## 📝 Entry CHANGELOG v1.5.2 (da aggiungere)

**Sezione**: `### 🎮 UX Improvements`

**Testo da inserire** (dopo "Nuovi Comandi"):

```markdown
**Comando R Enhanced - Report con Punteggio**
- Comando R (report partita) ora include info punteggio provvisorio
- Posizionamento: dopo tempo trascorso, prima statistiche carte
- Formato compatto: "Punteggio provvisorio: X punti (Base | Moltiplicatore | Bonus)"
- Free-play mode: mostra "Sistema punti disattivato" quando scoring OFF
- Benefit: feedback completo sullo stato partita in un'unica lettura TTS
- File modificato: `src/domain/services/game_service.py` (+10 linee)
- Test: 5 unit tests (100% passing)
```

**Posizione**: Inserire nella sezione `### 🎮 UX Improvements` della v1.5.2, subito dopo la sottosezione "Nuovi Comandi".

---

## 🔗 File Coinvolti

### Produzione

1. **`src/domain/services/game_service.py`**
   - Metodo: `get_game_report()`
   - Modifica: Aggiungi integrazione scoring
   - Linee: ~10 aggiunte

### Testing

2. **`tests/unit/src/domain/services/test_game_service_report_scoring.py`** (NUOVO)
   - Test classe: `TestGameReportWithScoring`
   - Test metodi: 5
   - Fixtures: 2
   - Linee: ~80 totali

### Documentazione

3. **`CHANGELOG.md`**
   - Sezione: v1.5.2 → UX Improvements
   - Aggiunta: Comando R enhanced
   - Linee: ~8 aggiunte

4. **`docs/TODO_REPORT_SCORING_INTEGRATION.md`** (QUESTO FILE)
   - Piano completo implementazione
   - Linee: ~500+ (documentazione)

---

## ✅ Stato Avanzamento

**Legenda**:
- 🔴 **NON INIZIATO**: Task non ancora avviato
- 🟡 **IN CORSO**: Task in lavorazione
- 🟢 **COMPLETATO**: Task finito e validato

### Progress Tracker

| Step | Task | Stato | Note |
|------|------|-------|------|
| 1 | Domain Layer - Modifica `get_game_report()` | 🔴 | Attende implementazione |
| 2 | Testing - Crea file test | 🔴 | Attende implementazione |
| 3 | Testing - Implementa 5 test | 🔴 | Attende implementazione |
| 4 | Validation - Run test suite | 🔴 | Attende implementazione |
| 5 | Validation - Test manuali | 🔴 | Attende implementazione |
| 6 | Documentazione - Update CHANGELOG | 🔴 | **ULTIMO STEP** |

**Progress totale**: 0/6 (0%)

---

## 📌 Note Implementative

### Decisioni Architetturali

1. **No Presentation Layer Separation**
   - Formatting score breakdown rimane in Domain layer
   - Motivazione: Semplicità + evita dipendenza ScoreFormatter
   - Trade-off accettabile per 1 riga di formatting

2. **Backward Compatibility Garantita**
   - Check `if self.scoring:` previene errori quando scoring=None
   - Comportamento v1.5.1 invariato se scoring disabilitato
   - Nessuna breaking change per utenti esistenti

3. **TTS Optimization**
   - Formato compatto: 1 riga per info punteggio
   - Separatori chiari: pipe `|` tra componenti
   - Nessun simbolo complesso (ok per screen reader)

### Edge Cases Gestiti

- ✅ Scoring service = None (free-play mode)
- ✅ Zero eventi scoring (punteggio = bonus mazzo only)
- ✅ Molti eventi scoring (punteggio alto)
- ✅ Report chiamato prima start_game() (elapsed=0)

---

## 🛠️ Comandi Utili

### Testing

```bash
# Run nuovo test file
pytest tests/unit/src/domain/services/test_game_service_report_scoring.py -v

# Run con coverage
pytest tests/unit/src/domain/services/test_game_service_report_scoring.py --cov=src/domain/services/game_service --cov-report=term-missing

# Run full domain test suite
pytest tests/unit/src/domain/services/ -v
```

### Git Workflow

```bash
# Commit modifiche Domain layer
git add src/domain/services/game_service.py
git commit -m "feat(domain): Add provisional score to game report (command R)

Integrate scoring info into get_game_report():
- Shows provisional score breakdown when scoring enabled
- Shows 'Sistema punti disattivato' when scoring OFF
- Maintains backward compatibility (scoring=None)
- Positioned between time and foundation stats
- TTS-optimized compact format (1 line)"

# Commit test suite
git add tests/unit/src/domain/services/test_game_service_report_scoring.py
git commit -m "test(domain): Add 5 tests for game report scoring integration

Test coverage:
- Provisional score included when scoring enabled
- Disabled message when scoring OFF
- Correct report line order (with/without scoring)
- Zero score edge case
- 100% test passing"

# Commit CHANGELOG update
git add CHANGELOG.md
git commit -m "docs: Update CHANGELOG v1.5.2 with command R enhancement

Documented UX improvement:
- Command R now includes provisional score info
- Compact breakdown format
- Free-play mode message"
```

---

## 🎯 Criteri di Successo

### Funzionalità

- ✅ Comando R include punteggio quando scoring ON
- ✅ Comando R mostra "disattivato" quando scoring OFF
- ✅ Breakdown compatto e leggibile (1 riga)
- ✅ Ordine corretto: mosse → tempo → score → carte

### Qualità

- ✅ 5/5 test PASSED
- ✅ Nessuna regressione su test esistenti
- ✅ Coverage ≥95% del metodo modificato
- ✅ TTS clarity verificata con screen reader

### Documentazione

- ✅ CHANGELOG aggiornato con entry v1.5.2
- ✅ Commit messages dettagliati
- ✅ Questo TODO file completato

---

## 📝 Riferimenti

- **Issue GitHub**: N/A (feature request utente diretto)
- **Branch**: `copilot/implement-scoring-system-v2`
- **Versione target**: v1.5.2
- **File piano**: `docs/TODO_REPORT_SCORING_INTEGRATION.md` (questo file)
- **Related docs**:
  - `docs/IMPLEMENTATION_SCORING_SYSTEM.md`
  - `docs/TODO_SCORING.md`
  - `README.md` (sezione Sistema Punti v1.5.2)

---

**Creato da**: Utente Nemex81 + AI Assistant  
**Data**: 11 Febbraio 2026, 02:05 CET  
**Status**: 🟡 READY FOR IMPLEMENTATION
