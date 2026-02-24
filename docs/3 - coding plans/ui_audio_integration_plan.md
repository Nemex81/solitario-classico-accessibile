# Piano di Integrazione Audio UI - Menu Principale e Finestra Opzioni

**Versione:** 1.0  
**Data:** 2026-02-24  
**Obiettivo:** Integrare eventi audio nel `MenuPanel` (menu principale) e `OptionsDialog` (finestra opzioni) per completare il feedback sonoro in tutte le interfacce utente.

---

## 🎯 Problema Identificato

### Situazione Attuale
Durante test manuali, utente ha riportato:
> "Nel menu principale come nella finestra delle opzioni non vengono riprodotti suoni"

### Analisi Root Cause
1. **MenuPanel** (`src/infrastructure/ui/menu_panel.py`):
   - Non riceve `audio_manager` nel costruttore
   - Nessun evento audio durante navigazione pulsanti (TAB/frecce)
   - Nessun evento audio al click pulsanti (ENTER)
   - Solo feedback TTS, manca feedback sonoro

2. **OptionsDialog** (`src/infrastructure/ui/options_dialog.py`):
   - Non riceve `audio_manager` nel costruttore
   - Nessun evento audio per cambio impostazioni
   - Nessun evento `SETTING_SAVED` al salvataggio
   - Solo feedback TTS, manca feedback sonoro

### Eventi Audio Interessati
Dal sistema audio centralizzato (`audio_events.py`):

**Menu Principale:**
- `UI_BUTTON_HOVER` → Focus su pulsante (TAB/frecce)
- `UI_BUTTON_CLICK` → Click pulsante (ENTER)
- `UI_MENU_OPEN` → Apertura menu (già gestito in `acs_wx.py`)
- `UI_MENU_CLOSE` → Chiusura menu

**Finestra Opzioni:**
- `UI_FOCUS_CHANGE` → Cambio widget (TAB)
- `SETTING_CHANGED` → Modifica impostazione (RadioBox, CheckBox, ComboBox)
- `SETTING_SAVED` → Salvataggio impostazioni (pulsante Salva)
- `UI_CANCEL` → Annullamento (pulsante Annulla, ESC)

---

## 📋 Piano di Implementazione

### Fase 1: Modifica MenuPanel

**File:** `src/infrastructure/ui/menu_panel.py`

#### 1.1 Aggiornare Costruttore

**Posizione:** Linea ~69 (`__init__`)

```python
def __init__(self, parent, controller, container=None, audio_manager=None, **kwargs):
    """Initialize MenuPanel with controller and optional audio manager.
    
    Args:
        parent: Parent panel container (frame.panel_container)
        controller: Application controller with menu action methods
        container: Optional DependencyContainer for future DI needs (v2.2.0)
        audio_manager: Optional AudioManager for sound effects (v3.5.1)
        **kwargs: Additional arguments passed to BasicPanel
    """
    self.container = container
    self.audio_manager = audio_manager  # ← AGGIUNGERE
    super().__init__(
        parent=parent,
        controller=controller,
        **kwargs
    )
```

#### 1.2 Aggiungere Eventi Audio su Focus Pulsante

**Posizione:** Linea ~150 (`on_button_focus`)

```python
def on_button_focus(self, event: wx.FocusEvent) -> None:
    """Announce button label when focused (accessibility).
    
    Called automatically when user TABs to a button or when SetFocus()
    is called programmatically. Announces button label via TTS for
    screen reader users.
    
    🆕 v3.5.1: Plays UI_BUTTON_HOVER sound effect.
    """
    button = event.GetEventObject()
    self.announce(button.GetLabel(), interrupt=False)
    
    # ✨ NUOVO: Play button hover sound
    if self.audio_manager:
        from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
        self.audio_manager.play_event(AudioEvent(
            event_type=AudioEventType.UI_BUTTON_HOVER
        ))
    
    event.Skip()
```

#### 1.3 Aggiungere Eventi Audio su Click Pulsante

**Metodi interessati:**
- `on_play_click` (linea ~172)
- `on_last_game_click` (linea ~188)
- `on_leaderboard_click` (linea ~202)
- `on_profile_menu_click` (linea ~216)
- `on_options_click` (linea ~230)
- `on_exit_click` (linea ~244)

**Pattern da applicare a TUTTI i metodi:**

