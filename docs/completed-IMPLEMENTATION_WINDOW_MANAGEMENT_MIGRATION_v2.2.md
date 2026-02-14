# Window Management Migration - Port da hs_deckmanager v2.2

## Metadata Documento
- **Versione Target**: 2.2.0
- **Branch**: `copilot/remove-pygame-migrate-wxpython`
- **Autore**: Assistente AI + Utente
- **Data Creazione**: 2026-02-14
- **Tipo Rilascio**: MINOR (architectural changes con backward compatibility)
- **Scopo**: Migrare sistema gestione finestre/dialog dal pattern attuale al pattern hs_deckmanager

---

## 📋 Executive Summary

### Problema Corrente

L'implementazione attuale (v2.1.0) presenta i seguenti problemi:

1. **Dialog modali creano nested event loops** - `ShowModal()` blocca event loop causando hang/timing issues
2. **Dependency injection mancante** - Componenti fortemente accoppiati, hard-coded dependencies
3. **Window management rudimentale** - `ViewManager` gestisce solo 2 panel (menu/gameplay), no gerarchia
4. **Dialog provider accoppiato** - `WxDialogProvider` instanziato direttamente in `test.py`, no IoC
5. **Factory pattern assente** - Creazione componenti UI sparsa nel codice, no centralizzazione
6. **Screen reader management inconsistente** - Passato manualmente a ogni componente

### Soluzione Target

Port del pattern architetturale da **hs_deckmanager** che fornisce:

1. ✅ **DependencyContainer** - IoC container per gestione centralizzata dipendenze
2. ✅ **WinController** - Manager gerarchico per finestre/dialog con parent stack
3. ✅ **ViewFactory + WidgetFactory** - Creazione centralizzata componenti UI
4. ✅ **Registration pattern** - Window classes registrate in dizionario `all_windows`
5. ✅ **Lazy initialization** - Finestre create on-demand, non all'avvio
6. ✅ **Parent hierarchy** - Stack-based parent tracking per navigation correct

### Benefici Attesi

- **Eliminazione nested loops** - Dialog non-blocking con callback pattern
- **Testabilità migliorata** - Dependency injection facilita mock/stub
- **Manutenibilità** - Factory centralizza creazione UI, modifiche in un posto solo
- **Scalabilità** - Facile aggiungere nuove finestre/dialog (register + create)
- **Separazione concerns** - Business logic (application) separata da UI (infrastructure)

---

## 🎯 Obiettivi Implementazione

### Obiettivo 1: Infrastructure Layer - Dependency Injection

**File da Creare**:
- `src/infrastructure/di/dependency_container.py` - IoC container (port da hs_deckmanager)

**Responsabilità**:
- Registrare tutte le dipendenze applicazione (TTS, ScreenReader, Settings, Managers, Controllers)
- Risolvere dipendenze con supporto singleton/transient
- Prevenire dipendenze circolari con resolving stack
- Thread-safety con lock (future-proof per async operations)

**Pattern hs_deckmanager da Portare**:
```python
# Da hs_deckmanager: scr/views/builder/dependency_container.py
class DependencyContainer:
    def __init__(self):
        self._dependencies = {}                 # Factory functions
        self._singleton_instances = {}          # Cached singletons
        self._resolving_stack = set()           # Circular dependency detection
        self._lock = Lock()                     # Thread-safety
    
    def register(self, key, factory, singleton=False):
        """Register dependency with optional singleton mode."""
    
    def resolve(self, key, *args, **kwargs):
        """Resolve dependency, return instance."""
    
    def has(self, key):
        """Check if dependency registered."""
```

**Adattamenti per Solitario**:
- Rimuovere `singleton` parameter (non usato in hs_deckmanager implementation)
- Mantenere API semplice: `register(key, factory)` + `resolve(key)`
- Aggiungere `resolve_optional(key)` per dipendenze opzionali (return None se missing)

---

### Obiettivo 2: Infrastructure Layer - Factory Pattern

**File da Creare**:
- `src/infrastructure/ui/factories/view_factory.py` - Factory per finestre/panel
- `src/infrastructure/ui/factories/widget_factory.py` - Factory per widget comuni
- `src/infrastructure/ui/factories/__init__.py` - Public API

**Responsabilità ViewFactory**:
```python
class ViewFactory:
    """Factory per creazione finestre/panel con dependency injection."""
    
    def __init__(self, container: DependencyContainer):
        self.container = container
    
    def create_window(self, key: WindowKey, parent=None, controller=None, **kwargs):
        """Create window by key, inject dependencies from container."""
        window_class = ALL_WINDOWS.get(key)
        if not window_class:
            raise ValueError(f"Unknown window key: {key}")
        
        # Resolve controller from container if not provided
        if not controller:
            controller = self.container.resolve("main_controller")
        
        # Create window with injected dependencies
        return window_class(
            parent=parent,
            controller=controller,
            container=self.container,
            **kwargs
        )
```

**Responsabilità WidgetFactory**:
- Creare button/label/textctrl con styling consistente
- Applicare tema/colori da ColorManager (futuro: dark mode support)
- Bind eventi comuni (focus, keyboard shortcuts)
- Gestire accessibility labels per screen reader

**Window Registration Pattern**:
```python
# src/infrastructure/ui/factories/view_factory.py
from enum import Enum

class WindowKey(Enum):
    """Keys per identificare finestre registrate."""
    MAIN_FRAME = "main_frame"           # SolitarioFrame (invisible event sink)
    MENU_PANEL = "menu_panel"           # MenuPanel
    GAMEPLAY_PANEL = "gameplay_panel"   # GameplayPanel
    OPTIONS_DIALOG = "options_dialog"   # OptionsDialog
    # Future: STATISTICS_WINDOW, HELP_WINDOW, etc.

ALL_WINDOWS = {
    WindowKey.MAIN_FRAME: SolitarioFrame,
    WindowKey.MENU_PANEL: MenuPanel,
    WindowKey.GAMEPLAY_PANEL: GameplayPanel,
    WindowKey.OPTIONS_DIALOG: OptionsDialog,
}
```

---

### Obiettivo 3: Infrastructure Layer - Window Controller

**File da Creare**:
- `src/infrastructure/ui/window_controller.py` - Port di `WinController` da hs_deckmanager

**Responsabilità**:
```python
class WindowController:
    """Gestore centralizzato finestre con parent stack e lazy initialization."""
    
    def __init__(self, container: DependencyContainer):
        self.container = container
        self.factory = ViewFactory(container=container)
        self.windows = {}                   # Cache finestre create {key: instance}
        self.current_window = None          # Finestra attualmente visibile
        self.parent_stack = []              # Stack parent per navigation
    
    def create_window(self, key: WindowKey, parent=None, **kwargs):
        """Create window (lazy) senza renderla visibile."""
        if key in self.windows:
            return self.windows[key]  # Return cached
        
        window = self.factory.create_window(key, parent, **kwargs)
        window.Bind(wx.EVT_CLOSE, lambda e: self.close_current_window())
        self.windows[key] = window
        return window
    
    def open_window(self, key: WindowKey, parent=None):
        """Open window, hide current, push parent to stack."""
        if key not in self.windows:
            raise ValueError(f"Window {key} not created yet")
        
        # Hide current window
        if self.current_window:
            self.current_window.Hide()
            self.parent_stack.append(self.current_window)
        
        # Show new window
        self.current_window = self.windows[key]
        self.current_window.Show()
    
    def close_current_window(self):
        """Close current window, restore parent from stack."""
        if not self.current_window:
            return
        
        self.current_window.Hide()
        
        # Restore parent from stack
        if self.parent_stack:
            self.current_window = self.parent_stack.pop()
            self.current_window.Show()
        else:
            self.current_window = None
```

**Differenze vs ViewManager Attuale**:

| Aspetto | ViewManager (v2.1) | WindowController (v2.2) |
|---------|-------------------|-------------------------|
| Creazione finestre | Eager (all'avvio) | Lazy (on-demand) |
| Parent tracking | Nessuno | Stack-based |
| Factory | No (manual instantiation) | Sì (ViewFactory) |
| Registry | No | Sì (ALL_WINDOWS dict) |
| Dependency injection | No | Sì (container) |
| Hide/Show | Loop su tutti panel | Solo current/parent |
| Close handler | No | Sì (EVT_CLOSE binding) |

---

### Obiettivo 4: Application Layer - Initialization Refactoring

**File da Modificare**:
- `test.py` - Entry point refactoring per usare DependencyContainer

**Pattern Attuale (v2.1)**:
```python
class SolitarioController:
    def __init__(self):
        # Hard-coded instantiation
        self.screen_reader = ScreenReader(tts=create_tts_provider("auto"))
        self.settings = GameSettings()
        self.engine = GameEngine.create(...)
        self.gameplay_controller = GamePlayController(...)
        # ...
```

**Pattern Target (v2.2)**:
```python
class SolitarioController:
    def __init__(self):
        # Create DependencyContainer
        self.container = DependencyContainer()
        
        # Register dependencies
        self._register_dependencies()
        
        # Resolve main components from container
        self.screen_reader = self.container.resolve("screen_reader")
        self.settings = self.container.resolve("settings")
        self.engine = self.container.resolve("engine")
        # ...
    
    def _register_dependencies(self):
        """Register all application dependencies in container."""
        
        # Infrastructure: TTS/ScreenReader
        self.container.register(
            "tts_provider",
            lambda: create_tts_provider(engine="auto")
        )
        self.container.register(
            "screen_reader",
            lambda: ScreenReader(
                tts=self.container.resolve("tts_provider"),
                enabled=True,
                verbose=False
            )
        )
        
        # Domain: Settings
        self.container.register("settings", lambda: GameSettings())
        
        # Application: Engine
        self.container.register(
            "engine",
            lambda: GameEngine.create(
                audio_enabled=True,
                tts_engine="auto",
                verbose=1,
                settings=self.container.resolve("settings"),
                use_native_dialogs=True,
                parent_window=None
            )
        )
        
        # Application: Controllers
        self.container.register(
            "gameplay_controller",
            lambda: GamePlayController(
                engine=self.container.resolve("engine"),
                screen_reader=self.container.resolve("screen_reader"),
                settings=self.container.resolve("settings"),
                on_new_game_request=self.show_new_game_dialog
            )
        )
        
        # Infrastructure: Window Controller
        self.container.register(
            "window_controller",
            lambda: WindowController(container=self.container)
        )
```

**Benefici**:
- Dependency graph esplicito e verificabile
- Facile sostituzione componenti per testing (mock TTS, fake ScreenReader)
- Lazy initialization (components created solo quando risolti)
- Prevenzione duplicazione istanze (container può cachare singleton)

---

### Obiettivo 5: Dialog System Refactoring

**File da Modificare**:
- `src/infrastructure/ui/wx_dialog_provider.py` - Aggiungere non-blocking dialog methods
- `src/application/dialog_manager.py` - Supportare callback-based API

**Pattern Attuale (v2.1) - BLOCKING**:
```python
# test.py - show_abandon_game_dialog()
result = self.dialog_manager.show_abandon_game_prompt()  # BLOCKS qui
if result:
    self.app.CallAfter(self._safe_abandon_to_menu)  # Deferred dopo unblock
```

**Problemi**:
- `ShowModal()` crea nested event loop → timing issues
- Focus può non tornare correttamente dopo dialog
- Screen reader può perdere contesto

**Pattern Target (v2.2) - NON-BLOCKING**:
```python
# test.py - show_abandon_game_dialog()
def on_abandon_result(confirmed: bool):
    if confirmed:
        self._safe_abandon_to_menu()  # No CallAfter needed, already deferred

self.dialog_manager.show_abandon_game_prompt_async(
    callback=on_abandon_result
)  # Returns immediately
```

**Implementazione WxDialogProvider**:
```python
class WxDialogProvider:
    def show_yes_no_async(self, title: str, message: str, callback: Callable[[bool], None]):
        """Show non-blocking yes/no dialog with callback."""
        
        dialog = wx.MessageDialog(
            parent=self.parent_frame,
            message=message,
            caption=title,
            style=wx.YES_NO | wx.ICON_QUESTION
        )
        
        def on_dialog_close(event):
            result = dialog.GetReturnCode() == wx.ID_YES
            dialog.Destroy()
            callback(result)  # Invoke callback with result
        
        dialog.Bind(wx.EVT_CLOSE, on_dialog_close)
        dialog.Show()  # NON-BLOCKING (not ShowModal)
```

**Vantaggi**:
- ✅ Nessun nested event loop (dialog non blocca main loop)
- ✅ Event handling remains consistent
- ✅ Screen reader focus gestito correttamente
- ✅ Callback pattern standard (async-friendly)

**Migration Path**:
1. Mantenere API synchronous esistente (backward compatibility)
2. Aggiungere metodi `*_async()` con callback parameter
3. Deprecare gradualmente API synchronous
4. Rimuovere `ShowModal()` in v3.0 (breaking change)

---

## 📦 Struttura File Completa Post-Migrazione

```
solitario-classico-accessibile/
├── src/
│   ├── domain/                          # Domain layer (unchanged)
│   │   └── services/
│   │       └── game_settings.py
│   ├── application/                     # Application layer
│   │   ├── game_engine.py              # Modified: Accept container in constructor
│   │   ├── gameplay_controller.py      # Modified: Accept container in constructor
│   │   ├── options_controller.py       # Modified: Accept container in constructor
│   │   └── dialog_manager.py           # Modified: Add async methods
│   └── infrastructure/                  # Infrastructure layer
│       ├── di/                          # NEW: Dependency Injection
│       │   ├── __init__.py
│       │   └── dependency_container.py  # NEW: IoC container
│       ├── ui/
│       │   ├── factories/               # NEW: Factory pattern
│       │   │   ├── __init__.py
│       │   │   ├── view_factory.py      # NEW: Window/panel factory
│       │   │   └── widget_factory.py    # NEW: Widget factory
│       │   ├── window_controller.py     # NEW: Port da hs_deckmanager WinController
│       │   ├── view_manager.py          # DEPRECATED: Sostituito da WindowController
│       │   ├── wx_dialog_provider.py    # Modified: Add async methods
│       │   ├── wx_app.py               # Modified: Accept container
│       │   ├── wx_frame.py             # Modified: Accept container
│       │   ├── menu_panel.py           # Modified: Accept container
│       │   ├── gameplay_panel.py       # Modified: Accept container
│       │   └── options_dialog.py       # Modified: Accept container
│       └── accessibility/
│           └── screen_reader.py        # Unchanged
├── test.py                              # Modified: Use DependencyContainer
└── docs/
    ├── IMPLEMENTATION_WINDOW_MANAGEMENT_MIGRATION_v2.2.md  # This document
    └── CHANGELOG.md                     # Updated with v2.2 entry
```

---

## 🔧 Implementation Strategy - 10 Commit Atomici

### Commit 1: Infrastructure - DependencyContainer
**Scope**: Creare IoC container base

**File Creati**:
- `src/infrastructure/di/__init__.py`
- `src/infrastructure/di/dependency_container.py`

**Implementazione**:
```python
# dependency_container.py
from threading import Lock
from typing import Callable, Any, Optional

class DependencyContainer:
    """IoC container per gestione centralizzata dipendenze.
    
    Port da hs_deckmanager con semplificazioni:
    - Rimosso singleton flag (non usato in pratica)
    - API minimalista: register(), resolve(), has()
    - Thread-safe con Lock
    - Circular dependency detection
    
    Example:
        >>> container = DependencyContainer()
        >>> container.register("settings", lambda: GameSettings())
        >>> settings = container.resolve("settings")
    """
    
    def __init__(self):
        self._dependencies: dict[str, Callable] = {}
        self._resolving_stack: set[str] = set()
        self._lock = Lock()
    
    def register(self, key: str, factory: Callable[[], Any]) -> None:
        """Register dependency factory function.
        
        Args:
            key: Unique identifier
            factory: Zero-argument function returning instance
        
        Raises:
            ValueError: If key already registered
        """
        if key in self._dependencies:
            raise ValueError(f"Dependency '{key}' already registered")
        self._dependencies[key] = factory
    
    def resolve(self, key: str) -> Any:
        """Resolve dependency, call factory and return instance.
        
        Args:
            key: Dependency identifier
        
        Returns:
            Instance created by factory
        
        Raises:
            ValueError: If key not registered or circular dependency
        """
        with self._lock:
            if key not in self._dependencies:
                raise ValueError(f"Dependency '{key}' not registered")
            
            if key in self._resolving_stack:
                raise ValueError(f"Circular dependency detected: {key}")
            
            self._resolving_stack.add(key)
            try:
                return self._dependencies[key]()
            finally:
                self._resolving_stack.discard(key)
    
    def resolve_optional(self, key: str) -> Optional[Any]:
        """Resolve dependency, return None if not registered."""
        try:
            return self.resolve(key)
        except ValueError:
            return None
    
    def has(self, key: str) -> bool:
        """Check if dependency registered."""
        return key in self._dependencies
```

**Testing**:
```python
# Test basico in test.py (temporary)
def test_container():
    container = DependencyContainer()
    container.register("test", lambda: "Hello")
    assert container.has("test")
    assert container.resolve("test") == "Hello"
    print("✓ DependencyContainer works")
```

**Commit Message**:
```
feat(v2.2): add DependencyContainer for IoC pattern

- Created src/infrastructure/di/dependency_container.py
- Port from hs_deckmanager with simplifications
- Thread-safe with Lock
- Circular dependency detection
- Minimal API: register(), resolve(), has(), resolve_optional()

No behavioral changes (new component, not integrated yet)

Ref: hs_deckmanager/scr/views/builder/dependency_container.py
```

---

### Commit 2: Infrastructure - Factory Pattern (ViewFactory)
**Scope**: Creare ViewFactory per window/panel creation

**File Creati**:
- `src/infrastructure/ui/factories/__init__.py`
- `src/infrastructure/ui/factories/view_factory.py`

**Implementazione**:
```python
# view_factory.py
from enum import Enum
from typing import Optional, Any
import wx

from src.infrastructure.di.dependency_container import DependencyContainer

# Import window classes (will be created/modified later)
from src.infrastructure.ui.wx_frame import SolitarioFrame
from src.infrastructure.ui.menu_panel import MenuPanel
from src.infrastructure.ui.gameplay_panel import GameplayPanel
from src.infrastructure.ui.options_dialog import OptionsDialog

class WindowKey(Enum):
    """Unique identifiers for registered windows."""
    MAIN_FRAME = "main_frame"
    MENU_PANEL = "menu_panel"
    GAMEPLAY_PANEL = "gameplay_panel"
    OPTIONS_DIALOG = "options_dialog"

ALL_WINDOWS = {
    WindowKey.MAIN_FRAME: SolitarioFrame,
    WindowKey.MENU_PANEL: MenuPanel,
    WindowKey.GAMEPLAY_PANEL: GameplayPanel,
    WindowKey.OPTIONS_DIALOG: OptionsDialog,
}

class ViewFactory:
    """Factory per creazione finestre con dependency injection.
    
    Port da hs_deckmanager ViewFactory con adattamenti:
    - Container obbligatorio (no fallback)
    - Controller resolution automatica da container
    - Supporto **kwargs per parametri custom (es. deck_name)
    
    Example:
        >>> factory = ViewFactory(container=container)
        >>> menu = factory.create_window(WindowKey.MENU_PANEL, parent=frame)
    """
    
    def __init__(self, container: DependencyContainer):
        if not container:
            raise ValueError("DependencyContainer required")
        self.container = container
    
    def create_window(
        self,
        key: WindowKey,
        parent: Optional[wx.Window] = None,
        controller: Optional[Any] = None,
        **kwargs
    ) -> wx.Window:
        """Create window by key with dependency injection.
        
        Args:
            key: Window identifier from WindowKey enum
            parent: Parent window (optional)
            controller: Controller instance (optional, resolved from container)
            **kwargs: Additional window-specific parameters
        
        Returns:
            Window instance
        
        Raises:
            ValueError: If key not registered
        """
        window_class = ALL_WINDOWS.get(key)
        if not window_class:
            raise ValueError(f"Unknown window key: {key}")
        
        # Resolve controller from container if not provided
        if not controller:
            controller = self.container.resolve_optional("main_controller")
        
        # Create window with injected dependencies
        return window_class(
            parent=parent,
            controller=controller,
            container=self.container,
            **kwargs
        )
```

**__init__.py**:
```python
# factories/__init__.py
from .view_factory import ViewFactory, WindowKey, ALL_WINDOWS

__all__ = ["ViewFactory", "WindowKey", "ALL_WINDOWS"]
```

**Commit Message**:
```
feat(v2.2): add ViewFactory for window creation with DI

- Created src/infrastructure/ui/factories/view_factory.py
- WindowKey enum for registered windows
- ALL_WINDOWS registry dict
- Automatic controller resolution from container
- Support for custom kwargs (future: deck_name, etc.)

No behavioral changes (new component, not integrated yet)

Ref: hs_deckmanager/scr/views/builder/view_factory.py
```

---

### Commit 3: Infrastructure - Factory Pattern (WidgetFactory)
**Scope**: Creare WidgetFactory per widget comuni

**File Creati**:
- `src/infrastructure/ui/factories/widget_factory.py`

**Implementazione**:
```python
# widget_factory.py
import wx
from typing import Optional, Callable, Tuple, List

from src.infrastructure.di.dependency_container import DependencyContainer

class WidgetFactory:
    """Factory per creazione widget comuni con styling consistente.
    
    Semplificazione rispetto a hs_deckmanager:
    - No ColorManager (solitario ha solo audio UI)
    - Focus su accessibility (screen reader labels)
    - Minimal styling (default wx appearance)
    
    Future enhancements:
    - Dark mode support via ColorManager
    - Custom fonts for better readability
    - Focus indicators for keyboard navigation
    """
    
    def __init__(self, container: DependencyContainer):
        self.container = container
    
    def create_button(
        self,
        parent: wx.Window,
        label: str,
        size: Tuple[int, int] = (180, 70),
        font_size: int = 16,
        event_handler: Optional[Callable] = None
    ) -> wx.Button:
        """Create button with consistent styling.
        
        Args:
            parent: Parent window
            label: Button text
            size: (width, height) in pixels
            font_size: Font size in points
            event_handler: Click handler (optional)
        
        Returns:
            wx.Button instance
        """
        button = wx.Button(parent, label=label, size=size)
        button.SetFont(wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        
        if event_handler:
            button.Bind(wx.EVT_BUTTON, event_handler)
        
        return button
    
    def create_sizer(self, orientation: int = wx.VERTICAL) -> wx.BoxSizer:
        """Create sizer for layout management."""
        return wx.BoxSizer(orientation)
    
    def add_to_sizer(
        self,
        sizer: wx.Sizer,
        element: wx.Window,
        proportion: int = 0,
        flag: int = wx.ALL,
        border: int = 10
    ) -> None:
        """Add element to sizer with default parameters."""
        sizer.Add(element, proportion=proportion, flag=flag, border=border)
```

**Aggiornamento __init__.py**:
```python
# factories/__init__.py
from .view_factory import ViewFactory, WindowKey, ALL_WINDOWS
from .widget_factory import WidgetFactory

__all__ = ["ViewFactory", "WindowKey", "ALL_WINDOWS", "WidgetFactory"]
```

**Commit Message**:
```
feat(v2.2): add WidgetFactory for consistent widget creation

- Created src/infrastructure/ui/factories/widget_factory.py
- Simplified version (no ColorManager, audio-first UI)
- Standard methods: create_button(), create_sizer(), add_to_sizer()
- Future-ready for dark mode and custom styling

No behavioral changes (new component, not integrated yet)

Ref: hs_deckmanager/scr/views/builder/view_factory.py (WidgetFactory class)
```

---

### Commit 4: Infrastructure - WindowController
**Scope**: Creare WindowController per gestione gerarchica finestre

**File Creati**:
- `src/infrastructure/ui/window_controller.py`

**Implementazione**:
```python
# window_controller.py
import wx
from typing import Optional, Dict, List

from src.infrastructure.di.dependency_container import DependencyContainer
from src.infrastructure.ui.factories import ViewFactory, WindowKey

class WindowController:
    """Gestore centralizzato finestre con parent stack e lazy initialization.
    
    Port da hs_deckmanager WinController con adattamenti:
    - Lazy window creation (on-demand)
    - Parent stack per navigation gerarchica
    - Auto-binding EVT_CLOSE per cleanup
    - Cache finestre create (no recreation)
    
    Pattern:
        1. create_window(key) - Crea finestra (lazy), non la mostra
        2. open_window(key) - Mostra finestra, nasconde corrente, push parent stack
        3. close_current_window() - Chiude corrente, pop parent da stack
    
    Example:
        >>> win_ctrl = WindowController(container=container)
        >>> win_ctrl.create_window(WindowKey.MENU_PANEL)
        >>> win_ctrl.open_window(WindowKey.MENU_PANEL)  # Shows menu
        >>> win_ctrl.create_window(WindowKey.GAMEPLAY_PANEL)
        >>> win_ctrl.open_window(WindowKey.GAMEPLAY_PANEL)  # Hides menu, shows gameplay
        >>> win_ctrl.close_current_window()  # Hides gameplay, shows menu
    """
    
    def __init__(self, container: DependencyContainer):
        if not container:
            raise ValueError("DependencyContainer required")
        
        self.container = container
        self.factory = ViewFactory(container=container)
        self.windows: Dict[WindowKey, wx.Window] = {}  # Cache created windows
        self.current_window: Optional[wx.Window] = None
        self.parent_stack: List[wx.Window] = []  # Stack for parent restoration
    
    def get_current_window(self) -> Optional[wx.Window]:
        """Get currently visible window."""
        return self.current_window
    
    def create_window(
        self,
        key: WindowKey,
        parent: Optional[wx.Window] = None,
        controller: Optional[Any] = None,
        **kwargs
    ) -> wx.Window:
        """Create window (lazy) without showing it.
        
        Args:
            key: Window identifier
            parent: Parent window (optional)
            controller: Controller instance (optional)
            **kwargs: Window-specific parameters
        
        Returns:
            Window instance (from cache if already created)
        """
        # Return cached if already created
        if key in self.windows:
            return self.windows[key]
        
        # Create via factory
        window = self.factory.create_window(
            key=key,
            parent=parent,
            controller=controller,
            **kwargs
        )
        
        # Bind close event to close_current_window()
        window.Bind(wx.EVT_CLOSE, lambda e: self.close_current_window())
        
        # Cache window
        self.windows[key] = window
        
        return window
    
    def open_window(self, key: WindowKey, parent: Optional[wx.Window] = None) -> None:
        """Open window, hide current, push parent to stack.
        
        Args:
            key: Window identifier
            parent: Parent window (optional override)
        
        Raises:
            ValueError: If window not created yet
        """
        if key not in self.windows:
            raise ValueError(f"Window {key} not created yet. Call create_window() first.")
        
        # Hide current window and push to parent stack
        if self.current_window:
            self.current_window.Hide()
            self.parent_stack.append(self.current_window)
        
        # Show new window
        self.current_window = self.windows[key]
        self.current_window.Show()
        
        # Set parent if provided
        if parent:
            self.current_window.SetParent(parent)
    
    def close_current_window(self) -> None:
        """Close current window, restore parent from stack."""
        if not self.current_window:
            return
        
        # Hide current
        self.current_window.Hide()
        
        # Restore parent from stack
        if self.parent_stack:
            self.current_window = self.parent_stack.pop()
            self.current_window.Show()
        else:
            # No parent, clear current
            self.current_window = None
```

**Commit Message**:
```
feat(v2.2): add WindowController for hierarchical window management

- Created src/infrastructure/ui/window_controller.py
- Port from hs_deckmanager WinController
- Lazy window creation (on-demand)
- Parent stack for proper navigation
- Auto-binding EVT_CLOSE for cleanup
- Window caching (no recreation)

Features:
- create_window(key) - Create window (lazy), don't show
- open_window(key) - Show window, hide current, push parent
- close_current_window() - Close current, restore parent

No behavioral changes (new component, not integrated yet)

Ref: hs_deckmanager/scr/views/view_manager.py (WinController class)
```

---

### Commit 5: Application Entry Point - DependencyContainer Integration
**Scope**: Refactoring test.py per usare DependencyContainer

**File Modificati**:
- `test.py`

**Modifiche**:

1. **Aggiungere import**:
```python
# Add at top of test.py
from src.infrastructure.di.dependency_container import DependencyContainer
from src.infrastructure.ui.window_controller import WindowController
from src.infrastructure.ui.factories import WindowKey
```

2. **Refactoring __init__ method**:
```python
class SolitarioController:
    def __init__(self):
        print("\n" + "="*60)
        print("🎴 SOLITARIO ACCESSIBILE - wxPython v2.2.0")
        print("="*60)
        print("Inizializzazione componenti con DependencyContainer...")
        
        # Create DependencyContainer
        self.container = DependencyContainer()
        
        # Register all dependencies
        self._register_dependencies()
        
        # Resolve main components from container
        self.screen_reader = self.container.resolve("screen_reader")
        self.settings = self.container.resolve("settings")
        self.engine = self.container.resolve("engine")
        self.gameplay_controller = self.container.resolve("gameplay_controller")
        self.dialog_manager = None  # Initialized in run() after frame creation
        
        # State flags (legacy, will be removed in future)
        self.is_menu_open = True
        self.is_options_mode = False
        self._timer_expired_announced = False
        
        # wxPython components (created in run())
        self.app = None
        self.frame = None
        self.window_controller = None  # NEW: Replaces view_manager
        
        print("="*60)
        print("✓ Applicazione avviata con DependencyContainer!")
        print("✓ IoC pattern attivo")
        print("="*60)
```

3. **Aggiungere _register_dependencies() method**:
```python
def _register_dependencies(self) -> None:
    """Register all application dependencies in container.
    
    Registration order:
    1. Infrastructure: TTS, ScreenReader
    2. Domain: GameSettings
    3. Application: GameEngine, Controllers
    4. Infrastructure: WindowController (after all deps registered)
    """
    print("Registrazione dipendenze nel container...")
    
    # 1. Infrastructure: TTS/ScreenReader
    self.container.register(
        "tts_provider",
        lambda: create_tts_provider(engine="auto")
    )
    self.container.register(
        "screen_reader",
        lambda: ScreenReader(
            tts=self.container.resolve("tts_provider"),
            enabled=True,
            verbose=False
        )
    )
    print("  ✓ TTS e ScreenReader registrati")
    
    # 2. Domain: Settings
    self.container.register("settings", lambda: GameSettings())
    print("  ✓ GameSettings registrato")
    
    # 3. Application: Engine
    self.container.register(
        "engine",
        lambda: GameEngine.create(
            audio_enabled=True,
            tts_engine="auto",
            verbose=1,
            settings=self.container.resolve("settings"),
            use_native_dialogs=True,
            parent_window=None
        )
    )
    print("  ✓ GameEngine registrato")
    
    # 4. Application: Controllers
    self.container.register(
        "gameplay_controller",
        lambda: GamePlayController(
            engine=self.container.resolve("engine"),
            screen_reader=self.container.resolve("screen_reader"),
            settings=self.container.resolve("settings"),
            on_new_game_request=self.show_new_game_dialog
        )
    )
    print("  ✓ GameplayController registrato")
    
    # 5. Infrastructure: WindowController (will be resolved in run())
    self.container.register(
        "window_controller",
        lambda: WindowController(container=self.container)
    )
    print("  ✓ WindowController registrato")
    
    print("✓ Tutte le dipendenze registrate nel container")
```

4. **Aggiornare run() method per usare WindowController**:
```python
def run(self) -> None:
    """Start wxPython application and enter main loop."""
    print("\nAvvio wxPython MainLoop()...")
    
    def on_init(app):
        """Callback after wx.App initialization."""
        # Create frame
        self.frame = SolitarioFrame(
            on_timer_tick=self._on_timer_tick,
            on_close=self._on_frame_close
        )
        
        # Initialize dialog manager
        from src.infrastructure.ui.wx_dialog_provider import WxDialogProvider
        dialog_provider = WxDialogProvider(parent_frame=self.frame)
        self.dialog_manager = SolitarioDialogManager(dialog_provider=dialog_provider)
        self.gameplay_controller.options_controller.dialog_manager = self.dialog_manager
        
        # Resolve WindowController from container
        print("Inizializzazione WindowController...")
        self.window_controller = self.container.resolve("window_controller")
        
        # Create panels via WindowController
        print("Creazione panels via WindowController...")
        self.window_controller.create_window(
            key=WindowKey.MENU_PANEL,
            parent=self.frame.panel_container,
            controller=self
        )
        self.window_controller.create_window(
            key=WindowKey.GAMEPLAY_PANEL,
            parent=self.frame.panel_container,
            controller=self
        )
        print("✓ WindowController pronto (menu, gameplay panels creati)")
        
        # Show initial menu panel
        print("Apertura menu iniziale...")
        self.window_controller.open_window(WindowKey.MENU_PANEL)
        print("✓ Menu visualizzato")
        
        # Start timer
        self.frame.start_timer(1000)
    
    self.app = SolitarioWxApp(on_init_complete=on_init)
    self.app.MainLoop()
    print("wxPython MainLoop terminato.")
```

5. **Aggiornare start_gameplay() per usare WindowController**:
```python
def start_gameplay(self) -> None:
    """Start gameplay (called from MenuPanel)."""
    if self.window_controller:
        self.window_controller.open_window(WindowKey.GAMEPLAY_PANEL)
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
```

6. **Aggiornare return_to_menu() per usare WindowController**:
```python
def return_to_menu(self) -> None:
    """Return from gameplay to menu."""
    if not self.window_controller:
        print("⚠ WindowController not initialized")
        return
    
    # Show menu panel via WindowController
    self.window_controller.open_window(WindowKey.MENU_PANEL)
    
    # Update state
    self.is_menu_open = True
    
    # Announce via TTS
    if self.screen_reader:
        self.screen_reader.tts.speak(
            "Ritorno al menu di gioco.",
            interrupt=True
        )
```

**Commit Message**:
```
refactor(v2.2): integrate DependencyContainer in test.py

- Refactored SolitarioController.__init__() to use DependencyContainer
- Added _register_dependencies() method
- All components resolved from container (TTS, ScreenReader, Engine, Controllers)
- Replaced ViewManager with WindowController
- Updated start_gameplay() and return_to_menu() to use WindowController

Behavioral changes:
- Dependency graph now explicit and verifiable
- Components created via factory functions (lazy, cacheable)
- Window management via WindowController (parent stack support)

Backward compatibility:
- Same keyboard commands
- Same UI flow (menu ↔ gameplay)
- Legacy state flags maintained (will be removed in future)

Testing:
- Manual test: App starts, menu shows
- Manual test: "Nuova partita" → Gameplay panel
- Manual test: ESC abandon → Menu panel
```

---

### Commit 6: Infrastructure - Panel Refactoring (MenuPanel)
**Scope**: Aggiornare MenuPanel per accettare container

**File Modificati**:
- `src/infrastructure/ui/menu_panel.py`

**Modifiche**:

1. **Aggiungere parametro container in __init__**:
```python
class MenuPanel(wx.Panel):
    def __init__(
        self,
        parent: wx.Window,
        controller: 'SolitarioController',
        container: Optional['DependencyContainer'] = None  # NEW
    ):
        super().__init__(parent)
        self.controller = controller
        self.container = container  # Store container for future use
        
        # Rest of initialization unchanged
        self._create_ui()
        self._bind_events()
```

2. **Aggiungere docstring update**:
```python
"""Menu panel per navigazione principale.

Args:
    parent: Parent window (SolitarioFrame.panel_container)
    controller: Main application controller
    container: DependencyContainer (optional, for future extensions)

Version:
    v1.7.3: Initial implementation (panel-swap pattern)
    v2.2.0: Added container parameter for dependency injection
"""
```

**Commit Message**:
```
refactor(v2.2): update MenuPanel to accept DependencyContainer

- Added container parameter to MenuPanel.__init__()
- Updated docstring with version history
- No behavioral changes (container stored but not used yet)
- Preparation for future factory-based widget creation

Backward compatibility: container parameter optional
```

---

### Commit 7: Infrastructure - Panel Refactoring (GameplayPanel)
**Scope**: Aggiornare GameplayPanel per accettare container

**File Modificati**:
- `src/infrastructure/ui/gameplay_panel.py`

**Modifiche**: Identiche a Commit 6, ma per GameplayPanel

```python
class GameplayPanel(wx.Panel):
    def __init__(
        self,
        parent: wx.Window,
        controller: 'SolitarioController',
        container: Optional['DependencyContainer'] = None  # NEW
    ):
        super().__init__(parent)
        self.controller = controller
        self.container = container  # Store for future use
        
        # Rest unchanged
        self.last_esc_time = 0.0
        self._create_ui()
        self._bind_events()
```

**Commit Message**:
```
refactor(v2.2): update GameplayPanel to accept DependencyContainer

- Added container parameter to GameplayPanel.__init__()
- Updated docstring with version history
- No behavioral changes (container stored but not used yet)
- Preparation for future factory-based widget creation

Backward compatibility: container parameter optional
```

---

### Commit 8: Infrastructure - Dialog Async Methods (Phase 1)
**Scope**: Aggiungere metodi async a WxDialogProvider (mantiene API sync)

**File Modificati**:
- `src/infrastructure/ui/wx_dialog_provider.py`

**Modifiche**:

1. **Aggiungere import Callable**:
```python
from typing import Optional, Callable
```

2. **Aggiungere metodo async per yes/no dialog**:
```python
def show_yes_no_async(
    self,
    title: str,
    message: str,
    callback: Callable[[bool], None]
) -> None:
    """Show non-blocking yes/no dialog with callback.
    
    Args:
        title: Dialog title
        message: Dialog message
        callback: Function called with result (True=Yes, False=No)
    
    Example:
        >>> def on_result(confirmed: bool):
        ...     if confirmed:
        ...         print("User confirmed")
        >>> provider.show_yes_no_async("Title", "Message?", on_result)
    
    Version:
        v2.2: Added async API to prevent nested event loops
    """
    dialog = wx.MessageDialog(
        parent=self.parent_frame,
        message=message,
        caption=title,
        style=wx.YES_NO | wx.ICON_QUESTION
    )
    
    def on_dialog_close(event):
        result = dialog.GetReturnCode() == wx.ID_YES
        dialog.Destroy()
        callback(result)  # Invoke callback with result
    
    dialog.Bind(wx.EVT_CLOSE, on_dialog_close)
    dialog.Show()  # NON-BLOCKING (not ShowModal)
```

3. **Mantenere API synchronous per backward compatibility**:
```python
# Existing methods unchanged
def show_yes_no(self, title: str, message: str) -> bool:
    """DEPRECATED: Use show_yes_no_async() to avoid nested event loops.
    
    Synchronous API maintained for backward compatibility.
    Will be removed in v3.0.
    """
    # Keep existing implementation
    dialog = wx.MessageDialog(
        parent=self.parent_frame,
        message=message,
        caption=title,
        style=wx.YES_NO | wx.ICON_QUESTION
    )
    result = dialog.ShowModal() == wx.ID_YES
    dialog.Destroy()
    return result
```

**Commit Message**:
```
feat(v2.2): add async dialog methods to WxDialogProvider

- Added show_yes_no_async() for non-blocking dialogs
- Uses Show() instead of ShowModal() (no nested event loop)
- Callback pattern for result handling
- Deprecated synchronous API (will be removed in v3.0)

Backward compatibility:
- Existing show_yes_no() method unchanged
- No breaking changes (async methods are additions)

Benefits:
- No nested event loops
- Better focus management
- Screen reader friendly
- Async-ready for future features
```

---

### Commit 9: Application - Dialog Manager Async API
**Scope**: Aggiungere metodi async a SolitarioDialogManager

**File Modificati**:
- `src/application/dialog_manager.py`

**Modifiche**:

1. **Aggiungere metodi async wrapper**:
```python
def show_abandon_game_prompt_async(self, callback: Callable[[bool], None]) -> None:
    """Show abandon game confirmation dialog (non-blocking).
    
    Args:
        callback: Function called with result (True=abandon, False=continue)
    
    Example:
        >>> def on_result(confirmed):
        ...     if confirmed:
        ...         self._safe_abandon_to_menu()
        >>> dialog_manager.show_abandon_game_prompt_async(on_result)
    
    Version:
        v2.2: Added async API
    """
    if not self.is_available:
        # Fallback TTS (no callback, announce only)
        self.tts.speak("Funzione non disponibile senza wxPython.", interrupt=True)
        return
    
    self.dialog_provider.show_yes_no_async(
        title="Abbandono Partita",
        message="Vuoi abbandonare la partita e tornare al menu di gioco?",
        callback=callback
    )

# Repeat for other prompts
def show_new_game_prompt_async(self, callback: Callable[[bool], None]) -> None:
    """Non-blocking new game confirmation."""
    if not self.is_available:
        self.tts.speak("Funzione non disponibile senza wxPython.", interrupt=True)
        return
    
    self.dialog_provider.show_yes_no_async(
        title="Nuova Partita",
        message="Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?",
        callback=callback
    )

def show_exit_app_prompt_async(self, callback: Callable[[bool], None]) -> None:
    """Non-blocking exit confirmation."""
    if not self.is_available:
        self.tts.speak("Funzione non disponibile senza wxPython.", interrupt=True)
        return
    
    self.dialog_provider.show_yes_no_async(
        title="Conferma Uscita",
        message="Vuoi uscire dall'applicazione?",
        callback=callback
    )
```

2. **Deprecare metodi sync**:
```python
def show_abandon_game_prompt(self) -> bool:
    """DEPRECATED: Use show_abandon_game_prompt_async().
    
    Synchronous API causes nested event loops.
    Maintained for backward compatibility, will be removed in v3.0.
    """
    # Keep existing implementation unchanged
    if not self.is_available:
        self.tts.speak("Funzione non disponibile senza wxPython.", interrupt=True)
        return False
    
    return self.dialog_provider.show_yes_no(
        title="Abbandono Partita",
        message="Vuoi abbandonare la partita e tornare al menu di gioco?"
    )
```

**Commit Message**:
```
feat(v2.2): add async methods to SolitarioDialogManager

- Added show_abandon_game_prompt_async()
- Added show_new_game_prompt_async()
- Added show_exit_app_prompt_async()
- Callback-based API for non-blocking dialogs
- Deprecated synchronous methods (will be removed in v3.0)

Backward compatibility:
- Existing synchronous methods unchanged
- No breaking changes (async methods are additions)

Usage:
  def on_result(confirmed):
      if confirmed:
          self._safe_abandon_to_menu()
  dialog_manager.show_abandon_game_prompt_async(on_result)
```

---

### Commit 10: Application - Migrate to Async Dialog API
**Scope**: Migrare test.py per usare dialog async (BREAKING interno)

**File Modificati**:
- `test.py`

**Modifiche**:

1. **Refactoring show_abandon_game_dialog()**:
```python
# OLD (v2.1) - BLOCKING
def show_abandon_game_dialog(self) -> None:
    result = self.dialog_manager.show_abandon_game_prompt()  # BLOCKS
    if result:
        self.app.CallAfter(self._safe_abandon_to_menu)

# NEW (v2.2) - NON-BLOCKING
def show_abandon_game_dialog(self) -> None:
    """Show abandon game confirmation dialog (non-blocking).
    
    Uses async dialog API to prevent nested event loops.
    Callback invoked after user responds.
    
    Version:
        v2.2: Migrated to async dialog API
    """
    def on_abandon_result(confirmed: bool):
        if confirmed:
            # No CallAfter needed, callback already deferred
            self._safe_abandon_to_menu()
    
    self.dialog_manager.show_abandon_game_prompt_async(
        callback=on_abandon_result
    )
```

2. **Refactoring show_new_game_dialog()**:
```python
def show_new_game_dialog(self) -> None:
    """Show new game confirmation dialog (non-blocking)."""
    def on_new_game_result(confirmed: bool):
        if confirmed:
            self.engine.reset_game()
            self.engine.new_game()
            self._timer_expired_announced = False
            
            if self.screen_reader:
                self.screen_reader.tts.speak(
                    "Nuova partita avviata! Usa H per l'aiuto comandi.",
                    interrupt=True
                )
    
    self.dialog_manager.show_new_game_prompt_async(
        callback=on_new_game_result
    )
```

3. **Refactoring quit_app()**:
```python
def quit_app(self) -> None:
    """Graceful application shutdown with confirmation (non-blocking).
    
    Version:
        v2.2: Migrated to async dialog API
    """
    def on_quit_result(confirmed: bool):
        if confirmed:
            print("\n" + "="*60)
            print("CHIUSURA APPLICAZIONE")
            print("="*60)
            
            if self.screen_reader:
                self.screen_reader.tts.speak("Chiusura in corso.", interrupt=True)
                wx.MilliSleep(800)
            
            sys.exit(0)
        else:
            if self.screen_reader:
                self.screen_reader.tts.speak("Uscita annullata.", interrupt=True)
    
    self.dialog_manager.show_exit_app_prompt_async(
        callback=on_quit_result
    )
```

4. **Rimuovere CallAfter da _safe_* methods (non più necessari)**:
```python
# _safe_abandon_to_menu(), _safe_decline_to_menu(), _safe_timeout_to_menu()
# rimangono invariati, ma ora chiamati direttamente da callback (già deferred)
```

**Commit Message**:
```
refactor(v2.2): migrate test.py to async dialog API

- Refactored show_abandon_game_dialog() to use async API
- Refactored show_new_game_dialog() to use async API
- Refactored quit_app() to use async API
- Removed CallAfter from dialog result handling (callback already deferred)
- Simplified deferred methods (_safe_*_to_menu)

Benefits:
- No nested event loops (Show() instead of ShowModal())
- Better focus management
- Screen reader friendly
- Cleaner callback-based flow

Behavioral changes:
- Dialog response handling now async (callback pattern)
- Same user experience (dialog appearance/behavior identical)

Testing:
- Manual test: ESC abandon → Dialog → Confirm → Menu
- Manual test: N key → Dialog → Confirm → New game
- Manual test: Exit button → Dialog → Confirm → App closes
- Manual test: All dialog ESC → Cancel works
```

---

### Commit 11: Documentation - CHANGELOG and README Update
**Scope**: Aggiornare CHANGELOG.md e README.md con v2.2.0 release notes

**File Modificati**:
- `CHANGELOG.md`
- `README.md`

**CHANGELOG.md Entry**:
```markdown
## [2.2.0] - 2026-02-14

### Added

#### Dependency Injection System
- **DependencyContainer** - IoC container per gestione centralizzata dipendenze
  - Registrazione factory functions: `register(key, factory)`
  - Risoluzione dipendenze: `resolve(key)`
  - Circular dependency detection
  - Thread-safe con Lock
  - Port da hs_deckmanager con semplificazioni

#### Factory Pattern
- **ViewFactory** - Factory per creazione finestre/panel
  - WindowKey enum per identificatori unici
  - ALL_WINDOWS registry dict
  - Automatic controller resolution da container
  - Support kwargs custom (future: deck_name, etc.)
- **WidgetFactory** - Factory per widget comuni
  - create_button(), create_sizer(), add_to_sizer()
  - Consistent styling (future: dark mode support)
  - Accessibility-first (screen reader labels)

#### Window Management
- **WindowController** - Gestore gerarchico finestre
  - Lazy window creation (on-demand)
  - Parent stack per navigation gerarchica
  - Auto-binding EVT_CLOSE per cleanup
  - Window caching (no recreation)
  - Pattern: create_window() → open_window() → close_current_window()
  - Port da hs_deckmanager WinController

#### Async Dialog API
- **WxDialogProvider** - Metodi async non-blocking
  - show_yes_no_async(title, message, callback)
  - Usa Show() invece di ShowModal() (no nested loops)
  - Callback pattern per result handling
- **SolitarioDialogManager** - Async wrappers
  - show_abandon_game_prompt_async(callback)
  - show_new_game_prompt_async(callback)
  - show_exit_app_prompt_async(callback)

### Changed

#### Architecture Refactoring
- **test.py** - Migrato a DependencyContainer
  - Dependency graph esplicito in _register_dependencies()
  - Tutti componenti risolti da container
  - WindowController sostituisce ViewManager
  - Async dialog API utilizzata ovunque
- **MenuPanel/GameplayPanel** - Container parameter aggiunto
  - Preparation per future factory-based widget creation
  - Backward compatible (container optional)

### Deprecated

- **ViewManager** - Sostituito da WindowController
  - Mantenuto per backward compatibility
  - Sarà rimosso in v3.0
- **Synchronous Dialog API** - Deprecati metodi blocking
  - show_abandon_game_prompt() → show_abandon_game_prompt_async()
  - show_new_game_prompt() → show_new_game_prompt_async()
  - show_exit_app_prompt() → show_exit_app_prompt_async()
  - Saranno rimossi in v3.0

### Technical

#### Files Added (6)
- `src/infrastructure/di/dependency_container.py` (120 LOC)
- `src/infrastructure/ui/factories/__init__.py` (3 LOC)
- `src/infrastructure/ui/factories/view_factory.py` (85 LOC)
- `src/infrastructure/ui/factories/widget_factory.py` (60 LOC)
- `src/infrastructure/ui/window_controller.py` (140 LOC)
- `docs/IMPLEMENTATION_WINDOW_MANAGEMENT_MIGRATION_v2.2.md` (2500+ LOC)

#### Files Modified (5)
- `test.py` (+150 LOC, refactored initialization and dialog handling)
- `src/infrastructure/ui/menu_panel.py` (+2 LOC, container parameter)
- `src/infrastructure/ui/gameplay_panel.py` (+2 LOC, container parameter)
- `src/infrastructure/ui/wx_dialog_provider.py` (+30 LOC, async methods)
- `src/application/dialog_manager.py` (+50 LOC, async wrappers)

#### Total Changes
- **Added**: ~600 LOC (new infrastructure)
- **Modified**: ~234 LOC (integration)
- **Total**: ~834 LOC

### Benefits

#### Architectural
- ✅ Dependency injection (testability, maintainability)
- ✅ Factory pattern (centralized UI creation)
- ✅ Hierarchical window management (proper navigation)
- ✅ Non-blocking dialogs (no nested event loops)

#### User Experience
- ✅ Same keyboard commands
- ✅ Same UI flow
- ✅ Better focus management
- ✅ Screen reader friendly

### Migration Guide

#### For Users
**NO ACTION REQUIRED** - App works identically:
- All keyboard commands unchanged
- All dialogs behave the same
- Same menu/gameplay flow

#### For Developers

**Dependency Registration**:
```python
container = DependencyContainer()
container.register("settings", lambda: GameSettings())
settings = container.resolve("settings")
```

**Window Creation**:
```python
win_ctrl = WindowController(container=container)
win_ctrl.create_window(WindowKey.MENU_PANEL)
win_ctrl.open_window(WindowKey.MENU_PANEL)
```

**Async Dialogs**:
```python
def on_result(confirmed: bool):
    if confirmed:
        do_action()

dialog_manager.show_yes_no_async("Title", "Message?", on_result)
```

### Breaking Changes

⚠️ **Internal Only** (no user-facing impact):
- ViewManager deprecated (use WindowController)
- Synchronous dialog API deprecated (use async methods)
- Direct component instantiation discouraged (use container)

### References

- **Implementation Guide**: `docs/IMPLEMENTATION_WINDOW_MANAGEMENT_MIGRATION_v2.2.md`
- **Source Pattern**: [hs_deckmanager](https://github.com/Nemex81/hs_deckmanager)
- **Commit Strategy**: 11 atomic commits (incremental migration)
```

**README.md Update**:
```markdown
# Solitario Classico Accessibile

Versione: **2.2.0** (Window Management Migration)

## Novità v2.2.0

- ✅ **Dependency Injection** - DependencyContainer per gestione dipendenze
- ✅ **Factory Pattern** - ViewFactory e WidgetFactory per UI creation
- ✅ **Window Management** - WindowController gerarchico con parent stack
- ✅ **Async Dialogs** - Dialog non-blocking per eliminare nested event loops
- ✅ **Port da hs_deckmanager** - Pattern architetturali production-ready

Per dettagli completi vedi [CHANGELOG.md](CHANGELOG.md#220---2026-02-14)
```

**Commit Message**:
```
chore(release): prepare v2.2.0 - Window Management Migration

- Updated CHANGELOG.md with comprehensive v2.2.0 entry
- Complete feature list and migration guide
- File statistics and technical details
- Updated README.md with version and highlights

Release type: MINOR
- Architectural changes (DependencyContainer, WindowController, Async Dialogs)
- Backward compatible (no breaking changes for users)
- Internal deprecations (ViewManager, sync dialog API)

Implementation complete:
- 11 atomic commits delivered
- 6 new files, 5 modified files
- ~834 LOC total changes
- Full documentation in IMPLEMENTATION_WINDOW_MANAGEMENT_MIGRATION_v2.2.md

Testing status:
✅ Manual test: App starts correctly
✅ Manual test: Menu navigation works
✅ Manual test: Gameplay flow unchanged
✅ Manual test: All dialogs non-blocking
✅ Manual test: ESC/focus handling correct

Production ready: YES
```

---

## ✅ Validation Checklist

### Pre-Implementation

- [ ] **Read complete guide** - Copilot deve leggere TUTTO questo documento
- [ ] **Understand pattern source** - Consultare hs_deckmanager per riferimento
- [ ] **Verify dependencies** - wxPython 4.1.1+, Python 3.9+

### During Implementation (Per Commit)

- [ ] **Syntax check** - Codice Python valido (no syntax errors)
- [ ] **Import check** - Tutti import necessari presenti
- [ ] **Type hints** - Dove possibile, aggiungere type hints
- [ ] **Docstrings** - Ogni classe/metodo documentato
- [ ] **Comments** - Commenti inline per logica complessa
- [ ] **Manual test** - Test manuale scenario critico

### Post-Commit Validation

- [ ] **Build success** - App parte senza errori import
- [ ] **Menu navigation** - TAB/frecce/click funzionano
- [ ] **Gameplay flow** - Nuova partita → Gameplay → ESC → Menu
- [ ] **Dialog async** - Tutti dialog non bloccano (Show non ShowModal)
- [ ] **Focus management** - Focus torna correttamente dopo dialog
- [ ] **Screen reader** - NVDA legge correttamente (Windows)
- [ ] **Console logs** - Nessun warning/error in console

### Final Release Validation (v2.2.0)

- [ ] **Complete audit** - Tutti 11 commit verificati
- [ ] **CHANGELOG updated** - Entry v2.2.0 completa
- [ ] **README updated** - Versione corrente documentata
- [ ] **No regressions** - Tutti comandi keyboard funzionano
- [ ] **Manual test suite** - Tutti scenari critici passati:
  - [ ] App start → Menu panel visible
  - [ ] Menu → Nuova partita → Gameplay
  - [ ] Gameplay → ESC abandon → Dialog → Confirm → Menu
  - [ ] Gameplay → ESC abandon → Dialog → Cancel → Gameplay
  - [ ] Gameplay → N key → Dialog → Confirm → New game
  - [ ] Menu → Opzioni → Modify → ESC → Save prompt
  - [ ] Menu → Esci → Dialog → Confirm → App closes
  - [ ] Timer STRICT → Expiration → Menu transition
  - [ ] Victory → Rematch → New game
  - [ ] Victory → Decline → Menu

---

## 🚨 Common Pitfalls

### Pitfall 1: Container Circular Dependency

**Sintomo**: ValueError "Circular dependency detected"

**Causa**: Factory function chiama resolve() per dipendenza che a sua volta richiede la prima

**Soluzione**:
```python
# ❌ WRONG - Circular
container.register("a", lambda: ClassA(b=container.resolve("b")))
container.register("b", lambda: ClassB(a=container.resolve("a")))

# ✅ CORRECT - Break cycle with setter
container.register("a", lambda: ClassA())
container.register("b", lambda: ClassB())
a = container.resolve("a")
b = container.resolve("b")
a.set_b(b)  # Inject after creation
```

### Pitfall 2: WindowController senza create_window()

**Sintomo**: ValueError "Window not created yet"

**Causa**: Chiamata open_window() senza prima create_window()

**Soluzione**:
```python
# ❌ WRONG
win_ctrl.open_window(WindowKey.MENU_PANEL)  # CRASH: not created

# ✅ CORRECT
win_ctrl.create_window(WindowKey.MENU_PANEL)  # Create first
win_ctrl.open_window(WindowKey.MENU_PANEL)   # Then open
```

### Pitfall 3: Dialog async callback senza self

**Sintomo**: NameError "self not defined" in callback

**Causa**: Callback inline perde contesto self

**Soluzione**:
```python
# ❌ WRONG
def show_dialog(self):
    dialog_manager.show_async(
        callback=lambda result: self._handle(result)  # self captured OK
    )

# ✅ BETTER - Named function
def show_dialog(self):
    def on_result(result: bool):
        if result:
            self._handle()  # self in scope
    
    dialog_manager.show_async(callback=on_result)
```

### Pitfall 4: Mescolare API sync e async

**Sintomo**: Nested event loops, focus issues

**Causa**: Usare show_yes_no() (sync) e show_yes_no_async() (async) insieme

**Soluzione**: Usare SOLO async API in v2.2+
```python
# ❌ WRONG - Mixed
result = dialog_manager.show_abandon_game_prompt()  # Sync, blocks
if result:
    dialog_manager.show_new_game_prompt_async(callback)  # Async

# ✅ CORRECT - All async
dialog_manager.show_abandon_game_prompt_async(on_abandon)
def on_abandon(confirmed):
    if confirmed:
        dialog_manager.show_new_game_prompt_async(on_new_game)
```

---

## 📚 References

### External Resources

- **hs_deckmanager Repository**: https://github.com/Nemex81/hs_deckmanager
  - `scr/views/builder/dependency_container.py` - DependencyContainer implementation
  - `scr/views/view_manager.py` - WinController implementation
  - `scr/views/builder/view_factory.py` - ViewFactory + WidgetFactory
  - `scr/app_initializer.py` - Dependency registration pattern

### Internal Documentation

- `docs/IMPLEMENTATION_TIMER_STRICT_MODE_SYSTEM_v2.1.md` - Previous migration (v2.1)
- `docs/ARCHITECTURE.md` - Deferred UI Transitions Pattern (v2.1)
- `CHANGELOG.md` - Complete version history

### wxPython Documentation

- [wx.MessageDialog](https://docs.wxpython.org/wx.MessageDialog.html) - Dialog API
- [wx.Frame.Show()](https://docs.wxpython.org/wx.Frame.html#wx.Frame.Show) - Non-blocking show
- [wx.Frame.ShowModal()](https://docs.wxpython.org/wx.Dialog.html#wx.Dialog.ShowModal) - Blocking show (AVOID)

---

## 🎯 Success Criteria

### Technical Success

- ✅ **DependencyContainer implemented** - IoC funzionante
- ✅ **Factory pattern implemented** - ViewFactory + WidgetFactory
- ✅ **WindowController implemented** - Gestione gerarchica finestre
- ✅ **Async dialog API implemented** - Show() invece ShowModal()
- ✅ **test.py refactored** - Usa container e async API
- ✅ **All panels accept container** - MenuPanel, GameplayPanel

### Functional Success

- ✅ **App starts correctly** - Menu panel visible
- ✅ **Navigation works** - Menu ↔ Gameplay ↔ Options
- ✅ **Dialogs non-blocking** - Nessun hang/freeze
- ✅ **Focus management correct** - Focus torna dopo dialog
- ✅ **Screen reader friendly** - NVDA legge correttamente
- ✅ **Zero regressions** - Tutti comandi keyboard funzionano

### Quality Success

- ✅ **Code maintainability** - Dependency graph chiaro
- ✅ **Testability** - Facile mockare componenti
- ✅ **Documentation complete** - CHANGELOG, README, docstrings
- ✅ **Architectural consistency** - Pattern hs_deckmanager applicato

---

## 🤖 Instructions for GitHub Copilot Agent

### Mandatory Steps

1. **READ THIS ENTIRE DOCUMENT** - Non saltare sezioni
2. **CONSULT hs_deckmanager** - Verifica pattern source prima di implementare
3. **FOLLOW COMMIT STRATEGY EXACTLY** - 11 commit atomici nell'ordine specificato
4. **TEST AFTER EACH COMMIT** - Manual test scenario critico
5. **ASK IF UNSURE** - Stop e chiedi conferma per ambiguità

### Implementation Rules

- ✅ **DO**: Port pattern da hs_deckmanager con adattamenti minimi
- ✅ **DO**: Mantenere backward compatibility dove possibile
- ✅ **DO**: Aggiungere type hints e docstrings complete
- ✅ **DO**: Test manuale dopo ogni commit
- ❌ **DON'T**: Inventare pattern custom (usa hs_deckmanager)
- ❌ **DON'T**: Breaking changes (deprecate invece di rimuovere)
- ❌ **DON'T**: Commit multiple modifiche insieme (atomic commits)

### Quality Standards

- **Code style**: PEP 8 compliant
- **Type hints**: Dove possibile (params, returns)
- **Docstrings**: Google style, esempi inclusi
- **Comments**: Inline per logica complessa
- **Commit messages**: Conventional commits format

### Testing Requirements

**After Each Commit**:
- Syntax check (no Python errors)
- Import check (app starts)
- Manual test (one critical scenario)

**After All Commits**:
- Complete manual test suite (10+ scenari)
- Console logs review (no warnings/errors)
- NVDA screen reader test (Windows)

---

## 🎁 Deliverables

Alla fine dell'implementazione v2.2.0:

1. **11 commit atomici** - Seguendo esattamente strategy descritta
2. **6 file nuovi** - DI infrastructure + factories + WindowController
3. **5 file modificati** - Integration in test.py + panels + dialog providers
4. **CHANGELOG.md updated** - Entry v2.2.0 completa
5. **README.md updated** - Versione corrente
6. **Zero regressions** - Tutti test manuali passati
7. **Production ready** - App deployabile

---

## ⚠️ REMINDER FINALE

> **L'obiettivo è PORT del pattern hs_deckmanager per eliminare nested event loops e migliorare architettura. NO invenzioni, SOLO adattamenti del pattern esistente testato e funzionante.**

**Versione Target**: 2.2.0  
**Tipo Release**: MINOR (architectural changes, backward compatible)  
**Riferimento**: [hs_deckmanager](https://github.com/Nemex81/hs_deckmanager)

---

**Fine Documento**
