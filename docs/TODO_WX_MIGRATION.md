# 📋 TODO – Migrazione wxPython Puro (v2.0.0)

**Branch**: `feature/wx-only-migration`  
**Tipo**: REFACTOR + BREAKING CHANGE  
**Priorità**: HIGH  
**Stato**: READY  
**Stima**: 20-25 ore (3-4 giorni lavorativi)

---

## 📖 Riferimento Documentazione

**Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente**:
- [`docs/MIGRATION_PLAN_WX_ONLY.md`](./MIGRATION_PLAN_WX_ONLY.md) - Piano completo e dettagliato

**Questo file TODO è solo un sommario operativo da consultare all'inizio di ogni fase di implementazione e da aggiornare alla fine di ogni di fase implementazione**.  
Il piano completo contiene:
- Analisi architettura attuale e target
- Gestione conflitti input e priorità eventi  
- Mapping completo 80+ key codes
- Scenari testing NVDA (6 scenari dettagliati)
- Rischi e mitigazioni con contingency plans
- Timeline giorno-per-giorno

---

## 🎯 Obiettivo Implementazione

**Eliminare dipendenza pygame e migrare a wxPython puro per gestione interfaccia audiogame**.

**Motivazioni**:
- **Accessibilità NVDA migliorata**: Eventi tastiera wx nativi meglio integrati con screen reader
- **Architettura più pulita**: Un solo framework UI (wx) invece di ibrido pygame+wx
- **Meno dipendenze**: Rimozione pygame (2.1.2) e pygame-menu (4.3.7)
- **Performance**: Event loop wx più efficiente, no overhead rendering pygame

**Impatto**:
- Breaking change: Entry point cambia da pygame-based a wx-based
- Backward compatibility: Comportamento utente finale identico (60+ comandi invariati)
- Testing critico: Validazione NVDA intensiva richiesta

---

## 📂 File Coinvolti

### Nuovi File (CREATE)
- [ ] `src/infrastructure/ui/wx_app.py` → Main wx.App wrapper
- [ ] `src/infrastructure/ui/wx_frame.py` → Invisible frame + event sink  
- [ ] `src/infrastructure/ui/wx_menu.py` → Menu virtuale wx-based
- [ ] `src/infrastructure/ui/wx_key_adapter.py` → wx→pygame event adapter
- [ ] `src/infrastructure/ui/wx_timer.py` → Timer manager wrapper
- [ ] `wx_main.py` (root) → Nuovo entry point wxPython
- [ ] `docs/MIGRATION_GUIDE_V2.md` → Guida migrazione v1.x→v2.0.0
- [ ] `tests/infrastructure/test_wx_components.py` → Unit test componenti wx

### File Modificati (MODIFY)
- [ ] `src/application/gameplay_controller.py` → Aggiungere `handle_wx_key_event()` wrapper
- [ ] `requirements.txt` → Rimuovere pygame, pygame-menu
- [ ] `README.md` → Aggiornare requisiti sistema e istruzioni avvio
- [ ] `CHANGELOG.md` → Sezione v2.0.0 con breaking changes

### File Deprecati (RENAME/BACKUP)
- [ ] `test.py` → `test_pygame_legacy.py` (backup)
- [ ] `src/infrastructure/ui/menu.py` → Deprecato ma mantenuto per riferimento

---

## 🛠 Checklist Implementazione

### FASE 1: Infrastruttura wx Base (3-4 ore)

#### Task 1.1: Creare `wx_app.py`
- [x] Creare file `src/infrastructure/ui/wx_app.py`
- [x] Implementare classe `SolitarioWxApp(wx.App)`
- [x] Callback `on_init_complete` per post-init setup
- [x] Testing: App si avvia senza errori
- [x] Testing: `OnInit()` chiamato correttamente
- [x] Testing: No crash all'uscita
- [x] Commit: `feat(infrastructure): Add wx_app.py base wrapper`

