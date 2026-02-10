# 🎯 PIANO DI IMPLEMENTAZIONE COMPLETO
## Feature: UX Improvements (Double-Tap Selection + Menu Shortcuts)
**Versione Target**: 1.4.3  
**Data Creazione**: 10 Febbraio 2026  
**Stato**: 🟡 IN SVILUPPO

---

## ⚠️ **NOTA CRITICA: ARCHITETTURA CORRETTA**

Questo progetto ha **DUE versioni parallele**:

| Versione | Path | Entry Point | Status | Usare per Feature v1.4.3? |
|----------|------|-------------|--------|---------------------------|
| **Clean Architecture** | `src/` | `test.py` | ✅ Corrente | ✅ **SÌ** - Usare questo! |
| **Legacy** | `scr/` | `acs.py` | ⚠️ Deprecato | ❌ NO - Non modificare |

**🚨 IMPORTANTE PER IMPLEMENTAZIONE**:
- **FASE 2 (Double-Tap)**: ✅ File `src/` già specificati correttamente
- **FASE 3 (Menu Shortcuts)**: ⚠️ Deve usare `src/infrastructure/ui/menu.py` (NON `scr/pygame_menu.py`)

---

## 📋 EXECUTIVE SUMMARY

Questo documento descrive l'implementazione di due miglioramenti UX per il Solitario Accessibile:

1. **Double-Tap Auto-Selection**: Ripristino funzionalità legacy per selezione automatica carta con doppia pressione dello stesso numero di pila
2. **Numeric Menu Shortcuts**: Aggiunta scorciatoie numeriche per navigazione rapida nei menu

**Obiettivo**: Migliorare l'accessibilità e la velocità di interazione per utenti con screen reader.

**Impatto**: 3 file modificati (Clean Arch), ~150 righe di codice, stima 2.5-3.5 ore di sviluppo.

---

## 🎮 FEATURE #1: Double-Tap Auto-Selection

### 📖 Descrizione Funzionale

Ripristinare il comportamento della versione legacy (`scr/game_engine.py`) dove la **seconda pressione consecutiva dello stesso numero di pila** seleziona automaticamente l'ultima carta della pila, sostituendo eventuali selezioni precedenti.

**Scope**:
- ✅ Pile base (1-7): Double-tap attivo
- ✅ Pile seme (SHIFT+1-4): Double-tap attivo
- ❌ Scarti (SHIFT+S): Double-tap disabilitato (solo hint)
- ❌ Mazzo (SHIFT+M): Double-tap disabilitato (solo hint)

### 🔄 Flusso Comportamentale

#### **Scenario 1: Prima Pressione (Qualunque Pila)**
```
Input: Utente preme "1"
Azione: CursorManager sposta cursore su pila base 1
Output: "Pila base 1. Carta in cima: 7 di Cuori. Premi ancora 1 per selezionare."
Stato: last_quick_pile = 0 (indice pila)
```

#### **Scenario 2: Seconda Pressione (Pile Base/Seme)**
```
Input: Utente preme "1" di nuovo
Condizione: pile_idx == last_quick_pile == 0 AND pila non vuota
Azione: 
  1. CursorManager move_to_top_card() → posiziona cursore su ultima carta
  2. CursorManager ritorna ("", True) → flag auto-selection
  3. GameEngine annulla selezione precedente (se presente)
  4. GameEngine chiama select_card_at_cursor()
Output: "Selezione precedente annullata. carte selezionate: 1. 7 di Cuori!"
Stato: last_quick_pile = None (reset)
```

#### **Scenario 3: Seconda Pressione (Scarti/Mazzo)**
```
Input: Utente preme "SHIFT+S" di nuovo
Condizione: pile_idx == 11 (scarti) AND last_quick_pile == 11
Azione: Nessuna selezione automatica
Output: "Cursore già sulla pila."
Stato: last_quick_pile = None (reset)
```

#### **Scenario 4: Pila Vuota (Secondo Tap)**
```
Input: Utente preme "3" due volte su pila base 3 vuota
Condizione: pile_idx == 2 AND pila.is_empty()
Output: "Pila vuota, nessuna carta da selezionare."
Stato: last_quick_pile = None
```

### 🛠️ Implementazione Tecnica

#### **Modifica 1.1: `src/domain/services/cursor_manager.py`** ✅

**Metodo Modificato**: `jump_to_pile(pile_idx: int, enable_double_tap: bool = True)`

**Cambiamenti**:
1. **Signature**: Cambio ritorno da `str` a `Tuple[str, bool]`
2. **Double-Tap Detection**: Aggiunta logica per riconoscere secondo tap
3. **Auto-Selection Flag**: Ritorno `(messaggio, should_auto_select)` invece di solo messaggio
4. **Cursor Positioning**: `move_to_top_card()` chiamato prima di ritornare flag auto-select

