# 📋 TODO – Timer + Profile + Stats Features (v2.7.0 → v3.0.0)

**Branch**: `refactoring-engine`  
**Tipo**: FEATURE STACK  
**Priorità**: HIGH  
**Stato**: Feature 1 COMPLETATA ✅  
**Stima Totale**: 5-6 ore agent time

---

## 📖 Riferimenti Documentazione

**Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:**

### Feature 1: Timer System v2.7.0 ✅ COMPLETATA
- **Piano Implementazione**: [`docs/3 - coding plans/IMPLEMENTATION_TIMER_SYSTEM.md`](3%20-%20coding%20plans/IMPLEMENTATION_TIMER_SYSTEM.md)
- **Design Doc**: [`docs/2 - projects/DESIGN_TIMER_MODE_SYSTEM.md`](2%20-%20projects/DESIGN_TIMER_MODE_SYSTEM.md)
- **Stima**: 45-70 min (8 commit atomici)
- **Completamento**: ~17 min (10 commit)

### Feature 2: Profile System v3.0.0 Backend
- **Piano Implementazione**: [`docs/3 - coding plans/IMPLEMENTATION_PROFILE_SYSTEM.md`](3%20-%20coding%20plans/IMPLEMENTATION_PROFILE_SYSTEM.md)
- **Design Doc**: [`docs/2 - projects/DESIGN_PROFILE_STATISTICS_SYSTEM.md`](2%20-%20projects/DESIGN_PROFILE_STATISTICS_SYSTEM.md)
- **Stima**: 2-2.5 ore (9 commit atomici)
- **Dipende da**: Feature 1 (EndReason enum) ✅

### Feature 3: Stats Presentation v3.0.0 UI
- **Piano Implementazione**: [`docs/3 - coding plans/IMPLEMENTATION_STATS_PRESENTATION.md`](3%20-%20coding%20plans/IMPLEMENTATION_STATS_PRESENTATION.md)
- **Design Doc**: [`docs/2 - projects/DESIGN_STATISTICS_PRESENTATION.md`](2%20-%20projects/DESIGN_STATISTICS_PRESENTATION.md)
- **Stima**: 2-3 ore (12-15 commit atomici)
- **Dipende da**: Feature 2 (ProfileService)

**Questo TODO è solo un sommario operativo.** I piani completi contengono:
- Architettura dettagliata
- Edge case coverage
- Test specifications
- Code snippets completi

---

## 🤖 Istruzioni per Copilot Agent

### Workflow Checkpoint-Driven per Ogni Fase

```
1. 📖 LEGGI questo TODO → identifica prossima fase
2. 🔍 CONSULTA piano completo → rivedi dettagli tecnici della fase
3. 💻 IMPLEMENTA → codifica solo la fase corrente (scope limitato)
4. 🧪 TESTA → scrivi/esegui test per la fase
5. 📝 COMMIT → messaggio conventional con [Phase N]
6. ✅ AGGIORNA piano implementazione → spunta checkbox fase completata
7. ✅ AGGIORNA questo TODO → spunta checkbox sotto
8. 🔄 RIPETI → passa alla fase successiva (torna al punto 1)
```

### Regole Fondamentali

✅ **DO:**
- Un commit atomico per fase logica
- Dopo ogni commit: aggiorna TODO + piano implementazione
- Prima di ogni fase: rileggi sezione pertinente nel piano
- Commit message: `type(scope): description [Phase N/M]`
- Approccio sequenziale: Feature 1 completa → Feature 2 completa → Feature 3 completa

❌ **DON'T:**
- Mega-commit con multiple fasi
- Implementare senza consultare piano dettagliato
- Saltare checkpoint (aggiornamento TODO/piano)
- Implementare feature 2/3 prima di completare prerequisiti

### Esempio Workflow Reale

```
[Feature 1 - Phase 1]
→ Leggi IMPLEMENTATION_TIMER_SYSTEM.md Phase 1
→ Implementa EndReason enum + test
→ Commit: "feat(domain): Add EndReason enum [Phase 1/8]"
→ Aggiorna IMPLEMENTATION_TIMER_SYSTEM.md (spunta Phase 1)
→ Aggiorna TODO.md (spunta Feature 1 - Phase 1)

[Feature 1 - Phase 2]
→ Leggi IMPLEMENTATION_TIMER_SYSTEM.md Phase 2
→ Implementa timer state attributes
→ Commit: "feat(game-service): Add timer state [Phase 2/8]"
→ Aggiorna plan + TODO

... continua fino a Phase 8 completata

[Feature 2 - Phase 1]
→ Leggi IMPLEMENTATION_PROFILE_SYSTEM.md Phase 1
→ Implementa data models
→ Commit: "feat(domain): Create profile data models [Phase 1/9]"
→ Aggiorna plan + TODO

... e così via
```