#### Task 1.2: Creare `wx_frame.py`
- [x] Creare file `src/infrastructure/ui/wx_frame.py`
- [x] Implementare classe `SolitarioFrame(wx.Frame)`
- [x] Frame invisibile (1x1 pixel, no taskbar)
- [x] Event binding: `EVT_KEY_DOWN`, `EVT_CHAR`, `EVT_CLOSE`
- [x] Timer management: `wx.Timer` per timeout check
- [x] Metodi: `start_timer()`, `stop_timer()`, `_on_timer_tick()`
- [x] Testing: Frame invisibile (no window visibile)
- [x] Testing: Eventi tastiera catturati correttamente
- [x] Testing: Timer funziona (1 tick/secondo ±50ms)
- [x] Testing: Chiusura graceful
- [x] Commit: `feat(infrastructure): Add wx_frame.py event sink`

#### Task 1.3: Creare `wx_menu.py`
- [x] Creare file `src/infrastructure/ui/wx_menu.py`
- [x] Implementare classe `WxVirtualMenu`
- [x] Metodi: `next_item()`, `prev_item()`, `execute()`, `handle_key_event()`
- [x] Navigazione UP/DOWN con wrap-around
- [x] Feedback TTS per ogni azione
- [x] Testing: Menu annuncia apertura
- [x] Testing: UP/DOWN navigano correttamente
- [x] Testing: ENTER esegue callback
- [x] Testing: Wrap-around (ultimo→primo)
- [x] Verifica API compatibile con `infrastructure/ui/menu.py` esistente
- [x] Commit: `feat(infrastructure): Add wx_menu.py virtual menu`

---

### FASE 2: Key Event Adapter (2-3 ore)

#### Task 2.1: Creare `wx_key_adapter.py`
- [x] Creare file `src/infrastructure/ui/wx_key_adapter.py`
- [x] Implementare classe `WxKeyEventAdapter`
- [x] Mapping completo `WX_TO_PYGAME_MAP` (80+ key codes)
  - [x] Frecce (UP, DOWN, LEFT, RIGHT)
  - [x] Tasti speciali (RETURN, SPACE, ESC, TAB, DELETE, HOME, END)
  - [x] Function keys (F1-F12)
  - [x] Numeri row (0-9)
  - [x] Lettere (A-Z maiuscole e minuscole)
  - [x] Numpad (0-9, ENTER, operatori)
- [x] Metodo `convert_to_pygame_event(wx_event)` → pygame.event.Event
- [x] Metodo `_get_pygame_mods(wx_event)` → traduzione modificatori
- [x] Testing: Mapping 60+ tasti usati nel gioco
- [x] Testing: Modificatori (SHIFT, CTRL, ALT) corretti
- [x] Testing: Lettere maiuscole/minuscole
- [x] Testing: Numpad vs numeri normali
- [x] Commit: `feat(infrastructure): Add wx key event adapter with 80+ mappings`

#### Task 2.2: Modificare `gameplay_controller.py`
- [x] Aprire `src/application/gameplay_controller.py`
- [x] Aggiungere metodo `handle_wx_key_event(self, wx_event)`
- [x] Import `WxKeyEventAdapter` nel metodo
- [x] Conversione wx→pygame tramite adapter
- [x] Chiamata a `handle_keyboard_events()` esistente
- [x] Testing: Comandi gameplay funzionano con wx events
- [x] Testing: SHIFT+1-4 (pile semi) funzionano
- [x] Testing: CTRL+ALT+W (debug victory) funziona
- [x] Testing: Tutti i 60+ comandi testati
- [x] Commit: `feat(application): Add wx event handler to gameplay controller`

---

### FASE 3: Nuovo Entry Point wxPython (2 ore)

#### Task 3.1: Creare `wx_main.py`
- [x] Creare file `wx_main.py` (root progetto)
- [x] Implementare classe `SolitarioController`
- [x] Metodo `run()` → avvia `wx.App.MainLoop()`
- [x] Callback `_on_init_complete()` → setup post-wx
- [x] Metodo `_on_key_event(event)` → router eventi
- [x] Gerarchia priorità eventi:
  - [x] Dialog modali (gestiti automaticamente da wx)
  - [x] Options window (forward a `options_controller`)
  - [x] Menu navigazione (chiamata `menu.handle_key_event()`)
  - [x] Gameplay (chiamata `controller.handle_wx_key_event()`)
- [x] Gestione ESC context-aware (6 contesti):
  - [x] Main menu → Exit dialog
  - [x] Game submenu → Return to main dialog
  - [x] Gameplay (primo ESC) → Abandon game dialog
  - [x] Gameplay (doppio ESC <2s) → Instant abandon
  - [x] Options window → Close options
  - [x] Dialog nativo → Close dialog (wx automatico)