```python
def on_play_click(self, event: wx.CommandEvent) -> None:
    """Handle "Gioca al solitario classico" button click.
    
    🆕 v3.5.1: Plays UI_BUTTON_CLICK sound before action.
    """
    # ✨ NUOVO: Play button click sound
    if self.audio_manager:
        from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
        self.audio_manager.play_event(AudioEvent(
            event_type=AudioEventType.UI_BUTTON_CLICK
        ))
    
    # Azione originale
    if self.controller:
        self.controller.start_gameplay()
```

**⚠️ IMPORTANTE:** Applicare lo stesso pattern a **tutti e 6 i metodi** click:
- Stesso codice audio in cima al metodo
- Mantenere logica esistente intatta

---

### Fase 2: Passare AudioManager a MenuPanel

**File:** `acs_wx.py`

**Posizione:** Linea ~1021 (dentro `on_init` callback in `run()`)

#### 2.1 Modificare Creazione MenuPanel

```python
# Create panels as children of frame.panel_container
menu_panel = MenuPanel(
    parent=self.frame.panel_container,
    controller=self,
    audio_manager=self.audio_manager  # ← AGGIUNGERE
)
gameplay_panel = GameplayPanel(
    parent=self.frame.panel_container,
    controller=self
)
```

---

### Fase 3: Modifica OptionsDialog

**File:** `src/infrastructure/ui/options_dialog.py`

#### 3.1 Aggiornare Costruttore

**Posizione:** Linea ~101 (`__init__`)

```python
def __init__(
    self,
    parent: wx.Window,
    controller: OptionsWindowController,
    screen_reader: Optional['ScreenReader'] = None,
    audio_manager=None,  # ← AGGIUNGERE
    title: str = "Opzioni di gioco",
    size: tuple = (600, 700)
):
    """Initialize OptionsDialog with native wx widgets.
    
    Args:
        parent: Parent window (typically main frame)
        controller: OptionsWindowController instance
        screen_reader: ScreenReader for optional TTS feedback
        audio_manager: Optional AudioManager for sound effects (v3.5.1)
        title: Dialog title
        size: Dialog size in pixels
    """
    super().__init__(
        parent=parent,
        title=title,
        size=size,
        style=wx.DEFAULT_DIALOG_STYLE
    )
    
    self.options_controller = controller
    self.screen_reader = screen_reader
    self.audio_manager = audio_manager  # ← AGGIUNGERE
    
    # Create UI...
    self._create_ui()
    self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
    self.Centre()
```

#### 3.2 Aggiungere Eventi Audio su Widget Change

**Posizione:** Linea ~420 (`on_setting_changed`)

**⚠️ ATTENZIONE:** Gestione differenziata per tipo di setting.

```python
def on_setting_changed(self, event: wx.Event) -> None:
    """Handle any setting change from widgets.
    
    🆕 v3.5.1: Plays audio feedback for setting changes.
    """
    # ✨ NUOVO: Determina tipo di evento audio in base al widget
    event_obj = event.GetEventObject()
    
    # Salva vecchio valore difficulty per rilevare cambio preset
    old_difficulty = self.options_controller.settings.difficulty_level
    
    # Update GameSettings from current widget values
    self._save_widgets_to_settings()
    
    # Determine audio event type based on widget
    if self.audio_manager:
        from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
        
        # Difficulty change triggers SETTING_LEVEL_CHANGED (cambio preset)
        if event_obj == self.difficulty_radio:
            new_difficulty = self.options_controller.settings.difficulty_level
            if new_difficulty != old_difficulty:
                self.audio_manager.play_event(AudioEvent(
                    event_type=AudioEventType.SETTING_LEVEL_CHANGED
                ))
        
        # Timer combo triggers SETTING_VOLUME_CHANGED (metafora: slider temporale)
        elif event_obj == self.timer_combo:
            self.audio_manager.play_event(AudioEvent(
                event_type=AudioEventType.SETTING_VOLUME_CHANGED
            ))
        
        # CheckBox triggers SETTING_SWITCH_ON/OFF
        elif isinstance(event_obj, wx.CheckBox):
            is_checked = event_obj.GetValue()
            event_type = (AudioEventType.SETTING_SWITCH_ON if is_checked 
                         else AudioEventType.SETTING_SWITCH_OFF)
            self.audio_manager.play_event(AudioEvent(event_type=event_type))
        
        # Altri widget (RadioBox) triggers SETTING_CHANGED generico
        else:
            self.audio_manager.play_event(AudioEvent(
                event_type=AudioEventType.SETTING_CHANGED
            ))
    
    # ✅ FIX BUG #67: Special handling for difficulty change
    if event_obj == self.difficulty_radio:
        preset = self.options_controller.settings.get_current_preset()
        preset.apply_to(self.options_controller.settings)
        self._load_settings_to_widgets()
        self._update_widget_lock_states()
        
        if self.screen_reader and self.screen_reader.tts:
            locked_count = len(preset.get_locked_options())
            self.screen_reader.tts.speak(
                f"{preset.name} applicato. {locked_count} opzioni bloccate.",
                interrupt=True
            )
    
    # Mark controller as dirty
    if self.options_controller.state == "OPEN_CLEAN":
        self.options_controller.state = "OPEN_DIRTY"
    
    event.Skip()
```

