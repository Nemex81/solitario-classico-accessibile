# ✅ FIX CHECKLIST v1.4.1 - Progress Tracking

**Branch**: `refactoring-engine`  
**Target**: Feature Parity 100% con versione legacy  
**Data Inizio**: 8 Febbraio 2026

---

## 📊 STATO GENERALE

- [ ] **FIX #1**: Menu Secondario (Commit #15)
- [ ] **FIX #2**: Finestra Opzioni Virtuali (Commit #15)
- [ ] **FIX #3**: Feedback Vocali Dettagliati (Commit #16)
- [ ] **Testing**: Validazione completa v1.4.1
- [ ] **Release**: CHANGELOG + Tag v1.4.1

---

## 🎯 FIX #1: MENU SECONDARIO

### Analisi & Design
- [ ] Revisione comportamento legacy (`scr/game_play.py`)
- [ ] Design struttura sottomenu
- [ ] Definizione callback handlers

### Implementazione `VirtualMenu`
**File**: `src/infrastructure/ui/menu.py`

- [ ] Aggiungere attributo `parent_menu: Optional[VirtualMenu]`
- [ ] Aggiungere attributo `_is_submenu: bool`
- [ ] Implementare metodo `open_submenu(submenu: VirtualMenu)`
- [ ] Implementare metodo `close_submenu() -> None`
- [ ] Gestire ESC per chiudere sottomenu
- [ ] Annunciare apertura sottomenu con TTS
- [ ] Testing navigazione gerarchica

### Implementazione Entry Point
**File**: `test.py`

- [ ] Creare `self.game_submenu` con 3 voci
  - [ ] "Nuova partita"
  - [ ] "Opzioni"
  - [ ] "Chiudi"
- [ ] Modificare `handle_menu_selection()` per aprire sottomenu
- [ ] Implementare `handle_game_submenu_selection()`
  - [ ] Item 0: avvia partita
  - [ ] Item 1: apri opzioni
  - [ ] Item 2: chiudi sottomenu
- [ ] Collegare sottomenu al menu principale (parent)
- [ ] Testing flusso completo menu → sottomenu → partita

---

## 🎯 FIX #2: FINESTRA OPZIONI VIRTUALI

### Analisi & Design
- [ ] Revisione comportamento legacy (`scr/game_engine.py` linee 345-366)
- [ ] Mappatura comandi F1-F5 + CTRL+F3
- [ ] Design validazioni per partita in corso

### Implementazione `GameEngine`
**File**: `src/application/game_engine.py`

- [ ] Aggiungere attributo `_options_open: bool = False`
- [ ] Implementare `open_options() -> str`
  - [ ] Validazione: blocca se partita in corso
  - [ ] Imposta flag `_options_open = True`
  - [ ] Ritorna messaggio vocale
- [ ] Implementare `close_options() -> str`
  - [ ] Imposta flag `_options_open = False`
  - [ ] Ritorna messaggio vocale
- [ ] Implementare `is_options_open() -> bool`
- [ ] Testing apertura/chiusura opzioni

### Implementazione `GameSettings`
**File**: `src/application/game_settings.py`

- [ ] Aggiornare `change_deck_type()` con validazione
  - [ ] Return: `Tuple[bool, str]` (success, message)
  - [ ] Validazione: blocca se `is_game_running`
- [ ] Aggiornare `cycle_difficulty()` con validazione
- [ ] Aggiornare `increment_timer()` con validazione
- [ ] Aggiornare `decrement_timer()` con validazione
- [ ] Aggiornare `toggle_shuffle_mode()` con validazione
- [ ] Implementare `disable_timer()` con validazione
- [ ] Testing tutte le modifiche settings

### Implementazione `GamePlayController`
**File**: `src/application/gameplay_controller.py`

- [ ] Aggiungere sezione gestione modalità opzioni in `handle_keyboard_events()`
- [ ] Handler tasto **O**: toggle opzioni
- [ ] Handler tasto **F1**: cambia mazzo (solo se opzioni aperte)
  - [ ] Vocalizza risultato
- [ ] Handler tasto **F2**: cambia difficoltà (solo se opzioni aperte)
  - [ ] Vocalizza risultato
- [ ] Handler tasto **F3**: decrementa timer (solo se opzioni aperte)
  - [ ] Vocalizza risultato