- [x] Double-ESC detection (`last_esc_time` tracking)
- [x] Timer callback `_check_timer_expiration()` → timeout check
- [x] Metodi helper:
  - [x] `_show_main_menu()`
  - [x] `_start_game()`
  - [x] `_show_exit_dialog()`
  - [x] `_show_abandon_game_dialog()`
  - [x] `_quit_app()`
- [x] Testing: App si avvia senza errori
- [x] Testing: Menu navigabile (UP/DOWN/ENTER)
- [x] Testing: Gameplay funziona (comandi base)
- [x] Testing: Dialog nativi si aprono
- [x] Testing: Timer timeout attivo
- [x] Testing: ESC in ogni contesto funziona
- [x] Testing: Double-ESC quick exit funziona
- [x] Commit: `feat: Add wx_main.py entry point - pygame replacement ready`

---

### FASE 4: Testing, Cleanup, Migrazione (3-4 ore)

#### Task 4.1: Testing Parallelo (2 ore)
- [ ] Test A: `python test.py` (pygame legacy) → Feature baseline
- [ ] Test B: `python wx_main.py` (wx nuovo) → Feature parity
- [ ] Checklist Parità Funzionale:
  - [ ] Menu navigazione identica
  - [ ] Avvio partita funzionante
  - [ ] 60+ comandi gameplay identici
  - [ ] Dialog nativi funzionano
  - [ ] Timer timeout preciso (±100ms)
  - [ ] Opzioni (O key) funzionante
  - [ ] ESC confirmation in tutti i 6 contesti
  - [ ] Double-ESC quick exit (< 2 secondi)
  - [ ] Vittoria detection e report statistiche
  - [ ] Scoring system attivo
- [ ] Fix bug minori emersi durante testing
- [ ] Commit: `test: Validate wx implementation feature parity with pygame`

#### Task 4.2: Testing NVDA Intensivo (2 ore)
- [ ] **Scenario 1: Menu Navigation**
  - [ ] Avvio app: NVDA annuncia "Menu. 2 opzioni. Gioca al solitario classico."
  - [ ] Freccia GIÙ: NVDA annuncia "Esci dal gioco"
  - [ ] Freccia SU: NVDA annuncia wrap-around
  - [ ] ENTER: NVDA annuncia apertura submenu
- [ ] **Scenario 2: Gameplay Commands**
  - [ ] Avvio partita: NVDA annuncia "Nuova partita avviata!"
  - [ ] Tasto 1: NVDA annuncia carta pila 1
  - [ ] SHIFT+1: NVDA annuncia carta pila semi cuori
  - [ ] D: NVDA annuncia pesca carte
  - [ ] H: NVDA annuncia help comandi (lungo messaggio)
- [ ] **Scenario 3: Dialog Native**
  - [ ] ESC in menu: NVDA annuncia dialog, legge "Vuoi uscire?"
  - [ ] TAB in dialog: NVDA cicla tra pulsanti Sì/No
  - [ ] ENTER su Sì: NVDA annuncia conferma azione
  - [ ] ESC in dialog: NVDA annuncia chiusura
  - [ ] Focus torna a menu: NVDA ri-annuncia voce corrente
- [ ] **Scenario 4: Timer Expiration**
  - [ ] Timer scade (STRICT mode): NVDA annuncia "Tempo scaduto!"
  - [ ] Report statistiche: NVDA legge report completo
  - [ ] Ritorno menu: NVDA annuncia menu di gioco
- [ ] **Scenario 5: Victory Flow**
  - [ ] Vittoria: NVDA annuncia "Vittoria!" + statistiche
  - [ ] Dialog rematch: NVDA legge "Vuoi giocare ancora?"
  - [ ] Selezione Sì: NVDA annuncia nuova partita
- [ ] **Scenario 6: Options Window**
  - [ ] Tasto O: NVDA annuncia apertura opzioni
  - [ ] Freccia GIÙ: NVDA annuncia ciascuna opzione
  - [ ] ENTER su opzione: NVDA annuncia cambio valore
  - [ ] ESC: NVDA annuncia chiusura, ritorno menu