---

## 🎯 Obiettivo Implementazione

### Cosa Viene Introdotto

Stack completo di 3 feature interdipendenti:

1. **Timer System v2.7.0** ✅: Gestione timer come evento di gioco reale con scadenza, overtime tracking, e comportamento STRICT/PERMISSIVE. Introduce `EndReason` enum per classificare motivi di termine partita.

2. **Profile System v3.0.0 Backend**: Gestione profili utente con persistenza JSON atomica, statistiche aggregate (globali, timer, difficoltà, scoring), session tracking, e recovery da crash.

3. **Stats Presentation v3.0.0 UI**: Layer di presentazione con dialog vittoria/abbandono integrate, statistiche dettagliate (3 pagine), leaderboard globale, accessibilità NVDA completa.

### Perché Viene Fatto

Sostituzione sistema punteggi limitato con:
- Profili persistenti per statistiche long-term
- Timer mode richiesto da utenti (competizione tempo)
- UI statistiche accessibile (NVDA-friendly)
- Foundation per future feature (multiplayer, achievements)

### Impatto Sistema

- **Domain**: Nuovi modelli (`UserProfile`, `SessionOutcome`, `EndReason`) ✅
- **Application**: `ProfileService`, `GameEngine` hooks, dialog integration
- **Infrastructure**: JSON storage con atomic writes, session recovery
- **Presentation**: 5 nuovi dialog, `StatsFormatter`, menu options
- **Accessibilità**: TTS announcements, keyboard navigation, NVDA optimized

---

## 🔄 Sequenza Implementazione Obbligatoria

```
┌─────────────────────────────────────┐
│ 1. Timer System v2.7.0 ✅          │ ← COMPLETATO
│    ~17 min (vs stima 45-70 min)    │
└─────────────────────────────────────┘
           ↓ (prerequisito soddisfatto)
┌─────────────────────────────────────┐
│ 2. Profile System v3.0.0 Backend    │ ← PROSSIMA
│    2-2.5 ore                        │
└─────────────────────────────────────┘
           ↓ (prerequisito)
┌─────────────────────────────────────┐
│ 3. Stats Presentation v3.0.0 UI     │
│    2-3 ore                          │
└─────────────────────────────────────┘
```

**Non saltare feature**. Feature 2 richiede `EndReason` da Feature 1 ✅. Feature 3 richiede `ProfileService` da Feature 2.

---

## ✅ FEATURE 1: Timer System v2.7.0 (completata in ~17 min)

**Piano Dettagliato**: [`IMPLEMENTATION_TIMER_SYSTEM.md`](3%20-%20coding%20plans/IMPLEMENTATION_TIMER_SYSTEM.md)

### Checklist Fasi (Tutte completate ✅)

- [x] **Phase 1**: EndReason enum creato e testato
  - File: `src/domain/models/game_end.py` (NEW)
  - Test: `tests/unit/test_game_end.py` (NEW)
  - Commit: `feat(domain): Add EndReason enum [Phase 1/8]`

- [x] **Phase 2**: Timer state attributes in GameService
  - File: `src/domain/services/game_service.py` (MODIFIED)
  - Test: `tests/unit/test_timer_state.py` (NEW)
  - Commit: `feat(game-service): Add timer state tracking [Phase 2/8]`

- [x] **Phase 3**: Timer expiry detection logic
  - File: `src/domain/services/game_service.py` (MODIFIED)
  - Test: `tests/unit/test_timer_logic.py` (NEW)
  - Commit: `feat(game-service): Implement timer expiry detection [Phase 3/8]`

- [x] **Phase 4**: STRICT mode auto-stop
  - File: `src/application/game_engine.py` (MODIFIED)
  - Test: `tests/integration/test_timer_integration.py` (NEW)
  - Commit: `feat(game-engine): Implement STRICT mode timeout [Phase 4/8]`

- [x] **Phase 5**: PERMISSIVE mode overtime tracking + backward compatibility
  - File: `src/application/game_engine.py` (MODIFIED)
  - Test: `tests/integration/test_timer_integration.py` (EXTEND)
  - Commit: `feat(game-engine): Implement PERMISSIVE mode overtime [Phase 5/8]`
  - **Nota**: Include anche Phase 7 (backward compatibility)

