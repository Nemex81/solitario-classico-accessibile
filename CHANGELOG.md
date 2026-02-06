# Changelog

Tutte le modifiche rilevanti a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/lang/it/).

## [1.3.2] - 2026-02-06

### ✨ Nuove Funzionalità

**Supporto Autentico Mazzo Napoletano (40 carte)**
- Implementato mazzo napoletano autentico da 40 carte (4 semi × 10 valori)
- Valori corretti: Asso, 2-7, Regina, Cavallo, Re (eliminati 8, 9, 10)
- Figure napoletane con valori autentici: Regina=8, Cavallo=9, Re=10
- Compatibilità: entrambi i mazzi (francese 52, napoletano 40) coesistono

### 🐛 Bug Fix Critici

**Fix Verifica Vittoria**
- Risolto bug critico: il controllo vittoria ora verifica TUTTE e 4 le pile semi
- Prima: `range(7, 10)` controllava solo 3 pile, ignorando la pila 10
- Dopo: `range(7, 11)` controlla correttamente tutte le pile (7, 8, 9, 10)
- Vittoria ora dinamica: 13 carte/seme (francese) o 10 carte/seme (napoletano)

### 🎨 Miglioramenti

**Statistiche Dinamiche**
- Le statistiche si adattano automaticamente al tipo di mazzo in uso
- Nomi semi dinamici: Cuori/Quadri/Fiori/Picche o Bastoni/Coppe/Denari/Spade
- Conteggi corretti: "X su 10 carte" (napoletano) o "X su 13 carte" (francese)
- Percentuali di completamento accurate: base 40 o 52 carte

### 🔧 Modifiche Tecniche

**File: `scr/decks.py`**
- `NeapolitanDeck.VALUES`: rimossi 8, 9, 10 → array da 10 elementi
- `NeapolitanDeck.FIGURE_VALUES`: Regina=8, Cavallo=9, Re=10 (era 11, 12, 13)
- Aggiunto `get_total_cards()` a entrambe le classi (40 per napoletano, 52 per francese)

**File: `scr/game_table.py`**
- `verifica_vittoria()`: fix range + controllo dinamico `len(self.mazzo.VALUES)`
- Documentazione inline dettagliata

**File: `scr/game_engine.py`**
- `aggiorna_statistiche_semi()`: logica dinamica per entrambi i mazzi
- `get_statistiche_semi()`: nomi e conteggi dinamici
- `get_report_game()`: percentuali calcolate su base corretta (40 o 52)

### 📊 Impatto

**Mazzo Napoletano:**
- Totale carte: 52 → 40
- Carte nelle pile base: 28 (invariato)
- Carte nel mazzo riserve: 24 → 12
- Vittoria richiede: 40 carte nelle pile semi (10 per seme)

**Mazzo Francese:**
- Nessuna modifica (52 carte, 13 per seme)
- Comportamento invariato

### ✅ Backward Compatibility

- Zero breaking changes
- Entrambi i mazzi funzionano correttamente
- Tutte le funzionalità esistenti preservate

## [1.3.1] - 2026-02-06

### 🐛 Bug Fix

**Navigazione Frecce su Pila Scarti**
- Risolto: Frecce SU/GIÙ ora funzionano correttamente sulla pila scarti
- Prima: Messaggio "non sei su una pila base" bloccava navigazione
- Dopo: Tutte le carte scoperte negli scarti sono consultabili
- Feedback vocale: "N di M: [Nome carta]" con posizione chiara
- Hint "Premi CTRL+INVIO per selezionare" solo su ultima carta

### ✨ Nuove Funzionalità

**Comandi HOME e END per Navigazione Rapida**
- **HOME**: Salta alla prima carta della pila corrente
- **END**: Salta all'ultima carta della pila corrente
- Supporto per pile base (0-6) e pila scarti (11)
- Messaggi informativi per pile non consultabili (semi, mazzo)
- Utile per pile con molte carte (navigazione veloce)

### 🎨 Miglioramenti UX

**Feedback Vocale Posizionale**
- Navigazione scarti mostra posizione "N di M"
- Esempio: "5 di 12: Fante di Cuori"
- HOME/END confermano con "Prima carta" / "Ultima carta"
- Messaggi chiari e concisi per screen reader

**Gestione Edge Cases**
- Scarti vuoti: messaggio chiaro "Scarti vuoti, nessuna carta da consultare"
- Pile semi/mazzo: suggerimenti alternativi (SHIFT+1-4, SHIFT+M)
- Validazione automatica bounds cursor_pos[0]

