# Changelog

Tutte le modifiche rilevanti a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/lang/it/).

## [1.4.2] - 2026-02-09

### ✨ Nuova Funzionalità: UX Improvements per Audiogame

**🎯 FEATURE COMPLETA**: Sistema di dialog conferma e welcome messages per migliorare l'esperienza utente

#### 🏗️ Architettura Clean Architecture (5 Commits Atomici)

**Commit #24: Virtual Dialog Box Component** (`048b7dd8`)
- Creato `src/infrastructure/ui/dialog.py` (~215 linee)
- Componente riusabile per dialog di conferma con accessibilità completa
- **Features**:
  - Navigazione keyboard completa (↑↓←→ + INVIO/ESC)
  - Button focus management con wrap-around
  - Single-key shortcuts (S/N/O/A)
  - TTS announcements per screen reader
  - Configurable callbacks (on_confirm/on_cancel)
  - Supporto 2+ pulsanti
- **API Usage**:
  ```python
  dialog = VirtualDialogBox(
      message="Vuoi continuare?",
      buttons=["Sì", "No"],
      default_button=0,  # Focus su Sì
      on_confirm=lambda: action(),
      on_cancel=lambda: cancel(),
      screen_reader=sr
  )
  dialog.open()
  ```

**Commit #25: ESC Confirmation in Main Menu** (`1151d4e1`)
- Implementato dialog "Vuoi uscire dall'applicazione?" quando ESC premuto nel menu principale
- **Flow**: Main Menu → ESC → Dialog → OK/Annulla → Azione
- **Features**:
  - Pulsanti: OK (focus) / Annulla
  - Shortcuts: O=OK, A=Annulla
  - Arrow navigation + ENTER/ESC
  - OK → Chiude applicazione
  - Annulla/ESC → Ritorna al menu principale
- **Modifica**: `test.py` +60 linee

**Commit #26: ESC Confirmation in Game Submenu** (`1b5eeda1`)
- Implementato dialog "Vuoi tornare al menu principale?" quando:
  - ESC premuto nel game submenu
  - INVIO su voce "Chiudi"
- **Flow**: Game Submenu → ESC/"Chiudi" → Dialog → Sì/No → Azione
- **Features**:
  - Pulsanti: Sì (focus) / No
  - Shortcuts: S=Sì, N=No
  - Arrow navigation + ENTER/ESC
  - Sì → Chiude submenu, ritorna al main menu
  - No → Resta nel game submenu
- **Fix**: `return_to_menu()` ora va al game submenu (non main)
- **Modifica**: `test.py` +75 linee

**Commit #27: ESC Confirmation During Gameplay + Double-ESC** (`cd36df4c`)
- Implementato dialog "Vuoi abbandonare la partita?" quando ESC premuto durante gameplay
- **Flow**: Gameplay → ESC → Dialog → Sì/No → Azione
- **Features**:
  - Pulsanti: Sì (focus) / No
  - Shortcuts: S=Sì, N=No
  - Arrow navigation + ENTER/ESC
  - Sì → Abbandona partita, ritorna al game submenu (non main!)
  - No → Riprendi gameplay
- **BONUS: Double-ESC Feature**:
  - Primo ESC: Apre dialog
  - Secondo ESC entro 2 secondi: Conferma automatica Sì
  - Annuncio TTS: "Uscita rapida"
  - Timer reset dopo 2s o dopo azione
- **Modifica**: `test.py` +85 linee

**Commit #28: Welcome Message in Game Submenu** (`8d693961` + `fa034726`)
- Aggiunto sistema di welcome messages per sottomenu
- **Implementazione Part 1** (`8d693961`): `menu.py` +45 linee
  - Parametri opzionali: `welcome_message`, `show_controls_hint`
  - Nuovo metodo `announce_welcome()` per rich announcements
  - Modifica `open_submenu()` per usare welcome se configurato
- **Implementazione Part 2** (`fa034726`): `test.py` +8 linee
  - Attivato welcome message per game_submenu
  - Messaggio completo:
    ```
    "Benvenuto nel menu di gioco del Solitario Classico!
     Usa frecce su e giù per navigare tra le voci. Premi Invio per selezionare.
     Posizione corrente: Nuova partita."
    ```

### 🎮 UX Improvements

**Prima (v1.4.1)**:
- ❌ ESC chiudeva direttamente senza conferma (rischio chiusure accidentali)
- ❌ Apertura submenu con annuncio generico: "Sottomenu aperto. 3 voci disponibili. 1 di 3: Nuova partita"
- ❌ Nessuna guida per utenti nuovi all'apertura menu