- [ ] Handler tasto **F4**: incrementa timer (solo se opzioni aperte)
  - [ ] Vocalizza risultato
- [ ] Handler tasto **F5**: toggle shuffle mode (solo se opzioni aperte)
  - [ ] Vocalizza risultato
- [ ] Handler combo **CTRL+F3**: disabilita timer (solo se opzioni aperte)
  - [ ] Vocalizza risultato
- [ ] Handler tasto **ESC**: chiudi opzioni (se aperte)
- [ ] Testing completo tutti i comandi opzioni

### Testing Opzioni
- [ ] Apertura opzioni da menu (prima di partita)
- [ ] Apertura opzioni durante partita (deve bloccare)
- [ ] Modifica mazzo (F1) e verifica annuncio
- [ ] Modifica difficoltà (F2) e verifica ciclo 1→2→3→1
- [ ] Modifica timer (F3/F4) e verifica limiti (5-60 min)
- [ ] Toggle shuffle mode (F5) e verifica annuncio
- [ ] Disabilita timer (CTRL+F3) e verifica annuncio
- [ ] Chiusura opzioni (O/ESC) e verifica annuncio

---

## 🎯 FIX #3: FEEDBACK VOCALI DETTAGLIATI

### Analisi & Design
- [ ] Revisione feedback legacy per pesca (`scr/game_engine.py` linee 758-803)
- [ ] Revisione feedback legacy per mosse (`scr/game_engine.py` linee 526-556)
- [ ] Identificazione parametri necessari per formatter

### 3.1 Pesca Carte
**File**: `src/presentation/game_formatter.py`

- [ ] Implementare `format_drawn_cards(cards: List[Card]) -> str`
  - [ ] Gestione lista vuota
  - [ ] Formato: "Hai pescato: <carta1>, <carta2>, <carta3>."
  - [ ] Uso di `card.get_display_name()` per nomi corretti
- [ ] Testing con diverse combinazioni (1 carta, 3 carte, liste vuote)

### 3.2 Report Mosse
**File**: `src/presentation/game_formatter.py`

- [ ] Implementare `format_move_report()` con parametri:
  - [ ] `moved_cards: List[Card]`
  - [ ] `origin_pile: Pile`
  - [ ] `dest_pile: Pile`
  - [ ] `card_under: Optional[Card] = None`
  - [ ] `revealed_card: Optional[Card] = None`
- [ ] Formato carte spostate:
  - [ ] Se >2 carte: mostra prima + conteggio
  - [ ] Se ≤2 carte: mostra tutte
- [ ] Annuncio origine: "Da: <nome_pila>"
- [ ] Annuncio destinazione: "A: <nome_pila>"
- [ ] Annuncio carta sotto (se non Re): "Sopra alla carta: <nome>"
- [ ] Annuncio carta scoperta: "Hai scoperto: <nome> in: <nome_pila>"
- [ ] Testing con diverse combinazioni mosse

### 3.3 Rimescolamenti
**File**: `src/presentation/game_formatter.py`

- [ ] Implementare `format_reshuffle_message()` con parametri:
  - [ ] `shuffle_mode: str` ("shuffle" o "reverse")
  - [ ] `auto_drawn_cards: Optional[List[Card]] = None`
- [ ] Annuncio modalità:
  - [ ] "shuffle": "Rimescolo gli scarti in modo casuale..."
  - [ ] "reverse": "Rimescolo gli scarti..."
- [ ] Annuncio auto-pesca (se presente):
  - [ ] "Pescata automatica: " + `format_drawn_cards()`
- [ ] Gestione mazzo vuoto post-rimescolamento
- [ ] Testing con entrambe le modalità

### Integrazione Formatter
**File**: `src/application/gameplay_controller.py`

- [ ] Identificare chiamate a `engine.draw_cards()`
- [ ] Sostituire output generico con `GameFormatter.format_drawn_cards()`
- [ ] Identificare chiamate a `engine.move_cards()`
- [ ] Sostituire output generico con `GameFormatter.format_move_report()`
- [ ] Identificare chiamate a `engine.reshuffle()`
- [ ] Sostituire output generico con `GameFormatter.format_reshuffle_message()`
- [ ] Testing integrazione completa