### 🔧 Modifiche Tecniche

**File: `scr/game_engine.py`**
- Refactoring `move_cursor_up()`: supporto pila scarti (col == 11)
- Refactoring `move_cursor_down()`: supporto pila scarti
- Nuovo metodo `move_cursor_to_first()`: implementa comando HOME
- Nuovo metodo `move_cursor_to_last()`: implementa comando END
- Logica unificata con feedback posizionale per scarti

**File: `scr/game_play.py`**
- Nuovi handler: `home_press()`, `end_press()`
- Integrazione in `handle_keyboard_EVENTS()`: K_HOME, K_END
- Aggiornato `h_press()` con documentazione nuovi comandi

### ✅ Backward Compatibility

**Zero breaking changes:**
- ✅ Comportamento pile base invariato (solo refactoring interno)
- ✅ Tutti i comandi esistenti funzionano come prima
- ✅ Logica double-tap (v1.3.0) intatta
- ✅ SHIFT shortcuts (v1.3.0) intatti

### 📊 Test Coverage

**Casi testati manualmente:**
- ✅ Frecce SU/GIÙ su pile base (comportamento invariato)
- ✅ Frecce SU/GIÙ su pila scarti con 10+ carte
- ✅ HOME/END su pile base
- ✅ HOME/END su pila scarti
- ✅ Messaggi blocco per pile semi/mazzo
- ✅ Edge cases: scarti vuoti, limiti navigazione
- ✅ Feedback vocale posizionale chiaro

## [1.3.0] - 2026-02-06

### ✨ Nuove Funzionalità

#### 🎯 Double-Tap Navigation & Quick Selection System

**Navigazione Rapida con Pattern Double-Tap**
- Primo tap: sposta cursore sulla pila + fornisce hint vocale
- Secondo tap consecutivo: seleziona automaticamente l'ultima carta sulla pila
- Sistema di tracking intelligente che si resetta con movimenti manuali (frecce, TAB)

**Nuovi Comandi Pile Base (1-7)**
- Tasti 1-7 ora supportano double-tap per selezione rapida
- Feedback vocale: "Pila [N]. [Nome carta]. Premi ancora [N] per selezionare."
- Auto-deseleziona selezione precedente quando si seleziona una nuova carta
- Gestione edge cases: pile vuote, carte coperte

**Quick Access Pile Semi (SHIFT+1-4)**
- SHIFT+1: Vai a pila Cuori (pile 7) + double-tap seleziona
- SHIFT+2: Vai a pila Quadri (pile 8) + double-tap seleziona
- SHIFT+3: Vai a pila Fiori (pile 9) + double-tap seleziona
- SHIFT+4: Vai a pila Picche (pile 10) + double-tap seleziona
- Feedback vocale: "Pila [Seme]. [Nome carta]. Premi ancora SHIFT+[N] per selezionare."

**Navigazione Rapida Scarti e Mazzo**
- SHIFT+S: Sposta cursore su pila scarti
  - Feedback: "Pila scarti. Carta in cima: [nome]. Usa frecce per navigare. CTRL+INVIO per selezionare ultima carta."
  - Mantiene separazione tra comando info `S` (read-only) e navigazione `SHIFT+S`
- SHIFT+M: Sposta cursore su pila mazzo
  - Feedback: "Pila riserve. Carte nel mazzo: [N]. Premi INVIO per pescare."
  - Mantiene separazione tra comando info `M` (read-only) e navigazione `SHIFT+M`

**ENTER su Mazzo = Pesca Automatica**
- Premendo ENTER quando il cursore è sul mazzo (pila 12), viene eseguita automaticamente la pescata
- Elimina la necessità di usare sempre D/P per pescare quando si è già sul mazzo
- Comandi D/P rimangono disponibili per pescare da qualunque posizione (backward compatibility)

### 🎨 Miglioramenti UX

**Hint Vocali Sempre Presenti**
- Gli hint vocali per la selezione sono forniti ad ogni primo tap, non solo la prima volta
- Messaggi contestuali diversi per ogni tipo di pila (base, semi, scarti, mazzo)
- Feedback chiaro per pile vuote e carte coperte

**Auto-Deseleziona Intelligente**
- Quando si seleziona una nuova carta con double-tap, la selezione precedente viene automaticamente annullata
- Feedback vocale: "Selezione precedente annullata. Carta selezionata: [Nome carta]!"

