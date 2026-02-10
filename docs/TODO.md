# 📋 TODO - Solitario Accessibile v1.4.3
**Piano di Implementazione**: UX Improvements (Double-Tap Selection + Menu Shortcuts)  
**Data Inizio**: 10 Febbraio 2026  
**Documentazione Completa**: `docs/IMPLEMENTATION_DOUBLE_TAP_AND_MENU_SHORTCUTS.md`

---

## ⚠️ **NOTA CRITICA: USARE FILE CLEAN ARCHITECTURE**

🚨 **ATTENZIONE**: Questo progetto ha DUE versioni parallele:

| Versione | Path | Entry Point | Usare per v1.4.3? |
|----------|------|-------------|-------------------|
| **Clean Architecture** | `src/` | `test.py` | ✅ **SÌ** |
| **Legacy** | `scr/` | `acs.py` | ❌ **NO** |

**FASE 2 (Double-Tap)**: ✅ File `src/` già specificati correttamente
**FASE 3 (Menu Shortcuts)**: ⚠️ Deve usare `src/infrastructure/ui/menu.py` (NON `scr/pygame_menu.py`)

---

## 🎯 OVERVIEW

**Obiettivo**: Implementare due miglioramenti UX per accessibilità:
1. **Double-Tap Auto-Selection**: Selezione automatica carta con doppia pressione numero pila
2. **Numeric Menu Shortcuts**: Scorciatoie numeriche per navigazione rapida menu

**Impatto**: 3 file Clean Arch, ~150 righe di codice  
**Stima Tempo**: 2.5-3.5 ore  
**Target Release**: v1.4.3

---

## ✅ FASE 1: Setup & Preparation

- [x] Creazione file `docs/IMPLEMENTATION_DOUBLE_TAP_AND_MENU_SHORTCUTS.md`
- [x] Creazione/aggiornamento `TODO.md` con checklist
- [x] Correzione path documentazione (src/ Clean Architecture)
- [ ] Review piano con stakeholder (se necessario)
- [ ] Setup branch di sviluppo (opzionale)

---

## 🔥 FASE 2: Feature #1 - Double-Tap Auto-Selection ✅ PATH CORRETTI

### Step 2.1: Modifica CursorManager (`src/domain/services/cursor_manager.py`) ✅

- [ ] **Aprire file**: `src/domain/services/cursor_manager.py` ✅ Path corretto
- [ ] **Import**: Aggiornare `from typing import Tuple, Optional, Dict, Any`
- [ ] **Metodo `jump_to_pile()`** (riga ~380):
  - [ ] Cambiare signature: `def jump_to_pile(...) -> Tuple[str, bool]`
  - [ ] Implementare double-tap detection: `if pile_idx == last_quick_pile`
  - [ ] Gestire pile stock/waste: ritorno `("Cursore già sulla pila.", False)`
  - [ ] Gestire pile tableau/foundation vuote: ritorno `("Pila vuota...", False)`
  - [ ] Gestire pile tableau/foundation con carte:
    - [ ] Chiamare `move_to_top_card()`
    - [ ] Ritornare `("", True)` per triggare auto-selection
  - [ ] Aggiornare hint primo tap: "Premi ancora [numero] per selezionare"
  - [ ] Reset `last_quick_pile = None` dopo secondo tap
- [ ] **Test isolato**: Verificare ritorno Tuple corretto in vari scenari

#### Test Checklist Step 2.1
- [ ] T1: Primo tap → ritorna `(messaggio, False)`
- [ ] T2: Secondo tap pile base → ritorna `("", True)`
- [ ] T3: Secondo tap pile vuota → ritorna `(errore, False)`
- [ ] T4: Secondo tap scarti/mazzo → ritorna `(hint, False)`

---

### Step 2.2: Modifica GameEngine (`src/application/game_engine.py`) ✅

- [ ] **Aprire file**: `src/application/game_engine.py` ✅ Path corretto
- [ ] **Metodo `jump_to_pile()`** (riga ~497):
  - [ ] Gestire ritorno Tuple: `msg, should_auto_select = self.cursor.jump_to_pile(...)`
  - [ ] Implementare blocco `if should_auto_select:`
    - [ ] Verificare selezione precedente: `if self.selection.has_selection()`
    - [ ] Annullare selezione: `self.selection.clear_selection()`
    - [ ] Creare messaggio: `msg_deselect = "Selezione precedente annullata. "`
    - [ ] Eseguire auto-selection: `success, msg_select = self.select_card_at_cursor()`
    - [ ] Combinare messaggi: `msg = msg_deselect + msg_select`
  - [ ] Mantenere vocal feedback: `self.screen_reader.tts.speak(msg, interrupt=True)`