#### 3.3 Aggiungere Evento Audio su Salva

**Posizione:** Linea ~477 (`on_save_click`)

```python
def on_save_click(self, event: wx.CommandEvent) -> None:
    """Handle Save button click.
    
    🆕 v3.5.1: Plays SETTING_SAVED sound before closing.
    """
    # ✨ NUOVO: Play save confirmation sound
    if self.audio_manager:
        from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
        self.audio_manager.play_event(AudioEvent(
            event_type=AudioEventType.SETTING_SAVED
        ))
    
    msg = self.options_controller.save_and_close()
    
    if self.screen_reader and self.screen_reader.tts:
        self.screen_reader.tts.speak(msg, interrupt=True)
    
    self.EndModal(wx.ID_OK)
```

#### 3.4 Aggiungere Evento Audio su Annulla

**Posizione:** Linea ~492 (`on_cancel_click`)

```python
def on_cancel_click(self, event: wx.CommandEvent) -> None:
    """Handle Cancel button click.
    
    🆕 v3.5.1: Plays UI_CANCEL sound before closing.
    """
    # ✨ NUOVO: Play cancel sound
    if self.audio_manager:
        from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
        self.audio_manager.play_event(AudioEvent(
            event_type=AudioEventType.UI_CANCEL
        ))
    
    msg = self.options_controller.discard_and_close()
    
    if self.screen_reader and self.screen_reader.tts:
        self.screen_reader.tts.speak(msg, interrupt=True)
    
    self.EndModal(wx.ID_CANCEL)
```

---

### Fase 4: Passare AudioManager a OptionsDialog

**File:** `acs_wx.py`

**Posizione:** Linea ~538 (`show_options` metodo)

#### 4.1 Modificare Creazione OptionsDialog

```python
def show_options(self) -> None:
    """Show options window using OptionsDialog with native wx widgets.
    
    🆕 v3.5.1: Passes audio_manager for sound effects.
    """
    from src.infrastructure.ui.options_dialog import OptionsDialog
    
    self.is_options_mode = True
    
    # Initialize controller state
    open_msg = self.gameplay_controller.options_controller.open_window()
    if self.screen_reader:
        self.screen_reader.tts.speak(open_msg, interrupt=True)
        wx.MilliSleep(500)
    
    log.dialog_shown("options", "Impostazioni di Gioco")
    
    # Create and show modal options dialog
    dlg = OptionsDialog(
        parent=self.frame,
        controller=self.gameplay_controller.options_controller,
        screen_reader=self.screen_reader,
        audio_manager=self.audio_manager  # ← AGGIUNGERE
    )
    result = dlg.ShowModal()
    
    # Log dialog closing
    result_str = "saved" if result == wx.ID_OK else "cancelled"
    log.dialog_closed("options", result_str)
    
    dlg.Destroy()
    self.is_options_mode = False
```

---

## 🧪 Testing Plan

### Test Manuali Menu Principale

1. **Test Navigazione Pulsanti**
   ```
   AZIONE: Premi TAB ripetutamente
   ASPETTATO: 
   - TTS legge nome pulsante (comportamento esistente)
   - Suono UI_BUTTON_HOVER ad ogni focus (NUOVO)
   ```

2. **Test Click Pulsante Gioca**
   ```
   AZIONE: Focus su "Gioca al solitario" → ENTER
   ASPETTATO:
   - Suono UI_BUTTON_CLICK (NUOVO)
   - Avvio gameplay (comportamento esistente)
   ```

3. **Test Click Pulsante Opzioni**
   ```
   AZIONE: Focus su "Opzioni di gioco" → ENTER
   ASPETTATO:
   - Suono UI_BUTTON_CLICK (NUOVO)
   - Apertura finestra opzioni (comportamento esistente)
   ```