### Estensione Model `Card`
**File**: `src/domain/models/card.py`

- [ ] Verificare esistenza metodo `get_display_name() -> str`
- [ ] Se mancante, implementare con formato: "<valore> di <seme>"
  - [ ] Es: "7 di Cuori", "Regina di Quadri", "Asso di Fiori"
- [ ] Testing con entrambi i mazzi (francese/napoletano)

---

## 🧪 TESTING COMPLETO v1.4.1

### Test Menu & Navigazione
- [ ] Avvio applicazione → menu principale annunciato
- [ ] Navigazione menu principale (UP/DOWN)
- [ ] ENTER su "Gioca al solitario" → sottomenu aperto
- [ ] Navigazione sottomenu (UP/DOWN)
- [ ] Voce "Nuova partita" annunciata correttamente
- [ ] Voce "Opzioni" annunciata correttamente
- [ ] Voce "Chiudi" annunciata correttamente
- [ ] Tasto rapido **N** avvia partita da sottomenu
- [ ] Tasto rapido **O** apre opzioni da sottomenu
- [ ] ESC chiude sottomenu e torna al principale

### Test Finestra Opzioni
- [ ] Apertura opzioni dal sottomenu → annuncio corretto
- [ ] F1: cambio mazzo (francesi ↔ napoletane) + annuncio
- [ ] F2: ciclo difficoltà (1→2→3→1) + annuncio
- [ ] F3: decremento timer (20→15→10→5→disabilita) + annuncio
- [ ] F4: incremento timer (20→25→...→60→disabilita) + annuncio
- [ ] F5: toggle shuffle mode (inversione ↔ mescolata) + annuncio
- [ ] CTRL+F3: disabilita timer + annuncio
- [ ] O/ESC: chiusura opzioni + annuncio
- [ ] Tentativo apertura opzioni durante partita → blocco + annuncio errore

### Test Feedback Vocali Durante Partita
- [ ] Pesca 1 carta → annuncio nome completo
- [ ] Pesca 3 carte (difficoltà 3) → annuncio tutte le carte
- [ ] Spostamento 1 carta → report completo (origine/destinazione/carta sotto)
- [ ] Spostamento multiple carte → report con conteggio
- [ ] Carta scoperta dopo spostamento → annuncio "Hai scoperto..."
- [ ] Mazzo vuoto → rimescolamento + annuncio modalità
- [ ] Rimescolamento con auto-pesca → annuncio carte pescate
- [ ] Mazzo vuoto post-rimescolamento → annuncio errore

### Test Feature Parity con Legacy
- [ ] Confronto feedback pesca (Clean vs Legacy)
- [ ] Confronto feedback mosse (Clean vs Legacy)
- [ ] Confronto feedback rimescolamenti (Clean vs Legacy)
- [ ] Confronto gestione opzioni (Clean vs Legacy)
- [ ] Confronto navigazione menu (Clean vs Legacy)
- [ ] Nessuna regressione funzionale

---

## 📝 COMMIT TRACKING

### Commit #15: Menu Secondario + Finestra Opzioni
**Titolo**: `feat: Add game submenu and virtual options window`

**Descrizione**:
```
Implement complete menu hierarchy and interactive settings management:

- Add submenu support to VirtualMenu (parent/child navigation)
- Create "Play Solitaire" submenu with 3 items:
  * New Game (N)
  * Options (O) → Virtual options window
  * Close (ESC)
- Implement virtual options window in GameEngine:
  * F1: Change deck type (French/Neapolitan)
  * F2: Cycle difficulty (1→2→3→1)
  * F3/F4: Adjust timer (±5 min, 5-60 range)
  * F5: Toggle shuffle mode (reverse/random)
  * CTRL+F3: Disable timer
  * O/ESC: Close options
- Add validation: block options during active game
- Full TTS announcements for all setting changes

Files modified:
- src/infrastructure/ui/menu.py
- src/application/game_engine.py
- src/application/game_settings.py
- src/application/gameplay_controller.py
- test.py

BREAKING CHANGES: None (fully backward compatible)
```

**Status**:
- [ ] Codice implementato
- [ ] Testing locale completato
- [ ] Commit creato
- [ ] Push a remoto

---

### Commit #16: Feedback Vocali Dettagliati
**Titolo**: `feat: Add detailed voice feedback for gameplay actions`

