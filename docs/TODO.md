# 📋 TODO – Timer + Profile + Stats Features (v2.7.0 → v3.1.0)

**Branch**: `refactoring-engine` (base) → `copilot/implement-profile-system-v3-1-0` (feature)  
**Tipo**: FEATURE STACK  
**Priorità**: HIGH  
**Stato**: Feature 1 ✅ + Feature 2 ✅ + Feature 3 🔄 90% (Phase 7.5 + 9 mancanti)  
**Stima Totale**: 5-6 ore agent time  
**Tempo Effettivo**: ~2.5 ore (Feature 1+2+3 core Phase 1-8)

---

## 📖 Riferimenti Documentazione

**Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:**

### Feature 1: Timer System v2.7.0 ✅ COMPLETATA
- **Piano Implementazione**: [`docs/3 - coding plans/IMPLEMENTATION_TIMER_SYSTEM.md`](3%20-%20coding%20plans/IMPLEMENTATION_TIMER_SYSTEM.md)
- **Design Doc**: [`docs/2 - projects/DESIGN_TIMER_MODE_SYSTEM.md`](2%20-%20projects/DESIGN_TIMER_MODE_SYSTEM.md)
- **Stima**: 45-70 min (8 commit atomici)
- **Completamento**: ~17 min (10 commit)

### Feature 2: Profile System v3.0.0 Backend ✅ COMPLETATA
- **Piano Implementazione**: [`docs/3 - coding plans/IMPLEMENTATION_PROFILE_SYSTEM.md`](3%20-%20coding%20plans/IMPLEMENTATION_PROFILE_SYSTEM.md)
- **Design Doc**: [`docs/2 - projects/DESIGN_PROFILE_STATISTICS_SYSTEM.md`](2%20-%20projects/DESIGN_PROFILE_STATISTICS_SYSTEM.md)
- **Stima**: 2-2.5 ore (9 commit atomici)
- **Completamento**: 100% (tutte le 9 fasi)
- **Dipende da**: Feature 1 (EndReason enum) ✅

### Feature 3: Stats Presentation v3.1.0 UI 🔄 IN CORSO (90%)
- **Piano Implementazione**: [`docs/3 - coding plans/IMPLEMENTATION_STATS_PRESENTATION.md`](3%20-%20coding%20plans/IMPLEMENTATION_STATS_PRESENTATION.md)
- **Phase 7.5 Fix Opzionali**: [`docs/3 - coding plans/PHASE_7_5_OPTIONAL_FIXES.md`](3%20-%20coding%20plans/PHASE_7_5_OPTIONAL_FIXES.md) ⚡ **12 min critici**
- **Phase 9 Menu Integration**: [`docs/3 - coding plans/PHASE_9_MENU_INTEGRATION_UPDATED.md`](3%20-%20coding%20plans/PHASE_9_MENU_INTEGRATION_UPDATED.md) 📋 **45 min**
- **Design Doc**: [`docs/2 - projects/DESIGN_STATISTICS_PRESENTATION.md`](2%20-%20projects/DESIGN_STATISTICS_PRESENTATION.md)
- **Stima**: 2-3 ore (12-15 commit atomici)
- **Completamento**: ~70 min (8/9 fasi core) + 12 min fix critici + 45 min menu = **~127 min totali**
- **Dipende da**: Feature 2 (ProfileService) ✅

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

---

## 🎯 Obiettivo Implementazione

### Cosa Viene Introdotto

Stack completo di 3 feature interdipendenti:

1. **Timer System v2.7.0** ✅: Gestione timer come evento di gioco reale con scadenza, overtime tracking, e comportamento STRICT/PERMISSIVE. Introduce `EndReason` enum per classificare motivi di termine partita.

2. **Profile System v3.0.0 Backend** ✅: Gestione profili utente con persistenza JSON atomica, statistiche aggregate (globali, timer, difficoltà, scoring), session tracking, e recovery da crash.

3. **Stats Presentation v3.1.0 UI** 🔄: Layer di presentazione con dialog vittoria/abbandono integrate, statistiche dettagliate (3 pagine), leaderboard globale, accessibilità NVDA completa. **Core implementato (Phase 1-8)**, fix opzionali (Phase 7.5) e menu integration (Phase 9) mancanti.