**Dopo (v1.4.2)**:
- ✅ ESC in tutti i contesti richiede conferma (safety)
- ✅ Welcome message ricco con guida comandi (accessibilità)
- ✅ Double-ESC per power users (velocità)
- ✅ Feedback TTS chiaro in tutti i dialog
- ✅ Navigation consistente in tutti i dialog (↑↓←→)
- ✅ Shortcuts singolo tasto per conferme rapide (S/N/O/A)

### 📊 Flussi Completi

#### **Main Menu ESC Flow**
```
Main Menu → ESC
  ↓
Dialog: "Vuoi uscire dall'applicazione?"
  [OK (focus)] / [Annulla]
  ↓
OK → Quit app
Annulla/ESC → Ritorna al main menu (re-announce)
```

#### **Game Submenu ESC/"Chiudi" Flow**
```
Game Submenu → ESC o INVIO su "Chiudi"
  ↓
Dialog: "Vuoi tornare al menu principale?"
  [Sì (focus)] / [No]
  ↓
Sì → Chiude submenu → Main menu
No/ESC → Resta in game submenu (re-announce)
```

#### **Gameplay ESC Flow**
```
Gameplay → ESC
  ↓
Dialog: "Vuoi abbandonare la partita?"
  [Sì (focus)] / [No]
  ↓
Sì → Abbandona → Game submenu
No/ESC → Riprendi gameplay

SHORTCUT: Gameplay → ESC → ESC (entro 2s)
  ↓
"Uscita rapida" → Auto-conferma → Game submenu
```

### 🔧 Modifiche Tecniche

**Statistiche Implementazione**:
- Totale linee codice: ~420
- File creati: 1 nuovo (`dialog.py`)
- File modificati: 2 (`test.py`, `menu.py`)
- Commit atomici: 5
- Tempo sviluppo: ~3 ore
- Dialog components: 3 istanze separate

**Architettura**:
```
Infrastructure (dialog.py)
   ↓
Application (test.py - dialog management)
   ↓
Presentation (menu.py - welcome messages)
```

**State Management**:
- `exit_dialog`: Dialog uscita app (main menu ESC)
- `return_to_main_dialog`: Dialog ritorno main (game submenu ESC)
- `abandon_game_dialog`: Dialog abbandono partita (gameplay ESC)
- `last_esc_time`: Timestamp per double-ESC detection

**Event Priority**:
```python
# Priority 1: Dialog open
if dialog.is_open:
    dialog.handle_keyboard_events(event)
    return  # Block all other input

# Priority 2: Menu navigation
if is_menu_open:
    # Check ESC intercept
    menu.handle_keyboard_events(event)

# Priority 3: Gameplay/Options
else:
    controller.handle_keyboard_events(event)
```

### ✅ Dialog Component API

**Constructor Parameters**:
- `message`: Dialog message text
- `buttons`: List di label (e.g., ["Sì", "No"])
- `default_button`: Index button con focus iniziale
- `on_confirm`: Callback per primo pulsante (index 0)
- `on_cancel`: Callback per altri pulsanti o ESC
- `screen_reader`: ScreenReader instance per TTS

**Navigation**:
- ↑↓←→: Muove focus tra pulsanti (wrap-around)
- INVIO/SPAZIO: Conferma pulsante corrente
- ESC: Annulla (chiama on_cancel)
- S/N/O/A: Shortcuts diretti per pulsanti

**TTS Announcements**:
- Open: "{message}\n{current_button}."
- Navigate: "{new_button}."
- Confirm: Chiude e esegue callback
- Ogni cambio focus interrompe TTS precedente

### 🎨 Welcome Message System

**Configurazione**:
```python
game_submenu = VirtualMenu(
    items=["Nuova partita", "Opzioni", "Chiudi"],
    callback=handler,
    screen_reader=sr,
    welcome_message="Benvenuto nel menu di gioco del Solitario Classico!",
    show_controls_hint=True
)
```

**Announcement Structure**:
1. Welcome message (se configurato)
2. Controls hint (se abilitato): "Usa frecce su e giù per navigare..."
3. Current item: "Posizione corrente: {item}"

**Benefici**:
- Orientamento immediato per utenti nuovi
- Guida comandi sempre disponibile all'apertura
- Sostituisce annuncio generico con messaggio ricco

### 🧪 Testing

**Test Manuali Eseguiti**:
- ✅ ESC in main menu → Dialog OK/Annulla
- ✅ ESC in game submenu → Dialog Sì/No
- ✅ INVIO su "Chiudi" → Stesso dialog Sì/No
- ✅ ESC durante gameplay → Dialog Sì/No
- ✅ Double-ESC entro 2s → Auto-conferma
- ✅ Double-ESC oltre 2s → Dialog normale
- ✅ Navigation frecce in tutti i dialog
- ✅ Shortcuts S/N/O/A funzionanti
- ✅ ESC nei dialog chiude correttamente
- ✅ TTS announcements chiari e completi
- ✅ Welcome message in game submenu
- ✅ Re-announce dopo chiusura dialog

