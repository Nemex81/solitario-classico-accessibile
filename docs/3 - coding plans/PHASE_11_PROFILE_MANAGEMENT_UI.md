# Piano di Correzione: TimerStats Extension v3.1.1 - Stats Formatter AttributeError Fix

**Branch**: `copilot/implement-profile-system-v3-1-0`  
**Tipo**: Bug Fix + Model Extension  
**Versione Target**: v3.1.1 (patch bump - bug fix con model extension)  
**Stima Tempo**: 20-25 minuti (agent time)  
**Commits Previsti**: 2-3 atomici  

---

## 📋 **OVERVIEW**

### **Problema Corrente**

DetailedStatsDialog crash con `AttributeError` quando aperto su profilo con 0 partite:

```
AttributeError: 'TimerStats' object has no attribute 'games_without_timer'. 
Did you mean: 'games_with_timer'?
```

**Root Cause**: StatsFormatter assume attributi TimerStats che non esistono nel Domain Model.

### **Soluzione Sistemica**

Estendere TimerStats Domain Model per tracciare:
1. `strict_mode_games` (partite con STRICT timer)
2. `permissive_mode_games` (partite con PERMISSIVE timer)

Aggiornare StatsFormatter per:
1. Calcolare `games_without_timer` da GlobalStats (cross-stat)
2. Usare attributi reali di TimerStats (non inventati)
3. Richiedere GlobalStats come parametro aggiuntivo

**Rationale Architetturale**:
- ✅ Business logic nel Domain Layer (non in Presentation)
- ✅ Single Source of Truth (nessun calcolo duplicato)
- ✅ Backward compatible (from_dict() con defaults)
- ✅ Future-proof (supporta analytics avanzate)

---

## 🎯 **OBIETTIVI**

1. ✅ Estendere TimerStats con 2 nuovi campi (strict/permissive mode tracking)
2. ✅ Aggiornare StatsFormatter.format_timer_stats_detailed() signature
3. ✅ Aggiornare DetailedStatsDialog per passare GlobalStats
4. ✅ Garantire backward compatibility con profili v3.1.0
5. ✅ Implementare defensive programming (max(0, ...) per corruzione dati)
6. ✅ Aggiornare CHANGELOG.md a v3.1.1

---

## 📂 **FILE DA MODIFICARE**

| File | Tipo Modifica | Linee Interessate | Criticità |
|------|---------------|-------------------|-----------|
| `src/domain/models/statistics.py` | EXTEND + UPDATE | ~88, ~96, ~110, ~119 | HIGH |
| `src/presentation/formatters/stats_formatter.py` | SIGNATURE + BODY | ~227-263 | HIGH |
| `src/presentation/dialogs/detailed_stats_dialog.py` | PARAM PASS | ~63 | MEDIUM |
| `CHANGELOG.md` | VERSION BUMP | Top | LOW |

**Nessun altro file richiede modifiche** - impatto isolato a stats presentation.

---

## 🔧 **IMPLEMENTAZIONE DETTAGLIATA**

### **Commit 1/3: Extend TimerStats Domain Model**

**Titolo**: `fix(domain): Extend TimerStats with timer mode breakdown tracking [v3.1.1]`

**File**: `src/domain/models/statistics.py`

#### **Modifica 1.1: Aggiungi Nuovi Attributi**

**LOCALIZZAZIONE**: Dataclass `TimerStats` (linea ~88)

**DOPO** il campo `average_time_vs_limit: float = 0.0`, **AGGIUNGI**:

```python
    # ========== v3.1.1: Timer mode breakdown ==========
    strict_mode_games: int = 0           # Games with STRICT timer
    permissive_mode_games: int = 0       # Games with PERMISSIVE timer
```

---

#### **Modifica 1.2: Aggiorna update_from_session()**

**LOCALIZZAZIONE**: Metodo `update_from_session()` (linea ~91)

**DOPO** `self.games_with_timer += 1`, **AGGIUNGI**:

