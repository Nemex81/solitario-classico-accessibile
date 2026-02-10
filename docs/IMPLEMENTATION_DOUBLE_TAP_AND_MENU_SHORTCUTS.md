# 🎯 PIANO DI IMPLEMENTAZIONE COMPLETO
## Feature: UX Improvements (Double-Tap Selection + Menu Shortcuts)
**Versione Target**: 1.4.3  
**Data Creazione**: 10 Febbraio 2026  
**Stato**: 🟡 IN SVILUPPO

---

## 📋 EXECUTIVE SUMMARY

Questo documento descrive l'implementazione di due miglioramenti UX per il Solitario Accessibile:

1. **Double-Tap Auto-Selection**: Ripristino funzionalità legacy per selezione automatica carta con doppia pressione dello stesso numero di pila
2. **Numeric Menu Shortcuts**: Aggiunta scorciatoie numeriche per navigazione rapida nei menu

**Obiettivo**: Migliorare l'accessibilità e la velocità di interazione per utenti con screen reader.

**Impatto**: 4 file modificati, ~150 righe di codice, stima 2.5-3.5 ore di sviluppo.

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

#### **Modifica 1.1: `src/domain/services/cursor_manager.py`**

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

#### **Modifica 1.2: `src/application/game_engine.py`**

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
- ✅ Menu Solitario In-Game: Shortcuts 1/2/3 per voci menu pausa

**Gestione Conflitti**: I tasti 1-7 sono già occupati durante il gioco (pile base). Soluzione: gli shortcut menu funzionano **solo quando il menu è aperto** (flag `is_solitaire_menu_open`).

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

#### **Menu Solitario** (pausa in-game, aperto con ESC)
| # | Voce Menu | Shortcut | Alternativa | Azione |
|---|-----------|----------|-------------|--------|
| 1 | Nuova partita | **`1`** | `N` | Avvia nuova partita |
| 2 | Opzioni | **`2`** | `O` | Apre opzioni |
| 3 | Chiudi partita | **`3`** | ESC | Chiudi e torna a menu principale |

**Visualizzazione** (quando ESC premuto durante partita):
```
MENU SOLITARIO:
1. Nuova partita
2. Opzioni
3. Chiudi partita
```

---

### 🔄 Flusso Comportamentale

#### **Scenario 1: Menu Principale - Shortcut 1**
```
Stato: Menu principale aperto (all'avvio app)
Input: Utente preme "1"
Azione: PyMenu.press_1() → selected_item = 0 → execute()
Output: "Hai selezionato Gioca al solitario classico"
Risultato: Chiude menu principale, apre gameplay
```

#### **Scenario 2: Menu Solitario - Apertura con ESC**
```
Stato: Partita in corso (is_game_running = True)
Input: Utente preme "ESC"
Azione: GamePlay.esc_press() → open_solitaire_menu()
Output: "MENU SOLITARIO: 1. Nuova partita, 2. Opzioni, 3. Chiudi partita"
Risultato: is_solitaire_menu_open = True
```

#### **Scenario 3: Menu Solitario - Shortcut 1 (Nuova Partita)**
```
Stato: Menu solitario aperto (is_solitaire_menu_open = True)
Input: Utente preme "1"
Azione: GamePlay.press_1() → verifica flag menu → chiama n_press() → chiude menu
Output: Conferma nuova partita + vocalizz nuovo gioco
Risultato: is_solitaire_menu_open = False, nuova partita avviata
```

#### **Scenario 4: In-Game - Tasto 1 (NO Conflitto)**
```
Stato: Partita in corso, menu chiuso (is_solitaire_menu_open = False)
Input: Utente preme "1"
Azione: GamePlay.press_1() → verifica flag menu (False) → chiama engine pile jump
Output: "Pila base 1. Carta in cima: [nome]. Premi ancora 1 per selezionare."
Risultato: Cursore spostato su pila base 1 (comportamento normale)
```

---

### 🛠️ Implementazione Tecnica

#### **Modifica 2.1: `scr/pygame_menu.py`** (Menu Principale)

**Cambiamenti**:
1. **Add Numeric Handlers**: Metodi `press_1()` ... `press_5()` per shortcut diretti
2. **Update Command Dictionary**: Aggiungere mappatura pygame.K_1 → press_1(), etc.
3. **Visual Enhancement**: Prefisso numerico alle voci menu (opzionale, migliora UX)

