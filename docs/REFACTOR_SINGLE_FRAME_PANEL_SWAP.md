# 🔧 Piano Refactoring: Single Frame con Panel Swap Pattern

**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Issue**: Dual window architecture (2 GUI aperte contemporaneamente)  
**Versione Target**: v1.7.3 (MINOR - architecture refactoring)  
**Stima Totale**: 60 minuti (1 commit con 8 modifiche + testing)

---

## 📊 Executive Summary

### Problema Attuale

**Sintomo**: App mostra **2 finestre separate** all'avvio:

1. **SolitarioFrame** (400x300px, minimizzato)
   - Frame principale per eventi globali e timer
   - Contiene label statico "Frame principale wxPython"
   - Minimizzato alla taskbar ma visible

2. **MenuView** (600x400px, fully visible)
   - wx.Frame indipendente con pulsanti
   - "Gioca", "Opzioni", "Esci"
   - **TAB navigation non funziona** (pulsanti non navigabili)

**Root Cause**: Architettura **dual-frame** invece di **single-frame con panel swap**.

**Riferimenti Pattern**:
- [wxPython single frame multiple panels](web:69) - Soluzione Show/Hide pattern
- [wxPython panel swap tutorial](web:72) - Modular code organization
- [Hide/Show panel sizer issues](web:73) - Layout considerations

### Soluzione

**Pattern**: **Single Frame con Panel Swap** (standard wxPython best practice)

**Architettura Corretta**:

```
SolitarioFrame (400x300, visibile e centrato)
└── Panel Container (sizer)
    ├── MenuPanel (nascosto/visibile)
    ├── GameplayPanel (nascosto/visibile)
    └── [altri panel future]
```

**Vantaggi**:
- ✅ **Una sola finestra** visibile (no confusione)
- ✅ **TAB navigation** funziona automaticamente
- ✅ **Focus management** gestito da wxPython
- ✅ **Sizer corretto** per resize/layout
- ✅ **Pattern standard** wxPython

---

## 🔍 Analisi Dettagliata Architettura Corrente

### File Coinvolti

#### 1. `src/infrastructure/ui/basic_view.py`

**Classe**: `BasicView(wx.Frame)`

**Problema**: BasicView è un **wx.Frame** (finestra indipendente)

```python
class BasicView(wx.Frame):  # ❌ FRAME = NUOVA FINESTRA
    def __init__(self, parent, controller, title, size=(800, 600), **kwargs):
        super().__init__(parent, title=title, size=size, **kwargs)
        # ... setup panel/sizer
```

**Conseguenza**: Ogni view crea una **finestra separata**.

---

#### 2. `src/infrastructure/ui/menu_view.py`

**Classe**: `MenuView(BasicView)`

**Eredita da**: `BasicView` (che è un `wx.Frame`)

```python
class MenuView(BasicView):  # ❌ BasicView = wx.Frame
    def __init__(self, parent, controller, **kwargs):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Solitario Classico Accessibile - Menu",
            size=(600, 400),  # ❌ FINESTRA SEPARATA 600x400
            **kwargs
        )
```

**Conseguenza**: MenuView è una **finestra indipendente 600x400**.

---

#### 3. `src/infrastructure/ui/wx_frame.py`

**Classe**: `SolitarioFrame(wx.Frame)`

**Scopo Corrente**: Frame invisibile per eventi globali

```python
class SolitarioFrame(wx.Frame):
    def __init__(self, on_key_event=None, on_timer_tick=None, ...):
        super().__init__(
            parent=None,
            title="Solitario Classico Accessibile",
            size=(400, 300),  # ❌ FRAME SEPARATO 400x300
            style=wx.DEFAULT_FRAME_STYLE
        )
        # ... setup panel statico con label
        self.Iconize()  # ❌ MINIMIZZA MA RESTA VISIBLE
```

**Problema**: Frame minimizzato ma ancora visibile in taskbar.

---

#### 4. `src/infrastructure/ui/view_manager.py`

**Classe**: `ViewManager`

**Metodo**: `push_view(view_name)` - Crea **nuova finestra**

```python
class ViewManager:
    def push_view(self, view_name: str) -> None:
        """Push view onto stack."""
        view = self.view_factories[view_name](parent=None)  # ❌ parent=None = FINESTRA INDIPENDENTE
        self.views_stack.append(view)
        view.Show()  # ❌ MOSTRA FINESTRA SEPARATA
```

**Problema**: Ogni `push_view()` crea una **finestra wxPython indipendente**.

---

### Flow Attuale (ERRATO)

```
1. test.py: controller = SolitarioController()
   │
   └─> SolitarioFrame(400x300) creato e minimizzato
       └─> Panel statico con label

2. controller.run()
   │
   └─> ViewManager.push_view('menu')
       │
       └─> MenuView(parent=None, size=(600,400))  # ❌ NUOVA FINESTRA!
           └─> BasicView.__init__() 
               └─> wx.Frame.__init__()  # ❌ CREA FRAME SEPARATO
                   └─> Panel con pulsanti

3. Risultato: 2 FINESTRE APERTE
   ├─> SolitarioFrame (minimizzato, visible in taskbar)
   └─> MenuView (fully visible, 600x400)
```