4. **Test Altri Pulsanti**
   - Ultima Partita → UI_BUTTON_CLICK
   - Leaderboard → UI_BUTTON_CLICK
   - Gestione Profili → UI_BUTTON_CLICK
   - Esci dal gioco → UI_BUTTON_CLICK

### Test Manuali Finestra Opzioni

5. **Test Cambio Difficoltà (Preset)**
   ```
   AZIONE: Cambia livello difficoltà (es. da 1 a 5)
   ASPETTATO:
   - Suono SETTING_LEVEL_CHANGED (NUOVO)
   - TTS annuncia preset applicato (comportamento esistente)
   - Widget bloccati/sbloccati (comportamento esistente)
   ```

6. **Test Toggle CheckBox**
   ```
   AZIONE: Focus su "Suggerimenti comandi" → SPACE (toggle)
   ASPETTATO:
   - Suono SETTING_SWITCH_ON (se checked) o SETTING_SWITCH_OFF (se unchecked) (NUOVO)
   - Stato checkbox cambia (comportamento esistente)
   ```

7. **Test Cambio RadioBox**
   ```
   AZIONE: Cambia "Tipo Mazzo" da Francese a Napoletano
   ASPETTATO:
   - Suono SETTING_CHANGED (NUOVO)
   - Valore aggiornato (comportamento esistente)
   ```

8. **Test Cambio Timer**
   ```
   AZIONE: Apri ComboBox timer → Cambia valore
   ASPETTATO:
   - Suono SETTING_VOLUME_CHANGED (NUOVO)
   - Durata timer aggiornata (comportamento esistente)
   ```

9. **Test Salvataggio**
   ```
   AZIONE: Modifica impostazione → Click "Salva modifiche"
   ASPETTATO:
   - Suono SETTING_SAVED (NUOVO)
   - TTS "Impostazioni salvate" (comportamento esistente)
   - Dialog chiuso con wx.ID_OK
   ```

10. **Test Annullamento**
    ```
    AZIONE: Modifica impostazione → Click "Annulla modifiche"
    ASPETTATO:
    - Suono UI_CANCEL (NUOVO)
    - TTS "Modifiche annullate" (comportamento esistente)
    - Dialog chiuso con wx.ID_CANCEL
    - Settings ripristinati (rollback)
    ```

11. **Test ESC con Modifiche**
    ```
    AZIONE: Modifica impostazione → ESC → "Salva" nella conferma
    ASPETTATO:
    - Dialog conferma (comportamento esistente)
    - Suono SETTING_SAVED se si salva (NUOVO)
    - Suono UI_CANCEL se si annulla (NUOVO)
    ```

### Test Unitari (Opzionali)

**File:** `tests/infrastructure/ui/test_menu_panel_audio.py` (NUOVO)

```python
def test_menu_button_focus_plays_hover_sound(mock_audio_manager):
    """Test that focusing a menu button plays UI_BUTTON_HOVER."""
    # Setup
    panel = MenuPanel(parent, controller, audio_manager=mock_audio_manager)
    btn = panel.FindWindowByLabel("Gioca al solitario classico")
    
    # Action
    btn.SetFocus()
    
    # Assert
    assert mock_audio_manager.play_event.called
    event = mock_audio_manager.play_event.call_args[0][0]
    assert event.event_type == AudioEventType.UI_BUTTON_HOVER

def test_menu_button_click_plays_click_sound(mock_audio_manager):
    """Test that clicking a menu button plays UI_BUTTON_CLICK."""
    # Similar pattern...
```

**File:** `tests/infrastructure/ui/test_options_dialog_audio.py` (NUOVO)

```python
def test_options_save_plays_saved_sound(mock_audio_manager):
    """Test that clicking Save button plays SETTING_SAVED."""
    # Similar pattern...
```

---

## 📊 Mappatura Completa Eventi Audio UI

