# TODO: Refactoring wxPython - Checklist Rapida

**Branch**: `copilot/remove-pygame-migrate-wxpython` (Issue #59)  
**Piano Completo**: `docs/IMPLEMENTATION_WX_REFACTORING_HS_PATTERN.md`  
**Pattern**: hs_deckmanager  
**Stima Totale**: 12 ore (2 giorni)

---

## 🚨 COMMIT 1: Fix Critico Frame Visibile (1.5h)

**File**: `src/infrastructure/ui/wx_frame.py`

### Modifiche

- [ ] **Line ~15**: Cambiare `size=(1, 1)` → `size=(400, 300)`
- [ ] **Line ~16**: Cambiare `style=wx.FRAME_NO_TASKBAR` → `style=wx.DEFAULT_FRAME_STYLE`
- [ ] **Aggiungere** dopo `__init__` body:
  - [ ] `self.Centre()`
  - [ ] `self.Show()`
  - [ ] `self.Iconize()`
- [ ] **Line ~30**: Cambiare `self.Bind(wx.EVT_KEY_DOWN, ...)` → `self.Bind(wx.EVT_CHAR_HOOK, ...)`
- [ ] **Aggiungere** setup panel:
  ```python
  self.panel = wx.Panel(self)
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  label = wx.StaticText(self.panel, label="Solitario Classico Accessibile\n\nFrame principale wxPython")
  self.sizer.Add(label, 1, wx.ALIGN_CENTER)
  self.panel.SetSizer(self.sizer)
  ```

### Testing

- [ ] Frame minimizzato visibile in taskbar
- [ ] Eventi tastiera catturati (testare con H, frecce, ESC)
- [ ] NVDA annuncia titolo frame su ALT+TAB focus
- [ ] ALT+F4 chiude app correttamente

### Commit

```bash
git add src/infrastructure/ui/wx_frame.py
git commit -m "feat(ui): Make SolitarioFrame visible and functional for OS focus

CRITICAL FIX: Previous 1x1px invisible frame was denied focus by OS.

Changes:
- Frame size: 1x1px → 400x300px
- Style: FRAME_NO_TASKBAR → DEFAULT_FRAME_STYLE  
- Add EVT_CHAR_HOOK for global keyboard capture
- Add Iconize() to minimize but maintain focus

Based on hs_deckmanager pattern. References: #59"
```

---

## 👨‍👩‍👧 COMMIT 2: Dialog Parent Hierarchy (1.5h)

**Files**: 
- `src/infrastructure/ui/dialogs/wx_dialog_provider.py`
- `test.py`

### Modifiche wx_dialog_provider.py

- [ ] **Line ~10**: Aggiungere parametro `parent_frame: Optional[wx.Frame]` al `__init__`
- [ ] **Line ~11**: Salvare `self.parent_frame = parent_frame`
- [ ] **Tutti i metodi dialog**:
  - [ ] `show_confirmation()`: Cambiare `parent=None` → `parent=self.parent_frame`
  - [ ] `show_info()`: Cambiare `parent=None` → `parent=self.parent_frame`
  - [ ] `show_statistics_report()`: Cambiare `parent=None` → `parent=self.parent_frame`
  - [ ] `show_options_window()`: Cambiare `parent=None` → `parent=self.parent_frame`
- [ ] **Aggiungere** `wx.Yield()` dopo ogni `dlg.Destroy()`

### Modifiche test.py

- [ ] **Line ~XX** (metodo `run` in `SolitarioController`):
  - [ ] Passare `parent_frame=self.frame` al constructor `WxDialogProvider`
  ```python
  dialog_provider = WxDialogProvider(parent_frame=self.frame)
  self.dialog_manager = SolitarioDialogManager(dialog_provider=dialog_provider, ...)
  ```

### Testing

- [ ] Dialog appare sopra frame (non separato in ALT+TAB)
- [ ] ESC chiude dialog e ritorna a frame
- [ ] TAB cicla pulsanti in dialog
- [ ] NVDA legge contenuto dialog automaticamente
- [ ] Focus ritorna a frame dopo chiusura dialog

### Commit

```bash
git add src/infrastructure/ui/dialogs/wx_dialog_provider.py test.py
git commit -m "feat(ui): Implement dialog parent hierarchy for modal behavior

Fix dialog appearing as separate windows in ALT+TAB.

Changes:
- WxDialogProvider: Add parent_frame parameter
- All dialogs: Use parent_frame instead of None
- Add wx.Yield() for event flush

Based on hs_deckmanager pattern. References: #59"
```

---

## 📋 COMMIT 3: ViewManager Stack Finestre (2h)

**File Nuovo**: `src/infrastructure/ui/view_manager.py`

### Implementazione

- [ ] **Creare file** `src/infrastructure/ui/view_manager.py`
- [ ] **Copiare** implementazione completa da piano (section "view_manager.py")
- [ ] **Verificare** import:
  ```python
  import wx
  from typing import List, Dict, Optional, Callable
  import logging
  ```

### Metodi da Implementare

- [ ] `__init__(parent_frame: wx.Frame)`
- [ ] `register_view(name: str, constructor: Callable)`
- [ ] `push_view(name: str, **kwargs) -> Optional[wx.Frame]`
- [ ] `pop_view() -> bool`
- [ ] `get_current_view() -> Optional[wx.Frame]`
- [ ] `clear_stack()`
- [ ] `__len__() -> int`

### Unit Tests

- [ ] **Creare** `tests/infrastructure/test_view_manager.py`
- [ ] Test: `test_register_view`
- [ ] Test: `test_push_view`
- [ ] Test: `test_pop_view`
- [ ] Test: `test_stack_depth`
- [ ] Test: `test_clear_stack`
- [ ] **Eseguire**: `pytest tests/infrastructure/test_view_manager.py -v`

### Commit

```bash
git add src/infrastructure/ui/view_manager.py tests/infrastructure/test_view_manager.py
git commit -m "feat(ui): Add ViewManager for multi-window stack management

Implement hs_deckmanager ViewManager pattern for LIFO window stack.

Features:
- register_view(): Factory pattern
- push_view(): Show new, hide previous
- pop_view(): Close current, restore previous

Tested with pytest. References: #59"
```

---

## 🏛️ COMMIT 4: BasicView Base Class (2h)

**File Nuovo**: `src/infrastructure/ui/basic_view.py`

### Implementazione

- [ ] **Creare file** `src/infrastructure/ui/basic_view.py`
- [ ] **Copiare** implementazione completa da piano (section "basic_view.py")
- [ ] **Verificare** import:
  ```python
  import wx
  from typing import Optional, Callable
  ```

### Struttura Class

- [ ] `class BasicView(wx.Frame)`
- [ ] `__init__` con parametri:
  - [ ] `parent: Optional[wx.Frame]`
  - [ ] `controller: Optional[object]`
  - [ ] `title: str`
  - [ ] `size: tuple`
- [ ] Setup automatico:
  - [ ] `self.panel = wx.Panel(self)`
  - [ ] `self.sizer = wx.BoxSizer(wx.VERTICAL)`
  - [ ] `self.panel.SetSizer(self.sizer)`
- [ ] Event bindings:
  - [ ] `self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)`
  - [ ] `self.Bind(wx.EVT_CLOSE, self.on_close)`
  - [ ] `self.Bind(wx.EVT_SET_FOCUS, self.on_focus)`
- [ ] Template methods:
  - [ ] `init_ui_elements()` - virtual (override in subclass)
  - [ ] `on_key_down(event)` - virtual
  - [ ] `on_focus(event)` - virtual
  - [ ] `on_close(event)` - virtual
  - [ ] `announce(message, interrupt)` - helper TTS

### Test Manuale

- [ ] **Creare** script test minimale:
  ```python
  from src.infrastructure.ui.basic_view import BasicView
  import wx
  
  class TestView(BasicView):
      def init_ui_elements(self):
          btn = wx.Button(self.panel, label="Test")
          self.sizer.Add(btn, flag=wx.ALL, border=10)
  
  app = wx.App()
  view = TestView(None, None, "Test", (400, 300))
  view.Show()
  app.MainLoop()
  ```
- [ ] Testare: Finestra visibile con pulsante
- [ ] Testare: Eventi tastiera catturati
- [ ] Testare: ESC chiude finestra

### Commit

```bash
git add src/infrastructure/ui/basic_view.py
git commit -m "feat(ui): Add BasicView base class for consistent view structure

Implement hs_deckmanager BasicView pattern for code reuse.

Features:
- Auto setup panel/sizer
- Template method: init_ui_elements()
- Event bindings: CHAR_HOOK, CLOSE, FOCUS
- TTS announce() helper

References: #59"
```

---

## 🎮 COMMIT 5: MenuView e GameplayView (3h)

**Files Nuovi**:
- `src/infrastructure/ui/menu_view.py`
- `src/infrastructure/ui/gameplay_view.py`

### Implementazione menu_view.py

- [ ] **Creare file** `src/infrastructure/ui/menu_view.py`
- [ ] **Import**:
  ```python
  from .basic_view import BasicView
  import wx
  ```
- [ ] **Class**: `class MenuView(BasicView)`
- [ ] **`__init__`**: Chiamare `super().__init__` con:
  - [ ] `title="Solitario Classico Accessibile - Menu"`
  - [ ] `size=(600, 400)`
- [ ] **`init_ui_elements()`**: Implementare UI:
  - [ ] Titolo: `wx.StaticText` con font bold 16pt
  - [ ] Pulsante "Gioca al solitario classico" → `on_play_click`
  - [ ] Pulsante "Opzioni di gioco" → `on_options_click`
  - [ ] Pulsante "Esci dal gioco" → `on_exit_click`
  - [ ] Bind `wx.EVT_SET_FOCUS` su ogni pulsante → `on_button_focus`
  - [ ] Layout verticale con border 20px
  - [ ] Focus iniziale su primo pulsante
  - [ ] Announce "Menu principale. 3 opzioni disponibili."
- [ ] **Metodi callback**:
  - [ ] `on_button_focus(event)`: Announce label pulsante
  - [ ] `on_play_click(event)`: Chiamare `self.controller.start_gameplay()`
  - [ ] `on_options_click(event)`: Chiamare `self.controller.show_options()`
  - [ ] `on_exit_click(event)`: Chiamare `self.controller.show_exit_dialog()`

### Implementazione gameplay_view.py

- [ ] **Creare file** `src/infrastructure/ui/gameplay_view.py`
- [ ] **Import**:
  ```python
  from .basic_view import BasicView
  import wx
  import time
  ```
- [ ] **Class**: `class GameplayView(BasicView)`
- [ ] **`__init__`**: 
  - [ ] Chiamare `super().__init__` con `title="Solitario - Partita in corso"`
  - [ ] Inizializzare `self.last_esc_time = 0`
- [ ] **`init_ui_elements()`**: Audiogame mode
  - [ ] Label semplice: "Partita in corso\n\nPremi H per comandi"
  - [ ] Nessun altro widget (audiogame puro)
- [ ] **`on_key_down(event)`**: Route eventi
  - [ ] Check `event.GetKeyCode() == wx.WXK_ESCAPE` → `_handle_esc(event)`
  - [ ] Altrimenti: `self.controller.gameplay_controller.handle_wx_key_event(event)`
- [ ] **`_handle_esc(event)`**: Double-ESC detection
  - [ ] Calcolare `current_time = time.time()`
  - [ ] Se `current_time - self.last_esc_time <= 2.0`:
    - [ ] Double-ESC: `self.announce("Uscita rapida!")`
    - [ ] Chiamare `self.controller.confirm_abandon_game(skip_dialog=True)`
    - [ ] Reset `self.last_esc_time = 0`
  - [ ] Altrimenti:
    - [ ] First ESC: Salvare `self.last_esc_time = current_time`
    - [ ] Chiamare `self.controller.show_abandon_game_dialog()`

### Testing

**MenuView**:
- [ ] TAB naviga tra pulsanti
- [ ] NVDA annuncia label su focus
- [ ] ENTER su pulsante trigger callback
- [ ] ESC chiude finestra (futuro: exit dialog)

**GameplayView**:
- [ ] Tasti 1-7 catturati
- [ ] H catturato (help)
- [ ] ESC singolo → dialog conferma
- [ ] ESC doppio (< 2 sec) → abandon immediato
- [ ] NVDA announcements funzionano

### Commit

```bash
git add src/infrastructure/ui/menu_view.py src/infrastructure/ui/gameplay_view.py
git commit -m "feat(ui): Add MenuView and GameplayView with native wx UI

Replace pygame virtual menu with wxPython button-based menu.

MenuView:
- wx.Button widgets (TAB navigable)
- NVDA announcements on focus
- Callbacks for play/options/exit

GameplayView:
- Audiogame mode (no visual UI)
- Full keyboard capture via EVT_CHAR_HOOK
- Double-ESC detection (2-second threshold)

References: #59"
```

---

## 🔗 COMMIT 6: Integrazione ViewManager in Controller (2h)

**File**: `test.py`

### Modifiche Class SolitarioController

- [ ] **Import** nuovi moduli:
  ```python
  from src.infrastructure.ui.view_manager import ViewManager
  from src.infrastructure.ui.menu_view import MenuView
  from src.infrastructure.ui.gameplay_view import GameplayView
  ```

- [ ] **`__init__`**: Aggiungere attributi
  - [ ] `self.view_manager: Optional[ViewManager] = None`

- [ ] **Metodo `run()`**: Modificare `on_init_complete`
  - [ ] Creare frame: `self.frame = SolitarioFrame(...)`
  - [ ] Cambiare `on_key_event=None` (eventi gestiti da view)
  - [ ] Creare ViewManager: `self.view_manager = ViewManager(self.frame)`
  - [ ] Registrare view:
    ```python
    self.view_manager.register_view(
        'menu',
        lambda parent: MenuView(parent, controller=self)
    )
    self.view_manager.register_view(
        'gameplay',
        lambda parent: GameplayView(parent, controller=self)
    )
    ```
  - [ ] Setup dialog manager con parent: `WxDialogProvider(parent_frame=self.frame)`
  - [ ] Push menu iniziale: `self.view_manager.push_view('menu')`

- [ ] **Nuovi metodi navigazione**:
  - [ ] `start_gameplay()`:
    ```python
    def start_gameplay(self):
        self.view_manager.push_view('gameplay')
        # ... init game engine ...
    ```
  - [ ] `return_to_menu()`:
    ```python
    def return_to_menu(self):
        self.view_manager.pop_view()
    ```
  - [ ] `show_exit_dialog()`:
    ```python
    def show_exit_dialog(self):
        result = self.dialog_manager.show_exit_app_prompt()
        if result:
            self.app.ExitMainLoop()
    ```
  - [ ] `show_abandon_game_dialog()`:
    ```python
    def show_abandon_game_dialog(self):
        result = self.dialog_manager.show_abandon_game_prompt()
        if result:
            self.return_to_menu()
    ```

- [ ] **Rimuovere**: Loop `pygame.event.get()` (se presente)

### Testing Integrazione Completa

- [ ] **Scenario 1**: Avvio app
  - [ ] App avvia con MenuView visibile
  - [ ] NVDA annuncia menu apertura
  
- [ ] **Scenario 2**: Navigazione menu → gameplay
  - [ ] TAB su "Gioca" + ENTER
  - [ ] GameplayView aperta
  - [ ] Menu nascosto
  
- [ ] **Scenario 3**: Gameplay → ESC → menu
  - [ ] ESC in gameplay
  - [ ] Dialog conferma abbandona
  - [ ] Conferma Sì
  - [ ] Ritorno a MenuView
  - [ ] GameplayView chiusa e destroyed
  
- [ ] **Scenario 4**: Dialog parent corretto
  - [ ] Dialog appaiono sopra view corrente
  - [ ] ALT+TAB mostra solo 1 finestra
  - [ ] ESC chiude dialog
  
- [ ] **Scenario 5**: NVDA accessibility
  - [ ] NVDA segue focus correttamente in ogni transizione
  - [ ] Announcements chiari per ogni azione
  
- [ ] **Scenario 6**: Timer gameplay
  - [ ] Timer tick continua durante gameplay
  - [ ] Timeout detection funziona

### Commit

```bash
git add test.py
git commit -m "feat(ui): Integrate ViewManager into main controller

Complete wxPython view system integration. Remove pygame event loop.

Changes:
- Add ViewManager instance to SolitarioController
- Register MenuView and GameplayView constructors
- Implement navigation methods: start_gameplay(), return_to_menu()
- Use wx.MainLoop() natively

Flow:
1. App init → MenuView shown
2. User "Gioca" → GameplayView pushed
3. User abandons → GameplayView popped, MenuView restored

Tested: Full menu → gameplay → menu cycle validated.

References: #59"
```

---

## ✅ Checklist Finale Post-Implementazione

### Funzionalità

- [ ] Frame wxPython riceve eventi tastiera al 100%
- [ ] Dialog box sono modal children (no ALT+TAB separato)
- [ ] Menu navigabile con TAB + ENTER
- [ ] Gameplay cattura tutti i 60+ comandi
- [ ] Timer timeout funziona con wx.Timer
- [ ] Double-ESC quick exit funziona
- [ ] Tutti i flussi esistenti preservati

### Accessibilità NVDA

- [ ] NVDA annuncia apertura app
- [ ] Menu pulsanti annunciati su focus (TAB)
- [ ] Gameplay comandi annunciati via TTS
- [ ] Dialog focus automatico e leggibili
- [ ] No conflitti hotkey NVDA
- [ ] Focus management corretto su transizioni

### Architettura

- [ ] Pattern hs_deckmanager implementato
- [ ] Clean Architecture preservata
- [ ] ViewManager per navigazione finestre
- [ ] BasicView riuso codice
- [ ] Zero import pygame in codice wx
- [ ] Tutti i file con type hints
- [ ] Docstring Google-style su classi/metodi nuovi

### Testing

- [ ] Unit tests ViewManager passano
- [ ] Test manuali 6 scenari completi
- [ ] Test NVDA tutti i flussi
- [ ] No regressioni vs branch main

### Documentazione

- [ ] Commit messages descrittivi (6 commit)
- [ ] Questo TODO completato e spuntato
- [ ] Piano completo (`IMPLEMENTATION_WX_REFACTORING_HS_PATTERN.md`) consultato

---

## 🚀 Ready for Merge Checklist

- [ ] Tutti i 6 commit pushati su branch `copilot/remove-pygame-migrate-wxpython`
- [ ] Testing completo (funzionale + NVDA + regressione)
- [ ] Nessun bug critico rilevato
- [ ] Documentazione aggiornata
- [ ] Code review (se richiesta)
- [ ] PR creato per merge in `main`

---

## 📞 Comandi Git Rapidi

```bash
# Controllo branch
git status
git branch

# Dopo ogni commit
git push origin copilot/remove-pygame-migrate-wxpython

# Verifica log commit
git log --oneline -6

# Testing
pytest tests/infrastructure/test_view_manager.py -v
python test.py

# PR finale
gh pr create --base main --head copilot/remove-pygame-migrate-wxpython \
  --title "feat: Complete wxPython refactoring (hs_deckmanager pattern)" \
  --body "Implements Issue #59. See docs/IMPLEMENTATION_WX_REFACTORING_HS_PATTERN.md"
```

---

**Fine TODO**

**Status**: ⏳ Pending Implementation  
**Progress**: 0/6 commits (0%)  
**Prossimo Step**: ➡️ COMMIT 1 (Fix Critico Frame)