---

## 🎯 Architettura Target (CORRETTA)

### Pattern: Single Frame con Panel Container

**Riferimento**: [wxPython One Frame Multiple Panels](web:72)

**Architettura**:

```
SolitarioFrame (wx.Frame - UNICA FINESTRA)
│
├── panel_container (wx.Panel - layout container)
│   │
│   ├── BoxSizer (vertical)
│   │   │
│   │   ├── MenuPanel (wx.Panel) - Show/Hide
│   │   ├── GameplayPanel (wx.Panel) - Show/Hide
│   │   └── [altri panel future]
│   │
│   └── Regole Sizer:
│       ├── Tutti i panel aggiunti con flag=wx.EXPAND
│       ├── Solo 1 panel visible alla volta
│       └── Switch con panel.Hide() + panel.Show() + Layout()
│
├── Keyboard Events (EVT_CHAR_HOOK)
│   └─> Forwarded to active panel
│
└── Timer (wx.Timer)
    └─> controller._on_timer_tick()
```

**Componenti**:

1. **SolitarioFrame**: Unica finestra visible (400x300, centrata)
2. **Panel Container**: wx.Panel per contenere view panel
3. **View Panels**: wx.Panel (NON wx.Frame) per menu/gameplay
4. **ViewManager**: Gestisce Show/Hide dei panel

---

### Flow Target (CORRETTO)

```
1. test.py: controller = SolitarioController()
   │
   └─> SolitarioFrame(400x300) creato e visibile
       │
       ├─> panel_container (wx.Panel)
       │   └─> BoxSizer verticale (vuoto)
       │
       ├─> Timer setup
       └─> Event bindings

2. controller.run()
   │
   └─> ViewManager.register_panels(frame.panel_container)
   │   ├─> MenuPanel creato (parent=panel_container)
   │   ├─> GameplayPanel creato (parent=panel_container)
   │   └─> Tutti aggiunti al sizer
   │
   └─> ViewManager.show_panel('menu')
       ├─> MenuPanel.Show()
       ├─> GameplayPanel.Hide()
       └─> panel_container.Layout()

3. Risultato: 1 FINESTRA, PANEL SWAP INTERNO
   └─> SolitarioFrame (visible, centrato)
       └─> MenuPanel visibile (pulsanti navigabili)
```

---

## 🛠️ Implementazione: 8 Modifiche + Testing

### MODIFICA 1: Refactor `BasicView` → `BasicPanel`

**File**: `src/infrastructure/ui/basic_view.py`

**Cambiamento**: `BasicView(wx.Frame)` → `BasicPanel(wx.Panel)`

**PRIMA** (linea ~34):
```python
class BasicView(wx.Frame):
    """Base class for application views (hs_deckmanager pattern)."""
    
    def __init__(
        self,
        parent: Optional[wx.Frame],  # ❌ Parent opzionale
        controller: Optional[object],
        title: str,  # ❌ Title per Frame
        size: tuple = (800, 600),  # ❌ Size per Frame
        **kwargs
    ):
        super().__init__(parent, title=title, size=size, **kwargs)  # ❌ wx.Frame
        
        self.controller = controller
        self.screen_reader = controller.screen_reader if controller else None
        
        # Setup panel and sizer
        self.panel = wx.Panel(self)  # ❌ Panel DENTRO Frame
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)
        
        # Bind events
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        
        # Template method
        self.init_ui_elements()
        
        self.Layout()
        self.Centre()  # ❌ Centre frame
```

**DOPO**:
```python
class BasicPanel(wx.Panel):  # ✅ wx.Panel invece di wx.Frame
    """Base class for application panels (single-frame pattern).
    
    All view panels inherit from this. Provides:
    - Automatic sizer setup
    - Controller reference
    - Screen reader access
    - Template method for UI initialization
    
    Note:
        This is a wx.Panel, not wx.Frame. All panels share the same
        parent frame and are swapped via Show/Hide by ViewManager.
    """
    
    def __init__(
        self,
        parent: wx.Panel,  # ✅ Parent OBBLIGATORIO (panel_container)
        controller: object,  # ✅ Controller OBBLIGATORIO
        **kwargs
    ):
        """Initialize BasicPanel.
        
        Args:
            parent: Parent panel container (from SolitarioFrame)
            controller: Application controller
            **kwargs: Additional wx.Panel arguments
        """
        super().__init__(parent, **kwargs)  # ✅ wx.Panel init
        
        # Store references
        self.controller = controller
        self.screen_reader = controller.screen_reader if controller else None
        
        # Setup sizer (no nested panel needed)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        # Bind keyboard events (EVT_CHAR_HOOK for panel)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        
        # Template method: Let subclass add UI
        self.init_ui_elements()
        
        # Apply layout
        self.Layout()
    
    def init_ui_elements(self) -> None:
        """Override in subclass to add UI elements."""
        pass
    
    def on_key_down(self, event: wx.KeyEvent) -> None:
        """Handle keyboard events (override in subclass)."""
        event.Skip()
    
    def on_focus(self, event: wx.FocusEvent) -> None:
        """Handle focus events (override in subclass)."""
        event.Skip()
    
    # ❌ RIMUOVI on_close() - Panel non ha EVT_CLOSE
    
    def announce(self, message: str, interrupt: bool = False) -> None:
        """Announce via TTS."""
        if self.screen_reader:
            self.screen_reader.tts.speak(message, interrupt=interrupt)


# ✅ AGGIORNA __all__
__all__ = ['BasicPanel']  # Cambiato da BasicView
```