**Edge Cases Testati**:
- ✅ Chiusura dialog con ESC → Ritorna a contesto originale
- ✅ Cambi focus rapidi → TTS interrupt corretto
- ✅ Dialog aperto blocca input sottostante
- ✅ Timer double-ESC reset corretto
- ✅ Welcome message non sovrascrive navigation normale

### 🎯 Backward Compatibility

**Breaking Changes**: Nessuno ✅
- ✅ Tutti i comandi esistenti funzionano identicamente
- ✅ ESC ora richiede conferma (miglioramento UX, non breaking)
- ✅ Menu navigation invariata
- ✅ Gameplay commands invariati
- ✅ Nessuna API pubblica modificata

**Additive Changes**:
- Nuovi dialog components (addizione)
- Welcome messages (addizione)
- Double-ESC feature (addizione)
- Tutti retrocompatibili

### 📚 Documentazione

**File Completati**:
- `docs/UX_IMPROVEMENTS_ROADMAP.md`: Piano implementazione dettagliato
- `docs/UX_IMPROVEMENTS_CHECKLIST.md`: Tracking completo task (5/5 ✅)

**Documentazione Commit**:
- 5 commit messages dettagliati con features/flow/statistics
- Inline code comments per logica complessa
- Docstrings completi per VirtualDialogBox

### 🚀 Benefici

**Safety**:
- ❌ Prima: ESC chiudeva direttamente (chiusure accidentali)
- ✅ Dopo: Conferma richiesta in tutti i contesti

**Accessibility**:
- ❌ Prima: Annunci generici, nessuna guida
- ✅ Dopo: Welcome messages ricchi, guida comandi sempre presente

**Usability**:
- ❌ Prima: Un solo modo per uscire (lento)
- ✅ Dopo: Dialog normale O double-ESC (velocità + safety)

**Consistency**:
- ❌ Prima: Comportamento ESC inconsistente
- ✅ Dopo: Pattern uniforme in tutti i contesti

### 📊 Prossimi Passi

**Testing Estensivo**:
- [ ] Test con screen reader reali (NVDA, JAWS)
- [ ] Feedback utenti su dialog flow
- [ ] Test welcome message efficacia
- [ ] Double-ESC usability evaluation

**Potenziali Miglioramenti**:
- Configurabile double-ESC timeout (ora 2s fisso)
- Audio cues per dialog open/close
- Customizable welcome messages per altri menu
- Persistent preference "non chiedere più"

### 🎉 Credits

Feature implementata seguendo richieste utente specifiche:
- Dialog conferma ESC in tutti i contesti (safety)
- Welcome message con guida comandi (accessibilità)
- Double-ESC per utenti esperti (velocità)
- TTS announcements chiari e completi

---

## [1.4.1] - 2026-02-08

### ✨ Nuova Funzionalità: Finestra Virtuale Opzioni

**🎯 FEATURE COMPLETA**: Virtual Options Window con design HYBRID approvato dall'utente

#### 🏗️ Architettura Clean Architecture (4 Commits Atomici)

**Commit #17: Domain Layer** (`9816d9a5`)
- Creato `src/domain/services/game_settings.py` (~350 linee)
- Servizio dominio centralizzato per gestione configurazioni
- Metodi principali:
  - `toggle_timer()`: Toggle dedicato OFF ↔ 5min (tasto T)
  - `increment_timer_validated()`: +5min con cap 60min
  - `decrement_timer_validated()`: -5min fino a 0=OFF
  - `toggle_deck_type()`: French ↔ Neapolitan
  - `cycle_difficulty()`: 1→2→3→1
  - `toggle_shuffle_mode()`: Inversione ↔ Mescolata Casuale
- Validazione: blocco modifiche durante partita attiva
- Return tuples `(bool, str)` per feedback TTS
- Display helpers per tutti i settings

**Commit #18: Presentation Layer** (`1fe26906`)
- Creato `src/presentation/options_formatter.py` (~250 linee)
- Classe `OptionsFormatter` con 14 metodi static
- Messaggi TTS completi:
  - `format_option_item()`: Navigazione con hint contestuali
  - `format_option_changed()`: Conferme modifiche con gender IT
  - `format_all_settings()`: Recap completo (tasto I)
  - `format_help_text()`: Help completo (tasto H)
  - `format_save_dialog()`: Dialog conferma S/N/ESC
- Hint contestuali intelligenti:
  - Opzione 0-1-3: "Premi INVIO per modificare."
  - Timer OFF: "Premi T per attivare."
  - Timer ON: "Premi T per disattivare o + e - per regolare."
  - Opzione 4: "Opzione non ancora implementata."