### Perché Viene Fatto

Sostituzione sistema punteggi limitato con:
- Profili persistenti per statistiche long-term ✅
- Timer mode richiesto da utenti (competizione tempo) ✅
- UI statistiche accessibile (NVDA-friendly) ✅
- Foundation per future feature (multiplayer, achievements)

### Impatto Sistema

- **Domain**: Nuovi modelli (`UserProfile`, `SessionOutcome`, `EndReason`) ✅
- **Application**: `ProfileService` ✅, `GameEngine` hooks ✅, dialog integration ✅
- **Infrastructure**: JSON storage con atomic writes ✅, session recovery ✅
- **Presentation**: 5 nuovi dialog ✅, `StatsFormatter` ✅, menu options ⏸️ (Phase 9)
- **Accessibilità**: TTS announcements ✅, keyboard navigation ✅, NVDA optimized ✅

---

## 🔄 Sequenza Implementazione Obbligatoria

```
┌─────────────────────────────────────┐
│ 1. Timer System v2.7.0 ✅          │ ← COMPLETATO
│    ~17 min (vs stima 45-70 min)    │
└─────────────────────────────────────┘
           ↓ (prerequisito soddisfatto)
┌─────────────────────────────────────┐
│ 2. Profile System v3.0.0 Backend ✅│ ← COMPLETATO
│    2-2.5 ore                        │
└─────────────────────────────────────┘
           ↓ (prerequisito)
┌─────────────────────────────────────┐
│ 3. Stats Presentation v3.1.0 UI 🔄 │ ← 90% (Phase 7.5 + 9 mancanti)
│    Phase 1-8: ~70 min COMPLETATE ✅│
│    Phase 7.5: 12 min critici ⚡     │
│    Phase 9: 45 min menu 📋          │
└─────────────────────────────────────┘
```

---

## ✅ FEATURE 1: Timer System v2.7.0 (completata in ~17 min)

**Piano Dettagliato**: [`IMPLEMENTATION_TIMER_SYSTEM.md`](3%20-%20coding%20plans/IMPLEMENTATION_TIMER_SYSTEM.md)

### Checklist Fasi (Tutte completate ✅)

- [x] **Phase 1-8**: Tutte completate (vedere piano dettagliato)
- [x] **Post-fixes**: Relative paths + type hints
- [x] **✅ Feature 1 COMPLETATA**

---

## ✅ FEATURE 2: Profile System v3.0.0 Backend (completata)

**Piano Dettagliato**: [`IMPLEMENTATION_PROFILE_SYSTEM.md`](3%20-%20coding%20plans/IMPLEMENTATION_PROFILE_SYSTEM.md)

### Checklist Fasi (Tutte completate ✅)

- [x] **Phase 1-9**: Tutte completate (vedere piano dettagliato)
- [x] **✅ Feature 2 COMPLETATA**

---

## 🔄 FEATURE 3: Stats Presentation v3.1.0 UI (90% - Phase 7.5 + 9 mancanti)

**Piano Dettagliato**: [`IMPLEMENTATION_STATS_PRESENTATION.md`](3%20-%20coding%20plans/IMPLEMENTATION_STATS_PRESENTATION.md)

**⚠️ STATO ATTUALE**: Copilot ha completato Phase 1-8 (~70 min), saltando Phase 7.5 (fix opzionali) e Phase 9 (menu integration).

### ✅ Checklist Fasi COMPLETATE (Phase 1-8)

- [x] **Phase 1**: StatsFormatter base + global stats  
  - **Commit**: `eb90583` (Phase 1.1), `df5eba8` (Phase 1.2)
  - **Files**: `src/presentation/formatters/stats_formatter.py` ✅
  - **Tests**: `tests/unit/test_stats_formatter.py` (15 tests, 93% coverage) ✅

- [x] **Phase 2-4**: Victory + Abandon + GameInfo dialogs  
  - **Commit**: `3cd9e30` (condensed: Phases 2-4 insieme)
  - **Files**:
    - `src/presentation/dialogs/victory_dialog.py` ✅
    - `src/presentation/dialogs/abandon_dialog.py` ✅
    - `src/presentation/dialogs/game_info_dialog.py` ✅
  - **Tests**: Manual NVDA checklist