**Rationale**:
- `wx.Panel` non crea finestra separata
- Parent diventa obbligatorio (panel_container)
- Rimosso `title` e `size` (gestiti dal Frame)
- Rimosso `Centre()` (panel non si centra)
- Rimosso `on_close()` (panel non si chiude)

---

### MODIFICA 2: Refactor `MenuView` → `MenuPanel`

**File**: `src/infrastructure/ui/menu_view.py`

**PRIMA** (linea ~23-83):
```python
from .basic_view import BasicView

class MenuView(BasicView):  # ❌ BasicView = wx.Frame
    def __init__(self, parent, controller, **kwargs):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Solitario Classico Accessibile - Menu",  # ❌ Title
            size=(600, 400),  # ❌ Size
            **kwargs
        )
    
    def init_ui_elements(self) -> None:
        # Title label
        title = wx.StaticText(self.panel, label="Menu Principale")  # ❌ self.panel
        # ... (pulsanti)
        self.sizer.Add(title, ...)
        # ...
```

**DOPO**:
```python
from .basic_panel import BasicPanel  # ✅ Cambiato import

class MenuPanel(BasicPanel):  # ✅ BasicPanel = wx.Panel
    """Main menu panel with native buttons (single-frame pattern).
    
    Displays menu options as wx.Button widgets. Part of single-frame
    architecture - shown/hidden by ViewManager.
    """
    
    def __init__(self, parent: wx.Panel, controller, **kwargs):
        """Initialize MenuPanel.
        
        Args:
            parent: Panel container from SolitarioFrame
            controller: Application controller
        """
        super().__init__(parent=parent, controller=controller, **kwargs)
    
    def init_ui_elements(self) -> None:
        """Create menu buttons."""
        # Title label (no self.panel - this IS the panel)
        title = wx.StaticText(self, label="Menu Principale")  # ✅ self invece di self.panel
        title.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.sizer.Add(title, flag=wx.CENTER | wx.TOP, border=20)
        
        # Buttons
        btn_play = wx.Button(self, label="Gioca al solitario classico")  # ✅ parent=self
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_click)
        btn_play.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        btn_options = wx.Button(self, label="Opzioni di gioco")
        btn_options.Bind(wx.EVT_BUTTON, self.on_options_click)
        btn_options.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        btn_exit = wx.Button(self, label="Esci dal gioco")
        btn_exit.Bind(wx.EVT_BUTTON, self.on_exit_click)
        btn_exit.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        # Layout
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        for btn in [btn_play, btn_options, btn_exit]:
            btn_sizer.Add(btn, 0, wx.ALL | wx.EXPAND, 20)
        
        self.sizer.Add(btn_sizer, 1, wx.ALIGN_CENTER)
        
        # Set initial focus
        btn_play.SetFocus()
        self.announce("Menu principale. 3 opzioni disponibili.", interrupt=True)
    
    # ... (on_button_focus, on_play_click, etc. invariati)


__all__ = ['MenuPanel']  # ✅ Cambiato da MenuView
```

**Cambiamenti**:
- Import: `BasicView` → `BasicPanel`
- Classe: `MenuView` → `MenuPanel`
- Rimosso `title` e `size` da `__init__`
- `self.panel` → `self` (questo È il panel)
- `__all__`: `MenuView` → `MenuPanel`

---

### MODIFICA 3: Refactor `GameplayView` → `GameplayPanel`

**File**: `src/infrastructure/ui/gameplay_view.py`

**Stessa logica di MenuPanel**:

```python
from .basic_panel import BasicPanel  # ✅

class GameplayPanel(BasicPanel):  # ✅
    def __init__(self, parent: wx.Panel, controller, **kwargs):
        super().__init__(parent=parent, controller=controller, **kwargs)
    
    def init_ui_elements(self) -> None:
        # Gameplay UI (info text, status label, etc.)
        # Usa `self` come parent, non `self.panel`
        pass
    
    # ... (on_key_down per comandi gameplay)

__all__ = ['GameplayPanel']
```

---

### MODIFICA 4: Refactor `SolitarioFrame` - Aggiungi Panel Container

**File**: `src/infrastructure/ui/wx_frame.py`