- [x] **Phase 6**: TTS announcements
  - File: `src/presentation/formatters/game_formatter.py` (MODIFIED)
  - Test: `tests/unit/test_game_formatter.py` (EXTEND)
  - Commit: `feat(presentation): Add timer expiry TTS [Phase 6/8]`

- [x] **Phase 7**: Backward compatibility wrapper
  - **Integrato in Phase 5** (decisione ottimale)

- [x] **Phase 8**: Session outcome population (stub)
  - File: `src/application/game_engine.py` (MODIFIED)
  - Test: `tests/integration/test_timer_integration.py` (EXTEND)
  - Commit: `feat(game-engine): Prepare session outcome for ProfileService [Phase 8/8]`

**Post-implementation fixes**:

- [x] **Fix**: Relative paths in integration tests
  - Commit: `fix(tests): Use relative paths in timer integration tests`

- [x] **Fix**: Type hints per Union[EndReason, bool]
  - Commit: `fix(typing): Add type hints for end_reason parameters`

**Validation**: Feature 1 100% completa ✅

- [x] **✅ Feature 1 COMPLETATA**

### Risultati

| Metrica | Atteso | Ottenuto | Delta |
|---------|--------|----------|-------|
| Commit atomici | 8 | 10 | +2 (fix post-review) |
| Test | 29 | 25 | -4 (consolidati) |
| Tempo | 45-70 min | ~17 min | 🚀 **3-4x più veloce** |
| Pass rate | ≥88% | 100% | ✅ Superiore |

---

## ✅ FEATURE 2: Profile System v3.0.0 Backend (2-2.5h)

**Piano Dettagliato**: [`IMPLEMENTATION_PROFILE_SYSTEM.md`](3%20-%20coding%20plans/IMPLEMENTATION_PROFILE_SYSTEM.md)

**✅ PREREQUISITO SODDISFATTO**: Feature 1 completata (EndReason enum disponibile)

### Checklist Fasi (Aggiorna dopo ogni commit)

- [x] **Phase 1**: Domain models (UserProfile, SessionOutcome, Stats) ✅
  - Files: `src/domain/models/profile.py`, `src/domain/models/statistics.py`
  - Test: `tests/unit/domain/test_profile_models.py`, `test_statistics_models.py` (44 tests passing)
  - Commit: `feat(domain): Create profile data models [Phase 1/9]` (7543c63)

- [x] **Phase 2**: ProfileStorage class (atomic writes) ✅
  - File: `src/infrastructure/storage/profile_storage.py` (NEW)
  - Test: `tests/unit/infrastructure/test_profile_storage.py` (18 tests passing)
  - Commit: `feat(infrastructure): Create ProfileStorage with atomic writes [Phase 2/9]` (aede3fd)

- [x] **Phase 3**: Stats aggregation logic ✅
  - File: `src/domain/services/stats_aggregator.py` (NEW)
  - Test: `tests/unit/domain/services/test_stats_aggregator.py` (12 tests passing, 91% coverage)
  - Commit: `feat(domain): Implement stats aggregation logic [Phase 3/9]` (c71692f)

- [x] **Phase 4**: ProfileService (CRUD operations) ✅
  - File: `src/domain/services/profile_service.py` (NEW)
  - Test: `tests/unit/domain/services/test_profile_service.py` (27 tests passing, 81% coverage)
  - Commit: `feat(domain): Create ProfileService with CRUD [Phase 4/9]` (6437dd6)

- [ ] **Phase 5**: DI container integration
  - File: `src/infrastructure/di_container.py` (MODIFIED)
  - Test: `tests/integration/test_di_profile.py` (NEW)
  - Commit: `feat(infrastructure): Integrate ProfileService in DI container [Phase 5/9]`

- [ ] **Phase 6**: SessionStorage (active session tracking)
  - File: `src/infrastructure/storage/session_storage.py` (NEW)
  - Test: `tests/unit/infrastructure/test_session_storage.py` (NEW)
  - Commit: `feat(infrastructure): Add session tracking storage [Phase 6/9]`

- [ ] **Phase 7**: SessionTracker (dirty shutdown recovery)
  - File: `src/domain/services/session_tracker.py` (NEW)
  - Test: `tests/integration/test_session_recovery.py` (NEW)
  - Commit: `feat(domain): Implement session recovery tracker [Phase 7/9]`