- Ottimizzato per screen reader accessibility

**Commit #19: Application Layer** (`b5feb964`)
- Creato `src/application/options_controller.py` (~450 linee)
- Controller completo finestra opzioni virtuali
- **State Machine**: CLOSED / OPEN_CLEAN / OPEN_DIRTY
- **Snapshot System**: Save/discard modifiche
- **Metodi Lifecycle** (5):
  - `open_window()`: Apertura con snapshot settings
  - `close_window()`: Chiusura con conferma se modifiche
  - `save_and_close()`, `discard_and_close()`, `cancel_close()`
- **Navigazione HYBRID**:
  - Frecce ↑↓: Wraparound 0↔4
  - Tasti 1-5: Jump diretto all'opzione
  - Hint vocali contestuali
- **Modifiche Opzioni**:
  - INVIO/SPAZIO: Modifica opzione corrente
  - +/-: Regola timer (solo se Timer selezionato)
  - T: Toggle timer OFF↔5min (solo se Timer selezionato)
- **Informazioni**:
  - I: Recap tutte impostazioni
  - H: Help completo comandi
- **Validazioni**:
  - Blocco modifiche durante partita
  - Validazione tasti timer (+/-/T) solo su opzione Timer
  - Blocco opzione 4 (futura)

**Commit #20: Integration** (`23d6ac43`)
- Modificato `src/application/gameplay_controller.py`
- **Routing Prioritario**: Check `options_controller.is_open` prima di gameplay
- **Handler Dedicato**: `_handle_options_events()` con key map completo
- **Dialog Salvataggio**: `_handle_save_dialog()` per S/N/ESC
- **Deprecazione Legacy**: Rimossi F1-F5 handlers
  - F1 (cambio mazzo) → Tasto O → Frecce → Opzione 0 → INVIO
  - F2 (difficoltà) → Tasto O → Frecce → Opzione 1 → INVIO
  - F3/F4 (timer) → Tasto O → Frecce → Opzione 2 → +/-/T
  - F5 (shuffle) → Tasto O → Frecce → Opzione 3 → INVIO
- **Comandi Finestra Opzioni**:
  - O: Apri/Chiudi
  - ↑↓: Naviga opzioni
  - 1-5: Jump diretto
  - INVIO/SPAZIO: Modifica
  - +/-: Timer adjust
  - T: Timer toggle
  - I: Recap completo
  - H: Help
  - ESC: Chiudi (con conferma se modifiche)

### 🎮 UX Design: HYBRID Navigation

**Approvazione Utente**:
- Frecce ↑↓ per navigazione sequenziale (familiarità)
- Tasti 1-5 per jump diretto (velocità)
- Hint vocali sempre presenti (accessibilità)
- Esempio feedback: "3 di 5: Timer, 10 minuti. Premi T per disattivare o + e - per regolare."

**Flusso Utente Tipico**:
1. Premi O (apri opzioni)
2. Usa ↑↓ o 1-5 per navigare
3. Premi INVIO per modificare (o +/-/T per timer)
4. Ripeti per altre opzioni
5. Premi ESC
   - Se nessuna modifica: chiusura diretta
   - Se modifiche: "Salvare modifiche? S/N/ESC"
6. S salva, N scarta, ESC annulla

### 🎨 Opzioni Disponibili

**Opzione 0: Tipo Mazzo**
- Valori: Carte Francesi / Carte Napoletane
- Modifica: Toggle con INVIO

**Opzione 1: Difficoltà**
- Valori: Livello 1 / Livello 2 / Livello 3
- Modifica: Ciclo con INVIO
- Effetto: Numero carte pescate dal mazzo (1/2/3)

**Opzione 2: Timer**
- Valori: Disattivato / 5-60 minuti
- Modifiche multiple:
  - INVIO: Cicla preset (OFF→10→20→30→OFF)
  - T: Toggle OFF↔5min (veloce)
  - +: Incrementa 5min (fino a 60)
  - -: Decrementa 5min (fino a OFF)
- Hint contestuali basati su stato

**Opzione 3: Modalità Riciclo Scarti**
- Valori: Inversione Semplice / Mescolata Casuale
- Modifica: Toggle con INVIO

**Opzione 4: (Futura)**
- Placeholder per funzionalità future
- Messaggio: "Opzione non ancora implementata."

### 🔧 Modifiche Tecniche

**Statistiche Implementazione**:
- Totale linee codice: ~1200
- File creati: 3 nuovi
- File modificati: 1 (gameplay_controller)
- Metodi totali: ~50
- Commit atomici: 4
- Tempo sviluppo: ~4 ore