```python
        self.games_with_timer += 1
        
        # Track timer mode breakdown (v3.1.1)
        if outcome.timer_mode == "STRICT":
            self.strict_mode_games += 1
        elif outcome.timer_mode == "PERMISSIVE":
            self.permissive_mode_games += 1
        elif outcome.timer_mode != "OFF":
            # Defensive: log unexpected values for debugging
            from src.infrastructure.logging import game_logger as log
            log.warning_issued("TimerStats", f"Unknown timer_mode: {outcome.timer_mode}")
        
        # Classify outcome (linea originale continua...)
```

**NOTA**: Il logging per timer_mode sconosciuti è opzionale ma raccomandato per robustezza.

---

#### **Modifica 1.3: Aggiorna to_dict()**

**LOCALIZZAZIONE**: Metodo `to_dict()` (linea ~110)

**NEL DIZIONARIO DI RITORNO**, **AGGIUNGI** prima della chiusura:

```python
        return {
            "games_with_timer": self.games_with_timer,
            "victories_within_time": self.victories_within_time,
            "victories_overtime": self.victories_overtime,
            "defeats_timeout": self.defeats_timeout,
            "total_overtime": self.total_overtime,
            "average_overtime": self.average_overtime,
            "max_overtime": self.max_overtime,
            "average_time_vs_limit": self.average_time_vs_limit,
            "strict_mode_games": self.strict_mode_games,       # ✨ NEW
            "permissive_mode_games": self.permissive_mode_games  # ✨ NEW
        }
```

---

#### **Modifica 1.4: Aggiorna from_dict() (Backward Compatibility)**

**LOCALIZZAZIONE**: Metodo `from_dict()` (linea ~119)

**SOSTITUISCI** implementazione completa:

```python
    @classmethod
    def from_dict(cls, data: dict) -> "TimerStats":
        """Create from JSON dict (backward compatible with v3.1.0).
        
        Provides default values for v3.1.1 fields (strict_mode_games,
        permissive_mode_games) to handle profiles saved with v3.1.0.
        
        Version:
            v3.1.1: Added backward compatibility for new mode tracking
        """
        # Provide defaults for new v3.1.1 fields
        data = data.copy()
        data.setdefault("strict_mode_games", 0)
        data.setdefault("permissive_mode_games", 0)
        return cls(**data)
```

---

### **Commit 2/3: Update StatsFormatter Cross-Stat Support**

**Titolo**: `fix(presentation): Update StatsFormatter to use cross-stat calculations [v3.1.1]`

**File**: `src/presentation/formatters/stats_formatter.py`

#### **Modifica 2.1: Aggiorna Signature format_timer_stats_detailed()**

**LOCALIZZAZIONE**: Metodo `format_timer_stats_detailed()` (linea ~227)

**SOSTITUISCI** signature:

**PRIMA**:
```python
def format_timer_stats_detailed(self, stats: TimerStats) -> str:
    """Format timer stats page (Page 2 of detailed stats).
```

**DOPO**:
```python
def format_timer_stats_detailed(self, stats: TimerStats, global_stats: GlobalStats) -> str:
    """Format timer stats page (Page 2 of detailed stats).
    
    Args:
        stats: TimerStats instance with timer-specific data
        global_stats: GlobalStats instance for cross-stat calculations
        
    Returns:
        Multi-line formatted text for timer performance (Page 2/3)
        
    Note:
        v3.1.1: Now requires global_stats parameter for games_without_timer
        calculation and complete timer mode breakdown display.
        
    Version:
        v3.1.1: Added global_stats parameter for cross-stat support
```

---

#### **Modifica 2.2: Sostituisci Body Completo**

**LOCALIZZAZIONE**: Metodo `format_timer_stats_detailed()` body (linee ~228-263)

**SOSTITUISCI** tutto il corpo con:

```python
    header = f"{'=' * 56}\n"
    header += f"    STATISTICHE TIMER\n"
    header += f"{'=' * 56}\n\n"
    
    # Calculate games_without_timer from GlobalStats (defensive: handle corruption)
    games_without_timer = max(0, global_stats.total_games - stats.games_with_timer)
    
    # Timer usage
    timer_section = "UTILIZZO TIMER\n"
    timer_section += f"Partite con timer attivo: {stats.games_with_timer}\n"
    timer_section += f"Partite senza timer: {games_without_timer}\n\n"
    
    if stats.games_with_timer > 0:
        # Performance breakdown
        perf_section = "PERFORMANCE TEMPORALE\n"
        perf_section += f"Entro il limite: {stats.victories_within_time}\n"
        perf_section += f"Overtime: {stats.victories_overtime}\n"
        perf_section += f"Timeout (sconfitte): {stats.defeats_timeout}\n"
        
        # Calculate success rate
        within_rate = stats.victories_within_time / stats.games_with_timer
        perf_section += f"Tasso completamento in tempo: {self.format_percentage(within_rate)}\n\n"
        
        # Overtime analytics
        overtime_section = "ANALISI OVERTIME\n"
        if stats.victories_overtime > 0:
            overtime_section += f"Overtime medio: {self.format_duration(stats.average_overtime)}\n"
            overtime_section += f"Overtime massimo: {self.format_duration(stats.max_overtime)}\n\n"
        else:
            overtime_section += "Nessuna partita in overtime\n\n"
        
        # Mode breakdown (now tracked in TimerStats v3.1.1!)
        mode_section = "PER MODALITÀ\n"
        mode_section += f"STRICT: {stats.strict_mode_games} partite\n"
        mode_section += f"PERMISSIVE: {stats.permissive_mode_games} partite\n"
        
        content = timer_section + perf_section + overtime_section + mode_section
    else:
        content = timer_section + "\nNessuna partita con timer giocata.\n"
    
    footer = f"\n{'─' * 56}\n"
    footer += "Pagina 2/3\n"
    footer += "PAGE UP - Pagina precedente | PAGE DOWN - Pagina successiva\n"
    footer += "ESC - Torna a Gestione Profili"
    
    return header + content + footer
```

**CRITICAL CHANGES**:
1. ✅ Usa `max(0, ...)` per defensive programming (gestisce corruzione)
2. ✅ Legge `stats.victories_within_time` (NON `games_within_time`)
3. ✅ Legge `stats.victories_overtime` (NON `games_overtime`)
4. ✅ Legge `stats.defeats_timeout` (NON `games_timeout`)
5. ✅ Legge `stats.average_overtime` (NON `avg_overtime_duration`)
6. ✅ Legge `stats.max_overtime` (NON `max_overtime_duration`)
7. ✅ Usa `stats.strict_mode_games` e `stats.permissive_mode_games` (NEW v3.1.1)

---

### **Commit 3/3: Wire DetailedStatsDialog + Version Bump**

**Titolo**: `fix(presentation): Pass GlobalStats to timer formatter in DetailedStatsDialog [v3.1.1]`

**Files**: 
- `src/presentation/dialogs/detailed_stats_dialog.py`
- `CHANGELOG.md`

#### **Modifica 3.1: Aggiorna DetailedStatsDialog Constructor**

**LOCALIZZAZIONE**: `__init__()` metodo (linea ~63)

**NELLA LISTA** `self.pages`, **MODIFICA** linea Page 2:

**PRIMA**:
```python
        self.pages: List[str] = [
            self.formatter.format_global_stats_detailed(global_stats, profile_name),
            self.formatter.format_timer_stats_detailed(timer_stats),
            self.formatter.format_scoring_difficulty_stats(scoring_stats, difficulty_stats)
        ]
```

**DOPO**:
```python
        self.pages: List[str] = [
            self.formatter.format_global_stats_detailed(global_stats, profile_name),
            self.formatter.format_timer_stats_detailed(timer_stats, global_stats),  # Pass global_stats (v3.1.1)
            self.formatter.format_scoring_difficulty_stats(scoring_stats, difficulty_stats)
        ]
```

---

#### **Modifica 3.2: Aggiorna CHANGELOG.md**

**LOCALIZZAZIONE**: Top del file `CHANGELOG.md`