- [x] **Phase 5-6**: Detailed Stats (3 pages) + Leaderboard  
  - **Commit**: `a2e13c2` (condensed: Phases 5-6 insieme)
  - **Files**:
    - `src/presentation/dialogs/detailed_stats_dialog.py` ✅
    - `src/presentation/dialogs/leaderboard_dialog.py` ✅
  - **Tests**: Manual checklist + formatter tests

- [x] **Phase 7**: GameEngine integration + ProfileService ATTIVATO  
  - **Commit**: `288cbef` (Phase 7)
  - **File**: `src/application/game_engine.py` (MODIFIED) ✅
  - **Changes**:
    - ✅ ProfileService recording ATTIVATO (linee 1257-1311)
    - ✅ SessionOutcome creato con tutti i dati
    - ✅ Victory/Abandon dialogs integrati
    - ✅ Profile summary building (vittorie, winrate, record)
    - ✅ New record detection
  - **Tests**: Integration tests

- [x] **Phase 8**: NVDA accessibility polish  
  - **Commit**: `846aa8f` (integrato in Phase 7 commit)
  - **Changes**: Focus management, TTS announcements, keyboard navigation
  - **Tests**: Manual NVDA checklist (30+ items)

### ⚡ Checklist Fasi OPZIONALI (Phase 7.5 - Fix Post-Integration)

**📘 GUIDA DETTAGLIATA**: [`PHASE_7_5_OPTIONAL_FIXES.md`](3%20-%20coding%20plans/PHASE_7_5_OPTIONAL_FIXES.md)

**⚠️ NOTA**: Copilot ha saltato 4 fix opzionali post-Phase 7. **2 fix critici raccomandati (12 min)**, 2 nice-to-have (20 min).

#### ⚡ Fix Critici (RACCOMANDATI - 12 min totali)

- [ ] **Fix 7.5.2**: Typo `ABANDON_CRASH` → `ABANDON_APP_CLOSE` (2 min)
  - **File**: `src/application/game_engine.py` (linea ~703)
  - **Change**: Replace TODO + typo con EndReason corretto
  - **Criticità**: Low (solo naming), ma rimuove TODO obsoleto
  - **Piano**: [PHASE_7_5_OPTIONAL_FIXES.md](3%20-%20coding%20plans/PHASE_7_5_OPTIONAL_FIXES.md) Fix 7.5.2

- [ ] **Fix 7.5.3**: Timer expiry verification + test (10 min)
  - **File**: `src/application/game_engine.py` (metodo `on_timer_tick()`)
  - **Change**: Verificare che STRICT mode chiami `end_game()` su timeout
  - **Criticità**: **MEDIUM** - Potenziale bug silente se logica mancante
  - **Test**: Manual timer test (30 sec STRICT)
  - **Piano**: [PHASE_7_5_OPTIONAL_FIXES.md](3%20-%20coding%20plans/PHASE_7_5_OPTIONAL_FIXES.md) Fix 7.5.3

#### 📋 Fix Nice-to-Have (OPZIONALI - 20 min totali)

- [ ] **Fix 7.5.1**: Semantic logging helpers `ProfileLogger` (15 min)
  - **File NUOVO**: `src/infrastructure/logging/profile_logger.py`
  - **Impatto**: Low (dev experience, log più leggibili)
  - **Piano**: [PHASE_7_5_OPTIONAL_FIXES.md](3%20-%20coding%20plans/PHASE_7_5_OPTIONAL_FIXES.md) Fix 7.5.1

- [ ] **Fix 7.5.4**: App startup recovery dialog (5 min)
  - **File**: `acs_wx.py` (startup check)
  - **Impatto**: Low (recovery già funziona, questo aggiunge solo dialog UI)
  - **Piano**: [PHASE_7_5_OPTIONAL_FIXES.md](3%20-%20coding%20plans/PHASE_7_5_OPTIONAL_FIXES.md) Fix 7.5.4

**DECISIONE RICHIESTA**: 
- **Scenario A**: Implementa tutti e 4 i fix (30-45 min) → Feature 100% completa
- **Scenario B**: Implementa solo fix critici 7.5.2 + 7.5.3 (12 min) → Evita bug, skip nice-to-have ⚡ **RACCOMANDATO**
- **Scenario C**: Skip Phase 7.5 → Crea Issue GitHub per fix post-merge

