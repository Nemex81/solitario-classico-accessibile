# TODO: Implementazione Features v1.4.3

## 🎯 Obiettivo

Implementare 3 features UX richieste dall'utente per migliorare l'accessibilità e la velocità di interazione del gioco:

1. ✅ **Feature #1**: Double-tap auto-selection per pile base e semi
2. ✅ **Feature #2**: Numeric shortcuts per menu (1-5)
3. ✅ **Feature #3**: New game confirmation dialog (menu + keyboard command)

**Status**: 🎉 **COMPLETATO AL 100%** (10 Febbraio 2026)

---

## 🆕 FASE 4: Feature #3 - New Game Confirmation Dialog ⭐ COMPLETATO

### 📝 Problema Identificato

**Issue**: Durante testing v1.4.3, è emerso che premendo "N" (Nuova partita) durante una partita già in corso, viene immediatamente avviata una nuova partita senza chiedere conferma. Questo può causare **perdita accidentale del progresso** di gioco.

**Root Cause**: Il dialog è implementato SOLO per la selezione menu, ma NON per il comando tastiera "N" premesso durante il gameplay. Il metodo `_new_game()` in `gameplay_controller.py` ha un TODO ma non chiama il dialog.

**Soluzione**: Implementare dialog di conferma sia da menu CHE da comando "N" tastiera, usando callback architecture per chiamare il dialog di test.py.

---

### ⚠️ REQUISITO CRITICO: DUE PERCORSI DA IMPLEMENTARE

**Percorso 1: Menu → Nuova Partita** (✅ GIÀ IMPLEMENTATO da Copilot)
- File: `test.py`, metodo `handle_game_submenu_selection()`
- Status: ✅ Implementato correttamente

**Percorso 2: Comando Tastiera "N" durante Gameplay** (✅ COMPLETATO)
- File: `src/application/gameplay_controller.py`, metodo `_new_game()`
- Status: ✅ Implementato con callback architecture
- Soluzione: Aggiunto callback a test.py

---

### Step 4.0: Modifica GamePlayController (⭐ COMPLETATO)

- [x] **Aprire file**: `src/application/gameplay_controller.py`
- [x] **Metodo `__init__()`** (riga ~35-55):
  - [x] Aggiungere parametro: `on_new_game_request: Optional[Callable[[], None]] = None`
  - [x] Salvare: `self.on_new_game_request = on_new_game_request`
  - [x] Documentare: "Callback quando utente richiede nuova partita con gioco attivo (v1.4.3)"
- [x] **Metodo `_new_game()`** (riga ~353-365):
  - [x] Trovare sezione con TODO: "Implementare dialog conferma in futuro"
  - [x] Sostituire TODO con check reale:
    ```python
    if not game_over and self.on_new_game_request is not None:
        # Game in progress AND callback available
        self.on_new_game_request()  # Trigger dialog via callback
        return  # Don't start game yet, wait for confirmation
    ```
  - [x] Rimuovere `pass` statement dopo TODO
  - [x] Mantenere `self.engine.new_game()` per caso no-game o no-callback

#### Test Checklist Step 4.0
- [x] **T0.1**: Callback None + nessuna partita → Avvia immediatamente (backward compatible)
- [x] **T0.2**: Callback set + nessuna partita → Avvia immediatamente (no dialog needed)
- [x] **T0.3**: Callback set + partita attiva → Chiama callback + NON avvia
- [x] **T0.4**: Callback None + partita attiva → Avvia immediatamente (backward compatible)

---

### Step 4.0b: Collegare Callback in test.py (⭐ COMPLETATO)

- [x] **Aprire file**: `test.py`
- [x] **Trovare sezione**: Inizializzazione `gameplay_controller` (riga ~150-160)
- [x] **Modifica instantiation**:
  ```python
  self.gameplay_controller = GamePlayController(
      engine=self.engine,
      screen_reader=self.screen_reader,
      settings=self.settings,
      on_new_game_request=self.show_new_game_dialog  # NEW (v1.4.3)
  )
  ```

#### Test Checklist Step 4.0b
- [x] **T0.5**: Callback correttamente passato al controller
- [x] **T0.6**: Lambda function risolve `self.show_new_game_dialog` correttamente
- [x] **T0.7**: Nessun errore a runtime durante instantiation

---

### Step 4.1: Aggiungere Dialog Instance (`test.py`) - ✅ COMPLETATO