**Codice Completo**:

```python
from typing import Tuple, Optional, Dict, Any

def jump_to_pile(self, pile_idx: int, enable_double_tap: bool = True) -> Tuple[str, bool]:
    """Jump to specific pile with optional double-tap auto-selection.
    
    Args:
        pile_idx: Target pile index (0-12)
            - 0-6: Tableau (base) piles
            - 7-10: Foundation (semi) piles
            - 11: Waste (scarti) pile
            - 12: Stock (mazzo) pile
        enable_double_tap: Enable double-tap detection for auto-selection
    
    Returns:
        Tuple of (feedback_message, should_auto_select)
        - feedback_message: String for screen reader announcement
        - should_auto_select: True if second tap should trigger automatic card selection
    
    Behavior:
        First tap: Move cursor to pile top card + announce hint
        Second tap (tableau/foundation): Auto-select top card (empty message + flag True)
        Second tap (stock/waste): No action (hint message + flag False)
    
    Examples:
        >>> # First tap on tableau pile 1
        >>> msg, auto = cursor.jump_to_pile(0)
        >>> print(msg)  # "Pila base 1. Carta in cima: 7 di Cuori. Premi ancora 1 per selezionare."
        >>> print(auto)  # False
        
        >>> # Second tap on same pile
        >>> msg, auto = cursor.jump_to_pile(0)
        >>> print(msg)  # ""
        >>> print(auto)  # True (triggers selection in GameEngine)
    """
    # Validate pile index
    if pile_idx < 0 or pile_idx >= len(self.table.pile):
        return ("Indice pila non valido!\n", False)
    
    # ═══════════════════════════════════════════════════════════
    # 🔥 DOUBLE-TAP DETECTION: Second press on same pile
    # ═══════════════════════════════════════════════════════════
    if enable_double_tap and self.pile_idx == pile_idx and self.last_quick_pile == pile_idx:
        pile = self.table.pile[pile_idx]
        
        # ─────────────────────────────────────────────────────
        # Stock/Waste: Disable auto-selection (hint only)
        # ─────────────────────────────────────────────────────
        if pile_idx >= 11:
            self.last_quick_pile = None
            return ("Cursore già sulla pila.\n", False)
        
        # ─────────────────────────────────────────────────────
        # Tableau/Foundation: Enable auto-selection
        # ─────────────────────────────────────────────────────
        if pile.is_empty():
            self.last_quick_pile = None
            return ("Pila vuota, nessuna carta da selezionare.\n", False)
        
        # ✅ Position cursor on top card BEFORE signaling selection
        self.move_to_top_card()
        
        # ✅ Signal GameEngine to execute automatic selection
        # Empty message because selection feedback will be announced by GameEngine
        self.last_quick_pile = None
        return ("", True)
    
    # ═══════════════════════════════════════════════════════════
    # 🎯 FIRST TAP: Move cursor and announce pile info
    # ═══════════════════════════════════════════════════════════
    self.pile_idx = pile_idx
    self.move_to_top_card()
    self.last_quick_pile = pile_idx if enable_double_tap else None
    
    msg = self._get_pile_summary()
    
    # ─────────────────────────────────────────────────────
    # Add context-specific hints
    # ─────────────────────────────────────────────────────
    pile = self.get_current_pile()
    
    if pile_idx == 12 and not pile.is_empty():
        # Stock pile hint
        msg += "Premi INVIO per pescare.\n"
        
    elif pile_idx == 11 and not pile.is_empty():
        # Waste pile hint
        msg += "Usa frecce per navigare. CTRL+INVIO per selezionare ultima carta.\n"
        
    elif not pile.is_empty() and pile_idx <= 10:
        # Tableau/Foundation piles: double-tap hint
        if pile_idx <= 6:
            # Tableau (base) piles: number 1-7
            msg += f"Premi ancora {pile_idx + 1} per selezionare.\n"
        else:
            # Foundation (semi) piles: SHIFT+1-4
            seme_num = pile_idx - 6
            msg += f"Premi ancora SHIFT+{seme_num} per selezionare.\n"
    
    return (msg, False)  # No auto-selection on first tap
```

**Aggiornamento Import**:
```python
from typing import Tuple, Optional, Dict, Any
```

---

#### **Modifica 1.2: `src/application/game_engine.py`** ✅

**Metodo Modificato**: `jump_to_pile(pile_idx: int)`

**Cambiamenti**:
1. **Handle Tuple Return**: Gestire ritorno `(msg, flag)` da CursorManager
2. **Auto-Selection Logic**: Implementare selezione automatica quando `should_auto_select == True`
3. **Clear Previous Selection**: Annullare selezione precedente silenziosamente prima di nuova selezione
4. **Voice Feedback**: Annunciare stato finale (con o senza auto-selection)

**Codice Completo**:

```python
def jump_to_pile(self, pile_idx: int) -> str:
    """Jump to specific pile with double-tap auto-selection support.
    
    Args:
        pile_idx: Pile index (0-12)
    
    Returns:
        Feedback message for screen reader
    
    Behavior:
        First tap: Move cursor to pile top card + announce pile info
        Second tap (tableau/foundation): 
            - Cancel previous selection if present (silent)
            - Auto-select top card
            - Announce: "Selezione precedente annullata. carte selezionate: 1. [nome carta]"
        Second tap (stock/waste): No action (hint only)
    
    Examples:
        >>> # First tap
        >>> engine.jump_to_pile(0)
        "Pila base 1. Carta in cima: 7 di Cuori. Premi ancora 1 per selezionare."
        
        >>> # Second tap (no previous selection)
        >>> engine.jump_to_pile(0)
        "carte selezionate: 1. 7 di Cuori!"
        
        >>> # Second tap (with previous selection)
        >>> engine.jump_to_pile(0)  # had 5 di Picche selected
        "Selezione precedente annullata. carte selezionate: 1. 7 di Cuori!"
    """
    # Get cursor movement feedback and auto-selection flag
    msg, should_auto_select = self.cursor.jump_to_pile(pile_idx, enable_double_tap=True)
    
    # ═══════════════════════════════════════════════════════════
    # 🔥 SECOND TAP: Execute automatic card selection
    # ═══════════════════════════════════════════════════════════
    if should_auto_select:
        msg_deselect = ""
        
        # ─────────────────────────────────────────────────────
        # Cancel previous selection if present (silent reset)
        # ─────────────────────────────────────────────────────
        if self.selection.has_selection():
            self.selection.clear_selection()
            msg_deselect = "Selezione precedente annullata. "
        
        # ─────────────────────────────────────────────────────
        # Execute automatic selection
        # ─────────────────────────────────────────────────────
        success, msg_select = self.select_card_at_cursor()
        
        # Combine messages: deselection (if any) + selection feedback
        msg = msg_deselect + msg_select
    
    # ═══════════════════════════════════════════════════════════
    # 🔊 Vocal announcement
    # ═══════════════════════════════════════════════════════════
    if self.screen_reader and msg:
        self.screen_reader.tts.speak(msg, interrupt=True)
    
    return msg
```

**Nessun Import Aggiuntivo Necessario** (usa già metodi esistenti).

---

### ✅ Testing Checklist Feature #1

#### **Test Pile Base (1-7)**
- [ ] **T1.1**: Primo tap su pila base 1 → Annuncia "Pila base 1. Carta in cima: [nome]. Premi ancora 1 per selezionare."
- [ ] **T1.2**: Secondo tap su pila base 1 → Seleziona automaticamente ultima carta + annuncia "carte selezionate: 1. [nome]!"
- [ ] **T1.3**: Secondo tap con selezione precedente attiva → Annuncia "Selezione precedente annullata. carte selezionate: 1. [nuovo nome]!"
- [ ] **T1.4**: Secondo tap su pila vuota → Annuncia "Pila vuota, nessuna carta da selezionare."
- [ ] **T1.5**: Terza pressione dopo selezione → Comportamento normale (primo tap, non double-tap)

#### **Test Pile Seme (SHIFT+1-4)**
- [ ] **T1.6**: Primo tap SHIFT+2 (Quadri) → Annuncia "Pila semi Quadri. Carta in cima: [nome]. Premi ancora SHIFT+2 per selezionare."
- [ ] **T1.7**: Secondo tap SHIFT+2 → Seleziona automaticamente carta + annuncia feedback corretto
- [ ] **T1.8**: Secondo tap su pila semi vuota → Messaggio errore appropriato

#### **Test Scarti/Mazzo (Comportamento Invariato)**
- [ ] **T1.9**: Secondo tap SHIFT+S (scarti) → Annuncia "Cursore già sulla pila." (NO auto-select)
- [ ] **T1.10**: Secondo tap SHIFT+M (mazzo) → Annuncia "Cursore già sulla pila." (NO auto-select)

#### **Test Edge Cases**
- [ ] **T1.11**: Tap su pila diversa resetta `last_quick_pile` → Primo tap su pila 1, poi tap su pila 2 = nuovo primo tap
- [ ] **T1.12**: Movimento cursore con frecce resetta `last_quick_pile` → Double-tap non attivo dopo frecce
- [ ] **T1.13**: Selezione manuale (INVIO) non interferisce con double-tap tracking

---

## 🎮 FEATURE #2: Numeric Menu Shortcuts

### 📖 Descrizione Funzionale

Implementare scorciatoie numeriche per attivare direttamente le voci dei menu, similmente al sistema già presente nella finestra virtuale opzioni (F1-F5).