### ⏸️ Checklist Fasi MANCANTI (Phase 9 - Menu Integration)

**📘 GUIDA DETTAGLIATA**: [`PHASE_9_MENU_INTEGRATION_UPDATED.md`](3%20-%20coding%20plans/PHASE_9_MENU_INTEGRATION_UPDATED.md)

**⚠️ NOTA**: Copilot ha saltato Phase 9, considerandola "opzionale". Richiesta implementazione.

- [ ] **Phase 9.1**: "Ultima Partita" menu option (15-22 min)
  - **File NUOVO**: `src/presentation/dialogs/last_game_dialog.py`
  - **File MODIFICA**: `src/application/game_engine.py` (add `last_session_outcome` storage)
  - **File MODIFICA**: `acs_wx.py` (add "U - Ultima Partita" menu item)
  - **Target**: Main menu handler in `acs_wx.py`
  - **Handler**: Bind "U" key → `game_engine.show_last_game_summary()`
  - **Funzionalità**: Dialog read-only con riassunto ultima partita giocata
  - **Piano**: [PHASE_9_MENU_INTEGRATION_UPDATED.md](3%20-%20coding%20plans/PHASE_9_MENU_INTEGRATION_UPDATED.md) Commit 9.1

- [ ] **Phase 9.2**: Leaderboard menu option (8-12 min)
  - **File MODIFICA**: `acs_wx.py` (main menu handler)
  - **Target**: Main menu options list
  - **Handler**: Bind "L" key → apri `LeaderboardDialog` (già creato in Phase 6)
  - **Funzionalità**: Mostra leaderboard globale (5 classifiche)
  - **Piano**: [PHASE_9_MENU_INTEGRATION_UPDATED.md](3%20-%20coding%20plans/PHASE_9_MENU_INTEGRATION_UPDATED.md) Commit 9.2

- [ ] **Phase 9.3**: Detailed stats in profile menu (10-15 min)
  - **File MODIFICA**: `acs_wx.py` (profile menu handler)
  - **Target**: Profile management menu (opzione "5. Statistiche Dettagliate")
  - **Handler**: Wire existing option → `DetailedStatsDialog` (già creato in Phase 5)
  - **Funzionalità**: 3-page stats navigation da profile menu
  - **Piano**: [PHASE_9_MENU_INTEGRATION_UPDATED.md](3%20-%20coding%20plans/PHASE_9_MENU_INTEGRATION_UPDATED.md) Commit 9.3

### 📊 Riepilogo Implementazione Feature 3

| Componente | Stato | Commit | Note |
|------------|-------|--------|------|
| **StatsFormatter** | ✅ | eb90583, df5eba8 | 9 metodi, 93% coverage |
| **VictoryDialog** | ✅ | 3cd9e30 | Stats integrate, TTS, NVDA |
| **AbandonDialog** | ✅ | 3cd9e30 | EndReason, impact stats |
| **GameInfoDialog** | ✅ | 3cd9e30 | Tasto I durante gioco |
| **DetailedStatsDialog** | ✅ | a2e13c2 | 3 pagine navigabili |
| **LeaderboardDialog** | ✅ | a2e13c2 | 5 classifiche |
| **GameEngine hooks** | ✅ | 288cbef | ProfileService ATTIVATO |
| **NVDA accessibility** | ✅ | 846aa8f | Focus, TTS, keyboard |
| **Fix 7.5.2 - Typo** | ❌ | - | 2 min (raccomandato) |
| **Fix 7.5.3 - Timer** | ❌ | - | 10 min (CRITICO) |
| **Fix 7.5.1 - Logging** | ❌ | - | 15 min (nice-to-have) |
| **Fix 7.5.4 - Recovery** | ❌ | - | 5 min (nice-to-have) |
| **LastGameDialog** | ❌ | - | Phase 9.1 mancante |
| **Menu "U" (Ultima Partita)** | ❌ | - | Phase 9.1 mancante |
| **Menu "L" (Leaderboard)** | ❌ | - | Phase 9.2 mancante |
| **Profile menu → Stats** | ❌ | - | Phase 9.3 mancante |

### ✅ Validation Core (Phase 1-8)