**Coerenza Modificatori**
- Nessun modificatore (1-7): Pile base (tableau)
- SHIFT (SHIFT+1-4, SHIFT+S, SHIFT+M): Accesso rapido pile speciali
- CTRL (CTRL+ENTER): Selezione diretta scarti (mantenuto esistente)

### 🔧 Modifiche Tecniche

**File: `scr/game_engine.py`**
- Aggiunto attributo `self.last_quick_move_pile` in `EngineData.__init__()` per tracking double-tap
- Nuovo metodo `move_cursor_to_pile_with_select(pile_index)` con logica double-tap completa
- Modificato `select_card()` per supportare ENTER su mazzo (chiama `self.pesca()`)
- Aggiunto reset tracking in tutti i metodi di movimento manuale:
  - `move_cursor_up()`, `move_cursor_down()`
  - `move_cursor_left()`, `move_cursor_right()`
  - `move_cursor_pile_type()` (TAB)
  - `cancel_selected_cards()`, `sposta_carte()`

**File: `scr/game_play.py`**
- Modificati handler `press_1()` a `press_7()` per usare `move_cursor_to_pile_with_select()`
- Nuovi handler per pile semi: `shift_1_press()` a `shift_4_press()`
- Nuovi handler speciali: `shift_s_press()` (scarti), `shift_m_press()` (mazzo)
- Modificato `handle_keyboard_EVENTS()` per supporto modificatore SHIFT
- Aggiornato `h_press()` con help text completo nuovi comandi

### ✅ Backward Compatibility

**Tutti i comandi esistenti rimangono funzionanti:**
- ✅ D/P per pescare da qualunque posizione
- ✅ Frecce SU/GIÙ/SINISTRA/DESTRA per navigazione manuale
- ✅ TAB per cambio tipo pila
- ✅ CTRL+ENTER per selezione scarti
- ✅ Comandi info S e M (read-only)
- ✅ Tutti gli altri comandi esistenti

**Nuovi comandi = aggiunte, non sostituzioni:**
- Nessuna deprecazione di comandi esistenti
- Tutti i comandi esistenti mantengono il loro comportamento originale
- Nuovi comandi forniscono alternative più veloci ma opzionali

### 📊 Test Coverage

**Casi Testati:**
- ✅ Double-tap pile base (1-7)
- ✅ Double-tap pile semi (SHIFT+1-4)
- ✅ Auto-deseleziona selezione precedente
- ✅ Reset tracking con movimenti manuali
- ✅ Navigazione scarti (SHIFT+S)
- ✅ Navigazione mazzo (SHIFT+M)
- ✅ ENTER su mazzo pesca correttamente
- ✅ Pile vuote edge case
- ✅ Carte coperte edge case
- ✅ Comandi info S/M non interferiscono con tracking

---

## [1.2.0] - 2026-02-06

### 🐛 Bug Fix
- **Fix F3 timer decrement**: F3 ora decrementa correttamente il timer di 5 minuti (simmetrico a F4)
  - `change_game_time()` ora accetta parametro `increment` (True/False)
  - F3 decrementa (-5 min), F4 incrementa (+5 min)
  - Limiti: minimo 5 minuti, massimo 60 minuti
  - Al minimo, decrementare disabilita il timer

- **Fix Auto-draw dopo rimescolamento** (🐛 CRITICAL FIX)
  - Risolto bug critico: la pescata automatica dopo rimescolamento ora funziona correttamente
  - Implementati nuovi metodi helper: `_genera_messaggio_carte_pescate()` e `_esegui_rimescolamento_e_pescata()`
  - Eliminata necessità di premere il comando pesca una seconda volta dopo il rimescolamento
  - Gestione robusta del caso limite: mazzo vuoto anche dopo rimescolamento

### ✨ Nuove Funzionalità
- **F5: Toggle modalità riciclo scarti**
  - Due modalità disponibili per riciclo scarti quando il mazzo finisce:
    - **INVERSIONE SEMPLICE** (default): comportamento originale - le carte vengono invertite
    - **MESCOLATA CASUALE** (nuova): le carte vengono mischiate casualmente
  - F5 alterna tra le due modalità (solo con opzioni aperte, tasto O)
  - Feedback vocale chiaro per entrambe le modalità
  - Modalità si resetta a default (inversione) ad ogni nuova partita
  - Non modificabile durante partita in corso