- [x] **Aprire file**: `test.py`
- [x] **Sezione `__init__()`**: Trovare blocco dichiarazioni dialog (dopo `abandon_game_dialog`)
- [x] **Aggiungere**: `self.new_game_dialog = None  # New game confirmation dialog (v1.4.3)`
- [x] **Posizionamento**: Dopo linea ~220 (dopo `self.abandon_game_dialog = None`)

#### Test Checklist Step 4.1
- [x] **T1.1**: Attributo dichiarato correttamente
- [x] **T1.2**: Inizializzato a None (lazy initialization)
- [x] **T1.3**: Nessun errore syntax

---

### Step 4.2: Modificare Handler Nuova Partita (`test.py`) - ✅ COMPLETATO

- [x] **Aprire file**: `test.py`
- [x] **Trovare metodo**: `handle_game_submenu_selection()` (riga ~210-230)
- [x] **Modificare blocco** `if selected_item == 0:` (Nuova partita):
  ```python
  if selected_item == 0:
      # Nuova partita - with safety check (v1.4.3)
      if self.engine.is_game_running():
          # Game in progress: show confirmation dialog
          self.show_new_game_dialog()
      else:
          # No game running: start immediately
          self._start_new_game()
  ```
- [x] **Sostituire chiamata diretta**: `self.is_menu_open = False; self.start_game()` → nuovo blocco if/else

#### Test Checklist Step 4.2
- [x] **T2.1**: Check `is_game_running()` presente PRIMA di avviare partita
- [x] **T2.2**: Dialog chiamato se partita attiva
- [x] **T2.3**: Avvio diretto se NO partita attiva (backward compatible)
- [x] **T2.4**: Nessuna doppia chiamata a `start_game()`

---

### Step 4.3: Implementare Dialog Callbacks (`test.py`) - ✅ COMPLETATO

- [x] **Aprire file**: `test.py`
- [x] **Posizione**: Dopo metodo `close_abandon_dialog()` (riga ~480)
- [x] **Aggiungere 3 metodi**:

#### Metodo 1: `show_new_game_dialog()` (Entry point)
```python
def show_new_game_dialog(self) -> None:
    """Show new game confirmation dialog (v1.4.3).
    
    Opens dialog asking "Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?" with
    Sì/No buttons. Sì has default focus.
    
    Triggered by:
    - "N" key during gameplay
    - "Nuova partita" menu selection when game is running
    
    Safety feature to prevent accidental game loss.
    """
    print("\n" + "="*60)
    print("DIALOG: Conferma nuova partita")
    print("="*60)
    
    self.new_game_dialog = VirtualDialogBox(
        message="Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?",
        buttons=["Sì", "No"],
        default_button=0,  # Focus on Sì
        on_confirm=self._confirm_new_game,
        on_cancel=self._cancel_new_game,
        screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr()
    )
    
    self.new_game_dialog.open()
```

#### Metodo 2: `_confirm_new_game()` (Sì button callback)
```python
def _confirm_new_game(self) -> None:
    """Callback: User confirmed starting new game (abandoning current).
    
    Called when user presses:
    - "S" key (Sì shortcut)
    - Arrow keys + ENTER on "Sì" button
    
    Actions:
    1. Close dialog
    2. Abandon current game (no stats save)
    3. Start new game
    
    New in v1.4.3: Safety feature for preventing accidental game loss.
    """
    print("Confermato - Abbandono partita corrente e avvio nuova")
    
    # Close dialog
    self.new_game_dialog = None
    
    # Announce action
    if self.screen_reader:
        self.screen_reader.tts.speak(
            "Partita precedente abbandonata.",
            interrupt=True
        )
        pygame.time.wait(300)
    
    # Start new game
    self._start_new_game()
```

#### Metodo 3: `_cancel_new_game()` (No button / ESC callback)
```python
def _cancel_new_game(self) -> None:
    """Callback: User cancelled new game dialog.
    
    Called when user presses:
    - "N" key (No shortcut)
    - ESC key
    - Arrow keys + ENTER on "No" button
    
    Actions:
    1. Close dialog
    2. Resume current game
    3. Announce cancellation
    
    New in v1.4.3: Safety feature for preventing accidental game loss.
    """
    print("Dialog chiuso - Azione annullata, continuo partita corrente")
    
    # Close dialog
    self.new_game_dialog = None
    
    # Announce cancellation
    if self.screen_reader:
        self.screen_reader.tts.speak(
            "Azione annullata. Torno alla partita.",
            interrupt=True
        )
        pygame.time.wait(300)
    
    # No further action needed, game continues
```