- [x] StatsFormatter creato e testato (15 tests passing)
- [x] Victory/Abandon dialogs mostrano stats aggiornate
- [x] ProfileService recording ATTIVATO in GameEngine
- [x] SessionOutcome creato con tutti i dati (time, moves, score, timer)
- [x] New record detection implementato
- [x] NVDA focus management su tutti i dialogs
- [x] Detailed stats 3 pagine (formatter pronto, dialog creato)
- [x] Leaderboard 5 classifiche (dialog creato)

### ⏸️ Validation Mancante (Phase 7.5 + 9)

**Phase 7.5 - Fix Opzionali**:
- [ ] Fix 7.5.2: Typo ABANDON_CRASH corretto
- [ ] Fix 7.5.3: Timer expiry STRICT mode testato
- [ ] Fix 7.5.1: ProfileLogger creato (opzionale)
- [ ] Fix 7.5.4: Startup recovery dialog (opzionale)

**Phase 9 - Menu Integration**:
- [ ] LastGameDialog creato
- [ ] Menu "U - Ultima Partita" funzionante
- [ ] Menu "L - Leaderboard" funzionante
- [ ] Profile menu opzione "5" wired a DetailedStatsDialog

**DECISIONE RICHIESTA**: 
- Completare Phase 7.5 critici (12 min) + Phase 9 (45 min) = **~57 min totali**?
- Oppure skip 7.5 e fare solo Phase 9 (45 min), Issue per fix post-merge?

---

## 🧪 Testing Strategy

### Unit Tests (Automated)

- **Feature 1** ✅: 25 unit tests (100% pass)
- **Feature 2** ✅: 63 unit tests (100% pass)
- **Feature 3** ✅: 15 unit tests StatsFormatter (100% pass)
- **Target Coverage**: ≥88% (project standard) ✅

### Integration Tests (Automated)

- **Feature 1** ✅: 7 integration tests
- **Feature 2** ✅: 12 integration tests
- **Feature 3** ⏸️: GameEngine hooks testati, dialog integration manuale

### Manual Tests (NVDA Accessibility)

- **Feature 3**: 30+ checklist items - **RICHIESTO TESTING**
- Test ogni dialog con NVDA attivo
- Verifica keyboard navigation, focus management, TTS announcements

---

## ✅ Criteri di Completamento

### Feature 1 (Timer System) ✅ COMPLETATA

- [x] Tutte le 8 fasi completate
- [x] 25 unit/integration tests passano (100%)
- [x] Timer STRICT/PERMISSIVE funzionante
- [x] TTS announcements single-fire
- [x] Session outcome popolato per ProfileService

### Feature 2 (Profile System) ✅ COMPLETATA

- [x] Tutte le 9 fasi completate
- [x] 63 unit/integration tests passano (100%)
- [x] ProfileStorage writes atomici
- [x] Stats aggregation corretta
- [x] Session recovery funzionante
- [x] ProfileService integrato in DI container

### Feature 3 (Stats Presentation) 🔄 90% COMPLETATA

**✅ Core Completato (Phase 1-8):**
- [x] StatsFormatter completo e testato (15 tests)
- [x] Victory/Abandon dialogs con stats integrate
- [x] GameInfo dialog (tasto I)
- [x] Detailed stats 3 pagine creato
- [x] Leaderboard creato
- [x] GameEngine ProfileService ATTIVATO
- [x] NVDA accessibility implementata

**⏸️ Mancante (Phase 7.5 - Fix Opzionali):**
- [ ] Fix 7.5.2: Typo ABANDON_CRASH (2 min - raccomandato)
- [ ] Fix 7.5.3: Timer expiry verification (10 min - CRITICO)
- [ ] Fix 7.5.1: Semantic logging (15 min - nice-to-have)
- [ ] Fix 7.5.4: Startup recovery dialog (5 min - nice-to-have)

**⏸️ Mancante (Phase 9 - Menu Integration):**
- [ ] LastGameDialog creato
- [ ] Menu "U - Ultima Partita" implementato
- [ ] Menu "L - Leaderboard" implementato
- [ ] Profile menu "5" wired a stats
- [ ] NVDA checklist 100% testata manualmente

### Stack Completo