| Interfaccia | Azione Utente | Evento Audio | File Wav |
|-------------|---------------|--------------|----------|
| **Menu Principale** | | | |
| | Focus pulsante (TAB) | `UI_BUTTON_HOVER` | `ui/button_hover.wav` |
| | Click pulsante (ENTER) | `UI_BUTTON_CLICK` | `ui/button_click.wav` |
| **Finestra Opzioni** | | | |
| | Cambio difficoltà | `SETTING_LEVEL_CHANGED` | `ui/focus_change.wav` |
| | Cambio timer (ComboBox) | `SETTING_VOLUME_CHANGED` | `ui/focus_change.wav` |
| | Toggle CheckBox ON | `SETTING_SWITCH_ON` | `ui/button_click.wav` |
| | Toggle CheckBox OFF | `SETTING_SWITCH_OFF` | `ui/button_hover.wav` |
| | Cambio RadioBox generico | `SETTING_CHANGED` | `ui/focus_change.wav` |
| | Click Salva | `SETTING_SAVED` | `ui/select.wav` |
| | Click Annulla / ESC | `UI_CANCEL` | `ui/cancel.wav` |

---

## 📝 Note Implementative

### Import Statement Pattern
Per evitare import circolari, usare sempre import locali:

```python
# ❌ NON fare import a livello modulo
from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType

# ✅ Fare import locale dentro metodi
def on_button_click(self, event):
    if self.audio_manager:
        from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
        self.audio_manager.play_event(...)
```

### Null Safety Pattern
Sempre verificare presenza `audio_manager` prima di usarlo:

```python
# ✅ Safe pattern
if self.audio_manager:
    self.audio_manager.play_event(...)

# ❌ Unsafe - causa AttributeError se None
self.audio_manager.play_event(...)
```

### Retrocompatibilità
Tutti i parametri `audio_manager` sono **opzionali** (`=None`):
- Se non passato, UI funziona senza audio (comportamento pre-v3.5.1)
- Se passato, audio attivo
- Mantiene compatibilità con test esistenti che non passano audio_manager

---

## 🔄 Checklist Implementazione

### MenuPanel
- [ ] Aggiornare costruttore con `audio_manager` parameter
- [ ] Aggiungere import locali in `on_button_focus`
- [ ] Play `UI_BUTTON_HOVER` in `on_button_focus`
- [ ] Aggiungere import locali in tutti i metodi `on_*_click`
- [ ] Play `UI_BUTTON_CLICK` in `on_play_click`
- [ ] Play `UI_BUTTON_CLICK` in `on_last_game_click`
- [ ] Play `UI_BUTTON_CLICK` in `on_leaderboard_click`
- [ ] Play `UI_BUTTON_CLICK` in `on_profile_menu_click`
- [ ] Play `UI_BUTTON_CLICK` in `on_options_click`
- [ ] Play `UI_BUTTON_CLICK` in `on_exit_click`
- [ ] Passare `audio_manager` in `acs_wx.py` (linea ~1021)

### OptionsDialog
- [ ] Aggiornare costruttore con `audio_manager` parameter
- [ ] Aggiungere logica differenziata in `on_setting_changed`
- [ ] Play `SETTING_LEVEL_CHANGED` per cambio difficoltà
- [ ] Play `SETTING_VOLUME_CHANGED` per cambio timer
- [ ] Play `SETTING_SWITCH_ON/OFF` per CheckBox
- [ ] Play `SETTING_CHANGED` per altri RadioBox
- [ ] Play `SETTING_SAVED` in `on_save_click`
- [ ] Play `UI_CANCEL` in `on_cancel_click`
- [ ] Passare `audio_manager` in `acs_wx.py` (linea ~550)

### Testing
- [ ] Test manuale menu: navigazione pulsanti
- [ ] Test manuale menu: click tutti i pulsanti
- [ ] Test manuale opzioni: cambio difficoltà
- [ ] Test manuale opzioni: toggle CheckBox
- [ ] Test manuale opzioni: cambio RadioBox
- [ ] Test manuale opzioni: cambio timer
- [ ] Test manuale opzioni: salvataggio
- [ ] Test manuale opzioni: annullamento
- [ ] Verifica assenza regressioni UI esistente
- [ ] Verifica retrocompatibilità (UI senza audio_manager funziona)

---

## 🎬 Risultato Atteso

Dopo implementazione:

1. **Menu Principale**: Feedback sonoro completo durante navigazione e selezione
2. **Finestra Opzioni**: Feedback sonoro differenziato per tipo di impostazione
3. **UX Coerente**: Audio + TTS lavorano insieme (complementari, non sovrapposti)
4. **Accessibilità**: Utenti ciechi ricevono conferma immediata delle azioni
5. **Retrocompatibilità**: Codice esistente continua a funzionare

**Versione Target:** v3.5.1  
**Stima Implementazione:** 1-2 ore  
**Rischio:** BASSO (modifiche isolate, pattern già testato in GameplayPanel)