- [ ] **Phase 8**: ProfileService session recording
  - File: `src/domain/services/profile_service.py` (MODIFIED)
  - Test: `tests/integration/test_profile_session_flow.py` (NEW)
  - Commit: `feat(domain): Add session recording to ProfileService [Phase 8/9]`

- [ ] **Phase 9**: GameEngine integration (stub)
  - File: `src/application/game_engine.py` (MODIFIED)
  - Test: `tests/integration/test_game_profile_integration.py` (NEW)
  - Commit: `feat(game-engine): Integrate ProfileService hooks [Phase 9/9]`

**Validation**: Spunta quando Feature 2 è 100% completa.

- [ ] **✅ Feature 2 COMPLETATA**

---

## ✅ FEATURE 3: Stats Presentation v3.0.0 UI (2-3h)

**Piano Dettagliato**: [`IMPLEMENTATION_STATS_PRESENTATION.md`](3%20-%20coding%20plans/IMPLEMENTATION_STATS_PRESENTATION.md)

**⚠️ PREREQUISITI**: Feature 1 ✅ + Feature 2 (EndReason + ProfileService)

### Checklist Fasi (Aggiorna dopo ogni commit)

- [ ] **Phase 1.1**: StatsFormatter base utilities
  - File: `src/presentation/formatters/stats_formatter.py` (NEW)
  - Test: `tests/unit/test_stats_formatter.py` (NEW)
  - Commit: `feat(presentation): Create StatsFormatter base [Phase 1.1/9]`

- [ ] **Phase 1.2**: StatsFormatter global stats methods
  - File: `src/presentation/formatters/stats_formatter.py` (MODIFIED)
  - Test: `tests/unit/test_stats_formatter.py` (EXTEND)
  - Commit: `feat(presentation): Add global stats formatting [Phase 1.2/9]`

- [ ] **Phase 2**: Victory dialog
  - File: `src/presentation/dialogs/victory_dialog.py` (NEW)
  - Test: Manual checklist in `tests/manual/NVDA_TEST_CHECKLIST.md`
  - Commit: `feat(presentation): Create victory dialog with stats [Phase 2/9]`

- [ ] **Phase 3**: Abandon dialog
  - File: `src/presentation/dialogs/abandon_dialog.py` (NEW)
  - Test: Manual checklist
  - Commit: `feat(presentation): Create abandon dialog [Phase 3/9]`

- [ ] **Phase 4**: Game info dialog (tasto I)
  - File: `src/presentation/dialogs/game_info_dialog.py` (NEW)
  - Test: Manual checklist
  - Commit: `feat(presentation): Create game info dialog [Phase 4/9]`

- [ ] **Phase 5.1**: Detailed stats dialog Page 1 (global)
  - File: `src/presentation/dialogs/detailed_stats_dialog.py` (NEW)
  - Test: Manual checklist
  - Commit: `feat(presentation): Create detailed stats Page 1 [Phase 5.1/9]`

- [ ] **Phase 5.2**: Detailed stats Page 2 (timer)
  - File: `src/presentation/formatters/stats_formatter.py` (MODIFIED)
  - File: `src/presentation/dialogs/detailed_stats_dialog.py` (MODIFIED)
  - Test: 1 formatter unit test
  - Commit: `feat(presentation): Add detailed stats Page 2 [Phase 5.2/9]`

- [ ] **Phase 5.3**: Detailed stats Page 3 (scoring/difficulty)
  - File: `src/presentation/formatters/stats_formatter.py` (MODIFIED)
  - File: `src/presentation/dialogs/detailed_stats_dialog.py` (MODIFIED)
  - Test: 1 formatter unit test
  - Commit: `feat(presentation): Add detailed stats Page 3 [Phase 5.3/9]`

- [ ] **Phase 6**: Leaderboard dialog
  - File: `src/presentation/dialogs/leaderboard_dialog.py` (NEW)
  - Test: 1 unit test + manual checklist
  - Commit: `feat(presentation): Create leaderboard dialog [Phase 6/9]`

- [ ] **Phase 7.1**: GameEngine integration (victory/abandon)
  - File: `src/application/game_engine.py` (MODIFIED)
  - Test: 2 integration tests
  - Commit: `feat(game-engine): Integrate victory/abandon dialogs [Phase 7.1/9]`