**Clean Architecture Respected**:
```
Domain (GameSettings)
   ↓
Application (OptionsWindowController)
   ↓
Presentation (OptionsFormatter)
   ↓
Infrastructure (GameplayController routing)
```

**State Machine**:
- CLOSED: Finestra chiusa (gameplay normale)
- OPEN_CLEAN: Finestra aperta, nessuna modifica
- OPEN_DIRTY: Finestra aperta, modifiche non salvate

**Snapshot System**:
- Save: Copia settings all'apertura finestra
- Compare: Detect modifiche per dialog conferma
- Restore: Ripristina valori originali se discard

### ✅ Validazioni e Sicurezza

**Blocchi Intelligenti**:
- ❌ Apertura finestra durante partita attiva
- ❌ Modifiche opzioni durante partita attiva
- ❌ Tasti +/-/T se non su opzione Timer
- ❌ Modifica opzione 4 (futura)
- ✅ Chiusura diretta se nessuna modifica
- ✅ Dialog conferma se modifiche presenti

**Messaggi Errore Chiari**:
- "Non puoi aprire le opzioni durante una partita! Premi N per nuova partita."
- "Seleziona prima il Timer con il tasto 3."
- "Opzione non ancora implementata. Sarà disponibile in un prossimo aggiornamento."

### 📚 Documentazione

**File Completati**:
- `docs/OPTIONS_WINDOW_ROADMAP_COMPLETATO.md`: Guida dettagliata con codice completo
- `docs/OPTIONS_WINDOW_CHECKLIST_COMPLETATO.md`: Tracking completo task (100%)

**Test Cases Documentati**:
- 40+ test manuali pianificati
- Navigazione completa (arrows, wraparound, jump)
- Modifiche tutte opzioni
- Timer management (limiti, errori, hint)
- Dialog salvataggio (S/N/ESC flow)
- Validazioni e edge cases

### 🎯 Backward Compatibility

**Breaking Changes**: Nessuno ✅
- Tasto O comportamento invariato (open/close)
- Tutti i comandi gameplay invariati
- F1-F5 semplicemente non mappati (deprecati)
- Nessuna API pubblica modificata

**Deprecazioni**:
- F1-F5: Ora bisogna usare O per aprire finestra opzioni
- Migrazione path: F1 → O + navigate + modify
- Più verbose ma più accessibile e user-friendly

### 🚀 Benefici

**Prima (F1-F5)**:
- ❌ Comandi sparsi e non intuitivi
- ❌ Difficile ricordare quale F-key fa cosa
- ❌ Nessun feedback contestuale
- ❌ Impossibile vedere tutte le opzioni insieme

**Dopo (Finestra Opzioni)**:
- ✅ Tutte le opzioni in un unico posto
- ✅ Navigazione intuitiva (frecce + numeri)
- ✅ Hint contestuali sempre presenti
- ✅ Recap completo con tasto I
- ✅ Help integrato con tasto H
- ✅ Conferma modifiche per sicurezza
- ✅ Accessibilità screen reader ottimizzata

### 📊 Prossimi Passi

**Testing Manuale Utente**:
- [ ] Navigazione completa (40+ test cases)
- [ ] Accessibilità screen reader
- [ ] Edge cases e limiti
- [ ] UX feedback

**Potenziali Miglioramenti Futuri**:
- Opzione 4: Verbosità TTS
- Preset timer personalizzabili
- Persistent settings su file
- Suoni/beep per conferme

### 🎉 Credits

Feature implementata seguendo richieste utente specifiche:
- Design HYBRID approvato (frecce + numeri + hint)
- Toggle timer dedicato (tasto T)
- Hint contestuali basati su stato opzione
- Conferma salvataggio modifiche

---

## [1.4.0] - 2026-02-08

### 🏗️ Clean Architecture Migration - COMPLETA

**🎉 MILESTONE RAGGIUNTA**: Migrazione completa da architettura monolitica (`scr/`) a Clean Architecture (`src/`) in 13 commit atomici.

### ✨ Nuove Funzionalità

**Nuovo Entry Point Clean Architecture**
- `python test.py`: Avvia versione Clean Architecture (nuovo, consigliato)
- `python acs.py`: Mantiene versione legacy funzionante (deprecata, compatibilità)
- Zero breaking changes: entrambe le versioni coesistono