**Scope**:
- ✅ Menu Principale: Shortcut 1 per "Gioca al solitario classico"
- ✅ Menu Solitario (submenu): Nessun shortcut (gestito da test.py con context-aware routing)

**Gestione Conflitti**: I tasti 1-7 sono già occupati durante il gioco (pile base). Soluzione: gli shortcut menu funzionano **solo quando il menu VirtualMenu è attivo** (routing gestito da `test.py`).

### 🗺️ Mappatura Shortcuts

#### **Menu Principale** (avvio applicazione)
| # | Voce Menu | Shortcut | Alternativa | Azione |
|---|-----------|----------|-------------|--------|
| 1 | Gioca al solitario classico | **`1`** | ENTER | Apre gameplay |
| 2 | Esci dal gioco | ESC | ESC | Conferma uscita |

**Visualizzazione**:
```
1. Gioca al solitario classico  ← aggiunto prefisso "1."
Esci dal gioco                   ← nessun prefisso (usa ESC)
```

---

#### **Menu Solitario (Game Submenu)** (aperto da menu principale)
| # | Voce Menu | Shortcut | Alternativa | Azione |
|---|-----------|----------|-------------|--------|
| 1 | Nuova partita | **`1`** | ENTER | Avvia nuova partita |
| 2 | Opzioni | **`2`** | ENTER | Apre opzioni |
| 3 | Chiudi | **`3`** | ESC | Torna a menu principale |

**Nota**: Durante gameplay, ESC apre dialog di conferma abbandono (gestito da `test.py`). I tasti 1-7 durante gameplay vanno alle pile base (NO conflitto con menu).

---

### 🔄 Flusso Comportamentale

#### **Scenario 1: Menu Principale - Shortcut 1**
```
Stato: Menu principale aperto (all'avvio app)
Input: Utente preme "1"
Azione: VirtualMenu.press_1() → selected_index = 0 → execute()
Output: "Hai selezionato Gioca al solitario classico"
Risultato: Callback apre game submenu
```

#### **Scenario 2: Game Submenu - Apertura da Menu Principale**
```
Stato: Menu principale, voce 1 selezionata
Input: Utente preme "1" o ENTER
Azione: main_menu.callback(0) → apre game_submenu
Output: "Benvenuto nel menu di gioco del Solitario Classico! ..."
Risultato: Game submenu attivo con 3 voci
```

#### **Scenario 3: Game Submenu - Shortcut 1 (Nuova Partita)**
```
Stato: Game submenu aperto
Input: Utente preme "1"
Azione: VirtualMenu.press_1() → selected_index = 0 → execute() → callback(0)
Output: "Nuova partita avviata! Usa H per l'aiuto comandi."
Risultato: Partita inizia, menu chiuso
```

#### **Scenario 4: Durante Gameplay - Tasto 1 (NO Conflitto)**
```
Stato: Partita in corso, menu chiuso
Input: Utente preme "1"
Azione: gameplay_controller.handle_keyboard_events() → chiama pile jump
Output: "Pila base 1. Carta in cima: [nome]. Premi ancora 1 per selezionare."
Risultato: Cursore su pila base 1 (comportamento normale, menu non interferisce)
```

---

### 🛠️ Implementazione Tecnica

#### **Modifica 2.1: `src/infrastructure/ui/menu.py`** ⚠️ **CRITICAL PATH**

**⚠️ ATTENZIONE**: Questo è il file **Clean Architecture** (`src/`), NON il file legacy (`scr/pygame_menu.py`).

**Cambiamenti**:
1. **Add Numeric Handlers**: Metodi `press_1()` ... `press_5()` per shortcut diretti
2. **Update Event Handler**: Aggiungere gestione K_1 .. K_5 in `handle_keyboard_events()`
3. **Build Command Dictionary**: Creare mappatura key → handler (opzionale, per codice più pulito)

**Codice Modifiche**:

```python
# ═══════════════════════════════════════════════════════════
# MODIFICA 1: __init__() - Build command mappings (OPTIONAL)
# ═══════════════════════════════════════════════════════════
def __init__(self, items, callback, screen, screen_reader, parent_menu=None, 
             welcome_message=None, show_controls_hint=True):
    """Initialize virtual menu with numeric shortcuts support."""
    # ... existing initialization code ...
    
    # ✅ Build keyboard command mappings
    self._build_key_handlers()

def _build_key_handlers(self) -> None:
    """Build keyboard command mappings for menu navigation.
    
    Maps keyboard events to handler methods, including:
    - Arrow keys for navigation
    - ENTER for selection
    - ESC for closing submenu
    - Numeric keys 1-5 for direct item selection (NEW)
    """
    self.key_handlers = {
        pygame.K_DOWN: self.next_item,
        pygame.K_UP: self.prev_item,
        pygame.K_RETURN: self.execute,
        pygame.K_ESCAPE: self._handle_esc,
        # ✅ NUMERIC SHORTCUTS (1 = first item, 2 = second, ...)
        pygame.K_1: self.press_1,
        pygame.K_2: self.press_2,
        pygame.K_3: self.press_3,
        pygame.K_4: self.press_4,
        pygame.K_5: self.press_5,
    }

# ═══════════════════════════════════════════════════════════
# MODIFICA 2: Numeric shortcut handlers (NEW METHODS)
# ═══════════════════════════════════════════════════════════
def press_1(self) -> None:
    """Shortcut: select first menu item and execute.
    
    Equivalent to navigating to item 1 and pressing ENTER.
    """
    if len(self.items) >= 1:
        self.selected_index = 0
        self.execute()

def press_2(self) -> None:
    """Shortcut: select second menu item and execute.
    
    Equivalent to navigating to item 2 and pressing ENTER.
    """
    if len(self.items) >= 2:
        self.selected_index = 1
        self.execute()

def press_3(self) -> None:
    """Shortcut: select third menu item and execute."""
    if len(self.items) >= 3:
        self.selected_index = 2
        self.execute()

def press_4(self) -> None:
    """Shortcut: select fourth menu item and execute."""
    if len(self.items) >= 4:
        self.selected_index = 3
        self.execute()

def press_5(self) -> None:
    """Shortcut: select fifth menu item and execute."""
    if len(self.items) >= 5:
        self.selected_index = 4
        self.execute()

# ═══════════════════════════════════════════════════════════
# MODIFICA 3: handle_keyboard_events() - Use key_handlers dict
# ═══════════════════════════════════════════════════════════
def _handle_esc(self) -> None:
    """Handle ESC key - close menu if has parent."""
    if self.parent_menu:
        self.parent_menu.close_submenu()

def handle_keyboard_events(self, event: pygame.event.Event) -> None:
    """Handle keyboard input for menu navigation with numeric shortcuts.
    
    Processes PyGame keyboard events and maps them to menu actions.
    Now includes support for numeric shortcuts 1-5.
    
    If a submenu is active, delegates all events to it.
    ESC key closes active submenu and returns to parent.
    
    Args:
        event: PyGame event to process
    
    Supported keys:
        - K_DOWN/K_UP: Navigate menu
        - K_RETURN: Execute selected item
        - K_ESCAPE: Close submenu (if has parent)
        - K_1..K_5: Direct selection shortcuts (NEW)
    """
    # If submenu is active, delegate all events to it
    if self._active_submenu:
        self._active_submenu.handle_keyboard_events(event)
        return
    
    if event.type == pygame.KEYDOWN:
        # ✅ Use key_handlers dictionary for cleaner code
        handler = self.key_handlers.get(event.key)
        if handler:
            handler()
```

**Posizionamento**: 
- `_build_key_handlers()`: Chiamato da `__init__()` (dopo altre inizializzazioni)
- Nuovi metodi `press_X()`: Dopo metodo `execute()` 
- `handle_keyboard_events()`: Modifica metodo esistente (usa dict invece di if/elif)

---

#### **Modifica 2.2: Verificare Routing in `test.py`** ✅

**Verifica Necessaria**: Il file `test.py` (entry point Clean Architecture) deve già gestire correttamente il routing eventi. Verificare che durante gameplay i tasti 1-7 vadano al `gameplay_controller` e NON al menu.

**Codice Esistente da Verificare** (linee ~500-600):

```python
def handle_events(self):
    for event in pygame.event.get():
        # ... dialog handlers ...
        
        # Route keyboard events based on state
        if self.is_menu_open:
            # ✅ Menu mode: route to VirtualMenu
            # VirtualMenu.handle_keyboard_events() gestisce i tasti 1-5
            self.menu.handle_keyboard_events(event)
        
        elif self.is_options_mode:
            # ✅ Options mode: route to gameplay controller
            self.gameplay_controller.handle_keyboard_events(event)
        
        else:
            # ✅ GAMEPLAY MODE: route to gameplay controller
            # Tasti 1-7 vanno alle pile base (NO conflitto con menu)
            self.gameplay_controller.handle_keyboard_events(event)
```

**✅ CONFERMATO**: Il routing in `test.py` è già corretto. Non servono modifiche.

---

### ✅ Testing Checklist Feature #2

#### **Test Menu Principale**
- [ ] **T2.1**: Avvio app → Menu mostra voci con event delegation corretto
- [ ] **T2.2**: Premere `1` → Apre game submenu direttamente (equivalente a ENTER su prima voce)
- [ ] **T2.3**: Premere `ESC` → Mostra dialog conferma uscita (comportamento invariato)
- [ ] **T2.4**: Frecce UP/DOWN → Funzionano ancora correttamente (no regressione)