**PRIMA** (linea ~115-147):
```python
class SolitarioFrame(wx.Frame):
    def __init__(self, on_key_event=None, on_timer_tick=None, ...):
        super().__init__(
            parent=None,
            id=wx.ID_ANY,
            title="Solitario Classico Accessibile",
            size=(400, 300),
            style=wx.DEFAULT_FRAME_STYLE
        )
        
        self.on_key_event = on_key_event
        self.on_timer_tick = on_timer_tick
        self.on_close = on_close
        
        self._timer = None
        
        # ❌ Panel statico con label
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        label = wx.StaticText(
            self.panel,
            label="Solitario Classico Accessibile\n\nFrame principale wxPython"
        )
        self.sizer.Add(label, 1, wx.ALIGN_CENTER)
        self.panel.SetSizer(self.sizer)
        
        # Bind events
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self.Bind(wx.EVT_CLOSE, self._on_close_event)
        
        # ❌ Show and minimize
        self.Centre()
        self.Show()
        self.Iconize()  # ❌ MINIMIZZA = VISIBLE IN TASKBAR
```

**DOPO**:
```python
class SolitarioFrame(wx.Frame):
    """Main application frame with panel container (single-frame pattern).
    
    Contains a panel_container that holds all view panels (menu, gameplay).
    Panels are swapped via Show/Hide by ViewManager.
    """
    
    def __init__(self, on_timer_tick=None, on_close=None, ...):
        """Initialize frame.
        
        Args:
            on_timer_tick: Timer callback
            on_close: Close callback
            
        Note:
            on_key_event removed - panels handle their own keyboard events.
        """
        super().__init__(
            parent=None,
            id=wx.ID_ANY,
            title="Solitario Classico Accessibile",
            size=(600, 450),  # ✅ Leggermente più grande per contenere panel
            style=wx.DEFAULT_FRAME_STYLE
        )
        
        # Callbacks (❌ rimosso on_key_event)
        self.on_timer_tick = on_timer_tick
        self.on_close = on_close
        
        self._timer = None
        
        # ✅ Panel container per view panels
        self.panel_container = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel_container.SetSizer(self.sizer)
        
        # ✅ NESSUN contenuto statico - ViewManager aggiungerà panel
        
        # Bind events
        # ❌ RIMOSSO EVT_CHAR_HOOK - Panel gestiscono propri eventi
        self.Bind(wx.EVT_CLOSE, self._on_close_event)
        
        # ✅ Show frame centrato (NON minimizzato)
        self.Centre()
        self.Show()
        # ❌ RIMOSSO Iconize() - Frame resta visibile
    
    # ❌ RIMOSSO _on_char_hook() - Non più necessario
    
    def _on_close_event(self, event: wx.CloseEvent) -> None:
        """Handle close."""
        if self._timer and self._timer.IsRunning():
            self.stop_timer()
        
        if self.on_close:
            self.on_close()
        
        self.Destroy()
    
    # ... (start_timer, stop_timer invariati)
```

**Cambiamenti Chiave**:
1. **Rimosso** `on_key_event` parameter e `_on_char_hook()` handler
2. **Rimosso** label statico - container vuoto
3. **Rinominato** `self.panel` → `self.panel_container` (chiarezza)
4. **Rimosso** `Iconize()` - frame resta visibile
5. **Size aumentato** a (600, 450) per contenere panel menu

---

### MODIFICA 5: Refactor `ViewManager` - Panel Swap Pattern

**File**: `src/infrastructure/ui/view_manager.py`

**PRIMA** (crea finestre separate):
```python
class ViewManager:
    def __init__(self, parent_frame: wx.Frame):
        self.parent_frame = parent_frame
        self.views_stack = []  # ❌ Stack di wx.Frame
        self.view_factories = {}  # Factory che crea Frame
    
    def register_view(self, name: str, factory: Callable) -> None:
        """Register view factory."""
        self.view_factories[name] = factory
    
    def push_view(self, view_name: str) -> None:
        """Push view onto stack."""
        view = self.view_factories[view_name](parent=None)  # ❌ parent=None
        self.views_stack.append(view)
        view.Show()  # ❌ Show finestra separata
    
    def pop_view(self) -> None:
        """Pop view from stack."""
        if self.views_stack:
            view = self.views_stack.pop()
            view.Close()  # ❌ Chiude finestra
```