**Descrizione**:
```
Enhance GameFormatter with legacy-style detailed announcements:

- format_drawn_cards(): Announce all drawn cards by name
  * Example: "Hai pescato: 7 di Cuori, Regina di Quadri, 3 di Fiori."
  
- format_move_report(): Complete move narration
  * Cards moved (with count if >2)
  * Origin pile
  * Destination pile
  * Card underneath (if not King)
  * Revealed card after move
  * Example: "Sposti: Asso di Cuori. Da: Pila base 1. A: Pila semi Cuori. 
              Sopra alla carta: Re di Cuori. Hai scoperto: 5 di Picche."
  
- format_reshuffle_message(): Reshuffle + auto-draw announcement
  * Shuffle mode (random/reverse)
  * Automatic draw after reshuffle
  * Example: "Rimescolo gli scarti in modo casuale nel mazzo riserve!
              Pescata automatica: Hai pescato: 9 di Quadri, Asso di Fiori."

- Add Card.get_display_name() for proper card naming
- Integrate all formatters into GamePlayController

Files modified:
- src/presentation/game_formatter.py
- src/domain/models/card.py
- src/application/gameplay_controller.py

Achieves 100% feature parity with legacy version feedback.
```

**Status**:
- [ ] Codice implementato
- [ ] Testing locale completato
- [ ] Commit creato
- [ ] Push a remoto

---

## 🚀 RELEASE v1.4.1

### Pre-Release
- [ ] Tutti i fix implementati e testati
- [ ] Feature parity 100% verificata
- [ ] Nessuna regressione rilevata
- [ ] Testing utente preliminare completato

### CHANGELOG Update
**File**: `CHANGELOG.md`

- [ ] Creare sezione `## [1.4.1] - 2026-02-08`
- [ ] Sezione **Added**:
  - [ ] Menu secondario "Gioca al solitario"
  - [ ] Finestra opzioni virtuali interattiva
  - [ ] Feedback vocali dettagliati per pesca carte
  - [ ] Feedback vocali dettagliati per spostamenti
  - [ ] Feedback vocali dettagliati per rimescolamenti
- [ ] Sezione **Fixed**:
  - [ ] Menu principale ora apre sottomenu (non partita diretta)
  - [ ] Gestione completa modifiche settings (F1-F5)
  - [ ] Output vocali generici sostituiti con descrizioni dettagliate
- [ ] Sezione **Technical**:
  - [ ] 2 commits (menu+opzioni, feedback vocali)
  - [ ] 5 file modificati
  - [ ] 100% feature parity con legacy raggiunta

### Git Tagging
- [ ] Commit finale su `refactoring-engine`
- [ ] Create tag: `git tag -a v1.4.1 -m "Release v1.4.1: Complete game logic"`
- [ ] Push tag: `git push origin v1.4.1`

### Documentation
- [ ] Aggiornare README.md con versione v1.4.1
- [ ] Archiviare FIX_ROADMAP_V1.4.1.md
- [ ] Archiviare FIX_CHECKLIST_V1.4.1.md
- [ ] Creare release notes su GitHub

---

## ✅ CRITERI DI SUCCESSO FINALE

### Funzionalità
- [ ] Menu principale → sottomenu → opzioni → partita (flusso completo)
- [ ] Tutte le opzioni modificabili (F1-F5 + CTRL+F3)
- [ ] Feedback vocali identici alla versione legacy
- [ ] Nessun crash o errore durante testing

### Qualità
- [ ] Codice pulito e documentato
- [ ] Test manuali completati al 100%
- [ ] Nessuna regressione rispetto a v1.4.0
- [ ] Feature parity 100% con `scr/` legacy

### Documentazione
- [ ] CHANGELOG aggiornato
- [ ] Commit messages descrittivi
- [ ] Roadmap e checklist completate
- [ ] README aggiornato

---

## 📊 PROGRESS SUMMARY

**Total Tasks**: 0/150+ completate  
**Commits**: 0/2 pronti  
**Testing**: 0% completato  
**Release**: Not ready

**Next Action**: 🚀 Iniziare implementazione Commit #15 (Menu + Opzioni)

---

**Fine Checklist v1.4.1**  
*Aggiornare i checkbox man mano che le task vengono completate*
