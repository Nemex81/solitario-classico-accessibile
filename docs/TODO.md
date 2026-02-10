# 📋 TODO - Solitario Accessibile v1.4.3
**Piano di Implementazione**: UX Improvements (Double-Tap Selection + Menu Shortcuts)  
**Data Inizio**: 10 Febbraio 2026  
**Documentazione Completa**: `docs/IMPLEMENTATION_DOUBLE_TAP_AND_MENU_SHORTCUTS.md`

---

## 🎯 OVERVIEW

**Obiettivo**: Implementare due miglioramenti UX per accessibilità:
1. **Double-Tap Auto-Selection**: Selezione automatica carta con doppia pressione numero pila
2. **Numeric Menu Shortcuts**: Scorciatoie numeriche per navigazione rapida menu

**Impatto**: 4 file, ~150 righe di codice  
**Stima Tempo**: 2.5-3.5 ore  
**Target Release**: v1.4.3

---

## ✅ FASE 1: Setup & Preparation

- [x] Creazione file `docs/IMPLEMENTATION_DOUBLE_TAP_AND_MENU_SHORTCUTS.md`
- [x] Creazione/aggiornamento `TODO.md` con checklist
- [ ] Review piano con stakeholder (se necessario)
- [ ] Setup branch di sviluppo (opzionale)

---

## 🔥 FASE 2: Feature #1 - Double-Tap Auto-Selection

### Step 2.1: Modifica CursorManager (`src/domain/services/cursor_manager.py`)

- [x] **Aprire file**: `src/domain/services/cursor_manager.py`
- [x] **Import**: Aggiornare `from typing import Tuple, Optional, Dict, Any` (già presente)
- [x] **Metodo `jump_to_pile()`** (riga ~315):
  - [x] Cambiare signature: `def jump_to_pile(...) -> Tuple[str, bool]`
  - [x] Implementare double-tap detection: `if pile_idx == last_quick_pile`
  - [x] Gestire pile stock/waste: ritorno `("Cursore già sulla pila.", False)`
  - [x] Gestire pile tableau/foundation vuote: ritorno `("Pila vuota...", False)`
  - [x] Gestire pile tableau/foundation con carte:
    - [x] Chiamare `move_to_top_card()`
    - [x] Ritornare `("", True)` per triggare auto-selection
  - [x] Aggiornare hint primo tap: "Premi ancora [numero] per selezionare"
  - [x] Reset `last_quick_pile = None` dopo secondo tap
- [x] **Test isolato**: Verificare ritorno Tuple corretto in vari scenari

#### Test Checklist Step 2.1
- [ ] T1: Primo tap → ritorna `(messaggio, False)`
- [ ] T2: Secondo tap pile base → ritorna `("", True)`
- [ ] T3: Secondo tap pile vuota → ritorna `(errore, False)`
- [ ] T4: Secondo tap scarti/mazzo → ritorna `(hint, False)`

---

### Step 2.2: Modifica GameEngine (`src/application/game_engine.py`)

- [x] **Aprire file**: `src/application/game_engine.py`
- [x] **Metodo `jump_to_pile()`** (riga ~376):
  - [x] Gestire ritorno Tuple: `msg, should_auto_select = self.cursor.jump_to_pile(...)`
  - [x] Implementare blocco `if should_auto_select:`
    - [x] Verificare selezione precedente: `if self.selection.has_selection()`
    - [x] Annullare selezione: `self.selection.clear_selection()`
    - [x] Creare messaggio: `msg_deselect = "Selezione precedente annullata. "`
    - [x] Eseguire auto-selection: `success, msg_select = self.select_card_at_cursor()`
    - [x] Combinare messaggi: `msg = msg_deselect + msg_select`
  - [x] Mantenere vocal feedback: `self.screen_reader.tts.speak(msg, interrupt=True)`
- [x] **Test integrazione**: CursorManager + GameEngine

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

## 🎨 FASE 3: Feature #2 - Numeric Menu Shortcuts

### Step 3.1: Modifica PyMenu (`scr/pygame_menu.py`)

