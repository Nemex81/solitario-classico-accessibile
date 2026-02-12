# Piano di Migrazione: Rimozione pygame e Transizione a wxPython Puro

**Progetto**: Solitario Classico Accessibile  
**Branch di riferimento**: `refactoring-engine`  
**Data creazione**: 12 Febbraio 2026  
**Versione target**: v2.0.0  
**Obiettivo**: Rimuovere completamente pygame e utilizzare solo wxPython per gestione interfaccia

---

## 📋 Indice

1. [Executive Summary](#executive-summary)
2. [Stato Attuale](#stato-attuale)
3. [Motivazioni della Migrazione](#motivazioni-della-migrazione)
4. [Architettura Target](#architettura-target)
5. [Piano di Implementazione](#piano-di-implementazione)
6. [Gestione Conflitti e Input](#gestione-conflitti-e-input)
7. [Testing e Validazione](#testing-e-validazione)
8. [Rischi e Mitigazioni](#rischi-e-mitigazioni)
9. [Timeline e Risorse](#timeline-e-risorse)
10. [Appendici](#appendici)

---

## Executive Summary

### Obiettivo Primario
Eliminare la dipendenza da **pygame** (attualmente usato per event loop e menu virtuale) e sostituirla con una soluzione basata esclusivamente su **wxPython**, mantenendo la natura di **audiogame accessibile** senza widget visivi.

### Benefici Attesi
1. **Accessibilità NVDA migliorata**: Eventi tastiera wx nativi meglio integrati con screen reader
2. **Dialog nativi già funzionanti**: WxDialogProvider implementato e testato (v1.6.x)
3. **Architettura più pulita**: Un solo framework UI invece di pygame + wx ibrido
4. **Manutenibilità**: Codebase più coerente e meno dipendenze (-2 pacchetti)
5. **Performance**: Event loop wx più efficiente, no overhead rendering pygame

### Sfide Principali
1. **Mapping eventi tastiera**: Traduzione `wx.KeyEvent` → comandi esistenti in `GamePlayController`
2. **Timer management**: Sostituzione `pygame.time.set_timer()` con `wx.Timer`
3. **Compatibility testing**: Validazione intensiva con NVDA su Windows
4. **Event conflicts**: Gestione corretta priorità eventi menu vs gameplay vs dialog
5. **Backward compatibility**: Preservare comportamento esistente 100%

### Stima Temporale
- **Sviluppo**: 11-14 ore effettive
- **Testing**: 6-8 ore con NVDA
- **Documentazione**: 2-3 ore
- **Totale**: ~20-25 ore (3-4 giorni lavorativi)

---

## Stato Attuale

### Architettura Esistente (refactoring-engine)

```
src/
├── domain/              ✅ 100% completato
│   ├── models/          Card, Deck, Pile, Table
│   ├── rules/           SolitaireRules, MoveValidator
│   └── services/        GameService, GameSettings, ScoringService
│
├── application/         ✅ 100% completato
│   ├── game_engine.py            Facade pattern
│   ├── gameplay_controller.py    60+ comandi tastiera
│   ├── options_controller.py     Gestione impostazioni
│   ├── input_handler.py          Key mapping
│   └── dialog_manager.py         Wrapper wxDialogs
│
├── infrastructure/      ⚠️  Ibrido pygame/wx
│   ├── accessibility/
│   │   ├── screen_reader.py      TTS abstraction
│   │   └── tts_provider.py       SAPI5/NVDA support
│   └── ui/
│       ├── menu.py               ⚠️  PYGAME-BASED (da sostituire)
│       ├── dialog.py             Legacy virtual dialogs
│       └── wx_dialog_provider.py ✅ Dialog nativi wx (v1.6)
│
└── presentation/        ✅ 100% completato
    └── formatters/      Formattazione messaggi TTS

test.py                  ⚠️  PYGAME EVENT LOOP (da riscrivere)
acs.py                   Legacy entry point (scr/ folder)
```

### Dipendenze pygame Attuali

**File**: `requirements.txt`
```txt
pygame==2.1.2
pygame-menu==4.3.7
```

**Utilizzo pygame nel progetto**:

| Componente | File | Funzione | Linee Codice |
|------------|------|----------|-------------|
| Event loop principale | `test.py` | `pygame.event.get()`, main loop | ~400 |
| Menu virtuale | `src/infrastructure/ui/menu.py` | Navigazione UP/DOWN/ENTER | ~150 |
| Timer events | `test.py` | `pygame.time.set_timer()` per timeout | ~50 |
| Display surface | `test.py` | Schermo bianco fittizio (audiogame) | ~10 |
| Window handle | `test.py` | Estrazione HWND per wxDialogs | ~20 |
| Key constants | `gameplay_controller.py` | `pygame.K_*` constants | ~200 |

**Totale linee dipendenti pygame**: ~830 linee

### Componenti già wx-based

✅ **WxDialogProvider** (v1.6.0-v1.6.3):  
- Dialog nativi per conferme (ESC, Nuova partita, Esci)
- Dialog statistiche fine partita
- Parent handle nativo (HWND/XID) già estratto da pygame surface
- **FUNZIONANTI E TESTATI**

✅ **DialogManager** (v1.6.1):  
- Wrapper application layer per WxDialogProvider
- Graceful degradation se wx non disponibile
- **PRONTO PER RIUSO**

---

## Motivazioni della Migrazione

### 1. Accessibilità NVDA (Priorità Massima)

**Problema attuale**:  
pygame gestisce eventi tastiera a basso livello, creando occasionali conflitti con NVDA:
- Alcuni tasti scorciatoia NVDA potrebbero essere intercettati da pygame
- Focus management non ottimale (pygame window vs NVDA cursor)
- Dialog wxPython appaiono come finestre separate in ALT+TAB (risolto in v1.6.3 ma soluzione ibrida)

**Soluzione wx pura**:  
- Eventi tastiera wx nativi 100% compatibili con screen reader Windows
- Focus management automatico wx integrato con NVDA
- Dialog modali figli della finestra principale (no separazione ALT+TAB)
- Supporto nativo accessibility API Windows (MSAA/UIA)

### 2. Architettura e Manutenibilità

**Problema attuale**:  
- Due framework UI (pygame per eventi, wx per dialog) = complessità inutile
- Estrazione window handle pygame→wx = workaround fragile
- Menu virtuale pygame = reinventare la ruota

**Soluzione wx pura**:  
- Un solo framework UI = codebase più pulita
- Event handling nativo wx = codice standard, documentato
- Meno dipendenze = deploy più semplice

### 3. Performance e Risorse

**Overhead pygame**:  
- Display surface 800x600 allocato ma mai usato (audiogame puro)
- Rendering engine caricato ma inutilizzato
- Event queue doppia (pygame + wx) = inefficienza

**Efficienza wx**:  
- Frame wx invisibile (1x1 pixel) = footprint minimo
- Event loop singolo = no overhead
- Timer wx.Timer più preciso di pygame.time.set_timer()

### 4. Allineamento con Best Practice

Il progetto è un **audiogame per non vedenti** senza grafica:  
- pygame è progettato per **giochi grafici 2D/3D**
- wxPython è progettato per **applicazioni desktop accessibili**
- **Mismatch concettuale**: stiamo usando il tool sbagliato per il job

---

## Architettura Target

### Struttura Finale (post-migrazione)

```
src/
├── domain/              [INVARIATO]
│
├── application/         [INVARIATO]
│
├── infrastructure/
│   ├── accessibility/   [INVARIATO]
│   │   ├── screen_reader.py
│   │   └── tts_provider.py
│   │
│   └── ui/              [NUOVO - WX PURO]
│       ├── wx_app.py              🆕 Main wx.App
│       ├── wx_frame.py            🆕 Invisible frame + event sink
│       ├── wx_menu.py             🆕 Menu virtuale wx-based
│       ├── wx_timer.py            🆕 Timer manager
│       ├── wx_key_adapter.py      🆕 wx.KeyEvent → Command adapter
│       └── wx_dialog_provider.py  [ESISTENTE - mantenuto]
│
└── presentation/        [INVARIATO]

wx_main.py               🆕 Nuovo entry point wxPython
test.py                  [DEPRECATO - mantenuto per testing parallelo]
acs.py                   [INVARIATO - legacy scr/ entry point]
```

### Componenti Nuovi da Creare

#### 1. `wx_app.py` - Main Application

**Responsabilità**:  
- Inizializzazione wx.App
- Creazione frame invisibile
- Setup event loop wxPython
- Callback on_init_complete per post-init setup

**Design Pattern**: Singleton wx.App

**Dipendenze**:  
- `wx_frame.py` (crea frame)
- `wx_menu.py` (crea menu)
- `game_engine.py` (crea motore gioco)

#### 2. `wx_frame.py` - Invisible Event Sink

**Responsabilità**:  
- Frame invisibile (1x1 pixel, no taskbar)
- Event binding: `EVT_KEY_DOWN`, `EVT_CHAR`, `EVT_CLOSE`
- Timer management: `wx.Timer` per check timeout
- Forward eventi a controller

**Design Pattern**: Observer (forward events)

**API Pubblica**:
```python
class SolitarioFrame(wx.Frame):
    def __init__(self, on_key_event: Callable[[wx.KeyEvent], None]):
        # Setup invisible frame
        pass
    
    def start_timer(self, interval_ms: int = 1000):
        # Avvia timer (sostituisce pygame.USEREVENT)
        pass
    
    def stop_timer(self):
        # Ferma timer
        pass
```

#### 3. `wx_menu.py` - Virtual Menu System

**Responsabilità**:  
- Menu virtuale navigabile (UP/DOWN/ENTER)
- Feedback TTS per ogni azione
- Wrap-around navigation
- Callback per selezione item

**Design Pattern**: Strategy (callback pattern)

**Compatibilità**: 100% drop-in replacement per `infrastructure/ui/menu.py` esistente

**API Pubblica**:
```python
class WxVirtualMenu:
    def __init__(self, 
                 items: List[str],
                 callback: Callable[[int], None],
                 screenreader: ScreenReader,
                 parent: Optional[wx.Window] = None):
        pass
    
    def handle_key_event(self, event: wx.KeyEvent) -> bool:
        # Returns True se evento gestito
        pass
    
    def next_item(self):
        pass
    
    def prev_item(self):
        pass
    
    def execute(self):
        pass
```

#### 4. `wx_key_adapter.py` - Key Event Adapter

**Responsabilità**:  
- Traduzione `wx.KeyEvent` → formato compatibile con `GamePlayController`
- Mapping `wx.WXK_*` constants → `pygame.K_*` equivalents (temporaneo)
- Estrazione modificatori (SHIFT, CTRL, ALT)

**Design Pattern**: Adapter

**API Pubblica**:
```python
class WxKeyEventAdapter:
    # Mapping wx → pygame key codes
    WX_TO_PYGAME_MAP: Dict[int, str] = { ... }
    
    @staticmethod
    def convert(wx_event: wx.KeyEvent) -> dict:
        """
        Returns:
            {
                'key': int,
                'mods': {'shift': bool, 'ctrl': bool, 'alt': bool},
                'unicode': str
            }
        """
        pass
    
    @staticmethod
    def to_pygame_constant(wx_keycode: int) -> int:
        # Per backward compatibility controller esistente
        pass
```

#### 5. `wx_timer.py` - Timer Manager

**Responsabilità**:  
- Wrapper per `wx.Timer`
- Gestione callback periodici
- Precisione 1 secondo per timeout partita

**Design Pattern**: Facade

**API Pubblica**:
```python
class WxTimerManager:
    def __init__(self, parent: wx.Window, callback: Callable[[], None]):
        pass
    
    def start(self, interval_ms: int = 1000):
        pass
    
    def stop(self):
        pass
    
    def is_running(self) -> bool:
        pass
```

---

## Piano di Implementazione

### Strategia: Migrazione Incrementale a 4 Fasi

**Branch di lavoro**: `feature/wx-only-migration` (branch off da `refactoring-engine`)

**Approccio**: Implementazione parallela con testing continuo, mantenimento `test.py` legacy come fallback.

---

### FASE 1: Infrastruttura wx Base (3-4 ore)

**Obiettivo**: Creare componenti infrastrutturali wx senza toccare codice esistente.

#### Task 1.1: Creare `wx_app.py` (1 ora)

**File**: `src/infrastructure/ui/wx_app.py`  
**Linee stimate**: ~80

**Implementazione**:
```python
# Struttura minimale
import wx

class SolitarioWxApp(wx.App):
    def __init__(self, on_init_complete=None):
        self.on_init_complete = on_init_complete
        super().__init__(False)  # No redirect stdout
    
    def OnInit(self):
        from src.infrastructure.ui.wx_frame import SolitarioFrame
        self.frame = SolitarioFrame()
        self.SetTopWindow(self.frame)
        
        if self.on_init_complete:
            wx.CallAfter(self.on_init_complete)
        
        return True
```

**Testing**:
- [ ] App si avvia senza errori
- [ ] `OnInit()` viene chiamato
- [ ] Callback `on_init_complete` funziona
- [ ] No crash all'uscita

#### Task 1.2: Creare `wx_frame.py` (1.5 ore)

**File**: `src/infrastructure/ui/wx_frame.py`  
**Linee stimate**: ~120

**Implementazione**:
```python
import wx
from typing import Callable, Optional

class SolitarioFrame(wx.Frame):
    def __init__(self, 
                 on_key_event: Optional[Callable[[wx.KeyEvent], None]] = None,
                 title: str = "Solitario Accessibile"):
        # Frame invisibile 1x1 pixel, no taskbar
        super().__init__(None, title=title, size=(1, 1), 
                        style=wx.FRAME_NO_TASKBAR)
        
        self.on_key_event = on_key_event
        
        # Event bindings
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.Bind(wx.EVT_CHAR, self._on_char)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        
        # Timer per timeout check
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer_tick)
        
        # Nascondi frame (audiogame invisibile)
        self.Hide()
    
    def _on_key_down(self, event: wx.KeyEvent):
        if self.on_key_event:
            self.on_key_event(event)
        event.Skip()  # Importante per propagazione
    
    def start_timer(self, interval_ms: int = 1000):
        self.timer.Start(interval_ms)
    
    def stop_timer(self):
        if self.timer.IsRunning():
            self.timer.Stop()
```

**Testing**:
- [ ] Frame si crea senza crash
- [ ] Frame invisibile (no window visibile)
- [ ] Eventi tastiera catturati
- [ ] Timer funziona (1 tick/secondo)
- [ ] Chiusura graceful

#### Task 1.3: Creare `wx_menu.py` (1.5 ore)

**File**: `src/infrastructure/ui/wx_menu.py`  
**Linee stimate**: ~150

**Implementazione**:
```python
import wx
from typing import List, Callable, Optional

class WxVirtualMenu:
    def __init__(self, 
                 items: List[str],
                 callback: Callable[[int], None],
                 screenreader,
                 parent: Optional[wx.Window] = None):
        self.items = items
        self.callback = callback
        self.sr = screenreader
        self.parent = parent
        self.selected_index = 0
        
        self._announce_menu()
    
    def _announce_menu(self):
        self.sr.tts.speak(f"Menu. {len(self.items)} opzioni.", interrupt=True)
        wx.CallLater(200, lambda: self.sr.tts.speak(self.items[0], interrupt=False))
    
    def handle_key_event(self, event: wx.KeyEvent) -> bool:
        key_code = event.GetKeyCode()
        
        if key_code == wx.WXK_DOWN:
            self.next_item()
            return True
        elif key_code == wx.WXK_UP:
            self.prev_item()
            return True
        elif key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.execute()
            return True
        
        return False
```

**Testing**:
- [ ] Menu annuncia apertura
- [ ] UP/DOWN navigano correttamente
- [ ] ENTER esegue callback
- [ ] Wrap-around funziona (ultimo→primo)
- [ ] TTS feedback per ogni azione

**Verifica Compatibilità**:
- [ ] API identica a `infrastructure/ui/menu.py` esistente
- [ ] Parametri costruttore compatibili
- [ ] Metodi pubblici identici

---

### FASE 2: Key Event Adapter (2-3 ore)

**Obiettivo**: Creare adapter per tradurre eventi wx → comandi gameplay esistenti.

#### Task 2.1: Creare `wx_key_adapter.py` (2 ore)

**File**: `src/infrastructure/ui/wx_key_adapter.py`  
**Linee stimate**: ~200

**Implementazione**:
```python
import wx
import pygame  # Temporaneo per compatibilità
from typing import Dict

class WxKeyEventAdapter:
    # Mapping completo wx → pygame
    WX_TO_PYGAME_MAP: Dict[int, int] = {
        # Frecce
        wx.WXK_UP: pygame.K_UP,
        wx.WXK_DOWN: pygame.K_DOWN,
        wx.WXK_LEFT: pygame.K_LEFT,
        wx.WXK_RIGHT: pygame.K_RIGHT,
        
        # Speciali
        wx.WXK_RETURN: pygame.K_RETURN,
        wx.WXK_SPACE: pygame.K_SPACE,
        wx.WXK_ESCAPE: pygame.K_ESCAPE,
        wx.WXK_TAB: pygame.K_TAB,
        wx.WXK_HOME: pygame.K_HOME,
        wx.WXK_END: pygame.K_END,
        wx.WXK_DELETE: pygame.K_DELETE,
        
        # Function keys
        wx.WXK_F1: pygame.K_F1,
        wx.WXK_F2: pygame.K_F2,
        wx.WXK_F3: pygame.K_F3,
        wx.WXK_F4: pygame.K_F4,
        wx.WXK_F5: pygame.K_F5,
        
        # Numeri tastierino
        wx.WXK_NUMPAD1: pygame.K_KP1,
        wx.WXK_NUMPAD2: pygame.K_KP2,
        # ... altri numpad
        
        # Lettere (A-Z)
        ord('A'): pygame.K_a,
        ord('B'): pygame.K_b,
        # ... tutte le lettere
        
        # Numeri (0-9)
        ord('0'): pygame.K_0,
        ord('1'): pygame.K_1,
        # ... tutti i numeri
    }
    
    @staticmethod
    def convert_to_pygame_event(wx_event: wx.KeyEvent) -> 'pygame.event.Event':
        """
        Converte wx.KeyEvent in pygame.event.Event compatibile.
        Usato per backward compatibility con GamePlayController.
        """
        key_code = wx_event.GetKeyCode()
        pygame_key = WxKeyEventAdapter.WX_TO_PYGAME_MAP.get(key_code, key_code)
        
        # Crea evento pygame simulato
        pygame_event = pygame.event.Event(
            pygame.KEYDOWN,
            {
                'key': pygame_key,
                'mod': WxKeyEventAdapter._get_pygame_mods(wx_event),
                'unicode': chr(key_code) if 32 <= key_code < 127 else ''
            }
        )
        
        return pygame_event
    
    @staticmethod
    def _get_pygame_mods(wx_event: wx.KeyEvent) -> int:
        """Traduce modificatori wx → pygame."""
        mods = 0
        if wx_event.ShiftDown():
            mods |= pygame.KMOD_SHIFT
        if wx_event.ControlDown():
            mods |= pygame.KMOD_CTRL
        if wx_event.AltDown():
            mods |= pygame.KMOD_ALT
        return mods
```

**Testing**:
- [ ] Mapping completo 60+ tasti
- [ ] Modificatori (SHIFT, CTRL, ALT) corretti
- [ ] Lettere maiuscole/minuscole
- [ ] Numpad vs numeri normali
- [ ] Function keys

#### Task 2.2: Modificare `gameplay_controller.py` (1 ora)

**File**: `src/application/gameplay_controller.py`  
**Linee modificate**: ~20

**Modifiche**:
```python
# Aggiungere metodo wrapper per wx events
class GamePlayController:
    # ... codice esistente ...
    
    def handle_wx_key_event(self, wx_event):
        """
        Wrapper per eventi wx.KeyEvent.
        Converte in pygame.event.Event e chiama handle_keyboard_events esistente.
        """
        from src.infrastructure.ui.wx_key_adapter import WxKeyEventAdapter
        
        pygame_event = WxKeyEventAdapter.convert_to_pygame_event(wx_event)
        self.handle_keyboard_events(pygame_event)
```

**Testing**:
- [ ] Comandi gameplay funzionano con wx events
- [ ] SHIFT+1-4 (pile semi) funzionano
- [ ] CTRL+ALT+W (debug victory) funziona
- [ ] Tutti i 60+ comandi testati

---

### FASE 3: Nuovo Entry Point wxPython (2 ore)

**Obiettivo**: Creare `wx_main.py` come sostituto di `test.py`.

#### Task 3.1: Creare `wx_main.py` (2 ore)

**File**: `wx_main.py` (root del progetto)  
**Linee stimate**: ~350 (simile a test.py ma wx-based)

**Struttura**:
```python
import wx
from src.infrastructure.ui.wx_app import SolitarioWxApp
from src.infrastructure.ui.wx_frame import SolitarioFrame
from src.infrastructure.ui.wx_menu import WxVirtualMenu
from src.application.game_engine import GameEngine
from src.application.gameplay_controller import GamePlayController

class SolitarioController:
    def __init__(self):
        self.app = None
        self.frame = None
        self.engine = None
        self.controller = None
        self.menu = None
        
        self.is_menu_open = True
        self.is_game_running = False
    
    def run(self):
        self.app = SolitarioWxApp(on_init_complete=self._on_init_complete)
        self.app.MainLoop()
    
    def _on_init_complete(self):
        # Inizializzazione post-wx
        self.frame = self.app.frame
        self.frame.on_key_event = self._on_key_event
        
        # Crea engine
        self.engine = GameEngine.create(...)
        
        # Crea controller
        self.controller = GamePlayController(...)
        
        # Mostra menu
        self._show_main_menu()
    
    def _on_key_event(self, event: wx.KeyEvent):
        if self.is_menu_open and self.menu:
            self.menu.handle_key_event(event)
        elif self.is_game_running:
            self.controller.handle_wx_key_event(event)
```

**Testing**:
- [ ] App si avvia
- [ ] Menu navigabile
- [ ] Gameplay funziona
- [ ] Dialog nativi aperti
- [ ] Timer timeout funziona
- [ ] Chiusura graceful

---

### FASE 4: Testing, Cleanup, Migrazione (3-4 ore)

#### Task 4.1: Testing Parallelo (2 ore)

**Test A**: `python test.py` (pygame legacy)  
**Test B**: `python wx_main.py` (wx nuovo)

**Checklist Parità Funzionale**:
- [ ] Menu navigazione identica
- [ ] Comandi gameplay identici (60+ comandi)
- [ ] Dialog nativi funzionano
- [ ] Timer timeout preciso
- [ ] Opzioni (O key) funzionante
- [ ] ESC confirmation in tutti i contesti
- [ ] Double-ESC quick exit
- [ ] NVDA compatibility completa

#### Task 4.2: Testing NVDA Intensivo (2 ore)

**Scenari Critici**:
1. **Menu navigation**: UP/DOWN annunciati correttamente
2. **Gameplay commands**: Ogni comando annunciato
3. **Dialog focus**: Focus automatico su dialog aperti
4. **Timer announcements**: Timeout vocalized
5. **Victory flow**: Stats report leggibile
6. **Options window**: Navigazione opzioni accessibile

**Validazione NVDA**:
- [ ] NVDA annuncia apertura app
- [ ] Nessun conflitto hotkey NVDA
- [ ] Focus trap nei dialog (ESC esce)
- [ ] Lettura completa report statistiche
- [ ] Browse mode disabilitato (focus mode)

#### Task 4.3: Rimozione pygame (1 ora)

**Step 1**: Commit su branch `feature/wx-only-migration`
```bash
git add .
git commit -m "feat: Complete wx-only implementation - pygame removal ready"
```

**Step 2**: Rimuovi dipendenze
```bash
# requirements.txt
# pygame==2.1.2  # REMOVED - v2.0.0
# pygame-menu==4.3.7  # REMOVED - v2.0.0
```

**Step 3**: Rename files
```bash
mv test.py test_pygame_legacy.py  # Backup
mv wx_main.py test.py  # Nuovo entry point principale
```

**Step 4**: Update README.md
```markdown
## Avvio Applicazione

```bash
python test.py  # Nuovo entry point wxPython (v2.0.0+)
```

## Legacy

```bash
python test_pygame_legacy.py  # Vecchio entry point (deprecato)
python acs.py  # Entry point scr/ legacy
```
```

**Step 5**: Testing post-rimozione
```bash
pip uninstall pygame pygame-menu
python test.py  # Deve funzionare senza pygame!
```

**Verifica**:
- [ ] App si avvia senza pygame
- [ ] No import errors
- [ ] Tutte le feature funzionanti
- [ ] NVDA compatibility confermata

#### Task 4.4: Documentazione (1 ora)

**File da aggiornare**:

1. **CHANGELOG.md**: Sezione v2.0.0
```markdown
## [2.0.0] - 2026-02-XX

### 🚨 BREAKING CHANGES
- Rimossa dipendenza pygame (sostituita con wxPython puro)
- Entry point cambiato: `test.py` ora usa wxPython nativamente
- Legacy entry point rinominato: `test_pygame_legacy.py`

### ✨ Features
- Nuovo sistema event handling wxPython nativo
- Accessibilità NVDA migliorata con eventi wx nativi
- Dialog modali nativi 100% (no separazione ALT+TAB)
- Timer wx.Timer più preciso

### 🐛 Bug Fixes
- Risolti conflitti hotkey pygame/NVDA
- Focus management migliorato per screen reader

### 📦 Dependencies
- **Removed**: pygame==2.1.2, pygame-menu==4.3.7
- **Added**: Nessuna nuova dipendenza (wxPython già presente)

### 🏗️ Architecture
- Infrastruttura UI completamente wx-based
- Adapter pattern per backward compatibility controller
- Clean Architecture mantenuta al 100%
```

2. **README.md**: Aggiornare requisiti
```markdown
## Requisiti Sistema

- Python 3.8+
- **wxPython >= 4.1.1** (UI framework)
- **NVDA screen reader** (Windows) o **Orca** (Linux)
- Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.14+

## Dipendenze Rimosse (v2.0.0)

- ~~pygame~~ (sostituito con wxPython puro)
- ~~pygame-menu~~ (menu virtuale wx custom)
```

3. **docs/MIGRATION_GUIDE_V2.md**: Guida per utenti esistenti
```markdown
# Guida Migrazione v1.x → v2.0.0

## Cosa Cambia per l'Utente Finale

**Niente!** L'esperienza utente è identica:
- Stesso comando avvio: `python test.py`
- Stessi comandi tastiera (60+ comandi)
- Stesse funzionalità
- Accessibilità NVDA migliorata

## Cosa Cambia per gli Sviluppatori

### Dipendenze
```bash
# Prima (v1.x)
pip install pygame pygame-menu wxPython

# Dopo (v2.0.0)
pip install wxPython  # Solo wxPython!
```

### Import Changes
```python
# Prima (v1.x)
import pygame
from src.infrastructure.ui.menu import VirtualMenu  # pygame-based

# Dopo (v2.0.0)
import wx
from src.infrastructure.ui.wx_menu import WxVirtualMenu  # wx-based
```

### Event Handling
```python
# Prima (v1.x)
for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
        controller.handle_keyboard_events(event)

# Dopo (v2.0.0)
def on_key_event(wx_event: wx.KeyEvent):
    controller.handle_wx_key_event(wx_event)

frame.on_key_event = on_key_event
```
```

---

## Gestione Conflitti e Input

### Priorità Eventi (Event Priority Hierarchy)

**Problema**: Con dialog nativi, menu virtuali e gameplay, servono regole chiare per priorità eventi.

**Soluzione**: Gerarchia a 4 livelli implementata in `wx_main.py`

```python
def _on_key_event(self, event: wx.KeyEvent):
    # PRIORITY 0: Dialog nativi (wx modal) - gestiti automaticamente
    # wxDialog.ShowModal() blocca eventi finché chiuso
    # No azione necessaria qui
    
    # PRIORITY 1: Options window aperta
    if self.is_options_mode:
        self.controller.handle_wx_key_event(event)
        # Check se options chiusa
        if not self.controller.options_controller.is_open:
            self._close_options_and_return_to_menu()
        return
    
    # PRIORITY 2: Menu navigazione
    if self.is_menu_open and self.menu:
        handled = self.menu.handle_key_event(event)
        if handled:
            return  # Evento consumato
        # ESC in menu → exit dialog
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self._show_exit_dialog()
            return
    
    # PRIORITY 3: Gameplay
    if self.is_game_running:
        # ESC detection (singolo vs doppio)
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self._handle_gameplay_esc(event)
            return
        # Altri comandi
        self.controller.handle_wx_key_event(event)
        return
    
    # PRIORITY 4: Unhandled - skip
    event.Skip()
```

### Gestione ESC Context-Aware

**Contesti ESC**:

| Contesto | Azione ESC | Implementazione |
|----------|-----------|----------------|
| Main menu | Exit dialog | `dialog_manager.show_exit_app_prompt()` |
| Game submenu | Return to main dialog | `dialog_manager.show_return_to_main_prompt()` |
| Gameplay (primo ESC) | Abandon game dialog | `dialog_manager.show_abandon_game_prompt()` |
| Gameplay (doppio ESC) | Instant abandon | Auto-confirm, no dialog |
| Options window | Close options | `options_controller.close_window()` |
| Dialog nativo | Close dialog | Gestito da wx automaticamente |

**Implementazione Double-ESC**:
```python
def _handle_gameplay_esc(self, event: wx.KeyEvent):
    import time
    current_time = time.time()
    
    # Check double-ESC (< 2 sec threshold)
    if self.last_esc_time > 0 and current_time - self.last_esc_time <= 2.0:
        # Double-ESC: instant abandon
        print("[DOUBLE-ESC] Quick exit!")
        if self.screen_reader:
            self.screen_reader.tts.speak("Uscita rapida!", interrupt=True)
        self._confirm_abandon_game()  # Skip dialog
        self.last_esc_time = 0
    else:
        # First ESC: show dialog
        self.last_esc_time = current_time
        self._show_abandon_game_dialog()
```

### Gestione Timer Events

**Problema**: pygame usava `pygame.USEREVENT + 1` per timer, wx usa `EVT_TIMER`.

**Soluzione**: Wrapper `wx.Timer` in `SolitarioFrame`

```python
# wx_frame.py
class SolitarioFrame(wx.Frame):
    def __init__(self, ...):
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer_tick)
    
    def _on_timer_tick(self, event: wx.TimerEvent):
        # Forward a controller principale
        if self.on_timer_callback:
            self.on_timer_callback()

# wx_main.py
class SolitarioController:
    def _on_init_complete(self):
        self.frame.on_timer_callback = self._check_timer_expiration
        self.frame.start_timer(1000)  # 1 sec interval
    
    def _check_timer_expiration(self):
        # Identico a test.py esistente
        if not self.is_game_running:
            return
        # ... logica timeout ...
```

### Gestione Focus NVDA

**Problema**: NVDA deve seguire focus correttamente tra menu, gameplay, dialog.

**Soluzione**: wx gestisce focus automaticamente, ma serve assistenza TTS

```python
# Quando si apre un dialog
def _show_exit_dialog(self):
    # Annuncia PRIMA di aprire (NVDA sente cambio focus)
    if self.screen_reader:
        self.screen_reader.tts.speak(
            "Apertura dialog conferma uscita.",
            interrupt=True
        )
    
    # Dialog modale (wx gestisce focus)
    result = self.dialog_manager.show_exit_app_prompt()
    
    # Annuncia risultato DOPO chiusura
    if result:
        # Confermato: app chiude
        pass
    else:
        # Annullato: ritorna a menu
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Dialog chiuso. Ritorno al menu.",
                interrupt=True
            )
        # Re-annuncia menu corrente
        self.menu._announce_menu()
```

---

## Testing e Validazione

### Suite di Test per Migrazione

#### Test Unitari (pytest)

**File**: `tests/infrastructure/test_wx_components.py`

```python
import pytest
import wx

class TestWxKeyAdapter:
    def test_arrow_keys_mapping(self):
        # Verifica mapping frecce
        pass
    
    def test_function_keys_mapping(self):
        # Verifica F1-F5
        pass
    
    def test_modifiers(self):
        # Verifica SHIFT, CTRL, ALT
        pass

class TestWxMenu:
    def test_menu_navigation(self):
        # UP/DOWN cycling
        pass
    
    def test_menu_selection(self):
        # ENTER callback
        pass
    
    def test_wrap_around(self):
        # Ultimo → Primo
        pass

class TestWxTimer:
    def test_timer_precision(self):
        # 1000ms ± 50ms tolerance
        pass
```

#### Test Integrazione (manuale con NVDA)

**Checklist NVDA Accessibility**:

**Scenario 1: Menu Navigation**
- [ ] Avvio app: NVDA annuncia "Menu. 2 opzioni. Gioca al solitario classico."
- [ ] Freccia GIÙ: NVDA annuncia "Esci dal gioco"
- [ ] Freccia SU: NVDA annuncia "Gioca al solitario classico" (wrap)
- [ ] ENTER: NVDA annuncia apertura submenu

**Scenario 2: Gameplay Commands**
- [ ] Avvio partita: NVDA annuncia "Nuova partita avviata!"
- [ ] Tasto 1: NVDA annuncia carta pila 1
- [ ] SHIFT+1: NVDA annuncia carta pila semi cuori
- [ ] D: NVDA annuncia pesca carte
- [ ] H: NVDA annuncia help comandi (lungo)

**Scenario 3: Dialog Native**
- [ ] ESC in menu: NVDA annuncia dialog, legge "Vuoi uscire?"
- [ ] TAB in dialog: NVDA cicla tra pulsanti Sì/No
- [ ] ENTER su Sì: NVDA annuncia chiusura app
- [ ] ESC in dialog: NVDA annuncia chiusura dialog
- [ ] Focus torna a menu: NVDA ri-annuncia voce corrente

**Scenario 4: Timer Expiration**
- [ ] Timer scade (STRICT): NVDA annuncia "Tempo scaduto! Partita terminata."
- [ ] Report statistiche: NVDA legge report completo (2-3 minuti)
- [ ] Ritorno menu: NVDA annuncia menu di gioco

**Scenario 5: Victory Flow**
- [ ] Vittoria: NVDA annuncia "Vittoria!"
- [ ] Dialog statistiche aperto: NVDA legge stats dettagliate
- [ ] Dialog rematch: NVDA legge "Vuoi giocare ancora?"
- [ ] Selezione Sì: NVDA annuncia "Nuova partita avviata!"

**Scenario 6: Options Window**
- [ ] Tasto O: NVDA annuncia apertura opzioni
- [ ] Freccia GIÙ: NVDA annuncia ciascuna opzione
- [ ] ENTER su opzione: NVDA annuncia cambio valore
- [ ] O o ESC: NVDA annuncia chiusura, ritorno menu

#### Test Performance

**Metriche da misurare**:

| Metrica | pygame (v1.x) | wx (v2.0.0) | Target |
|---------|---------------|-------------|--------|
| Avvio app | ~2.5s | ~1.8s | < 3s |
| Memoria base | ~45 MB | ~35 MB | < 50 MB |
| CPU idle | ~2% | ~1% | < 5% |
| Latency input | ~15ms | ~10ms | < 20ms |
| Timer precision | ±100ms | ±50ms | ±100ms |

**Tool**: `memory_profiler`, `cProfile`

```python
# Profiling script
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Avvia app wx
app = SolitarioController()
app.run()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

---

## Rischi e Mitigazioni

### Rischio 1: Breaking Changes Comandi Tastiera

**Probabilità**: Media  
**Impatto**: Alto (utenti non vedenti dipendono da muscle memory)

**Scenario**:
Mapping wx.WXK_* → pygame.K_* incompleto, alcuni tasti non funzionano.

**Mitigazione**:
1. **Mapping completo**: Verificare tutti i 60+ comandi in `WxKeyEventAdapter`
2. **Testing parallelo**: Mantenere `test.py` pygame legacy durante migrazione
3. **Fallback**: Se mapping non trovato, log warning + usa key code raw
4. **User testing**: Beta test con utenti non vedenti prima del merge

**Contingency Plan**:
Se post-merge emergono comandi rotti:
- Hotfix in 24h con mapping corretto
- Release v2.0.1 patch immediata
- Rollback possibile: ripristinare pygame temporaneamente

### Rischio 2: NVDA Compatibility Regressions

**Probabilità**: Bassa  
**Impatto**: Critico (app inutilizzabile per target user)

**Scenario**:
Eventi wx non propagati correttamente a NVDA, silenzio TTS o annunci mancanti.

**Mitigazione**:
1. **Testing NVDA intensivo**: 2 ore dedicate prima del merge
2. **event.Skip()**: Chiamare sempre dopo handling per propagazione
3. **TTS explicit**: Annunciare ogni azione importante via ScreenReader
4. **Focus management**: Usare wx.CallAfter per timing corretto

**Segnali di Warning**:
- NVDA non annuncia apertura app
- Silenzio su pressione tasti freccia
- Dialog non letti automaticamente

**Contingency Plan**:
Se NVDA non funziona:
- Immediate rollback a pygame
- Consultare documentazione wx accessibility
- Testare con Orca su Linux (cross-validation)

### Rischio 3: Timer Precision Loss

**Probabilità**: Bassa  
**Impatto**: Medio (timeout partita impreciso)

**Scenario**:
`wx.Timer` meno preciso di `pygame.time.set_timer()`, timeout ±200ms invece di ±50ms.

**Mitigazione**:
1. **Testing precision**: Misurare 100 tick timer, calcolare media/stddev
2. **Tolerance adjustment**: Se necessario, aumentare tolleranza a ±150ms
3. **Fallback**: Usare `threading.Timer` se wx.Timer insufficiente

**Acceptance Criteria**:
- Timeout 10 minuti deve scadere tra 9:59.5 e 10:00.5 (±500ms OK)

### Rischio 4: Dialog Focus Traps

**Probabilità**: Bassa  
**Impatto**: Medio (utente bloccato in dialog)

**Scenario**:
Dialog modale non rilascia focus correttamente, ESC non chiude, app bloccata.

**Mitigazione**:
1. **ESC binding**: Garantire `wx.ID_CANCEL` su pulsante No/Annulla
2. **Close handler**: Implementare `EVT_CLOSE` su ogni dialog
3. **Timeout auto-close**: Dialog si chiude dopo 5 minuti inattività
4. **Fallback**: CTRL+ALT+Q emergency exit (kill app)

**Testing**:
- [ ] ESC chiude ogni dialog
- [ ] ALT+F4 chiude app anche con dialog aperto
- [ ] Focus ritorna a menu dopo chiusura dialog

### Rischio 5: Cross-Platform Inconsistencies

**Probabilità**: Media  
**Impatto**: Medio (app non funziona su Linux/macOS)

**Scenario**:
wx comportamento diverso su Windows vs Linux, key codes differenti.

**Mitigazione**:
1. **Platform detection**: `sys.platform` checks in `wx_key_adapter.py`
2. **Conditional mapping**: Mapping separati per Windows/Linux/macOS
3. **Testing multi-platform**: Testare su VM Ubuntu e macOS Ventura
4. **Graceful degradation**: Se piattaforma sconosciuta, log warning + fallback

**Priorità Testing**:
1. Windows 10/11 (priorità massima - 80% utenti)
2. Ubuntu 22.04 (priorità media - 15% utenti)
3. macOS (priorità bassa - 5% utenti, poco usato per NVDA)

---

## Timeline e Risorse

### Timeline Stimata

```
Giorno 1 (8 ore):
├─ Ore 0-4:   FASE 1 - Infrastruttura wx base
│   ├─ 1h:    wx_app.py + testing
│   ├─ 1.5h:  wx_frame.py + testing
│   ├─ 1.5h:  wx_menu.py + testing
│   └─ commit: "feat: Add wx infrastructure components"
│
└─ Ore 4-8:   FASE 2 - Key event adapter
    ├─ 2h:    wx_key_adapter.py (mapping completo)
    ├─ 1h:    Modifiche gameplay_controller.py
    ├─ 1h:    Testing 60+ comandi
    └─ commit: "feat: Add wx key event adapter"

Giorno 2 (8 ore):
├─ Ore 0-2:   FASE 3 - Nuovo entry point
│   ├─ 2h:    wx_main.py completo
│   └─ commit: "feat: Add wx-based entry point"
│
├─ Ore 2-4:   FASE 4 - Testing parallelo
│   ├─ 1h:    Test funzionale parità pygame vs wx
│   ├─ 1h:    Fix bug minori
│   └─ commit: "test: Validate wx implementation parity"
│
├─ Ore 4-6:   Testing NVDA
│   ├─ 2h:    Scenari 1-6 completi con NVDA
│   └─ commit: "test: NVDA accessibility validated"
│
└─ Ore 6-8:   Cleanup e documentazione
    ├─ 1h:    Rimozione pygame, rename files
    ├─ 1h:    Update CHANGELOG, README, docs
    └─ commit: "feat!: Remove pygame dependency - v2.0.0"

Giorno 3 (4 ore):
└─ Ore 0-4:   Testing finale e merge
    ├─ 1h:    Regressione testing completo
    ├─ 1h:    PR review e addressing feedback
    ├─ 1h:    Merge in refactoring-engine
    └─ 1h:    Release notes e comunicazione utenti

Totale: 20 ore effettive (2.5 giorni lavorativi)
```

### Risorse Necessarie

**Sviluppatore**:
- 1 sviluppatore senior Python/wxPython
- Esperienza con screen reader accessibility
- Familiarità con architettura Clean

**Testing**:
- 1 tester non vedente con NVDA (2 ore giorno 2)
- VM Windows 10 con NVDA installato
- VM Ubuntu 22.04 con Orca installato (opzionale)

**Tool**:
- wxPython 4.1.1+ installato
- pytest per unit testing
- memory_profiler per performance testing
- Git per version control (branch strategy)

### Branch Strategy

```
refactoring-engine (base)
  ↓
  └─ feature/wx-only-migration (sviluppo)
      ├─ commit 1: Infrastruttura wx
      ├─ commit 2: Key adapter
      ├─ commit 3: Entry point wx
      ├─ commit 4: Testing e fixes
      ├─ commit 5: NVDA validation
      └─ commit 6: pygame removal
          ↓
          PR → refactoring-engine (review)
          ↓
          MERGE → refactoring-engine (v2.0.0)
```

---

## Appendici

### Appendice A: Mapping Completo Key Codes

**File di riferimento**: `wx_key_adapter.py`

```python
# Mapping completo wx.WXK_* → pygame.K_*
WX_TO_PYGAME_COMPLETE = {
    # === FRECCE ===
    wx.WXK_UP: pygame.K_UP,
    wx.WXK_DOWN: pygame.K_DOWN,
    wx.WXK_LEFT: pygame.K_LEFT,
    wx.WXK_RIGHT: pygame.K_RIGHT,
    
    # === TASTI SPECIALI ===
    wx.WXK_RETURN: pygame.K_RETURN,
    wx.WXK_SPACE: pygame.K_SPACE,
    wx.WXK_ESCAPE: pygame.K_ESCAPE,
    wx.WXK_TAB: pygame.K_TAB,
    wx.WXK_BACK: pygame.K_BACKSPACE,
    wx.WXK_DELETE: pygame.K_DELETE,
    wx.WXK_HOME: pygame.K_HOME,
    wx.WXK_END: pygame.K_END,
    wx.WXK_PAGEUP: pygame.K_PAGEUP,
    wx.WXK_PAGEDOWN: pygame.K_PAGEDOWN,
    
    # === FUNCTION KEYS ===
    wx.WXK_F1: pygame.K_F1,
    wx.WXK_F2: pygame.K_F2,
    wx.WXK_F3: pygame.K_F3,
    wx.WXK_F4: pygame.K_F4,
    wx.WXK_F5: pygame.K_F5,
    wx.WXK_F6: pygame.K_F6,
    wx.WXK_F7: pygame.K_F7,
    wx.WXK_F8: pygame.K_F8,
    wx.WXK_F9: pygame.K_F9,
    wx.WXK_F10: pygame.K_F10,
    wx.WXK_F11: pygame.K_F11,
    wx.WXK_F12: pygame.K_F12,
    
    # === NUMERI (ROW) ===
    ord('0'): pygame.K_0,
    ord('1'): pygame.K_1,
    ord('2'): pygame.K_2,
    ord('3'): pygame.K_3,
    ord('4'): pygame.K_4,
    ord('5'): pygame.K_5,
    ord('6'): pygame.K_6,
    ord('7'): pygame.K_7,
    ord('8'): pygame.K_8,
    ord('9'): pygame.K_9,
    
    # === LETTERE (A-Z) ===
    ord('A'): pygame.K_a,
    ord('B'): pygame.K_b,
    ord('C'): pygame.K_c,
    ord('D'): pygame.K_d,
    ord('E'): pygame.K_e,
    ord('F'): pygame.K_f,
    ord('G'): pygame.K_g,
    ord('H'): pygame.K_h,
    ord('I'): pygame.K_i,
    ord('J'): pygame.K_j,
    ord('K'): pygame.K_k,
    ord('L'): pygame.K_l,
    ord('M'): pygame.K_m,
    ord('N'): pygame.K_n,
    ord('O'): pygame.K_o,
    ord('P'): pygame.K_p,
    ord('Q'): pygame.K_q,
    ord('R'): pygame.K_r,
    ord('S'): pygame.K_s,
    ord('T'): pygame.K_t,
    ord('U'): pygame.K_u,
    ord('V'): pygame.K_v,
    ord('W'): pygame.K_w,
    ord('X'): pygame.K_x,
    ord('Y'): pygame.K_y,
    ord('Z'): pygame.K_z,
    
    # === NUMPAD ===
    wx.WXK_NUMPAD0: pygame.K_KP0,
    wx.WXK_NUMPAD1: pygame.K_KP1,
    wx.WXK_NUMPAD2: pygame.K_KP2,
    wx.WXK_NUMPAD3: pygame.K_KP3,
    wx.WXK_NUMPAD4: pygame.K_KP4,
    wx.WXK_NUMPAD5: pygame.K_KP5,
    wx.WXK_NUMPAD6: pygame.K_KP6,
    wx.WXK_NUMPAD7: pygame.K_KP7,
    wx.WXK_NUMPAD8: pygame.K_KP8,
    wx.WXK_NUMPAD9: pygame.K_KP9,
    wx.WXK_NUMPAD_ENTER: pygame.K_KP_ENTER,
    wx.WXK_NUMPAD_ADD: pygame.K_KP_PLUS,
    wx.WXK_NUMPAD_SUBTRACT: pygame.K_KP_MINUS,
    wx.WXK_NUMPAD_MULTIPLY: pygame.K_KP_MULTIPLY,
    wx.WXK_NUMPAD_DIVIDE: pygame.K_KP_DIVIDE,
}
```

**Totale mapping**: 80+ key codes

### Appendice B: Comandi Gameplay da Testare

**Riferimento**: 60+ comandi in `GamePlayController`

**Categoria: Navigazione Pile (15 comandi)**
- `1-7`: Pile base (tableau)
- `SHIFT+1-4`: Pile semi (foundation)
- `SHIFT+S`: Scarti
- `SHIFT+M`: Mazzo
- `UP/DOWN/LEFT/RIGHT`: Movimento cursore
- `HOME/END`: Primo/ultimo
- `TAB`: Ciclo pile

**Categoria: Azioni Carte (8 comandi)**
- `ENTER`: Seleziona carta
- `SPACE`: Sposta carte selezionate
- `DELETE`: Annulla selezione
- `D` o `P`: Pesca dal mazzo
- `A`: Auto-move foundation
- `U`: Undo mossa
- `R`: Redo mossa

**Categoria: Informazioni (12 comandi)**
- `F`: Focus corrente
- `G`: Report stato tavolo
- `R`: Report partita
- `X`: Info carta corrente
- `C`: Carte selezionate
- `S`: Top scarti
- `M`: Contatore mazzo
- `T`: Timer elapsed
- `I`: Impostazioni
- `H`: Help comandi
- `V`: Versione app

**Categoria: Gestione Partita (8 comandi)**
- `N`: Nuova partita (con conferma)
- `O`: Opzioni
- `ESC`: Abbandona partita (con conferma)
- `Double-ESC`: Abbandona istantaneo
- `F1-F5`: Cambio mazzo/difficoltà
- `CTRL+S`: Salva partita (futuro)
- `CTRL+L`: Carica partita (futuro)

**Categoria: Debug/Test (5 comandi)**
- `CTRL+ALT+W`: Vittoria forzata (debug)
- `CTRL+ALT+D`: Dump stato (debug)
- `CTRL+ALT+R`: Reload config (debug)

**Totale**: 48 comandi base + 12 varianti SHIFT = **60+ comandi**

### Appendice C: Checklist Pre-Merge

**Validazione Completa Prima del Merge**

#### Funzionalità Core
- [ ] Menu navigazione completa (UP/DOWN/ENTER)
- [ ] Avvio partita funzionante
- [ ] Tutti i 60+ comandi gameplay testati
- [ ] Timer timeout preciso (±100ms)
- [ ] Dialog nativi funzionanti
- [ ] Options window funzionante (O key)
- [ ] Vittoria detection corretta
- [ ] Scoring system attivo

#### Accessibilità NVDA
- [ ] NVDA annuncia apertura app
- [ ] Menu items annunciati correttamente
- [ ] Comandi gameplay vocalized
- [ ] Dialog nativi leggibili (TAB cicla pulsanti)
- [ ] Focus management corretto
- [ ] Report statistiche leggibile
- [ ] No hotkey conflicts NVDA

#### Qualità Codice
- [ ] Zero import pygame nel codice wx
- [ ] Type hints completi su nuovi file
- [ ] Docstring Google-style su classi/metodi
- [ ] No code duplication (DRY)
- [ ] Clean Architecture rispettata
- [ ] Unit tests passano (pytest)

#### Documentazione
- [ ] CHANGELOG.md aggiornato (v2.0.0)
- [ ] README.md aggiornato (requisiti, avvio)
- [ ] MIGRATION_GUIDE_V2.md creato
- [ ] Commit messages descrittivi
- [ ] PR description completa

#### Performance
- [ ] Avvio app < 3 secondi
- [ ] Memoria < 50 MB
- [ ] CPU idle < 5%
- [ ] Input latency < 20ms

#### Regressione
- [ ] Tutte le feature v1.x funzionanti
- [ ] Comportamento identico a pygame version
- [ ] No breaking changes non documentati
- [ ] Backward compatibility settings files

---

## Firma e Approvazione

**Autore Piano**: Perplexity AI Assistant  
**Revisore**: [Nome Sviluppatore]  
**Data Creazione**: 12 Febbraio 2026  
**Versione Documento**: 1.0  

**Approvazione Implementazione**:
- [ ] Piano revisionato e approvato
- [ ] Timeline accettata
- [ ] Risorse allocate
- [ ] Branch `feature/wx-only-migration` creato
- [ ] Inizio sviluppo autorizzato

**Note Finali**:
Questo piano copre ogni aspetto della migrazione pygame→wxPython puro, con focus su:
1. Preservazione accessibilità NVDA (priorità massima)
2. Architettura Clean mantenuta al 100%
3. Zero breaking changes per utente finale
4. Testing intensivo prima del merge
5. Documentazione completa per manutenibilità futura

Il risultato finale sarà un'applicazione più pulita, più accessibile, e più manutenibile, con dipendenze ridotte e performance migliorate.

---

**Fine Documento**