- **Auto-draw dopo rimescolamento**
  - Dopo ogni rimescolamento degli scarti nel mazzo, viene pescata automaticamente una carta
  - Elimina la necessità di premere nuovamente D/P per continuare a giocare
  - Migliora l'esperienza utente riducendo i passaggi richiesti
  - Annuncio vocale della carta pescata automaticamente: "Pescata automatica: hai pescato: [nome carta]"
  - Gestione robusta dei casi limite (mazzo vuoto dopo rimescolamento)

- **I: Visualizza impostazioni correnti**
  - Nuovo comando `I` per leggere le impostazioni di gioco:
    - Livello di difficoltà
    - Stato timer (attivo/disattivato e durata)
    - Modalità riciclo scarti (inversione/mescolata)

### 🎨 Miglioramenti UX
- Messaggi vocali distinti per inversione vs mescolata durante riciclo
- Report completo impostazioni con `get_settings_info()`
- Flusso di gioco più fluido con auto-draw integrato
- Singola pressione tasto pesca ora completa l'intera operazione (rimescolamento + pescata)

### 🔧 Modifiche Tecniche
- Aggiunto flag `shuffle_discards` in `EngineData.__init__()`
- Nuovo metodo `toggle_shuffle_mode()` per alternare modalità
- Nuovo metodo `get_shuffle_mode_status()` per query stato
- `riordina_scarti(shuffle_mode=False)` ora supporta entrambe le modalità
- Import `random` in `game_table.py` per shuffle casuale
- Refactoring metodo `pesca()` con nuovi helper methods per auto-draw:
  - `_genera_messaggio_carte_pescate()`: genera messaggio vocale per carte pescate
  - `_esegui_rimescolamento_e_pescata()`: gestisce rimescolamento + pescata automatica

### 📝 Documentazione
- Aggiunte sezioni README.md per gestione timer (⏱️) e modalità shuffle (🔀)
- Documentato comportamento auto-draw in tabella comandi
- Aggiornato CHANGELOG.md con dettagli tecnici e UX improvements

### ✅ Testing
- Creata suite di test `tests/unit/scr/test_game_engine_f3_f5.py`
- 14 test per coverage completo di F3, F5 e auto-draw
- Test per edge cases (timer=0, mazzo vuoto, toggle durante partita)
- Nuovi test specifici per auto-draw:
  - `test_auto_draw_verifica_carte_spostate`: verifica spostamento effettivo carte
  - `test_auto_draw_mazzo_vuoto_dopo_rimescolamento`: gestione caso limite

## [1.1.0] - 2026-02-05

### 🐛 Correzioni Critiche
- **#6**: Sistema di salvataggio statistiche finali (mosse, tempo, difficoltà)
  - Aggiunte variabili per statistiche finali in `EngineData`
  - `stop_game()` ora salva statistiche PRIMA del reset
  - `get_report_game()` usa statistiche salvate quando partita terminata
  - Fix ordine chiamate in `you_winner()` e `you_lost_by_time()`
- **#1**: Fix `get_report_mossa()` - logica semplificata e controlli bounds
- **#2**: Fix `copri_tutto()` - check pile vuote prima di accedere agli elementi
- **#3**: Fix `disable_timer()` - messaggi di errore appropriati
- **#4**: Rimosso controllo opzioni da `change_deck_type()`, chiarito `f1_press()`
- **#5**: Aggiunto comando H (aiuto) per mostrare tutti i comandi disponibili
- Fix 3 bug critici: `NameError` in `f3_press`, variable scope, range validation
- Fix validazione cursore per pile vuote in `move_cursor_up/down` e `sposta_carte`
- Fix controllo modificatore CTRL con bitwise AND in `enter_press()`, `f1_press()`, `f3_press()`
- Rimozione codice ridondante e fix commenti

### 🔒 Stabilità
- Prevenzione `IndexError` e race conditions con validazione cursore
- Gestione sicura dello stato del gioco

## [1.0.0] - 2026-02-05

### 🎉 Rilascio Stable - Architettura Refactored

### 📚 Documentazione
- Aggiunta documentazione completa di architettura e API
- Documentazione patterns Domain-Driven Design

### ✅ Testing
- Implementati test di integrazione end-to-end per flusso di gioco completo
- Coverage test aumentata significativamente

### 🏗️ Infrastruttura
- Aggiunto Dependency Injection Container per gestione dipendenze
- Implementato Command Pattern per undo/redo
- Creato `GameController` per orchestrazione use cases
- Aggiunte interfacce Protocol per dependency inversion