- [ ] **Aprire file**: `scr/pygame_menu.py`
- [ ] **Metodo `build_commands_list()`** (riga ~35):
  - [ ] Aggiungere mappatura: `pygame.K_1: self.press_1`
  - [ ] Aggiungere mappatura: `pygame.K_2: self.press_2`
  - [ ] Aggiungere mappatura: `pygame.K_3: self.press_3`
  - [ ] Aggiungere mappatura: `pygame.K_4: self.press_4`
  - [ ] Aggiungere mappatura: `pygame.K_5: self.press_5`
- [ ] **Nuovi metodi** (dopo `execute()`, riga ~70):
  - [ ] Implementare `press_1()`: if len >= 1, selected_item = 0, execute()
  - [ ] Implementare `press_2()`: if len >= 2, selected_item = 1, execute()
  - [ ] Implementare `press_3()`: if len >= 3, selected_item = 2, execute()
  - [ ] Implementare `press_4()`: if len >= 4, selected_item = 3, execute()
  - [ ] Implementare `press_5()`: if len >= 5, selected_item = 4, execute()
- [ ] **[OPZIONALE] Metodo `draw_menu()`** (riga ~80):
  - [ ] Aggiungere prefisso numerico: `f"{i + 1}. {item}"` (escluso ultimo)
  - [ ] Testare visualizzazione prefissi

#### Test Checklist Step 3.1
- [ ] T8: Menu mostra "1. Gioca al solitario classico"
- [ ] T9: Premere `1` → Esegue prima voce menu
- [ ] T10: Frecce UP/DOWN ancora funzionanti

---

### Step 3.2: Modifica GamePlay (`scr/game_play.py`)

- [ ] **Aprire file**: `scr/game_play.py`
- [ ] **Metodo `__init__()`** (riga ~35):
  - [ ] Aggiungere flag: `self.is_solitaire_menu_open = False`
- [ ] **Nuovi metodi** (dopo `vocalizza()`, riga ~50):
  - [ ] Implementare `open_solitaire_menu()`:
    - [ ] Set flag: `self.is_solitaire_menu_open = True`
    - [ ] Vocalizzare: "MENU SOLITARIO: 1. Nuova partita, 2. Opzioni, 3. Chiudi partita"
  - [ ] Implementare `close_solitaire_menu()`:
    - [ ] Set flag: `self.is_solitaire_menu_open = False`
    - [ ] Vocalizzare: "Menu chiuso, torno al gioco."
- [ ] **Modifica `esc_press()`** (riga ~340):
  - [ ] If `is_game_running` AND NOT `is_solitaire_menu_open`: chiama `open_solitaire_menu()`
  - [ ] If `is_game_running` AND `is_solitaire_menu_open`: chiama `close_solitaire_menu()`
  - [ ] Else (no game): chiama `quit_app()` (invariato)
- [ ] **Modifica `press_1()`** (riga ~150):
  - [ ] If `is_solitaire_menu_open`: chiama `n_press()` + `close_solitaire_menu()`
  - [ ] Else: esegue `move_cursor_to_pile_with_select(0)` (invariato)
- [ ] **Modifica `press_2()`** (riga ~155):
  - [ ] If `is_solitaire_menu_open`: chiama `o_press()` + `close_solitaire_menu()`
  - [ ] Else: esegue `move_cursor_to_pile_with_select(1)` (invariato)
- [ ] **Modifica `press_3()`** (riga ~160):
  - [ ] If `is_solitaire_menu_open`: conferma + `chiudi_partita()` + `close_solitaire_menu()`
  - [ ] Else: esegue `move_cursor_to_pile_with_select(2)` (invariato)

#### Test Checklist Step 3.2
- [ ] T11: ESC durante partita → Apre menu solitario
- [ ] T12: Menu aperto, premere `1` → Nuova partita + chiude menu
- [ ] T13: Menu aperto, premere `2` → Opzioni + chiude menu
- [ ] T14: Menu aperto, premere `3` → Conferma chiusura + chiude menu
- [ ] T15: Menu aperto, premere ESC → Chiude menu (torna al gioco)

---

### Step 3.3: Testing Feature #2 Completo