#### Metodo 4: `_start_new_game()` (Helper method - NUOVO)
```python
def _start_new_game(self) -> None:
    """Internal method: Start new game without confirmation.
    
    Called by:
    - handle_game_submenu_selection() when no game is running
    - _confirm_new_game() after user confirms dialog
    
    New in v1.4.3: Extracted to helper method for reuse.
    """
    self.is_menu_open = False
    self.start_game()
```

#### Test Checklist Step 4.3
- [x] **T3.1**: `show_new_game_dialog()` crea dialog correttamente
- [x] **T3.2**: `_confirm_new_game()` chiude dialog + avvia nuova partita
- [x] **T3.3**: `_cancel_new_game()` chiude dialog + mantiene partita corrente
- [x] **T3.4**: `_start_new_game()` helper funziona in entrambi i contesti
- [x] **T3.5**: TTS announcements appropriati per ogni azione
- [x] **T3.6**: Callbacks collegati correttamente a VirtualDialogBox

---

### Step 4.4: Gestione Eventi Dialog (`test.py`) - ✅ COMPLETATO

- [x] **Aprire file**: `test.py`
- [x] **Trovare metodo**: `handle_events()` (riga ~500-600)
- [x] **Posizione**: Dopo blocco `abandon_game_dialog` (PRIORITY 3), prima di `is_menu_open` check
- [x] **Aggiungere blocco PRIORITY 4**:
  ```python
  # PRIORITY 4: New game confirmation dialog open (v1.4.3)
  if self.new_game_dialog and self.new_game_dialog.is_open:
      self.new_game_dialog.handle_keyboard_events(event)
      continue  # Block all other input
  ```

#### Test Checklist Step 4.4
- [x] **T4.1**: Dialog ha priorità DOPO abandon dialog ma PRIMA di menu/gameplay
- [x] **T4.2**: Input bloccato quando dialog aperto (continue statement)
- [x] **T4.3**: Shortcuts S/N/ESC funzionano correttamente nel dialog
- [x] **T4.4**: Nessuna interferenza con altri dialog esistenti

---

### Step 4.5: Testing Feature #3 Completo (✅ VERIFICATO)

#### Test Comportamento Base
- [x] **T5.1**: Premere N senza partita attiva → Nuova partita inizia immediatamente (no dialog)
- [x] **T5.2**: ⭐ Premere N **DURANTE GAMEPLAY** con partita in corso → Dialog "Vuoi abbandonare..." appare
- [x] **T5.2b**: ⭐ Selezionare "Nuova partita" **DAL MENU** con partita in corso → Dialog appare
- [x] **T5.3**: Dialog aperto, premere S → Partita precedente abbandonata, nuova inizia
- [x] **T5.4**: Dialog aperto, premere N → Dialog chiuso, partita corrente continua
- [x] **T5.5**: Dialog aperto, premere ESC → Dialog chiuso, partita corrente continua

#### Test Navigation Dialog
- [x] **T5.6**: Frecce ↑↓←→ cambiano focus tra pulsanti Sì/No
- [x] **T5.7**: Focus parte su "Sì" (default_button=0)
- [x] **T5.8**: INVIO sul pulsante corrente esegue azione
- [x] **T5.9**: TTS annuncia messaggio dialog all'apertura

#### Test Integrazione con Altri Dialog
- [x] **T5.10**: Abandon game dialog + New game dialog non interferiscono
- [x] **T5.11**: Exit dialog + New game dialog non interferiscono
- [x] **T5.12**: Menu navigation bloccata quando new game dialog aperto
- [x] **T5.13**: Gameplay commands bloccati quando new game dialog aperto

#### Test Edge Cases
- [x] **T5.14**: Aprire dialog, premere ESC, ripremere N → Dialog riappare correttamente
- [x] **T5.15**: Doppio N durante gameplay → Primo apre dialog, secondo = shortcut "No"
- [x] **T5.16**: Conferma Sì + immediate N → Nuova partita avviata, nuovo N senza dialog
- [x] **T5.17**: `is_game_running()` ritorna False dopo conferma → No dialog mostrato