**AGGIUNGI** nuova entry **PRIMA** di `## [Unreleased]`:

```markdown
## [3.1.1] - 2026-02-18

### Fixed
- **DetailedStatsDialog AttributeError**: Fixed crash when opening stats on profile with 0 games
  - Root cause: StatsFormatter used non-existent TimerStats attributes
  - Solution: Extended TimerStats domain model with proper timer mode tracking
- **StatsFormatter**: Corrected attribute names to match TimerStats model
  - `games_within_time` → `victories_within_time`
  - `games_overtime` → `victories_overtime`
  - `games_timeout` → `defeats_timeout`
  - `avg_overtime_duration` → `average_overtime`
  - `max_overtime_duration` → `max_overtime`
- **Cross-stat calculation**: Added defensive programming for `games_without_timer`
  - Uses `max(0, total_games - games_with_timer)` to handle data corruption

### Added
- **TimerStats (Domain Model)**: Timer mode breakdown tracking
  - `strict_mode_games`: Count of STRICT mode games
  - `permissive_mode_games`: Count of PERMISSIVE mode games
  - Automatically tracked in `update_from_session()` via `SessionOutcome.timer_mode`
- **StatsFormatter**: Cross-stat calculation support
  - `format_timer_stats_detailed()` now accepts `global_stats` parameter
  - Enables accurate `games_without_timer` calculation

### Changed
- **StatsFormatter.format_timer_stats_detailed()** signature:
  - **BEFORE**: `format_timer_stats_detailed(self, stats: TimerStats) -> str`
  - **AFTER**: `format_timer_stats_detailed(self, stats: TimerStats, global_stats: GlobalStats) -> str`
  - **Impact**: DetailedStatsDialog updated to pass both parameters
- **TimerStats.from_dict()**: Added backward compatibility
  - Provides default values (`strict_mode_games=0`, `permissive_mode_games=0`) for v3.1.0 profiles
  - No migration script required - profiles auto-upgrade on load

### Technical
- **Architecture**: Business logic moved from Presentation to Domain Layer
- **Backward Compatibility**: 100% compatible with v3.1.0 profile files
- **Performance**: Negligible impact (+8 bytes per profile, O(1) operations)
- **Testing**: Manual verification required (no automated tests for stats presentation)

***

## [Unreleased]

<!-- Existing unreleased content continues here -->
```

---

## 🧪 **TEST PLAN (Manuale)**

### **Pre-Requisiti**
- Branch: `copilot/implement-profile-system-v3-1-0`
- Ambiente: Windows 11 + NVDA + Python 3.11
- App avviata: `python acs_wx.py`

---

### **Test Case 1: Nuovo Profilo (0 Partite)**

**Obiettivo**: Verificare nessun crash su profilo vuoto

**Steps**:
1. Avvia app → Menu Principale
2. Premi `P` → Gestione Profili
3. Button "1. Crea Nuovo Profilo"
   - Nome: "Test Zero"
   - Conferma
4. Button "5. Statistiche Dettagliate"
5. **ATTESO**: Dialog si apre senza crash
6. Verifica contenuto Page 2:
   - "Partite con timer attivo: 0"
   - "Partite senza timer: 0"
   - "Nessuna partita con timer giocata."
7. Premi ESC → Torna a Gestione Profili

**Risultato**: ✅ PASS / ❌ FAIL

---

### **Test Case 2: Profilo con 5 Partite (Mixed Timer Modes)**

**Obiettivo**: Verificare tracking timer mode breakdown

**Steps**:
1. Crea nuovo profilo "Test Mixed"
2. Gioca 5 partite:
   - 3 con STRICT timer (varia esito: 2 vittorie, 1 timeout)
   - 2 con PERMISSIVE timer (2 vittorie)
3. Menu → Gestione Profili → Statistiche Dettagliate
4. Naviga a Page 2 (Page Down)
5. **ATTESO**:
   - "Partite con timer attivo: 5"
   - "Partite senza timer: 0"
   - "STRICT: 3 partite"
   - "PERMISSIVE: 2 partite"
6. Verifica overtime section (se applicabile)

