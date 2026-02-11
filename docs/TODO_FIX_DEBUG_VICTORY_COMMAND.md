## Analisi del Problema 🔍

### Flusso Attuale (BROKEN ❌)

**Comando**: CTRL+ALT+W premuto durante gameplay

**Percorso esecuzione**:
1. `test.py` → `handle_events()` → NON gestisce CTRL+ALT+W (passa a gameplay_controller)
2. `gameplay_controller.py` → linea 571-577:
   ```python
   if (event.key == pygame.K_w and (mods & KMOD_CTRL) and (mods & pygame.KMOD_ALT)):
       msg = self.engine._debug_force_victory()
       self._vocalizza(msg)  # msg = "" (stringa vuota)
       return
   ```
3. `game_engine.py` → `_debug_force_victory()` → linee 1113-1141:
   ```python
   def _debug_force_victory(self) -> str:
       if not self.is_game_running():
           return "Nessuna partita in corso da simulare!"
       
       self.end_game(is_victory=True)  # ❌ NON passa use_native_dialogs
       return ""  # ❌ Ritorna stringa vuota
   ```

4. `game_engine.py` → `end_game()` → linee 1070-1111:
   ```python
   def end_game(self, is_victory: bool) -> None:
       # ... snapshot + score + report ...
       
       if self.screen_reader:
           self.screen_reader.tts.speak(report, interrupt=True)  # ✅ TTS funziona
       
       if self.dialogs:  # ❌ self.dialogs = None! (non inizializzato in create())
           self.dialogs.show_statistics_report(...)  # ❌ Mai eseguito
           
           if self.dialogs.show_yes_no(...):
               self.new_game()
               return
       
       self.service.reset_game()  # ❌ Resetta partita MA non torna al menu
   ```

### Problemi Identificati 🐛

1. **Dialog Provider NOT Initialized in test.py**:
   - `test.py` linea 111: `self.engine = GameEngine.create(...)` NON passa `use_native_dialogs=True`
   - Risultato: `self.engine.dialogs = None`

2. **No UI State Management in end_game()**:
   - `end_game()` resetta il game service MA non cambia `is_menu_open` in `test.py`
   - Risultato: rimani in gameplay mode senza partita attiva

3. **Missing Rematch Rejection Handler**:
   - Se dialogs disponibili ma user rifiuta rematch → `reset_game()` chiamato
   - MA `is_menu_open` resta False → UI bloccata

4. **Circular Dependency Risk**:
   - `end_game()` chiama `new_game()` se rematch accepted
   - MA dovrebbe passare controllo a `test.py` per gestire menu

## Strategia di Correzione 🛠️

### Fase 1: Abilita Dialog Provider in test.py ✅

**File**: `test.py` → `__init__()` linea 111

**Modifica**:
```python
# BEFORE:
self.engine = GameEngine.create(
    audio_enabled=(self.screen_reader is not None),
    tts_engine="auto",
    verbose=1,
    settings=self.settings
)

# AFTER:
self.engine = GameEngine.create(
    audio_enabled=(self.screen_reader is not None),
    tts_engine="auto",
    verbose=1,
    settings=self.settings,
    use_native_dialogs=True  # 🆕 ENABLE WX DIALOGS
)
```

**Rationale**: Questo abilita `WxDialogProvider` in `game_engine.py` → `self.dialogs` sarà popolato.

***

### Fase 2: Aggiungi Callback per End Game in GameEngine 🔄

**File**: `src/application/game_engine.py`

**Modifica `__init__()` (linea ~85)**:
```python
def __init__(
    self,
    table: GameTable,
    service: GameService,
    rules: SolitaireRules,
    cursor: CursorManager,
    selection: SelectionManager,
    screen_reader: Optional[ScreenReader] = None,
    settings: Optional[GameSettings] = None,
    score_storage: Optional[ScoreStorage] = None,
    dialog_provider: Optional['DialogProvider'] = None,
    on_game_ended: Optional[Callable[[bool], None]] = None  # 🆕 NEW
):
    # ... existing code ...
    self.dialogs = dialog_provider
    self.on_game_ended = on_game_ended  # 🆕 Store callback
```

