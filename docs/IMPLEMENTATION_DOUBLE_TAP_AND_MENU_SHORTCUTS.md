[File troppo lungo - limitato per brevità. Aggiungo solo la sezione modificata]

# La parte esistente resta identica fino a Feature #3, poi aggiungo:

## 🎮 FEATURE #3: New Game Confirmation Dialog ⭐ NUOVO

[... contenuto esistente invariato fino a Implementazione Tecnica ...]

### 🛠️ Implementazione Tecnica

#### **⚠️ DUE FILE DA MODIFICARE**

**File 1: `src/application/gameplay_controller.py`** - Handler comando "N" durante gameplay  
**File 2: `test.py`** - Dialog instance e callbacks

**Componenti Già Disponibili**:
- ✅ `VirtualDialogBox` già implementato (v1.4.2, commit #24)
- ✅ Pattern dialog conferma già usato per ESC handlers
- ✅ Metodi helper già disponibili in test.py

**Architettura Dialog**:
```
[User preme N] 
    ↓
[gameplay_controller._new_game()]
    ↓
 check is_game_running() ?
    ├─ NO → avvia direttamente
    └─ YES → chiama callback test.py
            ↓
        [test.py.show_new_game_dialog()]
            ↓
        [VirtualDialogBox aperto]
            ├─ Sì → _confirm_new_game() → _start_new_game()
            └─ No → _cancel_new_game() → resume game
```

---

#### **Modifica 3.1: `src/application/gameplay_controller.py` - Aggiungere Callback**

**Posizione**: Metodo `__init__()`

**PRIMA** (stato attuale):
```python
def __init__(
    self, 
    engine: GameEngine, 
    screen_reader, 
    settings: Optional[GameSettings] = None
):
    self.engine = engine
    self.sr = screen_reader
    self.settings = settings or GameSettings()
    self.options_controller = OptionsWindowController(self.settings)
    # ...
```

**DOPO** (aggiungere parametro callback):
```python
def __init__(
    self, 
    engine: GameEngine, 
    screen_reader, 
    settings: Optional[GameSettings] = None,
    on_new_game_request: Optional[Callable[[], None]] = None  # ✅ NEW PARAMETER (v1.4.3)
):
    """Initialize gameplay controller.
    
    Args:
        engine: GameEngine facade
        screen_reader: ScreenReader for TTS
        settings: GameSettings instance (optional)
        on_new_game_request: Callback quando utente richiede nuova partita con gioco attivo (v1.4.3)
            Se None, avvia direttamente (backward compatible)
            Se fornito, chiama callback per dialog conferma
    """
    self.engine = engine
    self.sr = screen_reader
    self.settings = settings or GameSettings()
    self.options_controller = OptionsWindowController(self.settings)
    self.on_new_game_request = on_new_game_request  # ✅ STORE CALLBACK (v1.4.3)
    # ...
```

---

#### **Modifica 3.2: `src/application/gameplay_controller.py` - Modificare Metodo `_new_game()`**

**Posizione**: Metodo `_new_game()` (riga ~353)

**PRIMA** (implementazione attuale con TODO):
```python
def _new_game(self) -> None:
    """N: Start new game (with confirmation if game running)."""
    state = self.engine.get_game_state()
    game_over = state.get('game_over', {}).get('is_over', True)
    
    if not game_over:
        # TODO: Implementare dialog conferma in futuro
        # Per ora avvia direttamente
        pass
    
    self.engine.new_game()
    # Message vocalized by engine.new_game()
```

**DOPO** (implementazione con callback dialog):
```python
def _new_game(self) -> None:
    """N: Start new game (with confirmation if game running).
    
    Behavior:
    - If no game running: Start immediately
    - If game running + callback set: Trigger dialog confirmation (v1.4.3)
    - If game running + no callback: Start immediately (backward compatible)
    
    New in v1.4.3: Delegates to test.py dialog when game is active.
    """
    # Check if game is currently running
    state = self.engine.get_game_state()
    game_over = state.get('game_over', {}).get('is_over', True)
    
    # ═══════════════════════════════════════════════════════════
    # ✅ SAFETY CHECK (v1.4.3): Game already in progress?
    # ═══════════════════════════════════════════════════════════
    if not game_over and self.on_new_game_request is not None:
        # Game in progress AND callback available
        # Delegate to test.py to show confirmation dialog
        self.on_new_game_request()  # ✅ TRIGGER DIALOG via callback
        return  # Don't start game yet, wait for user confirmation
    
    # ═══════════════════════════════════════════════════════════
    # NO GAME RUNNING or NO CALLBACK: Start immediately
    # ═══════════════════════════════════════════════════════════
    self.engine.new_game()
    # Message vocalized by engine.new_game()
```

---

#### **Modifica 3.3: `test.py` - Passare Callback a GamePlayController**

**Posizione**: Nel metodo `__init__()` dove viene istanziato `gameplay_controller`

**PRIMA** (stato attuale):
```python
def __init__(self):
    # ... existing initialization ...
    
    # Application: Gameplay controller (now with settings!)
    print("Inizializzazione controller gameplay...")
    self.gameplay_controller = GamePlayController(
        engine=self.engine,
        screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr(),
        settings=self.settings  # NEW PARAMETER (v1.4.2.1)
    )
    print("✓ Controller pronto")
    
    # ... rest of initialization ...
```

**DOPO** (aggiungere callback):
```python
def __init__(self):
    # ... existing initialization ...
    
    # Application: Gameplay controller (now with settings + new game callback!)
    print("Inizializzazione controller gameplay...")
    self.gameplay_controller = GamePlayController(
        engine=self.engine,
        screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr(),
        settings=self.settings,  # v1.4.2.1
        on_new_game_request=lambda: self.show_new_game_dialog()  # ✅ NEW PARAMETER (v1.4.3)
    )
    print("✓ Controller pronto")
    
    # ... rest of initialization ...
```

---

#### **Modifica 3.4: `test.py` - Aggiungere Dialog Instance**

[... contenuto invariato dalla versione precedente del documento ...]

---

#### **Modifica 3.5: `test.py` - Implementare Method `show_new_game_dialog()`**

**Posizione**: Dopo gli altri show_*_dialog() methods

**Codice**:
```python
def show_new_game_dialog(self) -> None:
    """Show new game confirmation dialog (v1.4.3).
    
    Opens dialog asking "Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?" with
    Sì/No buttons. Sì has default focus.
    
    Triggered by:
    - "N" key during gameplay (via gameplay_controller callback)
    - "Nuova partita" menu selection when game is running
    
    Safety feature to prevent accidental game loss.
    """
    print("\n" + "="*60)
    print("DIALOG: Conferma nuova partita")
    print("="*60)
    
    self.new_game_dialog.open()
```

---

#### **Modifica 3.6: `test.py` - Modificare Handler Menu "Nuova Partita"**

**Posizione**: Metodo `handle_game_submenu_selection()`, case 0 (Nuova partita)

**PRIMA** (stato attuale - Copilot ha già implementato questo!):
```python
def handle_game_submenu_selection(self, selected_item: int) -> None:
    if selected_item == 0:
        # Nuova partita - with safety check (v1.4.3)
        if self.engine.is_game_running():
            # Game in progress: show confirmation dialog
            self.show_new_game_dialog()
        else:
            # No game running: start immediately
            self._start_new_game()
```

**NOTA**: ✅ Questo è già implementato da Copilot! Nessuna modifica necessaria qui.

---

#### **Modifica 3.7: `test.py` - Implementare Dialog Callbacks**

[... contenuto invariato dalla versione precedente del documento ...]

---

#### **Modifica 3.8: `test.py` - Gestione Eventi Dialog**

[... contenuto invariato dalla versione precedente del documento ...]

---

### 📋 Posizioni Esatte nel Codice (AGGIORNATO)

| Modifica | File | Linea Approssimativa | Sezione | Azione |
|----------|------|---------------------|---------|--------|
| **3.1** | `gameplay_controller.py` | ~35-55 | `__init__()` parameters | Aggiungere parametro `on_new_game_request` |
| **3.2** | `gameplay_controller.py` | ~353-365 | Metodo `_new_game()` | Implementare callback check + early return |
| **3.3** | `test.py` | ~150-160 | `__init__()` gameplay controller | Passare callback `lambda: self.show_new_game_dialog()` |
| **3.4** | `test.py` | ~80-120 | `__init__()` dialogs | Aggiungere `new_game_dialog` instance |
| **3.5** | `test.py` | ~280-295 | Dialog handlers | Aggiungere `show_new_game_dialog()` method |
| **3.6** | `test.py` | ~210-225 | `handle_game_submenu_selection()` | ✅ Già implementato da Copilot! |
| **3.7** | `test.py` | ~300-350 | Dialog callbacks | Aggiungere `_confirm_new_game()` e `_cancel_new_game()` |
| **3.8** | `test.py` | ~180-220 | `handle_events()` | Aggiungere check `new_game_dialog.is_open` |

**Totale Modifiche**: 2 file (gameplay_controller.py + test.py), 8 sezioni

---

[... resto del documento invariato ...]

**Fine Documento**  
Ultimo aggiornamento: 10 Febbraio 2026, 12:25 CET  
**Correzione Critica**: Aggiunta modifica `gameplay_controller.py` per comando "N" durante gameplay