**Risultato**: ✅ PASS / ❌ FAIL

---

### **Test Case 3: Profilo Legacy (v3.1.0 Compatibility)**

**Obiettivo**: Verificare backward compatibility

**Setup**:
1. Copia profilo salvato con v3.1.0 in `~/.solitario/profiles/`
2. Profilo deve avere `games_with_timer > 0` ma **senza** `strict_mode_games`

**Steps**:
1. Avvia app (v3.1.1)
2. Menu → Gestione Profili
3. Carica profilo legacy
4. Button "5. Statistiche Dettagliate"
5. **ATTESO**: 
   - Nessun crash al caricamento
   - Page 2 mostra "STRICT: 0 partite, PERMISSIVE: 0 partite" (defaults)
6. Gioca 1 nuova partita con STRICT timer
7. Riaprì statistiche
8. **ATTESO**: "STRICT: 1 partite" (inizia tracking)

**Risultato**: ✅ PASS / ❌ FAIL

---

### **Test Case 4: Cross-Stat Calculation (games_without_timer)**

**Obiettivo**: Verificare calcolo corretto partite senza timer

**Steps**:
1. Crea profilo "Test NoTimer"
2. Gioca 10 partite:
   - 7 con timer attivo
   - 3 senza timer (timer disabilitato)
3. Statistiche Dettagliate → Page 2
4. **ATTESO**:
   - "Partite con timer attivo: 7"
   - "Partite senza timer: 3"
   - Totale: 7 + 3 = 10 (da GlobalStats)

**Risultato**: ✅ PASS / ❌ FAIL

---

### **Test Case 5: Data Corruption Handling (Defensive)**

**Obiettivo**: Verificare gestione stats corrotti

**Setup** (manuale - richiede edit JSON):
1. Crea profilo "Test Corrupt"
2. Chiudi app
3. Edita `~/.solitario/profiles/profile_xxx.json`:
   ```json
   "stats": {
     "global": {"total_games": 5},
     "timer": {"games_with_timer": 10}  // ❌ Inconsistente!
   }
   ```
4. Salva file

**Steps**:
1. Avvia app
2. Carica profilo "Test Corrupt"
3. Statistiche Dettagliate → Page 2
4. **ATTESO**:
   - "Partite senza timer: 0" (NON -5!)
   - Usa `max(0, 5 - 10) = 0` (defensive)

**Risultato**: ✅ PASS / ❌ FAIL

---

## 🔍 **VALIDATION CHECKLIST**

Dopo completamento commits, verifica:

### **Code Quality**
- [ ] ✅ Nessun typo in nomi attributi (`strict_mode_games`, `permissive_mode_games`)
- [ ] ✅ Signature `format_timer_stats_detailed()` corretta (2 parametri)
- [ ] ✅ `from_dict()` usa `setdefault()` per backward compatibility
- [ ] ✅ Defensive programming: `max(0, ...)` per games_without_timer
- [ ] ✅ Logging warning per timer_mode sconosciuti (opzionale ma presente)

### **Documentation**
- [ ] ✅ CHANGELOG.md aggiornato con entry v3.1.1
- [ ] ✅ Docstring `format_timer_stats_detailed()` menziona v3.1.1
- [ ] ✅ Docstring `from_dict()` spiega backward compatibility
- [ ] ✅ Commit messages seguono conventional commits

### **Architecture**
- [ ] ✅ Business logic nel Domain Layer (TimerStats)
- [ ] ✅ Presentation Layer solo formattazione (StatsFormatter)
- [ ] ✅ Nessun calcolo business logic in UI (DetailedStatsDialog)
- [ ] ✅ Single Source of Truth mantenuto

### **Compatibility**
- [ ] ✅ Profili v3.1.0 caricano senza crash
- [ ] ✅ Nessun breaking change per VictoryDialog (usa metodo diverso)
- [ ] ✅ Nessun breaking change per ProfileMenuPanel (delega)

---

## 📊 **METRICS ATTESE**