**DOPO** (pattern Show/Hide panel):
```python
class ViewManager:
    """Manage panel visibility in single-frame architecture.
    
    Registers view panels and swaps them via Show/Hide.
    Only one panel is visible at a time.
    
    Reference:
    - https://stackoverflow.com/questions/31138061/wxpython-switch-between-multiple-panels
    """
    
    def __init__(self, parent_frame: wx.Frame):
        """Initialize ViewManager.
        
        Args:
            parent_frame: SolitarioFrame instance with panel_container
        """
        self.parent_frame = parent_frame
        self.panel_container = parent_frame.panel_container  # ✅ Container per panel
        self.sizer = self.panel_container.GetSizer()
        
        self.panels = {}  # ✅ Dict di wx.Panel (non stack)
        self.current_panel_name = None  # ✅ Nome panel corrente
    
    def register_panel(self, name: str, panel: wx.Panel) -> None:
        """Register panel and add to sizer.
        
        Args:
            name: Panel identifier ('menu', 'gameplay', etc.)
            panel: wx.Panel instance
        
        Note:
            Panel is added to sizer with wx.EXPAND flag and initially hidden.
        """
        self.panels[name] = panel
        self.sizer.Add(panel, 1, wx.EXPAND)  # ✅ EXPAND per fill container
        panel.Hide()  # ✅ Nascosto di default
    
    def show_panel(self, panel_name: str) -> None:
        """Show specified panel, hiding current.
        
        Args:
            panel_name: Name of panel to show
        
        Raises:
            KeyError: If panel_name not registered
        
        Note:
            Pattern:
            1. Hide current panel
            2. Show target panel
            3. Call Layout() to refresh UI
        """
        if panel_name not in self.panels:
            raise KeyError(f"Panel '{panel_name}' not registered")
        
        # Hide current panel
        if self.current_panel_name:
            current_panel = self.panels[self.current_panel_name]
            current_panel.Hide()
        
        # Show target panel
        target_panel = self.panels[panel_name]
        target_panel.Show()
        self.current_panel_name = panel_name
        
        # Refresh layout
        self.panel_container.Layout()  # ✅ CRITICAL per refresh UI
        self.parent_frame.Layout()
    
    def get_current_panel_name(self) -> Optional[str]:
        """Get name of currently visible panel."""
        return self.current_panel_name
    
    def get_panel(self, panel_name: str) -> Optional[wx.Panel]:
        """Get panel by name."""
        return self.panels.get(panel_name)
```

**Cambiamenti Chiave**:
1. **Stack → Dict**: Non serve stack, solo dict di panel
2. **Factory → Direct panel**: Panel creati direttamente in `test.py`
3. **push/pop → show_panel**: Logica semplificata Show/Hide
4. **Layout() critical**: Refresh UI dopo swap

---

### MODIFICA 6: Refactor `test.py` - SolitarioController Integration

**File**: `test.py`

**Sezione**: `run()` method (~linea 463-520)

**PRIMA** (crea finestre separate):
```python
def run(self) -> None:
    def on_init(app):
        # Create frame
        self.frame = SolitarioFrame(
            on_key_event=None,  # ❌
            on_timer_tick=self._on_timer_tick,
            on_close=self._on_frame_close
        )
        
        # ViewManager
        self.view_manager = ViewManager(self.frame)
        
        # ❌ Register VIEW FACTORIES (creano Frame)
        self.view_manager.register_view(
            'menu',
            lambda parent: MenuView(parent, controller=self)  # ❌ MenuView = Frame
        )
        self.view_manager.register_view(
            'gameplay',
            lambda parent: GameplayView(parent, controller=self)  # ❌ Frame
        )
        
        # ❌ Push initial menu (crea finestra separata)
        self.view_manager.push_view('menu')
        
        # Start timer
        self.frame.start_timer(1000)
    
    self.app = SolitarioWxApp(on_init_complete=on_init)
    self.app.MainLoop()
```

**DOPO** (single frame con panel swap):
```python
def run(self) -> None:
    """Start wxPython app with single-frame architecture."""
    
    def on_init(app):
        # ✅ Create frame with panel container
        self.frame = SolitarioFrame(
            on_timer_tick=self._on_timer_tick,
            on_close=self._on_frame_close
        )
        
        # ✅ Initialize dialog manager
        from src.infrastructure.ui.wx_dialog_provider import WxDialogProvider
        dialog_provider = WxDialogProvider(parent_frame=self.frame)
        self.dialog_manager = SolitarioDialogManager(dialog_provider=dialog_provider)
        
        # Pass to options controller
        self.gameplay_controller.options_controller.dialog_manager = self.dialog_manager
        
        # ✅ Initialize ViewManager
        self.view_manager = ViewManager(self.frame)
        
        # ✅ Create panels (NON finestre) e registra
        from src.infrastructure.ui.menu_panel import MenuPanel
        from src.infrastructure.ui.gameplay_panel import GameplayPanel
        
        menu_panel = MenuPanel(
            parent=self.frame.panel_container,  # ✅ Parent = container
            controller=self
        )
        gameplay_panel = GameplayPanel(
            parent=self.frame.panel_container,  # ✅ Parent = container
            controller=self
        )
        
        # ✅ Register panels
        self.view_manager.register_panel('menu', menu_panel)
        self.view_manager.register_panel('gameplay', gameplay_panel)
        
        # ✅ Show initial menu panel
        self.view_manager.show_panel('menu')
        
        # Start timer
        self.frame.start_timer(1000)
    
    self.app = SolitarioWxApp(on_init_complete=on_init)
    self.app.MainLoop()
```