**Codice Modifiche**:

```python
# ═══════════════════════════════════════════════════════════
# MODIFICA 1: build_commands_list() - Add numeric shortcuts
# ═══════════════════════════════════════════════════════════
def build_commands_list(self):
    """Build keyboard command mappings for menu navigation.
    
    Maps keyboard events to handler methods, including:
    - Arrow keys for navigation
    - ENTER for selection
    - ESC for quit
    - Numeric keys 1-5 for direct item selection (NEW)
    """
    self.EVENTS_DN = {
        pygame.K_ESCAPE: self.esc_press,
        pygame.K_RETURN: self.execute,
        pygame.K_UP: self.prev_item,
        pygame.K_DOWN: self.next_item,
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
def press_1(self):
    """Shortcut: select first menu item and execute.
    
    Equivalent to navigating to item 1 and pressing ENTER.
    """
    if len(self.items) >= 1:
        self.selected_item = 0
        self.execute()

def press_2(self):
    """Shortcut: select second menu item and execute.
    
    Equivalent to navigating to item 2 and pressing ENTER.
    """
    if len(self.items) >= 2:
        self.selected_item = 1
        self.execute()

def press_3(self):
    """Shortcut: select third menu item and execute."""
    if len(self.items) >= 3:
        self.selected_item = 2
        self.execute()

def press_4(self):
    """Shortcut: select fourth menu item and execute."""
    if len(self.items) >= 4:
        self.selected_item = 3
        self.execute()

def press_5(self):
    """Shortcut: select fifth menu item and execute."""
    if len(self.items) >= 5:
        self.selected_item = 4
        self.execute()

# ═══════════════════════════════════════════════════════════
# MODIFICA 3: draw_menu() - Add numeric prefixes (OPTIONAL)
# ═══════════════════════════════════════════════════════════
def draw_menu(self):
    """Draw menu items on screen with numeric prefixes.
    
    Adds "1.", "2.", etc. prefixes to visually indicate shortcuts.
    Last item ("Esci dal gioco") has no prefix (uses ESC key).
    """
    self.screen.fill((255, 255, 255))
    
    for i, item in enumerate(self.items):
        # Color based on selection
        if i == self.selected_item:
            color = (255, 0, 0)  # Red for selected
        else:
            color = (0, 0, 0)    # Black for normal
        
        # ✅ Add numeric prefix for non-exit items
        # Example: "1. Gioca al solitario classico"
        if i < len(self.items) - 1:  # Don't number "Esci" (uses ESC)
            item_text = f"{i + 1}. {item}"
        else:
            item_text = item
        
        # Render and blit
        text = self.font.render(item_text, True, color)
        text_rect = text.get_rect(center=(self.screen.get_width() / 2, (i + 1) * 50))
        self.screen.blit(text, text_rect)
    
    pygame.display.flip()
```

**Posizionamento**: 
- `build_commands_list()`: Linea ~35
- Nuovi metodi `press_X()`: Dopo metodo `execute()` (linea ~70)
- `draw_menu()`: Linea ~80 (modifica esistente)

---

#### **Modifica 2.2: `scr/game_play.py`** (Menu Solitario In-Game)

**Cambiamenti**:
1. **Add Menu State Flag**: `self.is_solitaire_menu_open` per tracciare stato menu pausa
2. **Menu Management Methods**: `open_solitaire_menu()` e `close_solitaire_menu()`
3. **Modify ESC Handler**: Aprire menu invece di quit diretto
4. **Context-Aware Handlers**: Tasti 1/2/3 funzionano diversamente in menu vs. gioco

**Codice Modifiche**:

```python
# ═══════════════════════════════════════════════════════════
# MODIFICA 1: __init__() - Add menu state tracking
# ═══════════════════════════════════════════════════════════
def __init__(self, screen, screen_reader):
    super().__init__()
    # ... existing initialization code ...
    
    # ✅ NEW: Track solitaire menu state (opened with ESC during game)
    self.is_solitaire_menu_open = False

# ═══════════════════════════════════════════════════════════
# MODIFICA 2: Menu management methods (NEW METHODS)
# ═══════════════════════════════════════════════════════════
def open_solitaire_menu(self):
    """Open in-game solitaire pause menu.
    
    Announces available options with numeric shortcuts.
    Menu stays open until user selects an option or presses ESC again.
    """
    self.is_solitaire_menu_open = True
    menu_text = """MENU SOLITARIO:
1. Nuova partita
2. Opzioni
3. Chiudi partita
Premi ESC per tornare al gioco."""
    self.vocalizza(menu_text)

def close_solitaire_menu(self):
    """Close in-game solitaire pause menu and return to game."""
    self.is_solitaire_menu_open = False
    self.vocalizza("Menu chiuso, torno al gioco.")

# ═══════════════════════════════════════════════════════════
# MODIFICA 3: esc_press() - Open menu instead of immediate quit
# ═══════════════════════════════════════════════════════════
def esc_press(self):
    """Handle ESC key: open/close menu or quit game.
    
    Behavior:
    - If game running + menu closed: Open solitaire menu
    - If game running + menu open: Close menu (return to game)
    - If no game running: Quit application
    """
    if self.engine.is_game_running:
        # ✅ Toggle solitaire menu
        if not self.is_solitaire_menu_open:
            self.open_solitaire_menu()
        else:
            self.close_solitaire_menu()
    else:
        # No game running: quit app
        self.quit_app()

# ═══════════════════════════════════════════════════════════
# MODIFICA 4: Context-aware numeric handlers (MODIFY EXISTING)
# ═══════════════════════════════════════════════════════════
def press_1(self):
    """Handle key '1': Menu shortcut OR pile base 1 (context-aware).
    
    Context Menu (menu open): Execute "1. Nuova partita"
    Context Game (menu closed): Jump to pile base 1
    """
    if self.is_solitaire_menu_open:
        # ✅ MENU CONTEXT: "1. Nuova partita"
        self.n_press()
        self.close_solitaire_menu()
    else:
        # ✅ GAME CONTEXT: Pile base 1 (existing behavior)
        string = self.engine.move_cursor_to_pile_with_select(0)
        if string:
            self.vocalizza(string)

def press_2(self):
    """Handle key '2': Menu shortcut OR pile base 2 (context-aware).
    
    Context Menu: Execute "2. Opzioni"
    Context Game: Jump to pile base 2
    """
    if self.is_solitaire_menu_open:
        # ✅ MENU CONTEXT: "2. Opzioni"
        self.o_press()
        self.close_solitaire_menu()
    else:
        # ✅ GAME CONTEXT: Pile base 2
        string = self.engine.move_cursor_to_pile_with_select(1)
        if string:
            self.vocalizza(string)

def press_3(self):
    """Handle key '3': Menu shortcut OR pile base 3 (context-aware).
    
    Context Menu: Execute "3. Chiudi partita"
    Context Game: Jump to pile base 3
    """
    if self.is_solitaire_menu_open:
        # ✅ MENU CONTEXT: "3. Chiudi partita"
        self.create_yes_or_no_box(
            "Sei sicuro di voler abbandonare la partita?", 
            "Abbandonare la partita?"
        )
        if self.answare:
            string = self.engine.chiudi_partita()
            self.vocalizza(string)
        self.close_solitaire_menu()
    else:
        # ✅ GAME CONTEXT: Pile base 3
        string = self.engine.move_cursor_to_pile_with_select(2)
        if string:
            self.vocalizza(string)
```

**Posizionamento**:
- `__init__()`: Linea ~35 (aggiungere flag dopo inizializzazione engine)
- `open/close_solitaire_menu()`: Dopo metodo `vocalizza()` (linea ~50)
- `esc_press()`: Linea ~340 (modifica esistente)
- `press_1/2/3()`: Linee ~150-180 (modifica esistenti)

---

### ✅ Testing Checklist Feature #2

#### **Test Menu Principale**
- [ ] **T2.1**: Avvio app → Menu mostra "1. Gioca al solitario classico" e "Esci dal gioco"
- [ ] **T2.2**: Premere `1` → Avvia gameplay direttamente (equivalente a ENTER su prima voce)
- [ ] **T2.3**: Premere `ESC` → Conferma uscita (comportamento invariato)
- [ ] **T2.4**: Frecce UP/DOWN → Funzionano ancora correttamente (no regressione)