| Metrica | Before v3.1.1 | After v3.1.1 | Delta |
|---------|---------------|--------------|-------|
| **TimerStats attributi** | 8 | 10 | +2 |
| **StatsFormatter params** | 1 | 2 | +1 |
| **Profile JSON size** | ~2.5 KB | ~2.51 KB | +8 bytes |
| **Crash su 0 partite** | ❌ Sì | ✅ No | Fixed |
| **Backward compatibility** | N/A | ✅ 100% | Guaranteed |

---

## ⚠️ **CRITICAL NOTES FOR COPILOT**

### **DO**
- ✅ Usa `max(0, ...)` per calcolare `games_without_timer` (defensive)
- ✅ Testa signature change con mypy/pyright (type safety)
- ✅ Mantieni ordine dei campi in `to_dict()` (coerenza JSON)
- ✅ Usa nomi attributi ESATTI: `victories_within_time`, NON `games_within_time`
- ✅ Incrementa versione a **3.1.1** in CHANGELOG (patch bump per bug fix)

### **DON'T**
- ❌ NON modificare altri metodi di StatsFormatter (solo `format_timer_stats_detailed`)
- ❌ NON toccare VictoryDialog (usa `format_global_stats_summary()`, diverso)
- ❌ NON modificare ProfileMenuPanel (passa già tutto correttamente)
- ❌ NON cambiare serializzazione di altri stats models (solo TimerStats)
- ❌ NON rimuovere sezione "PER MODALITÀ" (ora funziona con nuovi campi!)

### **EDGE CASES TO HANDLE**
1. ✅ Profilo con `games_with_timer=0` → Mostra "Nessuna partita con timer"
2. ✅ Profilo con `strict_mode_games=0, permissive_mode_games=0` → Mostra 0
3. ✅ Profilo con `total_games < games_with_timer` → Usa max(0, ...)
4. ✅ SessionOutcome con `timer_mode="UNKNOWN"` → Log warning (non crash)

---

## 🎯 **SUCCESS CRITERIA**

Il fix è considerato **completato con successo** quando:

1. ✅ **Zero Crashes**: Button "Statistiche Dettagliate" apre dialog su qualsiasi profilo
2. ✅ **Correct Display**: Page 2 mostra conteggi corretti per STRICT/PERMISSIVE
3. ✅ **Backward Compatible**: Profili v3.1.0 caricano senza errori
4. ✅ **Defensive**: Gestisce gracefully stats corrotti (no valori negativi)
5. ✅ **Clean Architecture**: Business logic nel Domain, formattazione in Presentation
6. ✅ **Documented**: CHANGELOG.md aggiornato con entry v3.1.1 completa

---

## 📚 **REFERENCES**

- **Design Document**: `docs/DESIGN_PROFILE_STATISTICS_SYSTEM.md`
- **Implementation Plan**: `docs/IMPLEMENTATION_STATS_PRESENTATION.md`
- **Architecture**: `docs/ARCHITECTURE.md` (section Stats Presentation v3.1.0)
- **API Documentation**: `docs/API.md` (sections TimerStats, StatsFormatter)
- **Original Issue**: AttributeError on `stats.games_without_timer` (user-reported)

---

## 🚀 **DEPLOYMENT NOTES**

### **Version Bump Rationale**
- **From**: v3.1.0 (Stats Presentation UI complete)
- **To**: v3.1.1 (Bug fix + model extension)
- **Type**: PATCH (semver: bug fix with backward-compatible extension)

### **Migration Required?**
- ❌ **NO** - Automatic upgrade via `from_dict()` defaults
- ✅ Profili legacy continuano a funzionare immediatamente

### **Rollback Strategy**
Se necessario rollback a v3.1.0:
1. Revert commits 1-3
2. Nessuna modifica dati necessaria (nuovi campi ignorati da v3.1.0)

---

**Fine Piano di Correzione v3.1.1**

---

**Prepared by**: Perplexity AI (Claude 3.5 Sonnet)  
**Date**: 2026-02-18  
**For**: Copilot Agent Execution  
**Estimated Agent Time**: 20-25 minutes  
```