- [ ] Nessun conflitto hotkey NVDA rilevato
- [ ] Focus management corretto in tutti gli scenari
- [ ] Browse mode disabilitato (focus mode attivo)
- [ ] Commit: `test: NVDA accessibility validation passed (6 scenarios)`

#### Task 4.3: Rimozione pygame e Migrazione Entry Point (1 ora)
- [x] **Step 1**: Backup `test.py`
  - [x] Rinominare `test.py` → `test_pygame_legacy.py`
- [x] **Step 2**: Promuovere nuovo entry point
  - [x] Rinominare `wx_main.py` → `test.py`
- [x] **Step 3**: Aggiornare `requirements.txt`
  - [x] Commentare `pygame==2.1.2` con nota `# REMOVED v2.0.0`
  - [x] Commentare `pygame-menu==4.3.7` con nota `# REMOVED v2.0.0`
- [x] **Step 4**: Testing post-rimozione
  - [x] `python test.py` → App si avvia senza pygame
  - [x] No import errors o crash
  - [x] Tutte le feature funzionanti
- [x] **Step 5**: Deprecare file obsoleti
  - [x] Aggiungere header deprecation notice in `src/infrastructure/ui/menu.py`
  - [x] File mantenuto per riferimento ma non importato
- [x] Commit: `feat!: Remove pygame dependency - migrate to wx-only (v2.0.0)`

#### Task 4.4: Documentazione e Release Notes (1 ora)
- [ ] **Aggiornare CHANGELOG.md**
  - [ ] Sezione `## [2.0.0] - 2026-02-XX`
  - [ ] Subsection `### 🚨 BREAKING CHANGES`
  - [ ] Subsection `### ✨ Features`
  - [ ] Subsection `### 🐛 Bug Fixes`
  - [ ] Subsection `### 📦 Dependencies`
  - [ ] Subsection `### 🏗️ Architecture`
- [ ] **Aggiornare README.md**
  - [ ] Sezione requisiti sistema (rimuovere pygame)
  - [ ] Sezione installazione dipendenze
  - [ ] Note sulla migrazione v1.x→v2.0.0
- [ ] **Creare MIGRATION_GUIDE_V2.md**
  - [ ] Sezione "Cosa Cambia per l'Utente Finale" (Niente!)
  - [ ] Sezione "Cosa Cambia per gli Sviluppatori"
  - [ ] Esempi codice: Import changes, Event handling changes
  - [ ] FAQ troubleshooting
- [ ] **Creare unit test base**
  - [ ] File `tests/infrastructure/test_wx_components.py`
  - [ ] Classe `TestWxKeyAdapter` (mapping keys, modifiers)
  - [ ] Classe `TestWxMenu` (navigation, selection, wrap-around)
  - [ ] Classe `TestWxTimer` (precision ±50ms)
  - [ ] `pytest tests/infrastructure/test_wx_components.py` → Tutti passano
- [ ] Commit: `docs: Add v2.0.0 migration guide and update README/CHANGELOG`

---

## ✅ Criteri di Completamento

L'implementazione è considerata **COMPLETA** quando:

### Funzionalità Core
- [ ] Menu navigazione completa (UP/DOWN/ENTER)
- [ ] Avvio partita funzionante
- [ ] Tutti i 60+ comandi gameplay testati e funzionanti
- [ ] Timer timeout preciso (±100ms tolleranza)
- [ ] Dialog nativi funzionanti in tutti i contesti
- [ ] Options window funzionante (O key)
- [ ] Vittoria detection corretta
- [ ] Scoring system attivo e corretto
- [ ] Double-ESC quick exit (< 2 secondi)

### Accessibilità NVDA
- [ ] NVDA annuncia apertura app
- [ ] Menu items annunciati correttamente
- [ ] Comandi gameplay vocalized
- [ ] Dialog nativi leggibili (TAB cicla pulsanti)
- [ ] Focus management corretto (no perdita focus)
- [ ] Report statistiche leggibile completamente
- [ ] No hotkey conflicts NVDA rilevati
- [ ] Tutti i 6 scenari NVDA passati