#### **Test Menu Solitario In-Game**
- [ ] **T2.5**: Durante partita, premere `ESC` → Apre menu con voci "1. Nuova partita, 2. Opzioni, 3. Chiudi partita"
- [ ] **T2.6**: Menu aperto, premere `1` → Avvia nuova partita + chiude menu
- [ ] **T2.7**: Menu aperto, premere `2` → Apre opzioni + chiude menu
- [ ] **T2.8**: Menu aperto, premere `3` → Conferma chiusura partita + chiude menu
- [ ] **T2.9**: Menu aperto, premere `ESC` di nuovo → Chiude menu e torna al gioco (NO quit)

#### **Test Gestione Conflitti**
- [ ] **T2.10**: Menu chiuso, premere `1` → Sposta cursore su pila base 1 (NO menu action)
- [ ] **T2.11**: Menu chiuso, premere `2` → Sposta cursore su pila base 2 (NO menu action)
- [ ] **T2.12**: Menu chiuso, premere `3` → Sposta cursore su pila base 3 (NO menu action)
- [ ] **T2.13**: Menu aperto, premere `4-7` → Nessuna azione (solo 1-3 validi in menu)

#### **Test Edge Cases**
- [ ] **T2.14**: Aprire/chiudere menu più volte consecutivamente → Nessun bug stato
- [ ] **T2.15**: Menu aperto, annullare dialog conferma chiusura partita → Menu rimane aperto
- [ ] **T2.16**: Menu aperto, dialog box attivo → Tastiera menu disabilitata (no doppia gestione)

---

## 📊 RIEPILOGO MODIFICHE

### File Modificati

| File | Feature | Linee Modificate | Metodi Nuovi | Metodi Modificati | Stima Righe |
|------|---------|------------------|--------------|-------------------|-------------|
| **`cursor_manager.py`** | #1 | ~380-430 | - | `jump_to_pile()` | ~50 |
| **`game_engine.py`** | #1 | ~497-520 | - | `jump_to_pile()` | ~20 |
| **`pygame_menu.py`** | #2 | ~35, ~70-100, ~80-95 | `press_1()` .. `press_5()` | `build_commands_list()`, `draw_menu()` | ~40 |
| **`game_play.py`** | #2 | ~35, ~50-70, ~340, ~150-180 | `open/close_solitaire_menu()` | `__init__()`, `esc_press()`, `press_1/2/3()` | ~40 |
| **TOTALE** | | | **7 metodi** | **7 metodi** | **~150 righe** |

---

## 🚀 PIANO DI IMPLEMENTAZIONE SEQUENZIALE

### **FASE 1: Setup & Preparation** ⏱️ 15 min
- [x] Creazione file documentazione
- [x] Creazione TODO.md con checklist
- [ ] Review piano con stakeholder
- [ ] Setup branch di sviluppo (se necessario)

### **FASE 2: Feature #1 - Double-Tap Selection** ⏱️ 1-2 ore
#### **Step 2.1: Modifica CursorManager**
- [ ] Aprire `src/domain/services/cursor_manager.py`
- [ ] Aggiornare import: `from typing import Tuple, ...`
- [ ] Modificare signature `jump_to_pile()` → ritorno `Tuple[str, bool]`
- [ ] Implementare logica double-tap detection (pile_idx == last_quick_pile)
- [ ] Implementare logica auto-selection flag (stock/waste vs. tableau/foundation)
- [ ] Testare isolatamente (unit test se disponibili)

#### **Step 2.2: Modifica GameEngine**
- [ ] Aprire `src/application/game_engine.py`
- [ ] Modificare `jump_to_pile()` per gestire Tuple return
- [ ] Implementare logica auto-selection con annullamento selezione precedente
- [ ] Testare integrazione CursorManager → GameEngine

#### **Step 2.3: Testing Feature #1**
- [ ] Eseguire tutti i test checklist T1.1 - T1.13
- [ ] Verificare feedback vocale screen reader
- [ ] Testare edge cases (pile vuote, selezioni multiple, etc.)
- [ ] Bug fixing se necessario

### **FASE 3: Feature #2 - Menu Shortcuts** ⏱️ 1 ora
#### **Step 3.1: Modifica PyMenu (Menu Principale)**
- [ ] Aprire `scr/pygame_menu.py`
- [ ] Aggiungere handler `press_1()` ... `press_5()`
- [ ] Aggiornare `build_commands_list()` con mappatura numerica
- [ ] [OPZIONALE] Modificare `draw_menu()` per prefissi numerici
- [ ] Testare menu principale con shortcuts