#### **Test Game Submenu**
- [ ] **T2.5**: Menu principale, seleziona "Gioca" → Apre submenu con 3 voci + welcome message
- [ ] **T2.6**: Submenu aperto, premere `1` → Avvia nuova partita
- [ ] **T2.7**: Submenu aperto, premere `2` → Apre finestra opzioni
- [ ] **T2.8**: Submenu aperto, premere `3` → Mostra dialog conferma ritorno menu principale
- [ ] **T2.9**: Submenu aperto, premere `ESC` → Mostra dialog conferma ritorno (stesso comportamento di `3`)

#### **Test Gestione Conflitti (Gameplay vs Menu)**
- [ ] **T2.10**: Durante gameplay (menu chiuso), premere `1` → Sposta cursore su pila base 1 (NO menu action)
- [ ] **T2.11**: Durante gameplay (menu chiuso), premere `2` → Sposta cursore su pila base 2 (NO menu action)
- [ ] **T2.12**: Durante gameplay (menu chiuso), premere `3` → Sposta cursore su pila base 3 (NO menu action)
- [ ] **T2.13**: Durante gameplay, premere `ESC` → Mostra dialog abbandono partita (gestito da test.py)

#### **Test Edge Cases**
- [ ] **T2.14**: Premere tasti 4-7 nei menu → Nessuna azione (solo 1-3 validi)
- [ ] **T2.15**: Aprire/chiudere submenu più volte → Nessun bug stato
- [ ] **T2.16**: Submenu aperto, dialog attivo → Solo dialog risponde a tastiera (priorità corretta)

---

## 📊 RIEPILOGO MODIFICHE

### File Modificati (Clean Architecture)

| File | Feature | Linee Modificate | Metodi Nuovi | Metodi Modificati | Stima Righe |
|------|---------|------------------|--------------|-------------------|-------------|
| **`src/domain/services/cursor_manager.py`** | #1 | ~380-430 | - | `jump_to_pile()` | ~50 |
| **`src/application/game_engine.py`** | #1 | ~497-520 | - | `jump_to_pile()` | ~20 |
| **`src/infrastructure/ui/menu.py`** | #2 | ~50-150 | `press_1()` .. `press_5()`, `_build_key_handlers()`, `_handle_esc()` | `__init__()`, `handle_keyboard_events()` | ~80 |
| **`test.py`** | #2 | - | - | ✅ Nessuna (routing già corretto) | 0 |
| **TOTALE** | | | **8 metodi** | **5 metodi** | **~150 righe** |

---

## 🚀 PIANO DI IMPLEMENTAZIONE SEQUENZIALE

### **FASE 1: Setup & Preparation** ⏱️ 15 min
- [x] Creazione file documentazione
- [x] Creazione TODO.md con checklist
- [ ] Review piano con stakeholder
- [ ] Setup branch di sviluppo (se necessario)

### **FASE 2: Feature #1 - Double-Tap Selection** ⏱️ 1-2 ore ✅
#### **Step 2.1: Modifica CursorManager**
- [ ] Aprire `src/domain/services/cursor_manager.py` ✅ Path corretto
- [ ] Aggiornare import: `from typing import Tuple, ...`
- [ ] Modificare signature `jump_to_pile()` → ritorno `Tuple[str, bool]`
- [ ] Implementare logica double-tap detection (pile_idx == last_quick_pile)
- [ ] Implementare logica auto-selection flag (stock/waste vs. tableau/foundation)
- [ ] Testare isolatamente (unit test se disponibili)

#### **Step 2.2: Modifica GameEngine**
- [ ] Aprire `src/application/game_engine.py` ✅ Path corretto
- [ ] Modificare `jump_to_pile()` per gestire Tuple return
- [ ] Implementare logica auto-selection con annullamento selezione precedente
- [ ] Testare integrazione CursorManager → GameEngine

#### **Step 2.3: Testing Feature #1**
- [ ] Eseguire tutti i test checklist T1.1 - T1.13
- [ ] Verificare feedback vocale screen reader
- [ ] Testare edge cases (pile vuote, selezioni multiple, etc.)
- [ ] Bug fixing se necessario

### **FASE 3: Feature #2 - Menu Shortcuts** ⏱️ 1 ora ⚠️ **PATH CORRETTI**
#### **Step 3.1: Modifica VirtualMenu (Menu Clean Architecture)**
- [ ] ⚠️ **IMPORTANTE**: Aprire `src/infrastructure/ui/menu.py` (NON `scr/pygame_menu.py`)
- [ ] Aggiungere metodo `_build_key_handlers()` con mappatura K_1..K_5
- [ ] Aggiungere handler `press_1()` ... `press_5()`
- [ ] Aggiungere metodo helper `_handle_esc()`
- [ ] Modificare `handle_keyboard_events()` per usare `key_handlers` dict
- [ ] Chiamare `_build_key_handlers()` da `__init__()`
- [ ] Testare menu principale con shortcuts