### Qualità Codice
- [ ] Zero import pygame nel codice wx
- [ ] Type hints completi su nuovi file (wx_*.py)
- [ ] Docstring Google-style su classi/metodi pubblici
- [ ] No code duplication (DRY rispettato)
- [ ] Clean Architecture rispettata (no violazioni layer)
- [ ] Unit tests creati e passano (pytest green)
- [ ] No regressioni su test esistenti

### Documentazione
- [ ] CHANGELOG.md aggiornato (v2.0.0 con breaking changes)
- [ ] README.md aggiornato (requisiti, avvio, note migrazione)
- [ ] MIGRATION_GUIDE_V2.md creato e completo
- [ ] TODO_WX_MIGRATION.md aggiornato (tutte le checkbox spuntate)
- [ ] Commit messages convenzionali (feat!, docs, test, etc.)

### Performance
- [ ] Avvio app < 3 secondi
- [ ] Memoria base < 50 MB
- [ ] CPU idle < 5%
- [ ] Input latency < 20ms
- [ ] Timer precision ±50ms (migliorata vs pygame)

### Regressione
- [ ] Tutte le feature v1.x funzionanti identicamente
- [ ] Comportamento 100% compatibile per utente finale
- [ ] No breaking changes non documentati
- [ ] Settings files backward compatible

---

## 📝 Aggiornamenti Obbligatori Post-Implementazione

- [ ] **README.md**: Sezione requisiti aggiornata (no pygame)
- [ ] **CHANGELOG.md**: Entry v2.0.0 completa con breaking changes evidenziati
- [ ] **Versione**: Incrementata a `2.0.0` (MAJOR - breaking change)
- [ ] **Commit finale**: `feat!: Complete pygame removal migration to wx-only v2.0.0`
- [ ] **Push branch**: `git push origin feature/wx-only-migration`
- [ ] **Pull Request**: Creata con descrizione dettagliata e link a piano completo
- [ ] **Review**: Testing NVDA documentato in PR description
- [ ] **Merge**: In `refactoring-engine` dopo approvazione review

---

## 📌 Note Operative

### Branch Strategy
```bash
# Creare branch da refactoring-engine
git checkout refactoring-engine
git pull origin refactoring-engine
git checkout -b feature/wx-only-migration

# Durante sviluppo: commit frequenti
git add .
git commit -m "feat(infrastructure): ..."

# Push periodico per backup
git push origin feature/wx-only-migration

# A fine implementazione: PR
gh pr create --base refactoring-engine --title "feat!: Remove pygame, migrate to wx-only (v2.0.0)"
```

### Testing Rapido Durante Sviluppo
```bash
# Test pygame legacy (baseline)
python test_pygame_legacy.py

# Test wx nuovo (work in progress)
python wx_main.py

# Unit test componenti wx
pytest tests/infrastructure/test_wx_components.py -v

# Test completi (lento)
pytest tests/ -v
```

### Debug NVDA Issues
Se NVDA non annuncia correttamente:
1. Verificare `event.Skip()` chiamato dopo handling
2. Aggiungere `wx.CallAfter()` per timing TTS
3. Testare con Orca su Linux (cross-validation)
4. Consultare `docs/MIGRATION_PLAN_WX_ONLY.md` sezione "Rischi e Mitigazioni"

### Priorità Task
- **CRITICO**: FASE 1-3 (infrastruttura e entry point)
- **ALTO**: Task 4.2 (testing NVDA)
- **MEDIO**: Task 4.4 (documentazione)
- **BASSO**: Unit test (se tempo limitato, rimandare post-merge)

### Contingency Plan
Se emergono blockers insormontabili:
1. Mantenere `test_pygame_legacy.py` come fallback funzionante
2. Documentare issue in PR description
3. Merge solo quando parità funzionale 100% raggiunta
4. Rollback possibile: `git revert` commit problematici

---

## 🏁 Status Tracking

**Ultima modifica**: 2026-02-12  
**Progresso**: 0/120 task completati (0%)  
**Fase corrente**: READY - Non iniziato  
**Blockers**: Nessuno  
**Prossimo step**: Creare branch `feature/wx-only-migration` e iniziare FASE 1

---

**Fine TODO** - Per dettagli completi consultare [`docs/MIGRATION_PLAN_WX_ONLY.md`](./MIGRATION_PLAN_WX_ONLY.md)