- [ ] **Phase 7.2**: GameEngine integration (game info I key)
  - File: `src/application/game_engine.py` (MODIFIED)
  - Test: 1 integration test
  - Commit: `feat(game-engine): Add game info dialog hook [Phase 7.2/9]`

- [ ] **Phase 8**: NVDA accessibility polish
  - Files: All dialogs (MODIFIED)
  - Test: Complete manual NVDA checklist
  - Commit: `feat(presentation): Polish NVDA accessibility [Phase 8/9]`

- [ ] **Phase 9.1**: Menu integration (Ultima Partita)
  - File: `src/presentation/dialogs/last_game_dialog.py` (NEW)
  - File: `src/application/game_engine.py` (MODIFIED)
  - Test: Manual
  - Commit: `feat(presentation): Add Ultima Partita menu option [Phase 9.1/9]`

- [ ] **Phase 9.2**: Menu integration (Leaderboard)
  - File: Main menu (MODIFIED)
  - Test: Manual
  - Commit: `feat(presentation): Add leaderboard menu option [Phase 9.2/9]`

- [ ] **Phase 9.3**: Menu integration (Detailed stats)
  - File: Profile menu (MODIFIED)
  - Test: Manual
  - Commit: `feat(presentation): Wire detailed stats to profile menu [Phase 9.3/9]`

**Validation**: Spunta quando Feature 3 è 100% completa.

- [ ] **✅ Feature 3 COMPLETATA**

---

## 🧪 Testing Strategy

### Unit Tests (Automated)

- **Feature 1** ✅: 25 unit tests (100% pass) - domain + service logic
- **Feature 2**: 63-81 unit tests - models + storage + aggregation
- **Feature 3**: 15+ unit tests - formatters
- **Target Coverage**: ≥88% (project standard)

### Integration Tests (Automated)

- **Feature 1** ✅: 7 integration tests - timer → end_game flow
- **Feature 2**: 12 integration tests - ProfileService end-to-end
- **Feature 3**: 3 integration tests - dialog → ProfileService

### Manual Tests (NVDA Accessibility)

- **Feature 3**: 30+ checklist items in `tests/manual/NVDA_TEST_CHECKLIST.md`
- Test ogni dialog con NVDA attivo
- Verifica keyboard navigation, focus management, TTS announcements

### Test Execution

```bash
# Run all automated tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific feature tests
pytest tests/unit/test_game_end.py  # Feature 1 ✅
pytest tests/unit/domain/  # Feature 2
pytest tests/unit/test_stats_formatter.py  # Feature 3
```

---

## ✅ Criteri di Completamento

### Feature 1 (Timer System) ✅ COMPLETATA

- [x] Tutte le 8 fasi completate (checkbox spuntate nel piano)
- [x] 25 unit/integration tests passano (100%)
- [x] Timer STRICT termina partita correttamente
- [x] Timer PERMISSIVE traccia overtime
- [x] TTS announcements single-fire
- [x] `end_game()` accetta EndReason + backward compatible con bool
- [x] Session outcome popolato per ProfileService

### Feature 2 (Profile System)

- [ ] Tutte le 9 fasi completate (checkbox spuntate nel piano)
- [ ] 63-81 unit/integration tests passano
- [ ] ProfileStorage writes atomici (no corrupted JSON)
- [ ] Stats aggregation corretta (globali + timer + difficulty + scoring)
- [ ] Session recovery da dirty shutdown funziona
- [ ] ProfileService integrato in DI container
- [ ] Logging su eventi critici

### Feature 3 (Stats Presentation)

- [ ] Tutte le 9 fasi completate (checkbox spuntate nel piano)
- [ ] 15+ unit tests formatters passano
- [ ] Victory/Abandon dialog mostrano stats aggiornate
- [ ] Detailed stats 3 pagine navigabili (PageUp/PageDown)
- [ ] Leaderboard calcola ranking correttamente
- [ ] Menu options "U" e "L" funzionano
- [ ] NVDA checklist 100% passata (30+ items)

### Stack Completo

- [x] Feature 1 completata (100%) ✅
- [ ] Feature 2 completata (100%)
- [ ] Feature 3 completata (100%)
- [ ] Test coverage ≥88%
- [ ] Zero regressioni funzionali
- [ ] CHANGELOG.md aggiornato con v2.7.0 + v3.0.0
- [ ] README.md aggiornato se necessario
- [ ] Branch `refactoring-engine` ready per merge

---

## 📝 Aggiornamenti Obbligatori a Fine Implementazione