**Cambiamenti**:
1. **Rimosso** `on_key_event` da SolitarioFrame
2. **Import**: `MenuView/GameplayView` → `MenuPanel/GameplayPanel`
3. **Creazione diretta** panel con `parent=frame.panel_container`
4. **register_panel** invece di `register_view`
5. **show_panel** invece di `push_view`

---

### MODIFICA 7: Update `start_gameplay()` e `return_to_menu()`

**File**: `test.py`

**Metodi**: `start_gameplay()` e `return_to_menu()` (~linea 171-195)

**PRIMA**:
```python
def start_gameplay(self) -> None:
    if self.view_manager:
        self.view_manager.push_view('gameplay')  # ❌ Crea finestra
        self.is_menu_open = False
        # ...

def return_to_menu(self) -> None:
    if self.view_manager:
        self.view_manager.pop_view()  # ❌ Chiude finestra
        self.is_menu_open = True
        # ...
```

**DOPO**:
```python
def start_gameplay(self) -> None:
    """Switch from menu to gameplay panel."""
    if self.view_manager:
        self.view_manager.show_panel('gameplay')  # ✅ Swap panel
        self.is_menu_open = False
        # Initialize game
        self.engine.reset_game()
        self.engine.new_game()
        self._timer_expired_announced = False
        
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Nuova partita avviata! Usa H per l'aiuto comandi.",
                interrupt=True
            )

def return_to_menu(self) -> None:
    """Switch from gameplay to menu panel."""
    if self.view_manager:
        self.view_manager.show_panel('menu')  # ✅ Swap panel
        self.is_menu_open = True
        
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Ritorno al menu di gioco.",
                interrupt=True
            )
```

---

### MODIFICA 8: Update Imports in `__init__.py` Files

**File**: `src/infrastructure/ui/__init__.py`

**PRIMA**:
```python
from .basic_view import BasicView
from .menu_view import MenuView
from .gameplay_view import GameplayView

__all__ = ['BasicView', 'MenuView', 'GameplayView', ...]
```

**DOPO**:
```python
from .basic_panel import BasicPanel
from .menu_panel import MenuPanel
from .gameplay_panel import GameplayPanel

__all__ = ['BasicPanel', 'MenuPanel', 'GameplayPanel', ...]
```

---

## ✅ Acceptance Criteria

### Funzionalità

- [ ] **Una sola finestra** visibile all'avvio (600x450, centrata)
- [ ] Menu panel visibile con 3 pulsanti
- [ ] **TAB navigation** funziona tra pulsanti
- [ ] **ENTER** su "Gioca" → Swap a gameplay panel
- [ ] Gameplay panel visibile, menu panel nascosto
- [ ] **ESC** in gameplay → Dialog → Ritorno menu
- [ ] Menu panel visibile, gameplay panel nascosto
- [ ] **Timer tick** funziona senza crash
- [ ] **NVDA** annuncia pulsanti su focus

### Architettura

- [ ] `BasicPanel` è `wx.Panel` (non `wx.Frame`)
- [ ] `MenuPanel` eredita da `BasicPanel`
- [ ] `GameplayPanel` eredita da `BasicPanel`
- [ ] `SolitarioFrame` ha `panel_container` pubblico
- [ ] `ViewManager` usa `show_panel()` invece di `push_view()`
- [ ] Tutti i panel creati con `parent=frame.panel_container`
- [ ] `register_panel()` aggiunge a sizer con `wx.EXPAND`
- [ ] `show_panel()` chiama `Layout()` dopo swap

### Testing

- [ ] Import modules: OK
- [ ] App startup: 1 finestra visible
- [ ] Menu buttons clickable: OK
- [ ] TAB cycles through buttons: OK
- [ ] ENTER triggers correct action: OK
- [ ] Panel swap preserves focus: OK
- [ ] 30 secondi stabilità: OK

---

## 🧪 Testing Strategy

### Test 1: Import Validation

```bash
python -c "from src.infrastructure.ui.basic_panel import BasicPanel; print('✓ BasicPanel')"
python -c "from src.infrastructure.ui.menu_panel import MenuPanel; print('✓ MenuPanel')"
python -c "from src.infrastructure.ui.gameplay_panel import GameplayPanel; print('✓ GameplayPanel')"
python -c "from src.infrastructure.ui.view_manager import ViewManager; print('✓ ViewManager')"
python -c "from src.infrastructure.ui.wx_frame import SolitarioFrame; print('✓ SolitarioFrame')"
python -c "from test import SolitarioController; print('✓ test.py')"
```

### Test 2: Single Window Verification

```bash
python test.py

# Checklist visuale:
# 1. Conta finestre wxPython aperte
#    ✓ Deve essere 1 sola finestra (600x450, centrata)
#    ✓ Titolo: "Solitario Classico Accessibile"
# 
# 2. Verifica taskbar
#    ✓ Una sola icona presente
#    ✓ Nessuna finestra minimizzata
#
# 3. Verifica contenuto
#    ✓ Menu visibile con 3 pulsanti
#    ✓ "Gioca al solitario classico"
#    ✓ "Opzioni di gioco"
#    ✓ "Esci dal gioco"
```