- [ ] **Test integrazione**: CursorManager + GameEngine

#### Test Checklist Step 2.2
- [ ] T5: Secondo tap senza selezione precedente → seleziona carta
- [ ] T6: Secondo tap con selezione precedente → annulla old + seleziona new
- [ ] T7: Feedback vocale corretto per entrambi i casi

---

### Step 2.3: Testing Feature #1 Completo

#### Test Pile Base (1-7)
- [ ] **T1.1**: Primo tap pila 1 → Annuncia "Pila base 1. Carta in cima: [nome]. Premi ancora 1 per selezionare."
- [ ] **T1.2**: Secondo tap pila 1 → Seleziona automaticamente + annuncia "carte selezionate: 1. [nome]!"
- [ ] **T1.3**: Secondo tap con selezione attiva → Annuncia "Selezione precedente annullata. carte selezionate: 1. [nuovo nome]!"
- [ ] **T1.4**: Secondo tap pila vuota → Annuncia "Pila vuota, nessuna carta da selezionare."
- [ ] **T1.5**: Terza pressione dopo selezione → Comportamento primo tap (reset double-tap)

#### Test Pile Seme (SHIFT+1-4)
- [ ] **T1.6**: Primo tap SHIFT+2 → Annuncia "Pila semi Quadri. Carta in cima: [nome]. Premi ancora SHIFT+2 per selezionare."
- [ ] **T1.7**: Secondo tap SHIFT+2 → Seleziona automaticamente + feedback corretto
- [ ] **T1.8**: Secondo tap pila semi vuota → Messaggio errore appropriato

#### Test Scarti/Mazzo (Invariato)
- [ ] **T1.9**: Secondo tap SHIFT+S → "Cursore già sulla pila." (NO auto-select)
- [ ] **T1.10**: Secondo tap SHIFT+M → "Cursore già sulla pila." (NO auto-select)

#### Test Edge Cases
- [ ] **T1.11**: Tap pila diversa resetta `last_quick_pile`
- [ ] **T1.12**: Movimento frecce resetta `last_quick_pile`
- [ ] **T1.13**: Selezione manuale (INVIO) non interferisce con tracking

---

## 🎨 FASE 3: Feature #2 - Numeric Menu Shortcuts ⚠️ PATH CORRETTI

### Step 3.1: Modifica VirtualMenu (`src/infrastructure/ui/menu.py`) ⚠️ CRITICAL

⚠️ **ATTENZIONE**: Usare file **Clean Architecture**, NON il file legacy!
- ❌ **NON MODIFICARE**: `scr/pygame_menu.py` (legacy, non usato da test.py)
- ✅ **MODIFICARE**: `src/infrastructure/ui/menu.py` (Clean Arch, usato da test.py)

---

- [ ] **Aprire file**: `src/infrastructure/ui/menu.py` ✅ Path corretto Clean Arch
- [ ] **Metodo `__init__()`** (riga ~60):
  - [ ] Aggiungere chiamata: `self._build_key_handlers()` (alla fine di __init__)
- [ ] **Nuovo metodo `_build_key_handlers()`** (dopo `__init__()`, riga ~120):
  - [ ] Creare dict `self.key_handlers = {}`
  - [ ] Mappare: `pygame.K_DOWN: self.next_item`
  - [ ] Mappare: `pygame.K_UP: self.prev_item`
  - [ ] Mappare: `pygame.K_RETURN: self.execute`
  - [ ] Mappare: `pygame.K_ESCAPE: self._handle_esc`
  - [ ] Mappare: `pygame.K_1: self.press_1`
  - [ ] Mappare: `pygame.K_2: self.press_2`
  - [ ] Mappare: `pygame.K_3: self.press_3`
  - [ ] Mappare: `pygame.K_4: self.press_4`
  - [ ] Mappare: `pygame.K_5: self.press_5`
- [ ] **Nuovi metodi shortcut** (dopo `execute()`, riga ~200):
  - [ ] Implementare `press_1()`: if len >= 1, selected_index = 0, execute()
  - [ ] Implementare `press_2()`: if len >= 2, selected_index = 1, execute()
  - [ ] Implementare `press_3()`: if len >= 3, selected_index = 2, execute()
  - [ ] Implementare `press_4()`: if len >= 4, selected_index = 3, execute()
  - [ ] Implementare `press_5()`: if len >= 5, selected_index = 4, execute()
- [ ] **Nuovo metodo helper** (dopo shortcuts, riga ~250):
  - [ ] Implementare `_handle_esc()`: if parent_menu, parent_menu.close_submenu()