#### **Step 3.2: Verificare Routing Eventi in test.py**
- [ ] Aprire `test.py` (entry point Clean Architecture)
- [ ] Verificare metodo `handle_events()` (linee ~500-600)
- [ ] ✅ Confermare che routing `is_menu_open` → `self.menu.handle_keyboard_events(event)` è già presente
- [ ] ✅ Confermare che routing gameplay → `self.gameplay_controller.handle_keyboard_events(event)` è già presente
- [ ] ✅ Nessuna modifica necessaria (routing già corretto)

#### **Step 3.3: Testing Feature #2**
- [ ] Eseguire tutti i test checklist T2.1 - T2.16
- [ ] Verificare assenza conflitti tastiera (menu vs. pile base durante gameplay)
- [ ] Testare apertura/chiusura submenu multipla
- [ ] Testare shortcuts menu principale (tasto 1)
- [ ] Testare shortcuts game submenu (tasti 1/2/3)
- [ ] Bug fixing se necessario

### **FASE 4: Integration Testing** ⏱️ 30 min
- [ ] Testare entrambe le feature insieme in scenario reale
- [ ] Verificare double-tap selection accessibile da menu con shortcuts
- [ ] Verificare menu shortcuts non interferiscono con double-tap durante gameplay
- [ ] Test regressione: tutti i comandi esistenti funzionano ancora
- [ ] Performance check: nessun lag o rallentamento percepibile

### **FASE 5: Documentation & Release** ⏱️ 30 min
- [ ] Aggiornare `README.md` (se necessario aggiungere note shortcuts)
- [ ] Aggiornare `CHANGELOG.md` con sezione versione 1.4.3:
  ```markdown
  ## [1.4.3] - 2026-02-10
  
  ### Added
  - Double-tap auto-selection: seconda pressione numero pila seleziona automaticamente ultima carta (pile base 1-7 e pile seme SHIFT+1-4)
  - Numeric menu shortcuts: scorciatoie 1-5 per navigazione rapida menu principale e game submenu
  
  ### Changed
  - VirtualMenu supporta shortcuts numerici per selezione diretta voci
  - Hint migliorati per pile base/semi: "Premi ancora [numero] per selezionare"
  
  ### Fixed
  - Gestione routing eventi tra menu e gameplay (context-aware, no conflitti tastiera)
  ```
- [ ] Aggiornare help in-game gameplay_controller (se applicabile)
- [ ] Commit finale con messaggio descrittivo
- [ ] Merge su branch principale (se feature branch usato)
- [ ] Tag release v1.4.3

---

## 🎯 ACCEPTANCE CRITERIA

### Feature #1: Double-Tap Selection
✅ **Criterio 1**: Seconda pressione numero pila (1-7, SHIFT+1-4) seleziona automaticamente ultima carta  
✅ **Criterio 2**: Selezione precedente viene annullata automaticamente prima di nuova selezione  
✅ **Criterio 3**: Scarti e mazzo mantengono comportamento originale (hint, no auto-selection)  
✅ **Criterio 4**: Feedback vocale chiaro e consistente per tutte le azioni  

### Feature #2: Menu Shortcuts
✅ **Criterio 1**: Tasto `1` attiva prima voce menu principale ("Gioca al solitario")  
✅ **Criterio 2**: Tasti `1/2/3` attivano rispettive voci game submenu (quando submenu aperto)  
✅ **Criterio 3**: Nessun conflitto con pile base 1-7 durante gameplay (routing corretto in test.py)  
✅ **Criterio 4**: ESC gestito correttamente in tutti i contesti (menu, submenu, gameplay)  

### General
✅ **Criterio 5**: Zero regressioni su comandi esistenti  
✅ **Criterio 6**: Performance invariata (nessun lag percepibile)  
✅ **Criterio 7**: Accessibilità: tutti i messaggi vocali sono chiari e informativi  

---

## 🐛 TROUBLESHOOTING & FAQ

### Problema 1: Double-tap non funziona
**Sintomo**: Seconda pressione numero pila non seleziona carta  
**Cause Possibili**:
- `last_quick_pile` non impostato correttamente su primo tap
- Condizione `pile_idx == last_quick_pile` non verificata
- Flag `should_auto_select` non gestito in GameEngine

**Debug Steps**:
1. Verificare valore `last_quick_pile` dopo primo tap (dovrebbe essere pile_idx)
2. Verificare ritorno `jump_to_pile()` → dovrebbe essere `("", True)` su secondo tap
3. Verificare chiamata `select_card_at_cursor()` in GameEngine

---

### Problema 2: Selezione precedente non annullata
**Sintomo**: Double-tap su nuova pila aggiunge carta invece di sostituire  
**Causa**: `selection.clear_selection()` non chiamato prima di nuova selezione