### 🎨 Presentazione
- Implementato `GameFormatter` per output accessibile
- Supporto lingua italiana completo
- Formattazione stato di gioco per screen reader
- Formattazione posizione cursore con descrizioni dettagliate
- Formattazione risultati mosse con indicatori successo/fallimento
- Formattazione liste carte per lettura assistita
- 11 unit test con coverage 93.33%

### ⚙️ Application Layer
- Aggiunto `GameService` con logica di business
- Gestione completa use cases di gioco

## [0.8.0] - 2023-02-27

### 🐛 Correzioni
- Sistemata distribuzione carte nel tavolo di gioco

## [0.7.0] - 2023-02-26

### 🔄 Refactoring
- Nuovo approccio architetturale per `game_play.py`
- Revisione completa della logica di gioco

## [0.6.0] - 2023-02-24

### 🔄 Refactoring
- Revisione generale del codebase
- Migliorata struttura del codice

## [0.5.0] - 2023-02-23

### ✨ Nuove Funzionalità
- Revisione lettura gameplay per accessibilità
- Stabilizzato evento uscita app
- Update funzionalità carta con nuove caratteristiche

### 🎮 Gameplay
- Stabilizzato gameplay tavolo di gioco
- Stabilizzata classe `GamePlay`
- Revisione comandi gameplay
- Revisione movimento tra le pile di gioco

## [0.4.0] - 2023-02-22

### ✨ Nuove Funzionalità
- Primo tentativo di disegno tavolo di gioco
- Update sistema avvio nuova partita
- Inserito metodo `create_tableau` nella classe `GamePlay`

### 🎮 Logica di Gioco
- Modificato metodo `move_card` con nuovo sistema spostamento carta
- Inserito metodo `is_valid_card_move` in `game_engine.py`
- Aggiunto metodo `get_top_card` per accesso alla carta superiore
- Aggiunto metodo `move_card` in `game_play.py`

### 🎨 Interfaccia
- Sistemato gestione eventi tastiera
- Dialog box di conferma per uscita gioco (Invio/Escape)
- Menu principale funzionante
- Revisione menu di gioco

### 🏗️ Struttura
- Creato file `game_play.py` per tavolo di gioco
- Upgrade gestione menu
- Refactoring dei nomi file per maggiore chiarezza

## [0.3.0] - 2023-02-21

### 🔧 Configurazione
- Revisione variabili globali in `myglob.py`
- Update configurazione generale
- Sistemata inizializzazione applicazione

## [0.2.0] - 2023-02-21

### 🏗️ Struttura Base
- Implementata struttura iniziale del progetto
- Setup file di configurazione
- Creati moduli base del gioco

## [0.1.0] - 2023-02-21

### 🎉 Primo Commit
- Inizializzazione repository
- Setup progetto base Solitario Classico Accessibile
- Struttura iniziale del progetto

---

## Convenzioni Versioning

Questo progetto segue il [Semantic Versioning](https://semver.org/lang/it/):

- **MAJOR** (X.0.0): Cambiamenti incompatibili con API precedenti
- **MINOR** (0.X.0): Nuove funzionalità retrocompatibili
- **PATCH** (0.0.X): Bug fix retrocompatibili

### Tipi di Modifiche
- 🎉 **Added**: Nuove funzionalità
- 🔄 **Changed**: Modifiche a funzionalità esistenti
- 🗑️ **Deprecated**: Funzionalità deprecate
- 🐛 **Fixed**: Bug fix
- 🔒 **Security**: Correzioni di sicurezza
- ✅ **Tests**: Aggiunte o modifiche ai test
- 📚 **Documentation**: Modifiche alla documentazione

[1.3.2]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Nemex81/solitario-classico-accessibile/releases/tag/v1.0.0
[0.8.0]: https://github.com/Nemex81/solitario-classico-accessibile/releases/tag/v0.8.0
[0.7.0]: https://github.com/Nemex81/solitario-classico-accessibile/releases/tag/v0.7.0
[0.6.0]: https://github.com/Nemex81/solitario-classico-accessibile/releases/tag/v0.6.0
[0.5.0]: https://github.com/Nemex81/solitario-classico-accessibile/releases/tag/v0.5.0
[0.4.0]: https://github.com/Nemex81/solitario-classico-accessibile/releases/tag/v0.4.0
[0.3.0]: https://github.com/Nemex81/solitario-classico-accessibile/releases/tag/v0.3.0
[0.2.0]: https://github.com/Nemex81/solitario-classico-accessibile/releases/tag/v0.2.0
[0.1.0]: https://github.com/Nemex81/solitario-classico-accessibile/releases/tag/v0.1.0