- [ ] **Modifica `handle_keyboard_events()`** (riga ~300):
  - [ ] Sostituire blocco if/elif con: `handler = self.key_handlers.get(event.key)`
  - [ ] Aggiungere: `if handler: handler()`

#### Test Checklist Step 3.1
- [ ] T8: VirtualMenu importato correttamente in test.py
- [ ] T9: Menu principale: premere `1` → Esegue prima voce
- [ ] T10: Game submenu: premere `1/2/3` → Esegue rispettive voci
- [ ] T11: Frecce UP/DOWN ancora funzionanti (no regressione)

---

### Step 3.2: Verificare Routing Eventi (`test.py`) ✅ NESSUNA MODIFICA NECESSARIA

⚠️ **NOTA**: Il routing eventi in `test.py` è **GIÀ CORRETTO**. Nessuna modifica necessaria.

---

- [ ] **Aprire file**: `test.py` (entry point Clean Architecture)
- [ ] **Verificare metodo `handle_events()`** (linee ~500-650):
  - [ ] ✅ Confermare routing: `if self.is_menu_open: self.menu.handle_keyboard_events(event)`
  - [ ] ✅ Confermare routing: `elif self.is_options_mode: self.gameplay_controller...`
  - [ ] ✅ Confermare routing: `else: self.gameplay_controller.handle_keyboard_events(event)`
- [ ] **✅ NESSUNA MODIFICA NECESSARIA** - Routing già implementato correttamente
- [ ] **Testare separazione contesti**:
  - [ ] Menu aperto: tasti 1-5 vanno a VirtualMenu.press_X() ✅
  - [ ] Gameplay: tasti 1-7 vanno a gameplay_controller (pile base) ✅
  - [ ] NO conflitti tra menu e gameplay ✅

#### Test Checklist Step 3.2
- [ ] T12: Routing menu → VirtualMenu funzionante
- [ ] T13: Routing gameplay → GameplayController funzionante
- [ ] T14: Nessun conflitto tra tasti menu e pile base

---

### Step 3.3: Testing Feature #2 Completo

#### Test Menu Principale
- [ ] **T2.1**: Avvio app → VirtualMenu mostra voci correttamente
- [ ] **T2.2**: Premere `1` → Apre game submenu (equivalente ENTER)
- [ ] **T2.3**: Premere ESC → Dialog conferma uscita (invariato)
- [ ] **T2.4**: Frecce UP/DOWN → Funzionano (no regressione)

#### Test Game Submenu
- [ ] **T2.5**: Menu principale → ENTER/1 → Apre submenu con 3 voci + welcome
- [ ] **T2.6**: Submenu aperto + `1` → Nuova partita
- [ ] **T2.7**: Submenu aperto + `2` → Opzioni
- [ ] **T2.8**: Submenu aperto + `3` → Dialog conferma ritorno menu principale
- [ ] **T2.9**: Submenu aperto + ESC → Dialog conferma ritorno (stesso comportamento)

#### Test Gestione Conflitti (Menu vs Gameplay)
- [ ] **T2.10**: Durante gameplay + `1` → Pila base 1 (NO menu action)
- [ ] **T2.11**: Durante gameplay + `2` → Pila base 2 (NO menu action)
- [ ] **T2.12**: Durante gameplay + `3` → Pila base 3 (NO menu action)
- [ ] **T2.13**: Durante gameplay + ESC → Dialog abbandono partita (test.py)

#### Test Edge Cases
- [ ] **T2.14**: Premere tasti 4-7 nei menu → Nessuna azione (solo 1-3 validi)
- [ ] **T2.15**: Aprire/chiudere submenu multiplo → Nessun bug stato
- [ ] **T2.16**: Dialog box attivo → Priorità corretta (solo dialog risponde)

---

## 🔗 FASE 4: Integration Testing

- [ ] **Test Scenario 1**: Double-tap pila → ESC dialog → Chiudi dialog → Double-tap ancora funziona
- [ ] **Test Scenario 2**: Menu shortcut `1` nuova partita → Double-tap funziona su nuova partita
- [ ] **Test Scenario 3**: Double-tap + selezione → ESC dialog → Selezione ancora attiva dopo chiusura
- [ ] **Test Regressione Generale**:
  - [ ] Tutti i comandi esistenti (frecce, HOME, END, TAB, etc.) funzionano
  - [ ] Shortcuts pile seme (SHIFT+1-4) funzionano
  - [ ] Shortcuts scarti/mazzo (SHIFT+S/M) funzionano
  - [ ] Comandi info (F, G, R, T, X, etc.) funzionano
  - [ ] Comandi opzioni (F1-F5, O, N) funzionano
- [ ] **Performance Check**: Nessun lag percepibile durante interazioni rapide
- [ ] **Accessibilità Check**: Tutti i messaggi vocali sono chiari e informativi