- [x] Feature 1 completata (100%) ✅
- [x] Feature 2 completata (100%) ✅
- [ ] Feature 3 completata (90% - Phase 7.5 + 9 mancanti) 🔄
- [x] Test coverage ≥88% (su componenti implementati) ✅
- [ ] CHANGELOG.md aggiornato
- [ ] README.md aggiornato se necessario
- [ ] Branch ready per merge (dopo Phase 7.5 + 9)

---

## 📝 Aggiornamenti Obbligatori a Fine Implementazione

### Post Feature 3 (Stats Presentation v3.1.0 UI)

- [ ] **COMPLETARE Phase 7.5**: Fix critici 7.5.2 + 7.5.3 (12 min stimati) ⚡
- [ ] **COMPLETARE Phase 9**: Menu integration (45 min stimati) 📋
- [ ] Aggiornare `CHANGELOG.md` con entry v3.1.0 UI
  - Victory/abandon dialogs with stats ✅
  - Detailed stats (3 pages) ✅
  - Global leaderboard ✅
  - Menu integration (U, L, Stats) ⏸️
  - NVDA accessibility ✅
- [ ] Aggiornare `README.md` con screenshot/istruzioni nuove UI
- [ ] Testing manuale NVDA completo (30+ items)
- [ ] Commit finale: `chore: Complete v3.1.0 - Stats Presentation UI`
- [ ] Tag release: `git tag v3.1.0`

---

## 📌 Note Operative

### Phase 7.5 + Phase 9 Implementation Notes

**Workflow Raccomandato**:
```
1. ⚡ Phase 7.5 Fix Critici (12 min):
   - Fix 7.5.2: Typo ABANDON_CRASH (2 min)
   - Fix 7.5.3: Timer expiry test (10 min)
   
2. 📋 Phase 9 Menu Integration (45 min):
   - Commit 9.1: LastGameDialog + menu "U" (15-22 min)
   - Commit 9.2: Menu "L - Leaderboard" (8-12 min)
   - Commit 9.3: Profile menu "5" → Stats (10-15 min)
   
3. 📋 Issue Post-Merge (opzionale):
   - Fix 7.5.1: Semantic logging (15 min)
   - Fix 7.5.4: Startup recovery dialog (5 min)
```

**Tempo Totale**: 12 min (fix critici) + 45 min (menu) = **~57 minuti**

**File Target Identificati**:
- **Main entry point**: `acs_wx.py` (root directory)
- **GameEngine**: `src/application/game_engine.py` (già modificato in Phase 7)
- **Menu handlers**: Cercare in `acs_wx.py` i metodi:
  - Main menu builder/handler (pattern: "Nuova Partita", "Opzioni", "Esci")
  - Profile menu handler (pattern: "Cambia Profilo", "Crea Nuovo")

---

## 🚀 Quick Start per Copilot Agent - Phase 7.5 + 9

### Step-by-Step per Completamento

1. **✅ Phase 1-8 COMPLETATE** - Core dialogs + ProfileService funzionanti
2. **⚡ Next: Phase 7.5 Fix Critici** (12 min raccomandati)
   - Read [`PHASE_7_5_OPTIONAL_FIXES.md`](3%20-%20coding%20plans/PHASE_7_5_OPTIONAL_FIXES.md)
   - Implement Fix 7.5.2 (typo - 2 min)
   - Implement Fix 7.5.3 (timer test - 10 min)
   - Update TODO.md (spunta fix completati)
3. **📋 Next: Phase 9 Menu** (45 min)
   - Read [`PHASE_9_MENU_INTEGRATION_UPDATED.md`](3%20-%20coding%20plans/PHASE_9_MENU_INTEGRATION_UPDATED.md)
   - Implement Commit 9.1: LastGameDialog + menu "U"
   - Implement Commit 9.2: Menu "L" → LeaderboardDialog
   - Implement Commit 9.3: Profile menu "5" → DetailedStatsDialog
   - Update TODO.md (spunta Phase 9 checkboxes)
4. **🧪 Manual testing**: NVDA checklist completa
5. **✅ Ready for merge**

---

**Fine TODO.**

**STATUS**: Feature 3 al 90% - Phase 7.5 fix critici (12 min) + Phase 9 menu (45 min) richiesti per completamento 100%.
