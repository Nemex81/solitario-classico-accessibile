# Piano Implementazione: Refactoring wxPython Completo (Pattern hs_deckmanager)

**Progetto**: Solitario Classico Accessibile  
**Branch**: `copilot/remove-pygame-migrate-wxpython` (Issue #59)  
**Data**: 12 Febbraio 2026  
**Versione Target**: v2.0.0  
**Modello Architetturale**: hs_deckmanager (wxPython nativo puro)

---

## 📋 Executive Summary

### Obiettivo Principale

Eliminare **completamente** le dipendenze pygame e consolidare l'uso di **wxPython come unico framework** per:
- Gestione finestre (visibili e funzionali)
- Dialog box native modali
- Meccaniche di gioco e input utente
- Event loop nativo wxPython

### Modello di Riferimento

Il progetto **hs_deckmanager** (https://github.com/Nemex81/hs_deckmanager) fornisce il pattern architetturale target:

**Pattern Chiave hs_deckmanager**:
1. ✅ `wx.Frame` visibile come finestra principale (non invisibile 1x1px)
2. ✅ `wx.Dialog` per finestre secondarie modali
3. ✅ `wx.EVT_CHAR_HOOK` per cattura eventi tastiera globali
4. ✅ `Bind(wx.EVT_SET_FOCUS)` per focus management esplicito
5. ✅ Parent-child hierarchy corretta per gestione finestre
6. ✅ View Manager pattern per stack finestre multiple
7. ✅ BasicView base class per riuso componenti UI
8. ✅ Builder pattern per creazione widget consistenti

### Problema Attuale Identificato

Analizzando il branch `copilot/remove-pygame-migrate-wxpython` è emerso:

**BUG CRITICO**: `SolitarioFrame` configurato come **invisibile** (1x1 pixel):
```python
# src/infrastructure/ui/wx_frame.py - CONFIGURAZIONE ERRATA
size=(1, 1),  # ❌ Troppo piccola per ricevere focus OS
style=wx.FRAME_NO_TASKBAR  # ❌ Invisibile in taskbar
```

**Conseguenza**: Il window manager del sistema operativo **nega focus** alle finestre 1x1 pixel per policy sicurezza. wxPython non può bypassare questa restrizione (diversamente da pygame con SDL).

**Risultato**: Nessun evento tastiera catturato → app non risponde agli input.

### Soluzione: Adottare Pattern hs_deckmanager

Invece di frame invisibile per "headless audiogame", usare **frame minimizzato ma funzionale**:

```python
# SOLUZIONE hs_deckmanager pattern
size=(400, 300),  # Finestra piccola ma visibile per OS
style=wx.DEFAULT_FRAME_STYLE  # Frame normale accessibile

# Post-init
self.Iconize()  # Minimizza ma mantiene focus
```

---

## 🏗️ Architettura Target (Pattern hs_deckmanager)

### Struttura Progetto Finale

```
src/
├── domain/                    [INVARIATO - Clean Architecture]
│   ├── models/
│   ├── rules/
│   └── services/
│
├── application/               [INVARIATO]
│   ├── game_engine.py
│   ├── gameplay_controller.py
│   ├── options_controller.py
│   └── dialog_manager.py
│
├── infrastructure/
│   ├── accessibility/         [INVARIATO]
│   │   ├── screen_reader.py
│   │   └── tts_provider.py
│   │
│   └── ui/                    [REFACTORING COMPLETO - hs_deckmanager pattern]
│       ├── __init__.py
│       │
│       ├── wx_app.py          🆕 Main wx.App (SolitarioWxApp)
│       ├── wx_frame.py        🔧 Frame VISIBILE minimizzato (400x300)
│       │
│       ├── view_manager.py    🆕 Stack finestre (pattern hs_deckmanager)
│       ├── basic_view.py      🆕 Base class per view (come BasicView)
│       │
│       ├── menu_view.py       🆕 Menu principale wxPython nativo
│       ├── gameplay_view.py   🆕 Schermata gameplay (audiogame mode)
│       ├── options_view.py    🔧 Finestra opzioni wx nativa
│       │
│       └── dialogs/
│           ├── __init__.py
│           ├── dialog_provider.py     🔧 Interface astratta
│           ├── wx_dialog_provider.py  [ESISTENTE - mantenuto]
│           └── confirmation_dialog.py 🆕 Dialog riusabili
│
└── presentation/              [INVARIATO]
    └── formatters/

main.py                        🆕 Entry point principale (sostituisce test.py)
test.py                        [DEPRECATO - rinominato test_legacy.py]
```

### Componenti da Creare (Pattern hs_deckmanager)

#### 1. `view_manager.py` - Gestione Stack Finestre

**Ispirato a**: `scr/views/view_manager.py` di hs_deckmanager

**Responsabilità**:
- Gestire stack finestre multiple (menu → gameplay → options)
- Push/pop view con transizioni
- Nascondere view precedenti quando nuova aperta
- Ripristinare view precedente quando corrente chiusa

**API Pubblica**:
```python
class ViewManager:
    def __init__(self, parent_frame: wx.Frame):
        self.parent_frame = parent_frame
        self.views_stack: List[wx.Frame] = []
        self.view_constructors: Dict[str, Callable] = {}
    
    def register_view(self, name: str, constructor: Callable):
        """Registra constructor per view (factory pattern)."""
        pass
    
    def push_view(self, name: str, **kwargs) -> wx.Frame:
        """Crea e mostra nuova view (nasconde precedente)."""
        pass
    
    def pop_view(self) -> bool:
        """Chiudi view corrente e ripristina precedente."""
        pass
    
    def get_current_view(self) -> Optional[wx.Frame]:
        """Ritorna view attualmente visibile."""
        pass
```

**Esempio Utilizzo** (come hs_deckmanager):
```python
# Setup
vm = ViewManager(parent_frame=main_frame)
vm.register_view('menu', lambda parent: MenuView(parent, controller))
vm.register_view('gameplay', lambda parent: GameplayView(parent, controller))

# Navigazione
vm.push_view('menu')      # Mostra menu
vm.push_view('gameplay')  # Gameplay sopra menu (menu nascosto)
vm.pop_view()             # Chiudi gameplay, ritorna a menu
```

#### 2. `basic_view.py` - Base Class per View

**Ispirato a**: `scr/views/builder/proto_views.py::BasicView` di hs_deckmanager

**Responsabilità**:
- Setup automatico panel/sizer
- Focus management integrato
- Keyboard event routing
- Close handlers
- TTS announcements per accessibility

**Struttura**:
```python
class BasicView(wx.Frame):
    """Base class per finestre applicazione (pattern hs_deckmanager).
    
    Features:
    - Setup panel/sizer automatico
    - Focus management integrato
    - Keyboard event routing via EVT_CHAR_HOOK
    - Close handlers customizzabili
    - Screen reader announcements
    
    Usage:
        class MenuView(BasicView):
            def init_ui_elements(self):
                btn = wx.Button(self.panel, label="Gioca")
                self.sizer.Add(btn, flag=wx.ALL, border=10)
    """
    
    def __init__(
        self, 
        parent: Optional[wx.Frame],
        controller: Optional[object],
        title: str,
        size: tuple = (800, 600),
        **kwargs
    ):
        super().__init__(parent, title=title, size=size, **kwargs)
        
        self.controller = controller
        self.screen_reader = controller.screen_reader if controller else None
        
        # Setup base (come hs_deckmanager)
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)
        
        # Bind eventi globali
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        
        # Hook per subclasses
        self.init_ui_elements()
        
        self.Layout()
        self.Centre()
    
    def init_ui_elements(self):
        """Override in subclass per UI elements."""
        pass
    
    def on_key_down(self, event: wx.KeyEvent):
        """Gestione tasti globale (EVT_CHAR_HOOK)."""
        event.Skip()  # Propagazione default
    
    def on_focus(self, event: wx.FocusEvent):
        """Focus gained - announce per screen reader."""
        event.Skip()
    
    def on_close(self, event: wx.CloseEvent):
        """Cleanup prima chiusura."""
        event.Skip()
    
    def announce(self, message: str, interrupt: bool = False):
        """Helper TTS announcement."""
        if self.screen_reader:
            self.screen_reader.tts.speak(message, interrupt=interrupt)
```

#### 3. `menu_view.py` - Menu Principale Nativo

**Ispirato a**: `scr/views/main_views.py::HearthstoneAppFrame` di hs_deckmanager

**Differenza vs Menu Virtuale**:
- ❌ Vecchio: Menu testuale navigabile solo con UP/DOWN/ENTER
- ✅ Nuovo: `wx.Button` reali navigabili con TAB + screen reader friendly

**Implementazione**:
```python
class MenuView(BasicView):
    """Menu principale wxPython (pattern hs_deckmanager)."""
    
    def __init__(self, parent, controller, **kwargs):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Solitario Classico Accessibile - Menu",
            size=(600, 400),
            **kwargs
        )
    
    def init_ui_elements(self):
        """Crea pulsanti menu (come hs_deckmanager button layout)."""
        
        # Titolo
        title = wx.StaticText(self.panel, label="Menu Principale")
        title.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.sizer.Add(title, flag=wx.CENTER | wx.TOP, border=20)
        
        # Pulsanti (layout verticale come hs_deckmanager)
        btn_play = wx.Button(self.panel, label="Gioca al solitario classico")
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_click)
        btn_play.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        btn_options = wx.Button(self.panel, label="Opzioni di gioco")
        btn_options.Bind(wx.EVT_BUTTON, self.on_options_click)
        btn_options.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        btn_exit = wx.Button(self.panel, label="Esci dal gioco")
        btn_exit.Bind(wx.EVT_BUTTON, self.on_exit_click)
        btn_exit.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        # Layout
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        for btn in [btn_play, btn_options, btn_exit]:
            btn_sizer.Add(btn, 0, wx.ALL | wx.EXPAND, 20)
        
        self.sizer.Add(btn_sizer, 1, wx.ALIGN_CENTER)
        
        # Focus iniziale
        btn_play.SetFocus()
        self.announce("Menu principale. 3 opzioni disponibili.", interrupt=True)
    
    def on_button_focus(self, event):
        """Annuncia pulsante quando riceve focus (accessibility)."""
        button = event.GetEventObject()
        self.announce(button.GetLabel(), interrupt=False)
        event.Skip()
    
    def on_play_click(self, event):
        """Avvia gameplay."""
        self.controller.start_gameplay()
    
    def on_options_click(self, event):
        """Apri opzioni."""
        self.controller.show_options()
    
    def on_exit_click(self, event):
        """Conferma uscita."""
        self.controller.show_exit_dialog()
```

#### 4. `gameplay_view.py` - Schermata Gameplay Audiogame

**Responsabilità**:
- Catturare TUTTI gli eventi tastiera per comandi gameplay
- Nessun widget visibile (audiogame puro)
- Forward eventi a `GameplayController` esistente
- Gestire ESC (singolo vs doppio)

**Implementazione**:
```python
class GameplayView(BasicView):
    """Schermata gameplay audiogame (no UI visibile)."""
    
    def __init__(self, parent, controller, **kwargs):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Solitario - Partita in corso",
            size=(400, 300),
            **kwargs
        )
        
        self.last_esc_time = 0  # Per double-ESC detection
    
    def init_ui_elements(self):
        """Audiogame - no UI elements."""
        # Panel vuoto (audiogame mode)
        label = wx.StaticText(
            self.panel, 
            label="Partita in corso\n\nPremi H per comandi disponibili"
        )
        label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.sizer.Add(label, 1, wx.ALIGN_CENTER)
    
    def on_key_down(self, event: wx.KeyEvent):
        """Route tutti i tasti a GameplayController."""
        key_code = event.GetKeyCode()
        
        # ESC handling (singolo vs doppio)
        if key_code == wx.WXK_ESCAPE:
            self._handle_esc(event)
            return
        
        # Altri comandi → gameplay controller
        self.controller.gameplay_controller.handle_wx_key_event(event)
        event.Skip()
    
    def _handle_esc(self, event: wx.KeyEvent):
        """Gestione ESC context-aware con double-tap."""
        import time
        current_time = time.time()
        
        # Double-ESC detection (< 2 sec)
        if self.last_esc_time > 0 and current_time - self.last_esc_time <= 2.0:
            # Double-ESC: instant abandon
            self.announce("Uscita rapida!", interrupt=True)
            self.controller.confirm_abandon_game(skip_dialog=True)
            self.last_esc_time = 0
        else:
            # First ESC: show dialog
            self.last_esc_time = current_time
            self.controller.show_abandon_game_dialog()
```

---

## 📝 Piano Implementazione a 6 Commit Atomici

### Strategia

**Branch di lavoro**: `copilot/remove-pygame-migrate-wxpython`  
**Approccio**: Commit incrementali atomici testabili singolarmente

---

### COMMIT 1: Fix Critico - Frame Visibile Minimizzato

**Obiettivo**: Rendere `SolitarioFrame` **funzionale** per cattura eventi tastiera.

**Priorità**: 🔴 **CRITICA** - Blocca tutto il resto

#### File Modificati

**1. `src/infrastructure/ui/wx_frame.py`**

```python
# MODIFICHE:

class SolitarioFrame(wx.Frame):
    def __init__(
        self,
        on_key_event: Optional[Callable[[wx.KeyEvent], None]] = None,
        on_timer_tick: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        title: str = "Solitario Classico Accessibile"
    ):
        # === CAMBIO 1: Size funzionale per OS focus ===
        # PRIMA: size=(1, 1), style=wx.FRAME_NO_TASKBAR
        # DOPO:
        super().__init__(
            None, 
            title=title, 
            size=(400, 300),  # ✅ Visibile per window manager
            style=wx.DEFAULT_FRAME_STYLE  # ✅ Frame normale
        )
        
        self.on_key_event = on_key_event
        self.on_timer_tick = on_timer_tick
        self.on_close_callback = on_close
        
        # === CAMBIO 2: Setup panel per future view ===
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Placeholder text (temporaneo)
        label = wx.StaticText(
            self.panel,
            label="Solitario Classico Accessibile\n\nFrame principale wxPython"
        )
        self.sizer.Add(label, 1, wx.ALIGN_CENTER)
        self.panel.SetSizer(self.sizer)
        
        # === CAMBIO 3: Event bindings con EVT_CHAR_HOOK ===
        # PRIMA: solo EVT_KEY_DOWN
        # DOPO: EVT_CHAR_HOOK per cattura globale (hs_deckmanager pattern)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        
        # Timer setup (invariato)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer_tick)
        
        # === CAMBIO 4: Post-init window configuration ===
        self.Centre()  # Centra sullo schermo
        self.Show()    # Mostra frame
        self.Iconize() # ✅ Minimizza ma mantiene focus
        
        self.Layout()
    
    def _on_char_hook(self, event: wx.KeyEvent):
        """Hook globale per tastiera (EVT_CHAR_HOOK vs EVT_KEY_DOWN).
        
        EVT_CHAR_HOOK è chiamato PRIMA del routing normale,
        permettendo intercettazione globale anche senza focus su widget.
        Necessario per audiogame.
        """
        if self.on_key_event is not None:
            self.on_key_event(event)
        
        # CRITICAL: Skip per permettere propagazione
        event.Skip()
    
    # ... resto metodi invariato ...
```

**Rationale**:
- Frame 400x300 è **piccolo ma visibile** per window manager
- `Iconize()` minimizza in taskbar ma **mantiene focus** per eventi
- `wx.EVT_CHAR_HOOK` cattura eventi **prima** del routing normale
- Accessibile con ALT+TAB per utenti che vogliono vedere finestra

#### Testing COMMIT 1

**Test A**: Frame riceve eventi tastiera
```python
# Script test: test_frame_events.py
import wx
from src.infrastructure.ui.wx_frame import SolitarioFrame

def on_key(event):
    print(f"Key pressed: {event.GetKeyCode()}")

app = wx.App()
frame = SolitarioFrame(on_key_event=on_key)
app.MainLoop()
```

**Expected**:
- ✅ Frame minimizzato visibile in taskbar
- ✅ Pressione tasti stampa key codes
- ✅ Frecce, ENTER, ESC, lettere funzionano

**Test B**: NVDA compatibility
```
1. Avvia app con NVDA attivo
2. ALT+TAB su frame minimizzato
3. NVDA annuncia: "Solitario Classico Accessibile"
4. Premi H → NVDA annuncia key press
```

**Acceptance Criteria**:
- [ ] Frame visibile in taskbar quando minimizzato
- [ ] Eventi tastiera catturati al 100%
- [ ] NVDA annuncia titolo frame su focus
- [ ] ALT+F4 chiude app correttamente

**Commit Message**:
```
feat(ui): Make SolitarioFrame visible and functional for OS focus

CRITICAL FIX: Previous 1x1px invisible frame was denied focus by OS window 
manager, preventing keyboard event capture.

Changes:
- Frame size: 1x1px → 400x300px (visible for OS)
- Style: FRAME_NO_TASKBAR → DEFAULT_FRAME_STYLE
- Add EVT_CHAR_HOOK for global keyboard capture (hs_deckmanager pattern)
- Add Iconize() to minimize but maintain focus
- Add panel/sizer setup for future view integration

Testing:
- Manual: All keyboard events captured successfully
- NVDA: Frame title announced on focus
- Taskbar: Frame visible and accessible via ALT+TAB

Based on hs_deckmanager pattern analysis.

References: #59
```

---

### COMMIT 2: Parent Hierarchy per Dialog Box

**Obiettivo**: Dialog box come **modal children** del frame principale (no separazione ALT+TAB).

**Priorità**: 🔴 **CRITICA** - UX accessibility

#### File Modificati

**1. `src/infrastructure/ui/dialogs/wx_dialog_provider.py`**

```python
# MODIFICHE:

class WxDialogProvider(DialogProvider):
    def __init__(self, parent_frame: Optional[wx.Frame] = None):
        """
        Initialize con riferimento al frame principale.
        
        Args:
            parent_frame: wx.Frame principale (SolitarioFrame).
                          Dialog saranno modal children di questo frame.
        
        Pattern: Come DeckStatsDialog di hs_deckmanager che riceve
                 parent frame nel costruttore.
        """
        self.parent_frame = parent_frame
    
    def show_confirmation(
        self, 
        title: str, 
        message: str, 
        default_no: bool = True
    ) -> bool:
        """
        Mostra dialog conferma Sì/No.
        
        Args:
            title: Titolo dialog
            message: Testo messaggio
            default_no: Se True, focus iniziale su No (safety)
        
        Returns:
            True se Sì selezionato, False altrimenti
        """
        # === CAMBIO 1: Parent esplicito ===
        # PRIMA: parent=None (dialog root-level)
        # DOPO: parent=self.parent_frame (modal child)
        
        dlg = wx.MessageDialog(
            self.parent_frame,  # ✅ Parent corretto
            message=message,
            caption=title,
            style=wx.YES_NO | (
                wx.NO_DEFAULT if default_no else wx.YES_DEFAULT
            ) | wx.ICON_QUESTION
        )
        
        # === CAMBIO 2: Modalità bloccante garantita ===
        result = dlg.ShowModal()  # Blocca fino a chiusura
        dlg.Destroy()
        
        # === CAMBIO 3: Flush eventi pending ===
        wx.Yield()  # Permette elaborazione eventi accumulati
        
        return result == wx.ID_YES
    
    def show_info(self, title: str, message: str):
        """Mostra dialog informativo."""
        dlg = wx.MessageDialog(
            self.parent_frame,  # ✅ Parent corretto
            message=message,
            caption=title,
            style=wx.OK | wx.ICON_INFORMATION
        )
        dlg.ShowModal()
        dlg.Destroy()
        wx.Yield()
    
    def show_statistics_report(
        self, 
        title: str, 
        stats_text: str
    ) -> bool:
        """
        Mostra report statistiche con opzione rematch.
        
        Returns:
            True se utente vuole giocare ancora, False altrimenti
        """
        # Dialog statistiche (readonly)
        stats_dlg = wx.MessageDialog(
            self.parent_frame,  # ✅ Parent corretto
            message=stats_text,
            caption=title,
            style=wx.OK | wx.ICON_INFORMATION
        )
        stats_dlg.ShowModal()
        stats_dlg.Destroy()
        wx.Yield()
        
        # Dialog rematch
        rematch_dlg = wx.MessageDialog(
            self.parent_frame,  # ✅ Parent corretto
            message="Vuoi giocare ancora?",
            caption="Nuova partita",
            style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        )
        result = rematch_dlg.ShowModal()
        rematch_dlg.Destroy()
        wx.Yield()
        
        return result == wx.ID_YES
```

**2. `test.py` (Controller principale)**

```python
# MODIFICHE nella classe SolitarioController:

class SolitarioController:
    def __init__(self):
        # ... setup esistente ...
        self.frame: Optional[SolitarioFrame] = None
        self.dialog_manager: Optional[SolitarioDialogManager] = None
    
    def run(self):
        """Avvia applicazione wxPython."""
        
        def on_init_complete(app: SolitarioWxApp):
            # Crea frame principale
            self.frame = SolitarioFrame(
                on_key_event=self.handle_keyboard_event,
                on_timer_tick=self.handle_timer_tick,
                on_close=self.handle_close
            )
            
            # === CAMBIO: Passa frame a DialogManager ===
            # PRIMA: dialog_manager senza parent
            # DOPO: dialog_manager con parent_frame
            
            dialog_provider = WxDialogProvider(
                parent_frame=self.frame  # ✅ Parent esplicito
            )
            
            self.dialog_manager = SolitarioDialogManager(
                dialog_provider=dialog_provider,
                # ... altri params ...
            )
            
            # ... resto init ...
        
        # Avvia wx.MainLoop
        self.app = SolitarioWxApp(on_init_complete=on_init_complete)
        self.app.MainLoop()
```

#### Testing COMMIT 2

**Test A**: Dialog come modal children
```
1. Avvia app
2. Trigger dialog conferma (es. ESC per uscita)
3. Dialog appare SOPRA frame minimizzato
4. ALT+TAB mostra solo 1 finestra (dialog, non frame+dialog)
5. ESC chiude dialog
6. Focus ritorna a frame
```

**Test B**: NVDA focus in dialog
```
1. Apri dialog con NVDA attivo
2. NVDA annuncia titolo dialog + messaggio
3. TAB cicla tra pulsanti Sì/No
4. NVDA annuncia ciascun pulsante
5. ENTER conferma selezione
6. NVDA annuncia chiusura dialog
```

**Acceptance Criteria**:
- [ ] Dialog appare come modal child (no separazione ALT+TAB)
- [ ] ESC chiude dialog e ritorna a frame
- [ ] TAB cicla pulsanti in dialog
- [ ] NVDA legge contenuto dialog automaticamente
- [ ] Focus management corretto (dialog → frame)

**Commit Message**:
```
feat(ui): Implement dialog parent hierarchy for modal behavior

Fix dialog box appearing as separate windows in ALT+TAB. All dialogs
now created as modal children of SolitarioFrame (hs_deckmanager pattern).

Changes:
- WxDialogProvider: Add parent_frame parameter in constructor
- All dialog methods: Use parent_frame instead of None
- SolitarioController: Pass frame instance to DialogManager
- Add wx.Yield() after dialog destroy for event flush

Benefits:
- Single window in ALT+TAB (better UX)
- Modal behavior guaranteed (blocks parent frame)
- NVDA focus management improved
- Consistent with hs_deckmanager pattern

Testing:
- Manual: All dialogs appear as modal children
- NVDA: Focus automatically on dialog open, returns to frame on close
- ALT+TAB: Only one window visible

References: #59
```

---

### COMMIT 3: View Manager per Stack Finestre

**Obiettivo**: Implementare pattern hs_deckmanager per gestione finestre multiple.

**Priorità**: 🟡 **ALTA** - Architettura core

#### File Creati

**1. `src/infrastructure/ui/view_manager.py`**

```python
"""
View Manager per gestione stack finestre multiple.

Pattern: Ispirato a scr/views/view_manager.py di hs_deckmanager
Usage:
    vm = ViewManager(parent_frame)
    vm.register_view('menu', create_menu_view)
    vm.push_view('menu')      # Mostra menu
    vm.push_view('gameplay')  # Gameplay sopra menu (menu nascosto)
    vm.pop_view()             # Chiudi gameplay, ripristina menu
"""

import wx
from typing import List, Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class ViewManager:
    """Gestisce stack finestre multiple (pattern hs_deckmanager).
    
    Attributes:
        parent_frame: Frame principale (SolitarioFrame)
        views_stack: Stack finestre attive (LIFO)
        view_constructors: Factory methods per creare view
    
    Example:
        >>> vm = ViewManager(parent_frame=main_frame)
        >>> vm.register_view('menu', lambda p: MenuView(p, controller))
        >>> vm.push_view('menu')  # Mostra menu
        >>> vm.push_view('gameplay')  # Gameplay sopra menu
        >>> vm.pop_view()  # Torna a menu
    """
    
    def __init__(self, parent_frame: wx.Frame):
        """
        Args:
            parent_frame: Frame principale (SolitarioFrame) che contiene stack
        """
        self.parent_frame = parent_frame
        self.views_stack: List[wx.Frame] = []
        self.view_constructors: Dict[str, Callable] = {}
        
        logger.debug("ViewManager initialized")
    
    def register_view(self, name: str, constructor: Callable[[wx.Frame], wx.Frame]):
        """
        Registra constructor per view (factory pattern).
        
        Args:
            name: Nome univoco view (es. 'menu', 'gameplay')
            constructor: Callable che accetta parent e ritorna wx.Frame
                         Signature: (parent: wx.Frame) -> wx.Frame
        
        Example:
            >>> vm.register_view(
            ...     'menu',
            ...     lambda parent: MenuView(parent, controller)
            ... )
        """
        if name in self.view_constructors:
            logger.warning(f"View '{name}' already registered, overwriting")
        
        self.view_constructors[name] = constructor
        logger.debug(f"View '{name}' registered")
    
    def push_view(self, name: str, **kwargs) -> Optional[wx.Frame]:
        """
        Crea e mostra nuova view (nasconde precedente).
        
        Args:
            name: Nome view registrata
            **kwargs: Parametri aggiuntivi per constructor
        
        Returns:
            Nuova view creata, o None se nome non trovato
        
        Behavior:
            1. Nasconde view corrente (se esiste)
            2. Crea nuova view usando constructor
            3. Mostra nuova view
            4. Set focus su nuova view
            5. Push view su stack
        """
        if name not in self.view_constructors:
            logger.error(f"View '{name}' not registered")
            return None
        
        # Nascondi view corrente
        if self.views_stack:
            current_view = self.views_stack[-1]
            current_view.Hide()
            logger.debug(f"Hidden current view: {current_view.GetTitle()}")
        
        # Crea nuova view
        try:
            view = self.view_constructors[name](self.parent_frame, **kwargs)
        except Exception as e:
            logger.error(f"Failed to create view '{name}': {e}")
            # Ripristina view precedente se creazione fallisce
            if self.views_stack:
                self.views_stack[-1].Show()
            return None
        
        # Mostra e focus
        view.Show()
        view.SetFocus()
        
        # Push su stack
        self.views_stack.append(view)
        logger.info(f"Pushed view '{name}', stack depth: {len(self.views_stack)}")
        
        return view
    
    def pop_view(self) -> bool:
        """
        Chiudi view corrente e ripristina precedente.
        
        Returns:
            True se pop riuscito, False se stack vuoto
        
        Behavior:
            1. Pop view da stack
            2. Chiudi e distruggi view
            3. Ripristina view precedente (se esiste)
            4. Set focus su view precedente
        """
        if not self.views_stack:
            logger.warning("Cannot pop: views stack is empty")
            return False
        
        # Pop view corrente
        current_view = self.views_stack.pop()
        current_title = current_view.GetTitle()
        
        # Chiudi e distruggi
        current_view.Close()
        current_view.Destroy()
        logger.debug(f"Destroyed view: {current_title}")
        
        # Ripristina view precedente
        if self.views_stack:
            prev_view = self.views_stack[-1]
            prev_view.Show()
            prev_view.SetFocus()
            logger.info(
                f"Popped view '{current_title}', "
                f"restored '{prev_view.GetTitle()}', "
                f"stack depth: {len(self.views_stack)}"
            )
        else:
            logger.info(f"Popped view '{current_title}', stack now empty")
        
        return True
    
    def get_current_view(self) -> Optional[wx.Frame]:
        """
        Ritorna view attualmente visibile (top of stack).
        
        Returns:
            View corrente, o None se stack vuoto
        """
        return self.views_stack[-1] if self.views_stack else None
    
    def clear_stack(self):
        """
        Chiudi tutte le view e svuota stack.
        
        Warning: Usare solo durante shutdown applicazione.
        """
        logger.info(f"Clearing stack with {len(self.views_stack)} views")
        
        while self.views_stack:
            view = self.views_stack.pop()
            view.Close()
            view.Destroy()
        
        logger.debug("Stack cleared")
    
    def __len__(self) -> int:
        """Returns stack depth."""
        return len(self.views_stack)
```

#### Testing COMMIT 3

**Test Unit** (`tests/infrastructure/test_view_manager.py`):
```python
import pytest
import wx
from src.infrastructure.ui.view_manager import ViewManager

class DummyView(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(200, 200))

@pytest.fixture
def view_manager():
    app = wx.App()
    parent = wx.Frame(None, title="Parent")
    vm = ViewManager(parent)
    yield vm
    parent.Destroy()
    app.Destroy()

def test_register_view(view_manager):
    view_manager.register_view(
        'test',
        lambda parent: DummyView(parent, "Test")
    )
    assert 'test' in view_manager.view_constructors

def test_push_view(view_manager):
    view_manager.register_view(
        'test',
        lambda parent: DummyView(parent, "Test")
    )
    view = view_manager.push_view('test')
    assert view is not None
    assert len(view_manager) == 1
    assert view_manager.get_current_view() == view

def test_pop_view(view_manager):
    view_manager.register_view(
        'test',
        lambda parent: DummyView(parent, "Test")
    )
    view_manager.push_view('test')
    result = view_manager.pop_view()
    assert result is True
    assert len(view_manager) == 0
```

**Acceptance Criteria**:
- [ ] Unit tests passano al 100%
- [ ] Stack depth corretto dopo push/pop
- [ ] View precedente ripristinata dopo pop
- [ ] Clear stack funziona

**Commit Message**:
```
feat(ui): Add ViewManager for multi-window stack management

Implement ViewManager pattern from hs_deckmanager for managing multiple
window views (menu, gameplay, options) in LIFO stack.

Features:
- register_view(): Factory pattern for view constructors
- push_view(): Create and show new view (hide previous)
- pop_view(): Close current and restore previous
- get_current_view(): Get top of stack
- clear_stack(): Cleanup on shutdown

Benefits:
- Clean navigation between windows
- Previous view state preserved when hidden
- Memory efficient (destroy on pop)
- Unit tested (pytest)

Testing:
- Unit: 5 tests covering core operations
- Integration: Manual navigation menu → gameplay → menu

References: #59, hs_deckmanager pattern
```

---

### COMMIT 4: BasicView Base Class

**Obiettivo**: Creare base class riusabile per tutte le view.

**Priorità**: 🟡 **ALTA** - Riuso codice

#### File Creato

**1. `src/infrastructure/ui/basic_view.py`**

[Codice completo come specificato nella sezione "Architettura Target" - BasicView class]

#### Testing COMMIT 4

**Test**: Creare view minimale derivata da BasicView
```python
# Test script: test_basic_view.py
from src.infrastructure.ui.basic_view import BasicView
import wx

class TestView(BasicView):
    def init_ui_elements(self):
        btn = wx.Button(self.panel, label="Test Button")
        self.sizer.Add(btn, flag=wx.ALL, border=10)

app = wx.App()
view = TestView(
    parent=None,
    controller=None,
    title="Test View",
    size=(400, 300)
)
view.Show()
app.MainLoop()
```

**Expected**:
- ✅ Finestra visibile con pulsante
- ✅ Eventi tastiera catturati (EVT_CHAR_HOOK)
- ✅ ESC chiude finestra

**Acceptance Criteria**:
- [ ] BasicView inizializzabile
- [ ] init_ui_elements() chiamato automaticamente
- [ ] Panel/sizer setup automatico
- [ ] Eventi tastiera catturati

**Commit Message**:
```
feat(ui): Add BasicView base class for consistent view structure

Implement BasicView pattern from hs_deckmanager proto_views for code reuse
across all window views.

Features:
- Auto setup panel/sizer in __init__
- Event bindings: EVT_CHAR_HOOK, EVT_CLOSE, EVT_SET_FOCUS
- Template method pattern: init_ui_elements() hook
- TTS announce() helper for accessibility
- Consistent centering and layout

Benefits:
- Reduce boilerplate in MenuView, GameplayView, OptionsView
- Consistent keyboard handling across views
- Accessibility integrated from start

Testing:
- Manual: Test view with button created successfully
- Keyboard: All events captured via EVT_CHAR_HOOK

References: #59, hs_deckmanager BasicView
```

---

### COMMIT 5: MenuView e GameplayView Native

**Obiettivo**: Sostituire menu virtuale testuale con UI wxPython nativa.

**Priorità**: 🟢 **MEDIA** - Feature core

#### File Creati

**1. `src/infrastructure/ui/menu_view.py`**

[Codice completo come specificato nella sezione "Architettura Target" - MenuView class]

**2. `src/infrastructure/ui/gameplay_view.py`**

[Codice completo come specificato nella sezione "Architettura Target" - GameplayView class]

#### Testing COMMIT 5

**Test A**: MenuView navigazione
```
1. Avvia MenuView standalone
2. TAB naviga tra pulsanti
3. NVDA annuncia label pulsante su focus
4. ENTER su "Gioca" chiama callback
5. ESC chiude finestra (future: exit dialog)
```

**Test B**: GameplayView keyboard capture
```
1. Avvia GameplayView standalone
2. Premi tasti 1-7 → catturati
3. Premi H → catturato (help)
4. Premi ESC → _handle_esc chiamato
5. Doppio ESC (< 2 sec) → instant abandon
```

**Acceptance Criteria**:
- [ ] MenuView pulsanti navigabili con TAB
- [ ] NVDA annuncia pulsanti su focus
- [ ] GameplayView cattura tutti i tasti
- [ ] Double-ESC detection funziona

**Commit Message**:
```
feat(ui): Add MenuView and GameplayView with native wx UI

Replace pygame virtual menu with native wxPython button-based menu.
GameplayView implements audiogame mode with full keyboard capture.

MenuView (hs_deckmanager pattern):
- wx.Button widgets (TAB navigable)
- EVT_SET_FOCUS announcements for NVDA
- Callbacks for play/options/exit

GameplayView (audiogame mode):
- Empty panel (audiogame, no visual UI)
- EVT_CHAR_HOOK captures all keyboard
- Double-ESC detection for quick exit
- Forward events to GameplayController

Testing:
- MenuView: TAB navigation, NVDA announcements confirmed
- GameplayView: All 60+ commands captured successfully
- Double-ESC: 2-second threshold validated

References: #59
```

---

### COMMIT 6: Integrazione ViewManager in Controller

**Obiettivo**: Collegare tutti i componenti nel controller principale.

**Priorità**: 🟢 **MEDIA** - Integrazione finale

#### File Modificati

**1. `test.py` (Controller principale)**

```python
# MODIFICHE COMPLETE:

from src.infrastructure.ui.view_manager import ViewManager
from src.infrastructure.ui.menu_view import MenuView
from src.infrastructure.ui.gameplay_view import GameplayView

class SolitarioController:
    def __init__(self):
        # ... setup esistente ...
        self.view_manager: Optional[ViewManager] = None
    
    def run(self):
        """Avvia applicazione wxPython con ViewManager."""
        
        def on_init_complete(app: SolitarioWxApp):
            # Setup frame
            self.frame = SolitarioFrame(
                on_key_event=None,  # Eventi gestiti da view
                on_timer_tick=self.handle_timer_tick,
                on_close=self.handle_close
            )
            
            # Setup view manager
            self.view_manager = ViewManager(self.frame)
            
            # Register view constructors
            self.view_manager.register_view(
                'menu',
                lambda parent: MenuView(parent, controller=self)
            )
            self.view_manager.register_view(
                'gameplay',
                lambda parent: GameplayView(parent, controller=self)
            )
            
            # Setup dialog manager con parent
            dialog_provider = WxDialogProvider(parent_frame=self.frame)
            self.dialog_manager = SolitarioDialogManager(
                dialog_provider=dialog_provider,
                # ... params ...
            )
            
            # Mostra menu iniziale
            self.view_manager.push_view('menu')
        
        # Avvia wx.MainLoop
        self.app = SolitarioWxApp(on_init_complete=on_init_complete)
        self.app.MainLoop()
    
    # Nuovi metodi per navigazione view
    
    def start_gameplay(self):
        """Avvia gameplay view."""
        self.view_manager.push_view('gameplay')
        # ... init game engine ...
    
    def return_to_menu(self):
        """Chiudi gameplay e torna a menu."""
        self.view_manager.pop_view()
    
    def show_exit_dialog(self):
        """Mostra dialog conferma uscita."""
        result = self.dialog_manager.show_exit_app_prompt()
        if result:
            self.app.ExitMainLoop()
```

#### Testing COMMIT 6

**Test Integrazione Completa**:
```
1. Avvia app → MenuView visibile
2. TAB su "Gioca" + ENTER → GameplayView aperta
3. ESC in gameplay → Dialog conferma abbandona
4. Conferma → Ritorno a MenuView
5. NVDA annunci corretti in ogni passaggio
```

**Acceptance Criteria**:
- [ ] App avvia con MenuView
- [ ] Navigazione menu → gameplay → menu funziona
- [ ] Dialog appaiono sopra view corrente
- [ ] NVDA seguimi focus correttamente
- [ ] Timer tick funziona durante gameplay

**Commit Message**:
```
feat(ui): Integrate ViewManager into main controller

Complete integration of wxPython view system into SolitarioController.
Remove pygame event loop, use wx.MainLoop() natively.

Changes:
- SolitarioController: Add ViewManager instance
- Register MenuView and GameplayView constructors
- Implement start_gameplay(), return_to_menu() navigation
- Remove pygame.event.get() loop
- Use wx native event handling

Flow:
1. App init → ViewManager created
2. MenuView pushed as initial view
3. User selects "Gioca" → GameplayView pushed
4. User abandons → GameplayView popped, MenuView restored

Testing:
- Integration: Full menu → gameplay → menu cycle validated
- NVDA: Focus management correct across view transitions
- Timer: Continues ticking during gameplay

References: #59
```

---

## 📊 Riepilogo Piano Commit

| Commit | Priorità | File | LOC | Tempo | Descrizione |
|--------|----------|------|-----|-------|-------------|
| **1** | 🔴 Critica | `wx_frame.py` | ~80 | 1.5h | Frame visibile minimizzato |
| **2** | 🔴 Critica | `wx_dialog_provider.py`, `test.py` | ~100 | 1.5h | Dialog parent hierarchy |
| **3** | 🟡 Alta | `view_manager.py` (nuovo) | ~200 | 2h | Stack finestre manager |
| **4** | 🟡 Alta | `basic_view.py` (nuovo) | ~150 | 2h | Base class per view |
| **5** | 🟢 Media | `menu_view.py`, `gameplay_view.py` | ~250 | 3h | View native wx |
| **6** | 🟢 Media | `test.py` | ~150 | 2h | Integrazione ViewManager |

**Totale Stimato**: ~930 LOC | **12 ore** (2 giorni lavorativi)

---

## ✅ Success Criteria Finali

### Funzionalità
- ✅ Frame wxPython riceve eventi tastiera al 100%
- ✅ Dialog box sono modal children (no ALT+TAB separato)
- ✅ Menu navigabile con TAB + ENTER (no solo UP/DOWN)
- ✅ Gameplay cattura tutti i 60+ comandi esistenti
- ✅ Timer timeout funziona con wx.Timer
- ✅ Tutti i flussi esistenti (v1.x) preservati

### Accessibilità NVDA
- ✅ NVDA annuncia apertura app
- ✅ Menu pulsanti annunciati su focus
- ✅ Gameplay comandi annunciati via TTS esistente
- ✅ Dialog focus automatico e leggibili
- ✅ No conflitti hotkey NVDA

### Architettura
- ✅ Pattern hs_deckmanager implementato
- ✅ Clean Architecture preservata
- ✅ ViewManager per navigazione finestre
- ✅ BasicView riuso codice
- ✅ Zero dipendenze pygame nel codice wx

### Documentazione
- ✅ Commit messages descrittivi
- ✅ Docstring Google-style su nuovi file
- ✅ Type hints completi
- ✅ TODO checklist aggiornato

---

## 📚 Riferimenti

### Codice Modello
- [hs_deckmanager](https://github.com/Nemex81/hs_deckmanager)
  - `scr/views/main_views.py::HearthstoneAppFrame`
  - `scr/views/view_manager.py::ViewManager`
  - `scr/views/builder/proto_views.py::BasicView`
  - `scr/views/decks_view.py::DecksViewFrame`

### Documentazione wxPython
- [wx.Frame](https://docs.wxpython.org/wx.Frame.html)
- [wx.EVT_CHAR_HOOK](https://docs.wxpython.org/wx.KeyEvent.html)
- [wx.Dialog Modal](https://docs.wxpython.org/wx.Dialog.html#wx.Dialog.ShowModal)
- [wx.Timer](https://docs.wxpython.org/wx.Timer.html)

### Issue GitHub
- [#59: Refactoring wxPython completo](https://github.com/Nemex81/solitario-classico-accessibile/issues/59)

---

## 🎯 Prossimi Passi Immediati

1. **Review piano** con team/stakeholder
2. **Branch setup**: Verificare `copilot/remove-pygame-migrate-wxpython` aggiornato
3. **Environment**: `pip install wxPython>=4.1.1`
4. **Iniziare COMMIT 1**: Fix critico frame visibile
5. **Testing incrementale**: Validare ogni commit singolarmente
6. **NVDA testing**: Dopo COMMIT 2 (dialog hierarchy)
7. **Merge preparazione**: Dopo COMMIT 6 completo

---

**Fine Documento**

**Autore**: Perplexity AI Assistant  
**Data**: 12 Febbraio 2026  
**Versione**: 1.0  
**Status**: Ready for Implementation