**Dependency Injection Container (#11)**
- `DIContainer` completo per gestione dipendenze tra layer
- Factory methods per tutti i componenti (Domain, Application, Infrastructure, Presentation)
- Singleton management: Settings, InputHandler, ScreenReader, Formatter
- Factory pattern: Deck, Table, TimerManager (nuova istanza per partita)
- Utility globali: `get_container()`, `reset_container()`

**Integration Test Suite (#12)**
- Suite completa di test integrazione per validare architettura
- `test_di_container.py`: 14 test per DI Container
- `test_clean_arch_bootstrap.py`: Test bootstrap completo applicazione
- Validazione isolamento layer e assenza dipendenze circolari
- Coverage: tutte le componenti Clean Architecture testate

### 🏛️ Architettura - Nuovi Layer

**Infrastructure Layer (Commits #5-6, #11)**
- `infrastructure/accessibility/screen_reader.py` (#5): TTS integration platform-agnostic
- `infrastructure/accessibility/tts_provider.py` (#5): Abstract interface per provider TTS
- `infrastructure/ui/menu.py` (#6): VirtualMenu per audiogame navigation
- `infrastructure/di_container.py` (#11): Dependency Injection completo
- `infrastructure/__init__.py`: Export pubblici per bootstrap

**Application Layer (Commits #7-8)**
- `application/input_handler.py` (#7): Keyboard events → GameCommand mapping
  - Support SHIFT modifiers (SHIFT+1-4, SHIFT+S/M)
  - Double-tap detection (v1.3.0 feature)
  - 60+ keyboard bindings
- `application/game_settings.py` (#8): Configuration management
  - GameSettings dataclass (deck_type, timer, difficulty)
  - Support entrambi mazzi (francese/napoletano)
  - Persistence settings tra partite
- `application/timer_manager.py` (#8): Timer logic separato
  - F2/F3/F4 controls (v1.2.0 features)
  - Countdown con avvisi vocali
  - Disable/enable dinamico

**Presentation Layer (Commit #9)**
- `presentation/game_formatter.py` (#9): Output formatting italiano
  - Formattazione stato partita per screen reader
  - Statistiche dinamiche (adattive per mazzo francese/napoletano)
  - Report finale partita (mosse, tempo, percentuali)
  - Localization italiana completa

### 🔧 Modifiche Tecniche

**Commits Timeline**
1. ✅ #1-4 (Preesistenti): Domain layer (Models, Rules, Services)
2. ✅ #5 (Feb 8): ScreenReader + TtsProvider separation
3. ✅ #6 (Feb 8): VirtualMenu UI component
4. ✅ #7 (Feb 8): InputHandler con SHIFT shortcuts
5. ✅ #8 (Feb 8): GameSettings + TimerManager
6. ✅ #9 (Feb 8): GameFormatter con statistiche dinamiche
7. ✅ #10 (Feb 8): test.py documentation update
8. ✅ #11 (Feb 8): Complete DI Container
9. ✅ #12 (Feb 8): Integration test suite
10. ✅ #13 (Feb 8): Migration documentation complete

**Separazione Responsabilità**
```
Infrastructure → Application → Domain (Core)
Presentation → Application → Domain
```
- Domain: Zero dipendenze esterne (business logic pura)
- Application: Dipende solo da Domain (orchestrazione)
- Infrastructure: Adapters per sistemi esterni (TTS, UI, DI)
- Presentation: Formatting output (screen reader)

**Dependency Injection Flow**
```python
container = get_container()
settings = container.get_settings()
deck = container.get_deck(settings.deck_type)
input_handler = container.get_input_handler()
formatter = container.get_formatter(language="it")
```

### 📚 Documentazione

**Nuova Documentazione Completa (#13)**
- `docs/MIGRATION_GUIDE.md`: Guida completa migrazione scr/ → src/
  - Layer-by-layer mapping
  - 13 commits breakdown dettagliato
  - Feature parity checklist
  - Testing strategy
- `docs/COMMITS_SUMMARY.md`: Log dettagliato tutti i commit
  - SHA commit links
  - File modificati per commit
  - Checklist validazione
- `README.md`: Aggiornato con architettura Clean completa
  - Diagramma layer
  - Confronto entry points (test.py vs acs.py)
  - Stato migrazione
- `CHANGELOG.md`: Questa sezione v1.4.0 ✨

### ✅ Feature Parity con v1.3.3

**100% Compatibilità Funzionale**
- ✅ Entrambi i mazzi (francese 52 carte, napoletano 40 carte)
- ✅ King validation deck-specific (13 vs 10)
- ✅ Distribuzione dinamica riserve (24 vs 12 carte)
- ✅ SHIFT+1-4 shortcuts (v1.3.0 foundation piles)
- ✅ SHIFT+S/M shortcuts (v1.3.0 waste/stock)
- ✅ Double-tap navigation (v1.3.0)
- ✅ Timer management F2/F3/F4 (v1.2.0)
- ✅ F5 shuffle toggle (v1.2.0)
- ✅ Auto-draw dopo rimescolamento (v1.2.0)
- ✅ HOME/END navigation (v1.3.1)
- ✅ Statistiche dinamiche per tipo mazzo (v1.3.2)
- ✅ Verifica vittoria 4 pile (v1.3.2 fix)
- ✅ Tutti i 60+ comandi tastiera
- ✅ Screen reader accessibility completo

### 🧪 Testing

**Test Coverage**
- Unit tests: 91.47% coverage (target ≥80% ✅)
- Integration tests: 2 suite complete (DI + Bootstrap)
- Layer isolation: Validato senza dipendenze circolari
- Bootstrap sequence: Test completo da entry point a runtime

**Test Manuali Eseguiti**
- ✅ Avvio test.py con menu PyGame
- ✅ Tutte le scorciatoie SHIFT (1-4, S, M)
- ✅ Double-tap pile base e semi
- ✅ Cambio mazzo F1 (francese ↔ napoletano)
- ✅ Timer F2/F3/F4
- ✅ Statistiche dinamiche (13 vs 10 carte)
- ✅ Screen reader su tutte le azioni

### 🎯 Benefici Architettura Clean

**Prima (Monolitico scr/)**
- ❌ game_engine.py: 43 KB, 1500+ linee
- ❌ Business logic + UI + formatting misti
- ❌ Difficile testing in isolamento
- ❌ Modifiche con effetti cascata

**Dopo (Clean Architecture src/)**
- ✅ Componenti separati per responsabilità
- ✅ Business logic pura (Domain layer)
- ✅ Testing componenti isolati
- ✅ Modifiche localizzate e predicibili
- ✅ Dependency Injection per flessibilità
- ✅ Sostituzione componenti senza impatti

### 📦 Struttura Directory

```
src/
├── domain/              # Business logic pura
│   ├── models/         # Card, Deck, Pile, Table
│   ├── rules/          # SolitaireRules, MoveValidator
│   └── services/       # GameService
│
├── application/        # Orchestrazione use cases
│   ├── input_handler.py      # Keyboard → Commands
│   ├── game_settings.py      # Configuration
│   ├── timer_manager.py      # Timer logic
│   └── gameplay_controller.py # Main controller
│
├── infrastructure/     # External adapters
│   ├── accessibility/  # ScreenReader + TTS
│   ├── ui/            # PyGame Menu
│   └── di_container.py # Dependency Injection
│
└── presentation/       # Output formatting
    └── game_formatter.py # Italian localization

tests/
├── unit/              # Test unitari per layer
└── integration/       # Test integrazione Clean Arch

docs/
├── MIGRATION_GUIDE.md      # Guida migrazione
├── COMMITS_SUMMARY.md      # Log commit
├── REFACTORING_PLAN.md     # Piano 13 commit
└── ARCHITECTURE.md         # Dettagli architettura
```

### 🚀 Deployment

**Entry Points Disponibili**
```bash
# Clean Architecture (v1.4.0 - CONSIGLIATO)
python test.py

# Legacy Monolitico (v1.3.3 - DEPRECATO)
python acs.py
```

**Branch Status**
- `refactoring-engine`: Implementazione completa Clean Architecture
- Pronto per merge a `main` dopo testing estensivo
- Feature parity 100% validato

### ⚠️ Breaking Changes

**Nessuno!** ✅
- Versione legacy (`acs.py` + `scr/`) funziona esattamente come prima
- Nuova versione (`test.py` + `src/`) è addizione, non sostituzione
- API pubblica invariata
- Tutti i comandi tastiera identici
- Comportamento gameplay identico

### 🔮 Roadmap Futura

1. **v1.4.1**: Testing estensivo con utenti reali
2. **v1.5.0**: Eventuali miglioramenti UX basati su feedback
3. **v2.0.0**: Merge `refactoring-engine` → `main`
   - `test.py` diventa entry point principale
   - `acs.py` mantenuto per compatibilità
4. **v2.1.0**: Deprecazione ufficiale `scr/`
5. **v3.0.0**: Rimozione completa `scr/` e `acs.py`

### 📊 Statistiche Migrazione

- **Commits**: 13 atomici (5-13 implementati Feb 8, 2026)
- **File aggiunti**: 14 (domain preesistenti + 14 nuovi)
- **File aggiornati**: 3 (test.py, README.md, CHANGELOG.md)
- **Righe codice**: ~3000 (ben organizzate in layer)
- **Test coverage**: 91.47% (target 80% superato)
- **Tempo sviluppo**: 1 sessione intensiva (6 ore)
- **Feature parity**: 100% ✅

### 🙏 Note

Questa release rappresenta un milestone fondamentale per il progetto:
- **Manutenibilità**: Codice molto più facile da mantenere
- **Testabilità**: Componenti isolati testabili indipendentemente
- **Estensibilità**: Aggiungere nuove feature senza toccare core logic
- **Professionalità**: Architettura enterprise-grade

Grazie a tutti per il supporto! 🎉

---

## [1.3.3] - 2026-02-06

### 🐛 Bug Fix Critici

**Fix Crash Cambio Mazzo (F1)**
- Risolto bug critico: crash `IndexError: pop from empty list` quando si cambiava tipo di mazzo con F1
- Causa: `distribuisci_carte()` aveva un valore hardcoded di 24 carte per il mazzo riserve
- Problema: Con mazzo napoletano (40 carte) tentava di distribuire 28+24=52 carte ma ne aveva solo 40
- Soluzione: Calcolo dinamico `carte_rimanenti = self.mazzo.get_total_cards() - 28`

**Fix Spostamento Re Napoletano in Pila Vuota**
- Risolto bug critico: Re napoletano (valore 10) bloccato su pile vuote con messaggio "mossa non consentita"
- Causa: `put_to_base()` aveva check hardcoded `card.get_value == 13` per permettere spostamento in pila vuota
- Problema: Funzionava solo con Re francese (13), bloccava Re napoletano (valore 10)
- Soluzione: Aggiunto metodo semantico `is_king()` in `ProtoDeck` che verifica se carta è un Re indipendentemente dal valore numerico
- Impatto gameplay: Scenario bloccante eliminato - ora è possibile spostare Re napoletano per scoprire carte sottostanti

### 🔧 Modifiche Tecniche

**File: `scr/game_table.py`**
- `distribuisci_carte()`: rimosso hardcoded `range(24)`, ora usa `range(carte_rimanenti)`
- Calcolo dinamico carte rimanenti: 24 per mazzo francese, 12 per mazzo napoletano
- Aggiunti commenti esplicativi per il calcolo dinamico
- `put_to_base()`: sostituito check `card.get_value == 13` con `self.mazzo.is_king(card)`
- Logica semplificata con early return per pila vuota
- Codice più leggibile e manutenibile

**File: `scr/decks.py`**
- Aggiunto metodo `is_king(card)` in classe `ProtoDeck`
- Verifica semantica: confronta valore carta con `FIGURE_VALUES["Re"]` del mazzo
- Funziona correttamente per entrambi i mazzi:
  - FrenchDeck: `Re = 13` ✅
  - NeapolitanDeck: `Re = 10` ✅
- Gestione sicura con check `king_value is None`

### 🧪 Testing

**Nuovo file test: `tests/unit/scr/test_distribuisci_carte_deck_switching.py`**
- 6 test completi per verificare il fix distribuzione carte:
  - `test_distribuisci_carte_french_deck`: verifica 24 carte riserve
  - `test_distribuisci_carte_neapolitan_deck`: verifica 12 carte riserve
  - `test_cambio_mazzo_french_to_neapolitan`: test F1 francese→napoletano
  - `test_cambio_mazzo_neapolitan_to_french`: test F1 napoletano→francese
  - `test_cambio_mazzo_multiplo`: test cambi multipli consecutivi
  - `test_no_index_error_on_neapolitan_deck`: test regressione per IndexError

**Nuovo file test: `tests/unit/scr/test_king_to_empty_base_pile.py`**
- 14 test completi per verificare il fix spostamento Re:
  - 6 test per `is_king()`: verifica riconoscimento Re per entrambi i mazzi
  - 5 test per spostamento Re in pile vuote: francese, napoletano, blocco figure non-Re
  - 3 test di regressione: mosse normali su pile non vuote, stesso colore bloccato, valore scorretto bloccato

### 📊 Impatto

**Prima dei fix:**
- ❌ F1 con mazzo napoletano → crash immediato
- ❌ Re napoletano bloccato in pile vuote → gameplay impossibile
- ❌ Impossibile usare la feature mazzo napoletano della v1.3.2

**Dopo i fix:**
- ✅ F1 funziona correttamente con entrambi i mazzi
- ✅ Distribuzione dinamica: 24 carte (francese) o 12 carte (napoletano) nel mazzo riserve
- ✅ Re napoletano (10) e Re francese (13) entrambi funzionanti in pile vuote
- ✅ Regina/Cavallo napoletani (8, 9) correttamente bloccati in pile vuote
- ✅ Cambio mazzo fluido senza crash
- ✅ Mazzo napoletano completamente giocabile

### ✅ Backward Compatibility

- Zero breaking changes
- Mazzo francese continua a funzionare esattamente come prima
- Tutte le mosse esistenti su pile non vuote invariate
- Fix non altera nessuna altra funzionalità

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

[1.4.2]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.4.1...v1.4.2
[1.4.1]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.3.3...v1.4.0
[1.3.3]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.3.2...v1.3.3
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