### Test 3: TAB Navigation

```bash
python test.py

# Azioni:
# 1. Premi TAB
#    ✓ Focus si sposta su "Opzioni di gioco"
#    ✓ NVDA annuncia "Opzioni di gioco"
#
# 2. Premi TAB
#    ✓ Focus si sposta su "Esci dal gioco"
#    ✓ NVDA annuncia "Esci dal gioco"
#
# 3. Premi TAB
#    ✓ Focus torna a "Gioca al solitario classico"
#    ✓ Ciclo completo OK
```

### Test 4: Panel Swap Menu → Gameplay

```bash
python test.py

# Azioni:
# 1. Focus su "Gioca" (primo pulsante)
# 2. Premi ENTER
#    ✓ Menu panel nascosto
#    ✓ Gameplay panel visibile
#    ✓ NVDA annuncia "Nuova partita avviata!"
#    ✓ Finestra resta 600x450 (stessa dimensione)
#    ✓ Nessuna nuova finestra aperta
```

### Test 5: Panel Swap Gameplay → Menu

```bash
python test.py

# Azioni:
# 1. ENTER su "Gioca" → Entra gameplay
# 2. Premi ESC
#    ✓ Dialog conferma appare
# 3. Premi S (Sì)
#    ✓ Gameplay panel nascosto
#    ✓ Menu panel visibile
#    ✓ NVDA annuncia "Ritorno al menu"
#    ✓ Focus su primo pulsante "Gioca"
```

### Test 6: Timer Stability

```bash
python test.py

# Lascia app aperta per 30 secondi
# Verifica log:
#    ✓ Nessun AttributeError
#    ✓ Nessun crash timer
#    ✓ App responsive
```

### Test 7: Focus Preservation

```bash
python test.py

# Azioni:
# 1. TAB fino a "Opzioni"
# 2. Premi ENTER → Dialog opzioni
# 3. ESC → Chiude dialog
#    ✓ Focus torna su "Opzioni"
#    ✓ Menu panel ancora visibile
```

---

## 📝 Commit Strategy

### Commit Unico con Refactoring Completo

**Rationale**: Refactoring architetturale atomico (single frame) non può essere splittato senza rompere app.

```bash
# Stage tutti i file modificati
git add src/infrastructure/ui/basic_panel.py  # Rinominato da basic_view.py
git add src/infrastructure/ui/menu_panel.py   # Rinominato da menu_view.py
git add src/infrastructure/ui/gameplay_panel.py  # Rinominato da gameplay_view.py
git add src/infrastructure/ui/wx_frame.py
git add src/infrastructure/ui/view_manager.py
git add src/infrastructure/ui/__init__.py
git add test.py

# Rimuovi file vecchi
git rm src/infrastructure/ui/basic_view.py
git rm src/infrastructure/ui/menu_view.py
git rm src/infrastructure/ui/gameplay_view.py

git commit -m "refactor(ui): Migrate to single-frame panel-swap architecture

MAJOR REFACTORING: Fix dual-window issue with wxPython best practice.

Problem:
- Two separate windows at startup (SolitarioFrame + MenuView)
- MenuView as wx.Frame created independent window
- TAB navigation broken (buttons not focusable)
- Minimized frame visible in taskbar

Solution:
- Single-frame architecture with panel swap pattern
- All views are wx.Panel (not wx.Frame)
- Panels swap via Show/Hide in same frame
- ViewManager manages panel visibility

Architectural Changes:
1. BasicView(wx.Frame) → BasicPanel(wx.Panel)
   - Removed title, size, Centre(), on_close
   - Parent now mandatory (panel_container)
   - Removed nested self.panel (this IS the panel)

2. MenuView → MenuPanel (extends BasicPanel)
   - Creates buttons with parent=self
   - TAB navigation automatic
   - Focus management by wxPython

3. GameplayView → GameplayPanel (extends BasicPanel)
   - Same pattern as MenuPanel

4. SolitarioFrame refactored:
   - Added panel_container (wx.Panel) for views
   - Removed static label content
   - Removed Iconize() - frame stays visible
   - Removed EVT_CHAR_HOOK - panels handle own events
   - Size increased to (600, 450)

5. ViewManager refactored:
   - Stack replaced with dict of panels
   - push_view/pop_view → show_panel
   - Factory pattern → direct panel creation
   - Show/Hide pattern with Layout() refresh

6. SolitarioController (test.py):
   - Direct panel creation in run()
   - register_panel instead of register_view
   - show_panel instead of push_view
   - start_gameplay/return_to_menu use show_panel

Testing:
- Single window: OK (600x450, centered)
- TAB navigation: OK (cycles through buttons)
- Panel swap: OK (menu ↔ gameplay)
- Timer stability: OK (30+ seconds)
- NVDA accessibility: OK (announces buttons)
- Focus preservation: OK

References:
- https://stackoverflow.com/q/31138061 (panel swap pattern)
- https://stackoverflow.com/q/21899151 (modular code)
- wxPython best practices for single-frame apps

Fixes: Dual window issue, TAB navigation broken
Version: v1.7.3 (MINOR - architecture refactoring)"
```

