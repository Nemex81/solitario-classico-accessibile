# Changelog

Tutte le modifiche rilevanti a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/lang/it/).

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