#### Test TTS Announcements
- [x] **T5.18**: "Una partita è già in corso..." annunciato all'apertura dialog
- [x] **T5.19**: "Partita precedente abbandonata" annunciato dopo conferma Sì
- [x] **T5.20**: "Azione annullata. Torno alla partita." annunciato dopo No/ESC
- [x] **T5.21**: "Nuova partita avviata!" annunciato dopo inizio effettivo partita

---

## ✅ FASE 1: Feature #1 - Double-Tap Auto-Selection - COMPLETATO

[... contenuto invariato ...]

---

## ✅ FASE 2: Feature #2 - Numeric Menu Shortcuts - COMPLETATO

[... contenuto invariato ...]

---

## ✅ FASE 3: Feature #3 - New Game Confirmation Dialog (MENU PATH) - COMPLETATO

[... contenuto invariato ...]

---

## 📝 NOTES

### Session Log

**2026-02-08 (Implementazione Copilot - Sessione 1)**
- ✅ Fase 1 completata: Feature #1 Double-Tap implementata
  - Modificato `src/domain/services/cursor_manager.py`
  - Modificato `src/application/game_engine.py`
  - Test manuali passati

**2026-02-08 (Implementazione Copilot - Sessione 2)**
- ✅ Fase 2 completata: Feature #2 Numeric Shortcuts implementata
  - Modificato `src/infrastructure/ui/menu.py`
  - Test manuali passati su menu principale e sottomenu

**2026-02-10 (Implementazione Copilot - Sessione 3)**
- ✅ Fase 3 completata: Feature #3 New Game Dialog (MENU PATH)
  - Implementati tutti gli Step 4.1-4.4 in `test.py`
  - Dialog funzionante per path menu "Nuova partita"
  - ⚠️ PROBLEMA: Dialog NON implementato per comando tastiera "N" durante gameplay

**2026-02-10 12:25 CET (CORREZIONE CRITICA - Feature #3 Incompleta)**
- ⚠️ **PROBLEMA IDENTIFICATO**: Copilot ha implementato dialog SOLO per path menu
- ❌ **MANCANTE**: Dialog NON triggato da comando "N" tastiera durante gameplay
- 🔍 **ROOT CAUSE**: `gameplay_controller._new_game()` ha TODO ma non chiama dialog
- ✅ **SOLUZIONE**: Aggiungere callback `on_new_game_request` a gameplay_controller

**2026-02-10 (Implementazione Copilot - Sessione 4 - Correzione Feature #3)**
- ✅ Step 4.0: Modificato `src/application/gameplay_controller.py`
  - ✅ Aggiunto parametro `on_new_game_request` in `__init__()`
  - ✅ Salvato callback come `self.on_new_game_request`
  - ✅ Modificato `_new_game()` per chiamare callback quando partita attiva
  - ✅ Backward compatible: se callback None, avvia direttamente
- ✅ Step 4.0b: Modificato `test.py`
  - ✅ Aggiunto parametro `on_new_game_request=self.show_new_game_dialog` in GamePlayController init
  - ✅ Collegamento callback completato
- ✅ Aggiornato `CHANGELOG.md` con files modificati completi
- ✅ Aggiornato `docs/TODO.md` con stato completamento
- 🎉 **FEATURE #3 ORA COMPLETA**: Dialog funziona sia da menu che da tasto N durante gameplay

**2026-02-10 12:45 CET (COMPLETAMENTO VERIFICATO)**
- ✅ Step 4.0: Tutte le modifiche a `gameplay_controller.py` verificate e funzionanti
- ✅ Step 4.0b: Callback collegato correttamente in `test.py`
- ✅ Testing manuale completo: N da gameplay, menu "Nuova partita", shortcuts dialog
- ✅ CHANGELOG.md aggiornato con Feature #3 completa
- ✅ TODO.md: Checkpoint Step 4.0 e 4.0b spuntati
- 🎉 **v1.4.3 IMPLEMENTAZIONE 100% COMPLETA E VERIFICATA**

---

**Implementazione v1.4.3 COMPLETA AL 100%!**  
**Tutte e tre le feature implementate e funzionanti**

- ✅ Feature #1: Double-Tap Auto-Selection
- ✅ Feature #2: Numeric Menu Shortcuts  
- ✅ Feature #3: New Game Confirmation Dialog (completo: menu + keyboard command)

---

**Fine TODO**  
Ultimo aggiornamento: 10 Febbraio 2026 - v1.4.3 Implementazione 100% Completa
