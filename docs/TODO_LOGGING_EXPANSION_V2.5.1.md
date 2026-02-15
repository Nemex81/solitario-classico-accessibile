# TODO: Logging System Expansion v2.5.1

**Versione Target**: v2.5.1  
**Branch**: `refactoring-engine`  
**Effort Totale**: 15 commit atomici  
**Piano Dettagliato**: `docs/PLAN_LOGGING_EXPANSION_V2.5.1.md`

---

## 🎯 Obiettivo

Espandere il sistema di logging esistente (`src/infrastructure/logging/game_logger.py`) per tracciare 24 categorie di eventi attualmente non loggati, migliorando debugging, UX analytics e monitoraggio applicazione.

**Sistema Logging Esistente**: ✅ Già implementato (v2.3.0)  
**Funzioni Disponibili**: `log.game_started()`, `log.card_moved()`, `log.panel_switched()`, ecc.

---

## 📋 WORKFLOW SEQUENZIALE

```
LEGGI TODO (questo file)
    ↓
CONSULTA PIANO DETTAGLIATO (docs/PLAN_LOGGING_EXPANSION_V2.5.1.md)
    ↓
IMPLEMENTA FASE 1 (commit 1.1-1.4)
    ↓
AGGIORNA TODO (spunta ✅)
    ↓
IMPLEMENTA FASE 2 (commit 2.1-2.5)
    ↓
AGGIORNA TODO (spunta ✅)
    ↓
IMPLEMENTA FASE 3 (commit 3.1-3.6)
    ↓
COMPLETA ✅
```

---

## FASE 1: UI LIFECYCLE & PANEL TRANSITIONS

**Priorità**: ⭐⭐⭐ Alta  
**Commits**: 4 atomici  
**File Modificati**: `acs_wx.py`, `view_manager.py`

- [x] **1.1** - `acs_wx.py`: Log panel transitions in `start_gameplay()`, `return_to_menu()`
- [x] **1.2** - `acs_wx.py`: Log panel hiding in `_safe_abandon_to_menu()`, `_safe_timeout_to_menu()`, `_safe_return_to_main_menu()`
- [x] **1.3** - `view_manager.py`: Log ViewManager panel swaps in `show_panel()`
- [x] **1.4** - `acs_wx.py`: Log options dialog lifecycle in `show_options()`

**Criterio Completamento FASE 1**:
- ✅ Ogni transizione panel loggata con `log.panel_switched()`
- ✅ Ogni panel hiding loggato con `log.debug_state()`
- ✅ Dialog options loggato con `log.dialog_shown()` / `log.dialog_closed()`
- ✅ Testing: ciclo menu→gameplay→ESC→menu produce log completo

---

## FASE 2: SETTINGS & DIFFICULTY PRESETS

**Priorità**: ⭐⭐⭐ Alta  
**Commits**: 5 atomici  
**File Modificati**: `game_settings.py`, `options_controller.py`, `game_engine.py`

- [x] **2.1** - `game_settings.py`: Log settings persistence (`load_from_file()`, `save_to_file()`)
- [ ] **2.2** - `options_controller.py`: Log difficulty preset applications (`_apply_difficulty_preset()`)
- [ ] **2.3** - `game_settings.py`: Log individual setting changes (tutti i setter properties)
- [ ] **2.4** - `game_engine.py`: Log deck type change in `new_game()`
- [ ] **2.5** - `game_settings.py`: Log settings reset to defaults

**Criterio Completamento FASE 2**:
- ✅ Load/save settings loggato con `log.settings_changed()` / `log.warning_issued()`
- ✅ Preset applicati loggati con `log.settings_changed()` + `log.debug_state()`
- ✅ Ogni modifica singola impostazione loggata
- ✅ Testing: ciclo completo modifica impostazioni produce log dettagliato

---

## FASE 3: GAME OPERATIONS & SCORING

**Priorità**: ⭐⭐ Media  
**Commits**: 6 atomici  
**File Modificati**: `game_engine.py`, `gameplay_controller.py`, `game_service.py`, `score_storage.py`, `scoring_service.py`

- [ ] **3.1** - `game_engine.py`: Log card selection/deselection
- [ ] **3.2** - `game_engine.py`: Log auto-selection (double-tap feature)
- [ ] **3.3** - `gameplay_controller.py`: Log hint requests
- [ ] **3.4** - `game_service.py`: Log auto-complete & undo operations
- [ ] **3.5** - `score_storage.py`: Log score storage persistence
- [ ] **3.6** - `scoring_service.py`: Log scoring penalties/bonuses

**Criterio Completamento FASE 3**:
- ✅ Selezione/deselezione loggata con `log.debug_state()`
- ✅ Hint/undo loggati con `log.info_query_requested()`
- ✅ Score persistence loggato con `log.info_query_requested()` / `log.error_occurred()`
- ✅ Testing: partita completa produce log UX analytics

---

## 🎯 CRITERI COMPLETAMENTO GLOBALI

### Tutti i Commit Devono:
- ✅ Usare SOLO funzioni esistenti `game_logger.py` (NO nuove funzioni)
- ✅ Seguire pattern esistenti (livelli log corretti: INFO/DEBUG/WARNING/ERROR)
- ✅ Includere parametri contestuali (es. `{"pile": "tableau_3", "count": 5}`)
- ✅ Non rompere funzionalità esistente (zero breaking changes)
- ✅ Commit message convenzionale: `feat(logging): add logs for [event]`

### Testing Finale (Dopo FASE 3):
- ✅ Avvia app → menu → gameplay → modifica opzioni → vittoria → esci
- ✅ Verifica `solitaire.log` contiene log completi per TUTTE le azioni
- ✅ Nessun crash, nessun log mancante
- ✅ Zero warning Python durante esecuzione

---

## 📊 PROGRESS TRACKER

| Fase | Commits | Completato |
|------|---------|------------|
| FASE 1 | 4 | ✅ 4/4 |
| FASE 2 | 5 | ⚙️ 1/5 |
| FASE 3 | 6 | ⬜ 0/6 |
| **TOTALE** | **15** | **⚙️ 5/15** |

---

## 🚀 ISTRUZIONI COPILOT

1. **Consulta Piano Dettagliato**: Leggi `docs/PLAN_LOGGING_EXPANSION_V2.5.1.md` prima di iniziare
2. **Implementa Sequenzialmente**: FASE 1 → 2 → 3 (NO parallelo)
3. **Commit Atomici**: 1 commit = 1 file modificato (max 2 se strettamente correlati)
4. **Aggiorna TODO**: Spunta ✅ dopo ogni commit
5. **Testing Incrementale**: Testa dopo ogni fase completa

**IMPORTANTE**: Non aggiungere nuove funzioni a `game_logger.py`. Usa SOLO quelle esistenti.

---

**Versione**: v2.5.1  
**Autore**: Nemex81  
**Data Creazione**: 2026-02-15