**Modifica `end_game()` (linea 1070-1111)**:
```python
def end_game(self, is_victory: bool) -> None:
    """Handle game end with full reporting and rematch prompt.
    
    Complete flow:
    1. Snapshot statistics
    2. Calculate final score
    3. Save score to storage
    4. Generate complete report
    5. Announce via TTS (always)
    6. Show native dialog (if available)
    7. Prompt for rematch (if dialogs available)
    8. 🆕 Call on_game_ended callback to return control to test.py
    """
    
    # Steps 1-3: Snapshot + Score + Storage (unchanged)
    self.service._snapshot_statistics()
    final_stats = self.service.get_final_statistics()
    
    final_score = None
    if self.settings and self.settings.scoring_enabled and self.service.scoring:
        final_score = self.service.scoring.calculate_final_score(
            elapsed_seconds=final_stats['elapsed_time'],
            move_count=final_stats['move_count'],
            is_victory=is_victory,
            timer_strict_mode=self.settings.timer_strict_mode if self.settings else True
        )
    
    if final_score and self.score_storage:
        self.score_storage.save_score(final_score)
    
    # Step 4: Generate Report
    from src.presentation.formatters.report_formatter import ReportFormatter
    
    deck_type = self.settings.deck_type if self.settings else "french"
    report = ReportFormatter.format_final_report(
        stats=final_stats,
        final_score=final_score,
        is_victory=is_victory,
        deck_type=deck_type
    )
    
    # Step 5: TTS Announcement (Always)
    if self.screen_reader:
        self.screen_reader.tts.speak(report, interrupt=True)
    
    # Step 6-7: Native Dialogs (If Available)
    wants_rematch = False
    if self.dialogs:
        self.dialogs.show_statistics_report(
            stats=final_stats,
            final_score=final_score,
            is_victory=is_victory,
            deck_type=deck_type
        )
        
        wants_rematch = self.dialogs.show_yes_no(
            "Vuoi giocare ancora?", 
            "Rivincita?"
        )
    
    # Step 8: 🆕 Delegate to test.py via callback
    if self.on_game_ended:
        # Pass control back to test.py with rematch decision
        self.on_game_ended(wants_rematch)
    else:
        # Fallback: Old behavior (no callback)
        if wants_rematch:
            self.new_game()
        else:
            self.service.reset_game()
```

***

### Fase 3: Aggiungi Handler in test.py per End Game Callback 📞

**File**: `test.py`

**Aggiungi nuovo metodo (dopo `_handle_game_over_by_timeout`, linea ~665)**:
```python
def handle_game_ended(self, wants_rematch: bool) -> None:
    """Handle game end callback from GameEngine.end_game().
    
    Called when:
    - Victory detected (all 4 suits complete)
    - CTRL+ALT+W debug command used
    - Timer expired in STRICT mode (via separate path)
    
    Args:
        wants_rematch: True if user chose rematch in dialog
    
    Flow:
        - If rematch: Start new game immediately (stays in gameplay)
        - If no rematch: Return to game submenu
    
    Side effects:
        - Resets timer flags
        - Updates is_menu_open state
        - Announces menu/game start via TTS
    
    Note:
        This is the ONLY method that should handle UI state after
        end_game() is called. Separates concerns between engine
        (game logic) and test.py (UI state).
    """
    print("\n" + "="*60)
    print(f"CALLBACK: Game ended - Rematch: {wants_rematch}")
    print("="*60)
    
    # Reset timer flags (important for next game)
    self._timer_expired_announced = False
    
    if wants_rematch:
        # User chose rematch: Stay in gameplay, start new game
        print("User requested rematch - Starting new game")
        self.start_game()  # This will announce "Nuova partita avviata!"
    else:
        # User declined rematch: Return to game submenu
        print("User declined rematch - Returning to game submenu")
        self.is_menu_open = True  # 🆕 CRITICAL: Enable menu state
        
        # Announce return to menu
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Ritorno al menu di gioco.",
                interrupt=True
            )
            pygame.time.wait(400)
            
            # Re-announce game submenu with welcome message
            self.game_submenu.announce_welcome()
```