#### **Step 3.2: Modifica GamePlay (Menu Solitario)**
- [ ] Aprire `scr/game_play.py`
- [ ] Aggiungere flag `is_solitaire_menu_open` in `__init__()`
- [ ] Implementare `open_solitaire_menu()` e `close_solitaire_menu()`
- [ ] Modificare `esc_press()` per gestione menu toggle
- [ ] Modificare `press_1/2/3()` per context-awareness (menu vs. game)
- [ ] Testare menu solitario in-game

#### **Step 3.3: Testing Feature #2**
- [ ] Eseguire tutti i test checklist T2.1 - T2.16
- [ ] Verificare assenza conflitti tastiera (menu vs. pile base)
- [ ] Testare apertura/chiusura menu multipla
- [ ] Bug fixing se necessario

### **FASE 4: Integration Testing** ⏱️ 30 min
- [ ] Testare entrambe le feature insieme in scenario reale
- [ ] Verificare double-tap selection durante/dopo menu solitario
- [ ] Verificare menu shortcuts non interferiscono con double-tap
- [ ] Test regressione: tutti i comandi esistenti funzionano ancora
- [ ] Performance check: nessun lag o rallentamento percepibile

### **FASE 5: Documentation & Release** ⏱️ 30 min
- [ ] Aggiornare `README.md` (se necessario aggiungere note shortcuts)
- [ ] Aggiornare `CHANGELOG.md` con sezione versione 1.4.3:
  ```markdown
  ## [1.4.3] - 2026-02-10
  
  ### Added
  - Double-tap auto-selection: seconda pressione numero pila seleziona automaticamente ultima carta (pile base 1-7 e pile seme SHIFT+1-4)
  - Numeric menu shortcuts: scorciatoie 1-5 per navigazione rapida menu principale e menu solitario in-game
  
  ### Changed
  - Menu solitario ora si apre con ESC invece di dialog conferma immediato (toggle menu)
  - Hint migliorati per pile base/semi: "Premi ancora [numero] per selezionare"
  
  ### Fixed
  - Gestione conflitti tastiera tra menu shortcuts e pile base (context-aware handlers)
  ```
- [ ] Aggiornare help in-game (`h_press()`) con nuovi comandi
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
✅ **Criterio 2**: Tasti `1/2/3` attivano rispettive voci menu solitario (solo quando menu aperto)  
✅ **Criterio 3**: Nessun conflitto con pile base 1-7 (context-aware)  
✅ **Criterio 4**: Menu solitario toggle con ESC (apri/chiudi)  

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
**Sintomo**: Premere `1` durante gioco apre menu invece di selezionare pila  
**Causa**: Flag `is_solitaire_menu_open` non verificato correttamente

**Fix**:
```python
def press_1(self):
    if self.is_solitaire_menu_open:  # ← Verificare ordine condizioni
        # menu action
    else:
        # game action (pile)
```

---

### Problema 4: Menu rimane aperto dopo selezione
**Sintomo**: Dopo premere `1/2/3` in menu, menu non si chiude  
**Causa**: `close_solitaire_menu()` non chiamato dopo azione

**Fix**: Assicurarsi che **ogni** handler menu chiami `self.close_solitaire_menu()` dopo esecuzione.

---

## 📚 REFERENCES

### Codice Legacy
- `scr/game_engine.py` (versione legacy con double-tap originale)
- `scr/pygame_menu.py` (sistema menu base)
- `scr/game_play.py` (gestione eventi tastiera)

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

**Q: Perché menu solitario usa context-aware handlers invece di disabilitare tasti 1-7 durante menu?**  
**A**: Context-awareness permette riutilizzo handler esistenti senza duplicazione codice. Inoltre, mantiene coerenza: stessi tasti, diverso comportamento in base a contesto.

---

### Future Enhancements

**Possibili Miglioramenti Futuri**:
- [ ] Aggiungere shortcut ALT+numero per spostamento diretto su pile seme (alternativa a SHIFT+numero)
- [ ] Implementare "memory" ultima pila visitata per tornare rapidamente con shortcut dedicato
- [ ] Aggiungere animazioni/feedback audio per double-tap riuscito
- [ ] Estendere sistema menu shortcuts ad altri dialog box (opzioni, conferme, etc.)

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
Ultimo aggiornamento: 10 Febbraio 2026