---

## 📚 FASE 5: Documentation & Release

### Aggiornamenti Documentazione

- [ ] **`README.md`** (se necessario):
  - [ ] Aggiungere nota double-tap nella sezione "NAVIGAZIONE"
  - [ ] Aggiungere nota menu shortcuts nella sezione "MENU"
  - [ ] Esempio: "Premi due volte 1-7 per selezione rapida carta"

- [ ] **`CHANGELOG.md`** - Aggiungere sezione v1.4.3:
  ```markdown
  ## [1.4.3] - 2026-02-10
  
  ### Added
  - Double-tap auto-selection: seconda pressione numero pila seleziona automaticamente ultima carta (pile base 1-7 e pile seme SHIFT+1-4)
  - Numeric menu shortcuts: scorciatoie 1-5 per navigazione rapida menu principale e game submenu (Clean Architecture)
  
  ### Changed
  - Hint migliorati per pile base/semi: "Premi ancora [numero] per selezionare"
  - VirtualMenu (Clean Arch) supporta shortcuts numerici diretti
  
  ### Fixed
  - Gestione routing eventi tra VirtualMenu e gameplay (context-aware, no conflitti tastiera)
  - Annullamento automatico selezione precedente durante double-tap su nuova pila
  ```

- [ ] **Help In-Game** - Verificare se applicabile a Clean Arch:
  - [ ] Controllare se gameplay_controller ha help command
  - [ ] Se presente, aggiungere note double-tap e menu shortcuts

### Git Operations

- [ ] **Commit Finale**:
  - [ ] Messaggio: `feat: Add double-tap auto-selection and numeric menu shortcuts (v1.4.3)`
  - [ ] Body: Link a `docs/IMPLEMENTATION_DOUBLE_TAP_AND_MENU_SHORTCUTS.md`

- [ ] **Merge** (se feature branch usato):
  - [ ] Review codice finale
  - [ ] Merge su `refactoring-engine` (o main)
  - [ ] Risolvere eventuali conflitti

- [ ] **Tag Release**:
  - [ ] Creare tag: `git tag -a v1.4.3 -m "Release 1.4.3: UX Improvements"`
  - [ ] Push tag: `git push origin v1.4.3`

---

## 📊 PROGRESS TRACKER

### Stato Generale
```
[####______] 45% - Documentazione corretta
```

### Breakdown per Fase
| Fase | Status | Completamento | Note |
|------|--------|---------------|------|
| **1. Setup** | 🟢 IN PROGRESS | 75% (3/4) | Path corretti ✅ |
| **2. Double-Tap** | ⚪ TODO | 0% (0/30) | Path src/ corretti ✅ |
| **3. Menu Shortcuts** | ⚪ TODO | 0% (28) | Path src/ corretti ✅ |
| **4. Integration** | ⚪ TODO | 0% (12) | - |
| **5. Docs & Release** | ⚪ TODO | 0% (10) | - |

**Totale Task**: 84  
**Completati**: 3  
**Rimanenti**: 81

---

## 🐛 ISSUES TRACKER

### Blockers
_Nessuno al momento_

### Known Issues
_Nessuno al momento_

### Questions/Clarifications Needed
_Nessuno al momento_

---

## 📝 NOTES

### Session Log

**2026-02-10 10:47**
- ✅ Creato file documentazione completa `docs/IMPLEMENTATION_DOUBLE_TAP_AND_MENU_SHORTCUTS.md`
- ✅ Aggiornato `TODO.md` con checklist dettagliata
- 🔄 Prossimo step: Review piano e inizio implementazione Feature #1

**2026-02-10 11:40**
- ⚠️ **CORREZIONE CRITICA**: Identificato conflitto architetturale
- ✅ Aggiornata documentazione completa con path corretti (src/ Clean Arch)
- ✅ Aggiornato TODO.md con path corretti FASE 3
- 📝 Note: FASE 2 già corretta, solo FASE 3 aveva path sbagliati (scr/ legacy)
- 🔄 Prossimo step: Commentare PR Copilot e riavviare implementazione con path corretti

---

**Per iniziare l'implementazione**, procedere con:
```bash
# 1. Aprire file CursorManager (FASE 2)
code src/domain/services/cursor_manager.py

# 2. Aprire file VirtualMenu (FASE 3) - PATH CORRETTO!
code src/infrastructure/ui/menu.py

# 3. Seguire Step 2.1 e 3.1 in questo TODO
# 4. Checkare le box man mano che si completa
```

---

**Fine TODO**  
Ultimo aggiornamento: 10 Febbraio 2026 - 11:40 CET (v2 - Path corretti Clean Architecture)