**Modifica `__init__()` per passare callback (linea 111)**:
```python
# AFTER GameSettings initialization (linea ~106)
self.settings = GameSettings()
print("✓ Impostazioni pronte")

# NEW v1.6.1: Dialog manager initialization (unchanged)
print("Inizializzazione dialog manager...")
self.dialog_manager = SolitarioDialogManager()
# ...

# Application: Game engine setup (NOW WITH CALLBACK!)
print("Inizializzazione motore di gioco...")
self.engine = GameEngine.create(
    audio_enabled=(self.screen_reader is not None),
    tts_engine="auto",
    verbose=1,
    settings=self.settings,
    use_native_dialogs=True  # 🆕 ENABLE WX DIALOGS
)

# 🆕 INJECT CALLBACK AFTER CREATION
self.engine.on_game_ended = self.handle_game_ended

print("✓ Game engine pronto")
```

***

### Fase 4: Fix GameEngine.create() per Supportare Callback 🔧

**File**: `src/application/game_engine.py`

**Modifica `create()` classmethod (linea ~110)**:
```python
@classmethod
def create(
    cls,
    audio_enabled: bool = True,
    tts_engine: str = "auto",
    verbose: int = 1,
    settings: Optional[GameSettings] = None,
    use_native_dialogs: bool = False
) -> "GameEngine":
    """Factory method to create fully initialized game engine.
    
    Args:
        audio_enabled: Enable audio feedback
        tts_engine: TTS engine ("auto", "nvda", "sapi5")
        verbose: Audio verbosity level (0-2)
        settings: GameSettings instance for configuration
        use_native_dialogs: Enable native wxPython dialogs (NEW v1.6.0)
        
    Returns:
        Initialized GameEngine instance ready to play
    
    Note:
        on_game_ended callback must be set manually after creation:
        
        >>> engine = GameEngine.create(use_native_dialogs=True)
        >>> engine.on_game_ended = my_callback_function
    """
    # ... existing code unchanged ...
    
    # ✨ NEW v1.6.0: Create dialog provider if requested
    dialog_provider = None
    if use_native_dialogs:
        try:
            from src.infrastructure.ui.wx_dialog_provider import WxDialogProvider
            dialog_provider = WxDialogProvider()
        except ImportError:
            # wxPython not available, graceful degradation
            dialog_provider = None
    
    # 🆕 PASS on_game_ended=None (will be set by caller)
    return cls(
        table, service, rules, cursor, selection, 
        screen_reader, settings, score_storage, 
        dialog_provider,
        on_game_ended=None  # 🆕 Caller must set this manually
    )
```

***

## Riepilogo Modifiche 📋

| File | Linee | Tipo | Descrizione |
|------|-------|------|-------------|
| `test.py` | 111 | MODIFY | Abilita `use_native_dialogs=True` in `GameEngine.create()` |
| `test.py` | 117 | ADD | Inietta callback `self.engine.on_game_ended = self.handle_game_ended` |
| `test.py` | ~665 | ADD | Nuovo metodo `handle_game_ended(wants_rematch)` (~40 LOC) |
| `game_engine.py` | ~85 | MODIFY | Aggiungi parametro `on_game_ended` a `__init__()` |
| `game_engine.py` | 1070-1111 | MODIFY | Refactor `end_game()` per usare callback invece di logica diretta |
| `game_engine.py` | ~110 | MODIFY | Documenta che callback va settato post-creazione |

**Total**: ~60 LOC aggiunte, ~30 LOC modificate

***

## Flusso Corretto (FIXED ✅)

**Comando**: CTRL+ALT+W premuto durante gameplay

1. `gameplay_controller.py` → intercetta CTRL+ALT+W
2. `game_engine._debug_force_victory()` → chiama `end_game(is_victory=True)`
3. `game_engine.end_game()`:
   - Snapshot statistiche ✅
   - Calcola score ✅
   - Vocalize report via TTS ✅
   - **Mostra dialog WX con statistiche** ✅ (ora funziona perché `self.dialogs` popolato)
   - **Mostra dialog "Rivincita?"** ✅
   - **Chiama `self.on_game_ended(wants_rematch)`** ✅
4. `test.py.handle_game_ended()`:
   - Se rematch=True → chiama `start_game()` (resta in gameplay)
   - Se rematch=False → setta `is_menu_open=True` + annuncia menu ✅

**Risultato**: Dialog WX visibili, UI torna al menu se no rematch, rematch funziona correttamente.

***