### Post Feature 1 (Timer System v2.7.0) ✅

- [ ] Aggiornare `CHANGELOG.md` con entry v2.7.0
  - Timer STRICT/PERMISSIVE modes
  - EndReason enum
  - Session outcome tracking
- [ ] Incrementare versione: `v2.6.1` → `v2.7.0` (MINOR: new feature)
- [ ] Commit finale: `chore: Release v2.7.0 - Timer System`

### Post Feature 2 (Profile System v3.0.0)

- [ ] Aggiornare `CHANGELOG.md` con entry v3.0.0 (breaking)
  - Profile management system
  - Statistics aggregation
  - Session tracking + recovery
  - Breaking: Score system replaced by profile stats
- [ ] Incrementare versione: `v2.7.0` → `v3.0.0` (MAJOR: breaking change)
- [ ] Commit finale: `chore: Release v3.0.0 - Profile System Backend`

### Post Feature 3 (Stats Presentation v3.0.0 UI)

- [ ] Aggiornare `CHANGELOG.md` con entry v3.0.0 UI
  - Victory/abandon dialogs with stats
  - Detailed stats (3 pages)
  - Global leaderboard
  - NVDA accessibility
- [ ] Aggiornare `README.md` con screenshot/istruzioni nuove UI
- [ ] Commit finale: `chore: Complete v3.0.0 - Stats Presentation UI`
- [ ] Tag release: `git tag v3.0.0`

---

## 📌 Note Operative

### Dependency Chain (CRITICO)

```
Feature 1 (EndReason enum) ✅
    ↓ RICHIESTO DA
Feature 2 (SessionOutcome.end_reason: EndReason)
    ↓ RICHIESTO DA
Feature 3 (Dialog usa ProfileService + EndReason)
```

**✅ Feature 1 completata - Prerequisito soddisfatto per Feature 2**

### Storage Path Consistency

Tutti i file di persistenza usano:
```python
Path.home() / ".solitario" / "<subdir>"
```

- Profiles: `~/.solitario/profiles/`
- Scores: `~/.solitario/scores/` (legacy, verrà deprecato)
- Sessions: `~/.solitario/.sessions/`

### Atomic Writes Pattern

Ogni write su JSON usa:
```python
def _atomic_write_json(path: Path, data: dict):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=2))
    temp.rename(path)  # Atomic on POSIX
```

Nessuna eccezione: evita JSON corrotti su crash.

### Test Naming Convention

```
tests/unit/domain/test_user_profile.py  # Domain models
tests/unit/infrastructure/test_profile_storage.py  # Infrastructure
tests/integration/test_profile_session_flow.py  # Cross-layer
tests/manual/NVDA_TEST_CHECKLIST.md  # Manual UI tests
```

### Commit Message Format

```
type(scope): short description [Phase N/M]

- Bullet point detail 1
- Bullet point detail 2

Refs: DESIGN_DOC.md Section X
```

**Types**: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`  
**Scopes**: `domain`, `infrastructure`, `application`, `presentation`, `game-service`, `game-engine`

---

## 🚀 Quick Start per Copilot Agent

### Step-by-Step Execution

1. **✅ Feature 1 COMPLETATA** - Timer System v2.7.0 implementato con successo
2. **Next: Feature 2** - Apri [`IMPLEMENTATION_PROFILE_SYSTEM.md`](3%20-%20coding%20plans/IMPLEMENTATION_PROFILE_SYSTEM.md)
3. **Read Phase 1** dettagli completi
4. **Implement** UserProfile + SessionOutcome models + tests
5. **Commit** con message conventional
6. **Update** `IMPLEMENTATION_PROFILE_SYSTEM.md` (spunta Phase 1)
7. **Update** questo TODO (spunta Feature 2 - Phase 1)
8. **Repeat** per Phase 2-9 di Feature 2
9. **Move to Feature 3** solo quando Feature 2 è 100% completa
10. **Repeat workflow** per Feature 3 (Phase 1-9)

### Checkpoints Critici

- **✅ Dopo Feature 1 completata**: EndReason enum exists e 25 test passano
- **Dopo Feature 2 completata**: Verifica che ProfileService funziona end-to-end
- **Dopo Feature 3 completata**: Esegui full NVDA manual checklist

---

**Fine TODO.**

Consultabile in 2 minuti. Piano dettagliato nei 3 implementation plan linkati sopra.
Questo è il **cruscotto operativo** per Copilot Agent.