---

## 🔍 Comandi Verifica Finali

```bash
# ════════════════════════════════════════════════════════════════
# VERIFICA 1: File rinominati
# ════════════════════════════════════════════════════════════════
ls -la src/infrastructure/ui/ | grep -E "(basic|menu|gameplay)"
# Output atteso:
# basic_panel.py (nuovo)
# menu_panel.py (nuovo)
# gameplay_panel.py (nuovo)
# basic_view.py (NON presente - rimosso)
# menu_view.py (NON presente - rimosso)
# gameplay_view.py (NON presente - rimosso)

# ════════════════════════════════════════════════════════════════
# VERIFICA 2: Import wx.Panel
# ════════════════════════════════════════════════════════════════
grep -n "class BasicPanel(wx.Panel)" src/infrastructure/ui/basic_panel.py
grep -n "class MenuPanel(BasicPanel)" src/infrastructure/ui/menu_panel.py
grep -n "class GameplayPanel(BasicPanel)" src/infrastructure/ui/gameplay_panel.py

# ════════════════════════════════════════════════════════════════
# VERIFICA 3: panel_container in SolitarioFrame
# ════════════════════════════════════════════════════════════════
grep -n "self.panel_container = wx.Panel" src/infrastructure/ui/wx_frame.py

# ════════════════════════════════════════════════════════════════
# VERIFICA 4: ViewManager.show_panel
# ════════════════════════════════════════════════════════════════
grep -n "def show_panel" src/infrastructure/ui/view_manager.py
grep -n "def register_panel" src/infrastructure/ui/view_manager.py

# ════════════════════════════════════════════════════════════════
# VERIFICA 5: test.py usage
# ════════════════════════════════════════════════════════════════
grep -n "MenuPanel" test.py
grep -n "GameplayPanel" test.py
grep -n "register_panel" test.py
grep -n "show_panel" test.py

# ════════════════════════════════════════════════════════════════
# VERIFICA 6: Rimossi riferimenti obsoleti
# ════════════════════════════════════════════════════════════════
grep -rn "BasicView" src/
grep -rn "MenuView" src/
grep -rn "push_view" src/
grep -rn "pop_view" src/
# Output atteso: 0 risultati (tutti rimossi)

# ════════════════════════════════════════════════════════════════
# VERIFICA 7: Full app test (manual)
# ════════════════════════════════════════════════════════════════
python test.py
# Checklist:
# - 1 finestra visible ✓
# - 600x450, centrata ✓
# - Menu con 3 pulsanti ✓
# - TAB navigation OK ✓
# - ENTER gioca → Gameplay ✓
# - ESC → Menu ✓
# - Timer 30+ sec OK ✓
```

---

## 📚 Riferimenti

### wxPython Documentation

- [Show/Hide panels pattern](https://stackoverflow.com/questions/31138061/wxpython-switch-between-multiple-panels)
- [One Frame Multiple Panels](https://stackoverflow.com/questions/21899151/wxpython-one-frame-multiple-panels-modularized-code)
- [Panel swap sizer issues](https://stackoverflow.com/questions/2562063/why-does-hideing-and-showing-panels-in-wxpython-result-in-the-sizer-changi)
- [wxPython multi-panel discussion](https://discuss.wxpython.org/t/showing-and-hiding-panels/19295)

### Pattern Best Practices

1. **Single Frame Rule**: wxPython app dovrebbe avere **un solo wx.Frame principale**
2. **Panel Container**: Frame contiene panel_container che ospita tutti i panel
3. **Show/Hide Pattern**: Swap panel con `panel.Hide()` + `panel.Show()` + `Layout()`
4. **Sizer wx.EXPAND**: Tutti i panel aggiunti con flag `wx.EXPAND` per fill container
5. **Layout() Critical**: Chiamare `Layout()` su container E frame dopo swap

---

## 🎯 Success Criteria

### Prima del Refactoring (BROKEN)

- ❌ 2 finestre aperte (SolitarioFrame + MenuView)
- ❌ TAB non naviga pulsanti
- ❌ Focus management broken
- ❌ Frame minimizzato visible in taskbar
- ❌ Architettura non standard

### Dopo il Refactoring (FIXED)

- ✅ 1 finestra visible (SolitarioFrame 600x450)
- ✅ TAB naviga pulsanti automaticamente
- ✅ Focus management gestito da wxPython
- ✅ Nessuna finestra minimizzata
- ✅ Architettura standard wxPython
- ✅ Panel swap fluido menu ↔ gameplay
- ✅ NVDA accessibility ottimale

---

**Fine Piano Refactoring**

**Prossimo Step**: Implementa 8 modifiche, testa, e commit refactoring completo.