**Fix**:
```python
if self.selection.has_selection():
    self.selection.clear_selection()  # ← Verificare questa riga
```

---

### Problema 3: Conflitto tastiera menu vs. pile
**Sintomo**: Premere `1` durante gioco apre menu o non fa nulla  
**Causa**: Routing eventi in `test.py` non corretto O modifiche applicate a file legacy `scr/`

**Fix**:
1. ⚠️ **Verificare di aver modificato `src/infrastructure/ui/menu.py`** (NON `scr/pygame_menu.py`)
2. Verificare che `test.py` route correttamente:
   ```python
   if self.is_menu_open:
       self.menu.handle_keyboard_events(event)  # Menu shortcuts attivi
   else:
       self.gameplay_controller.handle_keyboard_events(event)  # Pile base attive
   ```

---

### Problema 4: Menu shortcuts non funzionano affatto
**Sintomo**: Premere `1` in menu non fa nulla  
**Causa Più Probabile**: ⚠️ **Modifiche applicate a file LEGACY (`scr/`) invece di Clean Architecture (`src/`)**

**Fix**:
1. Verificare quale file è stato modificato:
   - ❌ Se modificato `scr/pygame_menu.py` → file sbagliato (legacy non usato da test.py)
   - ✅ Se modificato `src/infrastructure/ui/menu.py` → file corretto
2. Riapplicare modifiche al file corretto `src/infrastructure/ui/menu.py`
3. Verificare che `test.py` usi `VirtualMenu` da `src/infrastructure/ui/menu.py`

---

## 📚 REFERENCES

### Codice Clean Architecture (DA USARE)
- ✅ `src/domain/services/cursor_manager.py` (Feature #1)
- ✅ `src/application/game_engine.py` (Feature #1)
- ✅ `src/infrastructure/ui/menu.py` (Feature #2) ⚠️ **PATH CRITICO**
- ✅ `test.py` (Entry point, routing eventi)

### Codice Legacy (NON MODIFICARE)
- ❌ `scr/game_engine.py` (vecchia implementazione double-tap, solo riferimento)
- ❌ `scr/pygame_menu.py` (vecchio menu, non usato da test.py)
- ❌ `scr/game_play.py` (vecchio gameplay, non usato da test.py)
- ❌ `acs.py` (entry point legacy deprecato)

### Documentazione Correlata
- `docs/REFACTORING_PLAN.md` (piano refactoring generale)
- `docs/IMPLEMENTATION_SUMMARY.md` (summary implementazione DDD)
- `README.md` (comandi tastiera attuali)

### Risorse Pygame
- [Pygame Events Documentation](https://www.pygame.org/docs/ref/event.html)
- [Pygame Key Constants](https://www.pygame.org/docs/ref/key.html)

---

## 📝 NOTES & CONSIDERATIONS

### Design Decisions

**Q: Perché double-tap solo per pile base/semi e non scarti/mazzo?**  
**A**: Scarti e mazzo hanno già shortcut dedicati (CTRL+INVIO per scarti, INVIO per mazzo). Double-tap creerebbe ambiguità e potrebbe causare selezioni accidentali.

**Q: Perché usare flag booleano invece di exception/evento per auto-selection?**  
**A**: Flag booleano è più semplice, esplicito e type-safe (`Tuple[str, bool]`). Evita overhead di exception handling e rende il flusso più chiaro.

**Q: Perché modificare `src/infrastructure/ui/menu.py` invece di `scr/pygame_menu.py`?**  
**A**: ⚠️ **CRITICO** - Il progetto ha due versioni parallele:
- **Clean Architecture** (`src/`) usata da `test.py` (entry point corrente) ✅
- **Legacy** (`scr/`) usata da `acs.py` (deprecato) ❌

Feature v1.4.3 DEVE essere implementata sulla versione Clean Architecture per essere utilizzabile.

---

### Future Enhancements

**Possibili Miglioramenti Futuri**:
- [ ] Aggiungere shortcut ALT+numero per spostamento diretto su pile seme (alternativa a SHIFT+numero)
- [ ] Implementare "memory" ultima pila visitata per tornare rapidamente con shortcut dedicato
- [ ] Aggiungere animazioni/feedback audio per double-tap riuscito
- [ ] Estendere sistema menu shortcuts ad altri dialog box (conferme, etc.)

---

## ✅ SIGN-OFF

**Sviluppatore**: _________________________  
**Data Completamento**: _____________  
**Versione**: 1.4.3  
**Status**: [ ] In Progress | [ ] Completed | [ ] Blocked

**Note Finali**:
_______________________________________________________
_______________________________________________________
_______________________________________________________

---

**Fine Documento**  
Ultimo aggiornamento: 10 Febbraio 2026 (v2 - Correzione path Clean Architecture)