#### Test Menu Principale
- [ ] **T2.1**: Avvio app → Menu mostra prefisso "1." su prima voce
- [ ] **T2.2**: Premere `1` → Avvia gameplay (equivalente ENTER)
- [ ] **T2.3**: Premere ESC → Conferma uscita (invariato)
- [ ] **T2.4**: Frecce UP/DOWN → Funzionano (no regressione)

#### Test Menu Solitario In-Game
- [ ] **T2.5**: ESC durante partita → Menu con voci "1. Nuova partita, 2. Opzioni, 3. Chiudi"
- [ ] **T2.6**: Menu aperto + `1` → Nuova partita + menu chiuso
- [ ] **T2.7**: Menu aperto + `2` → Opzioni + menu chiuso
- [ ] **T2.8**: Menu aperto + `3` → Conferma chiusura + menu chiuso
- [ ] **T2.9**: Menu aperto + ESC → Chiude menu (NO quit)

#### Test Gestione Conflitti
- [ ] **T2.10**: Menu chiuso + `1` → Pila base 1 (NO menu)
- [ ] **T2.11**: Menu chiuso + `2` → Pila base 2 (NO menu)
- [ ] **T2.12**: Menu chiuso + `3` → Pila base 3 (NO menu)
- [ ] **T2.13**: Menu aperto + `4-7` → Nessuna azione (solo 1-3 validi)

#### Test Edge Cases
- [ ] **T2.14**: Aprire/chiudere menu multiplo → Nessun bug stato
- [ ] **T2.15**: Annullare dialog conferma → Menu rimane aperto
- [ ] **T2.16**: Dialog box attivo → Tastiera menu disabilitata

---

## 🔗 FASE 4: Integration Testing

- [ ] **Test Scenario 1**: Double-tap pila → ESC menu → Chiudi menu → Double-tap ancora funziona
- [ ] **Test Scenario 2**: Menu aperto → Shortcut `1` nuova partita → Double-tap funziona su nuova partita
- [ ] **Test Scenario 3**: Double-tap + selezione → ESC menu → Selezione ancora attiva dopo chiusura menu
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
  - Numeric menu shortcuts: scorciatoie 1-5 per navigazione rapida menu principale e menu solitario in-game
  - Menu solitario in-game: apri/chiudi con ESC (toggle) invece di conferma immediata
  
  ### Changed
  - Hint migliorati per pile base/semi: "Premi ancora [numero] per selezionare"
  - Gestione ESC durante partita: apre menu pausa invece di dialog conferma diretto
  
  ### Fixed
  - Gestione conflitti tastiera tra menu shortcuts e pile base (context-aware handlers)
  - Annullamento automatico selezione precedente durante double-tap su nuova pila
  ```

- [ ] **Help In-Game** - Aggiornare `h_press()` in `game_play.py`:
  - [ ] Aggiungere riga: "- Numeri 1-7: vai alla pila base + **doppio tocco seleziona**"
  - [ ] Aggiungere riga: "- SHIFT+1-4: vai alla pila semi + **doppio tocco seleziona**"
  - [ ] Aggiungere sezione: "MENU: Premi ESC per aprire menu in-game (1=Nuova, 2=Opzioni, 3=Chiudi)"

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
[####______] 40% - In sviluppo
```

### Breakdown per Fase
| Fase | Status | Completamento | Note |
|------|--------|---------------|------|
| **1. Setup** | 🟢 IN PROGRESS | 66% (2/3) | Docs creati |
| **2. Double-Tap** | ⚪ TODO | 0% (0/30) | - |
| **3. Menu Shortcuts** | ⚪ TODO | 0% (28) | - |
| **4. Integration** | ⚪ TODO | 0% (12) | - |
| **5. Docs & Release** | ⚪ TODO | 0% (10) | - |

**Totale Task**: 83  
**Completati**: 2  
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

---

**Per iniziare l'implementazione**, procedere con:
```bash
# 1. Aprire file CursorManager
code src/domain/services/cursor_manager.py

# 2. Seguire Step 2.1 in questo TODO
# 3. Checkare le box man mano che si completa
```

---

**Fine TODO**  
Ultimo aggiornamento: 10 Febbraio 2026 - 10:47 CET
