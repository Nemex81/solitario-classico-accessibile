# 🤖 Piano di Implementazione Copilot - Completamento Migrazione wxPython

**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Stato**: Parziale (OptionsDialog completato, gameplay rotto)  
**Obiettivo**: Completare migrazione da pygame a wxPython mantenendo 100% compatibilità funzionale

---

## 📋 Indice

1. [Contesto e Gap Analisi](#contesto-e-gap-analisi)
2. [Architettura Validata](#architettura-validata)
3. [Task 1: Espandere Keyboard Mapping](#task-1-espandere-keyboard-mapping)
4. [Task 2: Semplificare ESC Handler](#task-2-semplificare-esc-handler)
5. [Testing e Validazione](#testing-e-validazione)
6. [Commit Strategy](#commit-strategy)

---

## 🎯 Contesto e Gap Analisi

### Situazione Attuale

**Branch Legacy** (`refactoring-engine` - pygame):
- ✅ 60+ comandi keyboard funzionanti
- ✅ SHIFT combinations (SHIFT+1-4, SHIFT+S, SHIFT+M)
- ✅ CTRL combinations (CTRL+ENTER, CTRL+ALT+W)
- ✅ Navigazione completa (HOME/END/TAB/DELETE)
- ✅ Query informazioni (F/G/R/X/C/S/M/T/I/H)
- ✅ Gestione partita (N/O/ESC)
- ⚠️ ESC con double-tap (< 2s) per abbandono rapido

**Branch Copilot** (`copilot/remove-pygame-migrate-wxpython` - wxPython):
- ✅ OptionsDialog nativo completamente implementato e funzionante
- ✅ Domain layer (CursorManager + GameEngine) perfetto e immutato
- ❌ GameplayController: **solo 8 tasti mappati su 60+**
- ❌ ESC handler: mantiene double-tap (da rimuovere per decisione utente)

### Gap Identificati

| Componente | File | Gap Funzionale |
|-----------|------|----------------|
| **GameplayController** | `src/application/gameplay_controller.py` | Metodo `handle_wx_key_event()` incompleto: mancano 52+ tasti |
| **GameplayPanel** | `src/infrastructure/ui/gameplay_panel.py` | ESC handler con doppio-tap da semplificare |

---

## 🏗️ Architettura Validata

### Flusso Eventi Keyboard (wxPython)

```
┌──────────────────────────────────────────────────────────────┐
│ GameplayPanel (wx.Panel)                                     │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ on_key_down(wx.KeyEvent)                                 │ │
│ │   │                                                       │ │
│ │   ├─> ESC? → _handle_esc()                              │ │
│ │   │            └─> controller.show_abandon_game_dialog()│ │
│ │   │                                                       │ │
│ │   └─> Altri tasti → controller.handle_wx_key_event()    │ │
│ └──────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│ GameplayController                                           │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ handle_wx_key_event(wx.KeyEvent) → bool                 │ │
│ │   │                                                       │ │
│ │   ├─> Parse modifiers (SHIFT/CTRL/ALT)                  │ │
│ │   ├─> Map wx key codes to _helper_methods()             │ │
│ │   └─> Return True if handled                            │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ Helper methods (identici a versione pygame):                │
│ • _nav_pile_base(0-6)      • _cursor_up/down/left/right    │
│ • _nav_pile_semi(7-10)     • _cursor_home/end/tab          │
│ • _nav_pile_scarti()       • _select_card()                │
│ • _nav_pile_mazzo()        • _move_cards()                 │
│ • _get_focus/table_info    • _draw_cards()                 │
│ • _get_game_report         • _cancel_selection()           │
│ • etc...                                                    │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│ GameEngine (domain layer - IMMUTATO)                        │
│ • jump_to_pile(pile_idx) → (msg, hint)                     │
│ • move_cursor(direction) → (msg, hint)                     │
│ • select_card_at_cursor() → (success, msg)                 │
│ • execute_move() → (success, msg)                          │
│ • draw_from_stock() → (success, msg)                       │
│ • etc...                                                    │
└──────────────────────────────────────────────────────────────┘
```

**Principio**: `handle_wx_key_event()` è un **adattatore wx → metodi helper**, che poi chiamano `GameEngine` (stessa logica di pygame).

---

## 🔧 Task 1: Espandere Keyboard Mapping

### File Target
`src/application/gameplay_controller.py`

### Metodo da Modificare
`handle_wx_key_event(self, event) -> bool` (linee ~698-739)

### Stato Attuale (8 tasti mappati)

```python
def handle_wx_key_event(self, event) -> bool:
    """Handle wxPython keyboard events - INCOMPLETE (only 8 keys)."""
    import wx
    
    key_code = event.GetKeyCode()
    
    # Arrow keys
    if key_code == wx.WXK_UP: self._cursor_up(); return True
    elif key_code == wx.WXK_DOWN: self._cursor_down(); return True
    elif key_code == wx.WXK_LEFT: self._cursor_left(); return True
    elif key_code == wx.WXK_RIGHT: self._cursor_right(); return True
    
    # ENTER/RETURN
    elif key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
        self._select_card(); return True
    
    # SPACE
    elif key_code == wx.WXK_SPACE: self._move_cards(); return True
    
    # D or P
    elif key_code in (ord('D'), ord('P'), ord('d'), ord('p')):
        self._draw_cards(); return True
    
    return False  # Key not handled
```

### Implementazione Completa (60+ tasti)

**IMPORTANTE**: Seguire l'ordine di priority come nella versione pygame.

#### Step 1: Parse Modifiers PRIMA di tutto

```python
def handle_wx_key_event(self, event) -> bool:
    """Handle wxPython keyboard events by routing to gameplay methods.
    
    Maps wx.KeyEvent to 60+ gameplay commands with full modifier support.
    Returns True if key was handled, False otherwise.
    
    Priority Order:
    1. SHIFT combinations (foundations, waste, stock)
    2. CTRL combinations (CTRL+ENTER, CTRL+ALT+W debug)
    3. Number keys 1-7 (tableau piles)
    4. Arrow keys + HOME/END/TAB (navigation)
    5. Action keys (ENTER/SPACE/DELETE)
    6. Draw keys (D/P)
    7. Query keys (F/G/R/X/C/S/M/T/I/H)
    8. Game management (N/O)
    
    Args:
        event: wx.KeyEvent from wxPython event loop
    
    Returns:
        bool: True if key was handled, False if not recognized
    
    Note:
        ESC is handled separately in GameplayPanel._handle_esc()
        to support dialog workflow. Do not map ESC here.
    
    Version: v1.7.5 (complete wxPython keyboard mapping)
    """
    import wx
    
    key_code = event.GetKeyCode()
    modifiers = event.GetModifiers()
    
    # Parse modifier flags
    has_shift = bool(modifiers & wx.MOD_SHIFT)
    has_ctrl = bool(modifiers & wx.MOD_CONTROL)
    has_alt = bool(modifiers & wx.MOD_ALT)
```

#### Step 2: Priority 1 - SHIFT Combinations

```python
    # ═══════════════════════════════════════════════════════════
    # PRIORITY 1: SHIFT COMBINATIONS (must be checked FIRST)
    # ═══════════════════════════════════════════════════════════
    if has_shift:
        # SHIFT+1-4: Foundation piles (semi)
        if key_code == ord('1'):
            self._nav_pile_semi(7)  # Hearts (Cuori)
            return True
        elif key_code == ord('2'):
            self._nav_pile_semi(8)  # Diamonds (Quadri)
            return True
        elif key_code == ord('3'):
            self._nav_pile_semi(9)  # Clubs (Fiori)
            return True
        elif key_code == ord('4'):
            self._nav_pile_semi(10)  # Spades (Picche)
            return True
        
        # SHIFT+S: Waste pile (scarti)
        elif key_code in (ord('S'), ord('s')):
            self._nav_pile_scarti()
            return True
        
        # SHIFT+M: Stock pile (mazzo)
        elif key_code in (ord('M'), ord('m')):
            self._nav_pile_mazzo()
            return True
```

#### Step 3: Priority 2 - CTRL Combinations

```python
    # ═══════════════════════════════════════════════════════════
    # PRIORITY 2: CTRL COMBINATIONS
    # ═══════════════════════════════════════════════════════════
    if has_ctrl:
        # CTRL+ENTER: Select from waste pile
        if key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.engine.select_from_waste()
            return True
        
        # CTRL+ALT+W: Debug force victory
        if has_alt and key_code in (ord('W'), ord('w')):
            msg = self.engine._debug_force_victory()
            if msg:
                self._vocalizza(msg)
            return True
```

#### Step 4: Number Keys 1-7 (NO SHIFT)

```python
    # ═══════════════════════════════════════════════════════════
    # NUMBER KEYS 1-7: Tableau piles (pile base)
    # ═══════════════════════════════════════════════════════════
    if ord('1') <= key_code <= ord('7'):
        pile_idx = key_code - ord('1')  # 0-6
        self._nav_pile_base(pile_idx)
        return True
```

#### Step 5: Arrow Keys + Advanced Navigation

```python
    # ═══════════════════════════════════════════════════════════
    # ARROW KEYS: Cursor navigation
    # ═══════════════════════════════════════════════════════════
    if key_code == wx.WXK_UP:
        self._cursor_up()
        return True
    elif key_code == wx.WXK_DOWN:
        self._cursor_down()
        return True
    elif key_code == wx.WXK_LEFT:
        self._cursor_left()
        return True
    elif key_code == wx.WXK_RIGHT:
        self._cursor_right()
        return True
    
    # ═══════════════════════════════════════════════════════════
    # ADVANCED NAVIGATION: HOME/END/TAB/DELETE
    # ═══════════════════════════════════════════════════════════
    elif key_code == wx.WXK_HOME:
        self._cursor_home()
        return True
    elif key_code == wx.WXK_END:
        self._cursor_end()
        return True
    elif key_code == wx.WXK_TAB:
        self._cursor_tab()
        return True
    elif key_code == wx.WXK_DELETE:
        self._cancel_selection()
        return True
```

#### Step 6: Action Keys (ENTER/SPACE)

```python
    # ═══════════════════════════════════════════════════════════
    # ACTION KEYS: Select and Move
    # ═══════════════════════════════════════════════════════════
    elif key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
        self._select_card()
        return True
    
    elif key_code == wx.WXK_SPACE:
        self._move_cards()
        return True
```

#### Step 7: Draw Keys (D/P)

```python
    # ═══════════════════════════════════════════════════════════
    # DRAW KEYS: D or P
    # ═══════════════════════════════════════════════════════════
    elif key_code in (ord('D'), ord('d'), ord('P'), ord('p')):
        self._draw_cards()
        return True
```

#### Step 8: Query Information Keys (10 commands)

```python
    # ═══════════════════════════════════════════════════════════
    # QUERY INFORMATION KEYS (10 commands)
    # ═══════════════════════════════════════════════════════════
    
    # F: Get focus (cursor position)
    elif key_code in (ord('F'), ord('f')):
        self._get_focus()
        return True
    
    # G: Get table info (all piles status)
    elif key_code in (ord('G'), ord('g')):
        self._get_table_info()
        return True
    
    # R: Get game report (stats, time, moves)
    elif key_code in (ord('R'), ord('r')):
        self._get_game_report()
        return True
    
    # X: Get card info (detailed card at cursor)
    elif key_code in (ord('X'), ord('x')):
        self._get_card_info()
        return True
    
    # C: Get selected cards (current selection)
    elif key_code in (ord('C'), ord('c')):
        self._get_selected_cards()
        return True
    
    # S: Get scarto top (waste pile top card)
    # NOTE: SHIFT+S handled above, this is plain S
    elif not has_shift and key_code in (ord('S'), ord('s')):
        self._get_scarto_top()
        return True
    
    # M: Get deck count (stock pile remaining)
    # NOTE: SHIFT+M handled above, this is plain M
    elif not has_shift and key_code in (ord('M'), ord('m')):
        self._get_deck_count()
        return True
    
    # T: Get timer (elapsed or countdown)
    elif key_code in (ord('T'), ord('t')):
        self._get_timer()
        return True
    
    # I: Get settings (current game configuration)
    elif key_code in (ord('I'), ord('i')):
        self._get_settings()
        return True
    
    # H: Show help (command list)
    elif key_code in (ord('H'), ord('h')):
        self._show_help()
        return True
```

#### Step 9: Game Management Keys (N/O)

```python
    # ═══════════════════════════════════════════════════════════
    # GAME MANAGEMENT KEYS
    # ═══════════════════════════════════════════════════════════
    
    # N: New game
    elif key_code in (ord('N'), ord('n')):
        self._new_game()
        return True
    
    # O: Open/close options window
    elif key_code in (ord('O'), ord('o')):
        self._handle_o_key()
        return True
```

#### Step 10: Key Not Handled

```python
    # ═══════════════════════════════════════════════════════════
    # KEY NOT RECOGNIZED
    # ═══════════════════════════════════════════════════════════
    return False
```

### Validazione Mapping

**Checklist Completa** (verificare tutti i 60+ comandi):

- [ ] **Numeri 1-7**: Pile base (tableau)
- [ ] **SHIFT+1-4**: Pile fondazioni (foundation)
- [ ] **SHIFT+S**: Pile scarti (waste)
- [ ] **SHIFT+M**: Pile mazzo (stock)
- [ ] **Frecce**: UP/DOWN/LEFT/RIGHT
- [ ] **HOME**: Prima carta pila
- [ ] **END**: Ultima carta pila
- [ ] **TAB**: Pila tipo diverso
- [ ] **DELETE**: Annulla selezione
- [ ] **ENTER**: Seleziona carta
- [ ] **CTRL+ENTER**: Seleziona da scarti
- [ ] **SPACE**: Sposta carte
- [ ] **D/P**: Pesca dal mazzo
- [ ] **F**: Posizione cursore
- [ ] **G**: Stato tavolo
- [ ] **R**: Report partita
- [ ] **X**: Info carta
- [ ] **C**: Carte selezionate
- [ ] **S**: Top scarti
- [ ] **M**: Contatore mazzo
- [ ] **T**: Timer
- [ ] **I**: Impostazioni
- [ ] **H**: Aiuto comandi
- [ ] **N**: Nuova partita
- [ ] **O**: Opzioni
- [ ] **CTRL+ALT+W**: Debug vittoria

---

## 🛠️ Task 2: Semplificare ESC Handler

### File Target
`src/infrastructure/ui/gameplay_panel.py`

### Problema Attuale

Gestione ESC con double-tap (< 2s) per abbandono rapido:

```python
# Linea 53
DOUBLE_ESC_THRESHOLD = 2.0

# Linea 59 (in __init__)
self.last_esc_time = 0.0

# Linee 118-166 (metodo _handle_esc)
def _handle_esc(self, event: wx.KeyEvent) -> None:
    """Handle ESC with context-aware double-tap detection."""
    current_time = time.time()
    
    # Doppio-ESC (< 2s): Abbandono immediato
    if self.last_esc_time > 0 and current_time - self.last_esc_time <= 2.0:
        self.announce("Uscita rapida!", interrupt=True)
        if self.controller:
            self.controller.confirm_abandon_game(skip_dialog=True)  # ❌ NON VOLUTO
        self.last_esc_time = 0.0
    else:
        # Primo ESC: Dialog conferma
        self.last_esc_time = current_time
        if self.controller:
            self.controller.show_abandon_game_dialog()  # ✅ GIUSTO
```

### Comportamento Richiesto

**Decisione Utente**: ESC deve **sempre** mostrare dialog conferma, senza scorciatoie.

### Modifiche da Applicare

#### Modifica 1: Rimuovere Costante (linea ~53)

**PRIMA**:
```python
# Double-tap ESC threshold for quick exit (seconds)
DOUBLE_ESC_THRESHOLD = 2.0
```

**DOPO**:
```python
# (rimossa - feature double-tap ESC non più necessaria)
```

#### Modifica 2: Rimuovere Attributo Tracking (linea ~59)

**PRIMA** (nel metodo `__init__`):
```python
# ESC double-tap tracking for quick exit
self.last_esc_time = 0.0
```

**DOPO**:
```python
# (rimosso - feature double-tap ESC non più necessaria)
```

#### Modifica 3: Semplificare Metodo _handle_esc (linee ~118-166)

**PRIMA** (logica complessa con double-tap):
```python
def _handle_esc(self, event: wx.KeyEvent) -> None:
    """Handle ESC with context-aware double-tap detection."""
    current_time = time.time()
    
    # Doppio-ESC (< 2s): Abbandono immediato
    if self.last_esc_time > 0 and current_time - self.last_esc_time <= 2.0:
        self.announce("Uscita rapida!", interrupt=True)
        if self.controller:
            self.controller.confirm_abandon_game(skip_dialog=True)
        self.last_esc_time = 0.0
    else:
        # Primo ESC: Dialog conferma
        self.last_esc_time = current_time
        if self.controller:
            self.controller.show_abandon_game_dialog()
```

**DOPO** (logica semplificata):
```python
def _handle_esc(self, event: wx.KeyEvent) -> None:
    """Handle ESC: always show abandon confirmation dialog.
    
    Removed: Double-tap ESC feature for quick exit (user request).
    Now: ESC always opens confirmation dialog, no shortcuts.
    
    This ensures users always have a chance to cancel accidental
    ESC presses during gameplay.
    
    Args:
        event: wx.KeyEvent (not used, kept for signature consistency)
    
    Version: v1.7.5 (simplified ESC handler)
    """
    if self.controller:
        self.controller.show_abandon_game_dialog()
```

### Validazione Comportamento ESC

**Test Case**:
1. Durante partita, premi **ESC**
2. **Risultato Atteso**: Dialog "Vuoi abbandonare la partita?" appare
3. **Non Deve**: Uscita immediata con secondo ESC

**Checklist**:
- [ ] Costante `DOUBLE_ESC_THRESHOLD` rimossa
- [ ] Attributo `self.last_esc_time` rimosso da `__init__`
- [ ] Metodo `_handle_esc()` semplificato a singola chiamata
- [ ] Import `time` non più necessario (può essere rimosso se non usato altrove)

---

## 🧪 Testing e Validazione

### Test Plan Completo

#### Test 1: Keyboard Mapping (60+ comandi)

**File di Test**: Manuale (in-game testing)

**Procedura**:
1. Avviare gioco wxPython: `python test.py`
2. Iniziare nuova partita
3. Testare OGNI tasto dalla checklist sopra
4. Verificare feedback TTS corretto
5. Verificare azione eseguita nel GameEngine

**Criteri di Successo**:
- ✅ Tutti i 60+ tasti producono azione corretta
- ✅ Feedback TTS identico a versione pygame
- ✅ Nessun errore in console
- ✅ Double-tap numeri 1-7 e SHIFT+1-4 attiva selezione automatica

#### Test 2: ESC Behavior

**Procedura**:
1. Durante partita, premi **ESC**
2. Verifica apparizione dialog "Vuoi abbandonare?"
3. Premi **NO** → partita continua
4. Premi **ESC** nuovamente (entro 2 secondi)
5. Verifica che dialog appaia di nuovo (NO abbandono automatico)

**Criteri di Successo**:
- ✅ ESC sempre mostra dialog
- ✅ Nessun abbandono immediato con doppio ESC
- ✅ Selezione NO riporta al gioco
- ✅ Selezione SI abbandona partita

#### Test 3: SHIFT/CTRL Modifiers

**Procedura**:
1. **SHIFT+1**: Deve navigare a pile fondazioni (non pile base)
2. **SHIFT+S**: Deve navigare a scarti (non query top card)
3. **SHIFT+M**: Deve navigare a mazzo (non query counter)
4. **CTRL+ENTER**: Deve selezionare da scarti
5. **CTRL+ALT+W**: Deve forzare vittoria (debug)

**Criteri di Successo**:
- ✅ SHIFT combinations funzionano correttamente
- ✅ CTRL combinations funzionano correttamente
- ✅ Plain keys (senza modifiers) eseguono azione diversa

#### Test 4: Options Window Integration

**Procedura**:
1. Premi **O** → finestra opzioni si apre
2. Verifica che comandi gameplay (frecce/numeri) siano bloccati
3. Premi **ESC** in opzioni → chiusura con conferma se modificato
4. Chiudi opzioni → gameplay riprende normalmente

**Criteri di Successo**:
- ✅ Opzioni bloccano gameplay
- ✅ Chiusura opzioni ripristina controlli
- ✅ Nessuna interferenza tra i due contesti

#### Test 5: Compatibility Cross-Check

**Procedura**:
1. Checkout branch `refactoring-engine` (pygame)
2. Gioca una partita completa, testando tutti i comandi
3. Checkout branch `copilot/remove-pygame-migrate-wxpython` (wxPython)
4. Gioca stessa partita, testando stessi comandi
5. Confronta comportamenti

**Criteri di Successo**:
- ✅ Comportamento identico in entrambi i branch
- ✅ Feedback TTS identico
- ✅ Logica di gioco identica
- ✅ Unica differenza: UI nativa wxPython vs pygame

---

## 📦 Commit Strategy

### Commit Incrementali e Logici

Per facilitare review e rollback, suddividere le modifiche in **3 commit atomici**:

---

#### **Commit 1: Expand keyboard mapping - Navigation & Actions**

**Scope**: Aggiungere tasti di navigazione e azioni (24 tasti)

**File**: `src/application/gameplay_controller.py`

**Modifiche**:
1. Aggiungere parsing modifiers (has_shift/has_ctrl/has_alt)
2. Implementare numeri 1-7 (tableau piles)
3. Implementare HOME/END/TAB/DELETE (navigation)

**Commit Message**:
```
feat(wx): expand keyboard mapping with navigation keys (24 commands)

Add support for:
- Number keys 1-7 (tableau pile navigation)
- HOME/END (first/last card in pile)
- TAB (jump to different pile type)
- DELETE (cancel selection)

This brings wxPython keyboard handling closer to pygame parity.

Related to: wxPython migration completion
Part 1 of 3
```

**Testing dopo Commit 1**:
- [ ] Numeri 1-7 funzionano
- [ ] HOME/END/TAB/DELETE funzionano
- [ ] Nessuna regressione sui tasti già funzionanti

---

#### **Commit 2: Expand keyboard mapping - SHIFT/CTRL combinations & Queries**

**Scope**: Aggiungere SHIFT/CTRL combinations e query keys (28 tasti)

**File**: `src/application/gameplay_controller.py`

**Modifiche**:
1. Implementare SHIFT+1-4 (foundation piles)
2. Implementare SHIFT+S/M (waste/stock direct jump)
3. Implementare CTRL+ENTER (select from waste)
4. Implementare CTRL+ALT+W (debug victory)
5. Implementare query keys F/G/R/X/C/S/M/T/I/H (10 comandi)

**Commit Message**:
```
feat(wx): add SHIFT/CTRL combinations and query commands (28 keys)

Add support for:
- SHIFT+1-4: Foundation piles (semi)
- SHIFT+S: Waste pile direct jump
- SHIFT+M: Stock pile direct jump
- CTRL+ENTER: Select from waste
- CTRL+ALT+W: Debug force victory
- Query keys: F/G/R/X/C/S/M/T/I/H (info commands)

This achieves full keyboard parity with pygame version (60+ commands).

Related to: wxPython migration completion
Part 2 of 3
```

**Testing dopo Commit 2**:
- [ ] SHIFT+1-4 navigano a fondazioni
- [ ] SHIFT+S/M navigano correttamente
- [ ] CTRL+ENTER seleziona da scarti
- [ ] CTRL+ALT+W forza vittoria
- [ ] Tutti i 10 query keys funzionano

---

#### **Commit 3: Simplify ESC handler - Remove double-tap feature**

**Scope**: Rimuovere feature double-tap ESC (user request)

**File**: `src/infrastructure/ui/gameplay_panel.py`

**Modifiche**:
1. Rimuovere costante `DOUBLE_ESC_THRESHOLD`
2. Rimuovere attributo `self.last_esc_time` da `__init__`
3. Semplificare metodo `_handle_esc()` a singola chiamata dialog
4. (Opzionale) Rimuovere import `time` se non usato altrove

**Commit Message**:
```
refactor(wx): simplify ESC handler - always show confirmation dialog

Remove double-tap ESC feature for quick exit (user request).

Changes:
- Remove DOUBLE_ESC_THRESHOLD constant
- Remove self.last_esc_time attribute
- Simplify _handle_esc() to always show dialog

Rationale: User wants explicit confirmation for all game exits,
preventing accidental abandonment with double ESC press.

Related to: wxPython migration completion
Part 3 of 3 - FINAL
```

**Testing dopo Commit 3**:
- [ ] ESC sempre mostra dialog
- [ ] Doppio ESC NON produce abbandono immediato
- [ ] Dialog funziona correttamente (SI/NO)

---

### Merge Strategy

Dopo i 3 commit:
1. ✅ Tutti i test passano
2. ✅ Codice reviewed
3. ✅ Documentazione aggiornata

**Merge in `main`**:
```bash
git checkout main
git merge copilot/remove-pygame-migrate-wxpython --no-ff
git push origin main
```

**Tag Release**:
```bash
git tag -a v1.7.5 -m "Complete wxPython migration with full keyboard support"
git push origin v1.7.5
```

---

## 📚 Riferimenti e Note Tecniche

### File di Riferimento (Branch Legacy)

Per confronto e validazione logica:

1. **`src/application/gameplay_controller.py`** (branch `refactoring-engine`)
   - Linee 698-739: `handle_keyboard_events()` con pygame
   - Mapping completo con SHIFT/CTRL combinations
   - Logica da replicare in wxPython

2. **`src/domain/services/cursor_manager.py`**
   - Metodo `jump_to_pile()`: Restituisce `(message, should_auto_select, hint)`
   - Double-tap detection già implementato nel domain layer
   - **NON MODIFICARE**: Funziona correttamente

3. **`src/application/game_engine.py`**
   - Metodo `jump_to_pile()`: Gestisce auto-selezione double-tap
   - Tutti i metodi helper già implementati
   - **NON MODIFICARE**: Funziona correttamente

### wxPython Key Codes Reference

**Costanti wx utili**:
```python
import wx

# Navigation
wx.WXK_UP, wx.WXK_DOWN, wx.WXK_LEFT, wx.WXK_RIGHT
wx.WXK_HOME, wx.WXK_END, wx.WXK_TAB
wx.WXK_DELETE

# Actions
wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER
wx.WXK_SPACE
wx.WXK_ESCAPE

# Modifiers
event.GetModifiers() -> int
wx.MOD_SHIFT, wx.MOD_CONTROL, wx.MOD_ALT

# Letter keys
ord('A'), ord('a')  # Case-insensitive: gestire entrambi
```

### Differenze pygame vs wxPython

| Aspetto | pygame | wxPython |
|---------|--------|----------|
| **Key constants** | `pygame.K_UP` | `wx.WXK_UP` |
| **Modifiers** | `pygame.key.get_mods()` | `event.GetModifiers()` |
| **Key code** | `event.key` | `event.GetKeyCode()` |
| **Letter keys** | `pygame.K_a` | `ord('A')` o `ord('a')` |
| **Case sensitivity** | Separato (`K_a` vs `K_A`) | `ord('A')` e `ord('a')` diversi |

**IMPORTANTE**: In wxPython, gestire SEMPRE entrambi i case per le lettere:
```python
if key_code in (ord('N'), ord('n')):  # Gestisce sia N che n
```

### Debugging Tips

**Log key events** (durante sviluppo):
```python
def handle_wx_key_event(self, event) -> bool:
    import wx
    key_code = event.GetKeyCode()
    modifiers = event.GetModifiers()
    
    # DEBUG: Log all key presses
    print(f"Key: {key_code}, Mod: {modifiers}, Char: {chr(key_code) if 32 <= key_code < 127 else 'N/A'}")
    
    # ... resto della logica
```

**Verificare modifiers**:
```python
has_shift = bool(modifiers & wx.MOD_SHIFT)
print(f"SHIFT pressed: {has_shift}")
```

---

## ✅ Checklist Finale

Prima di considerare la migrazione completa:

### Funzionalità
- [ ] Tutti i 60+ comandi keyboard funzionano
- [ ] SHIFT combinations corrette
- [ ] CTRL combinations corrette
- [ ] ESC sempre mostra dialog (no double-tap)
- [ ] Options window integrata e funzionante
- [ ] Double-tap numeri (auto-selezione) funziona

### Testing
- [ ] Test completo keyboard mapping
- [ ] Test ESC behavior
- [ ] Test SHIFT/CTRL modifiers
- [ ] Test options integration
- [ ] Cross-check compatibility con branch pygame

### Documentazione
- [ ] Commit messages descrittivi
- [ ] Commenti nel codice aggiornati
- [ ] Questo documento validato e aggiornato
- [ ] CHANGELOG.md aggiornato

### Codice
- [ ] Nessuna regressione nei test esistenti
- [ ] Codice formattato correttamente
- [ ] Import puliti (rimuovere import inutilizzati)
- [ ] Type hints corretti

---

## 🎉 Conclusione

Una volta completati i 3 commit e passati tutti i test, la migrazione wxPython sarà **100% completa** con:

✅ **UI nativa wxPython** (OptionsDialog con widget accessibili)  
✅ **Keyboard mapping completo** (60+ comandi identici a pygame)  
✅ **Comportamento ESC semplificato** (sempre dialog conferma)  
✅ **Domain layer immutato** (CursorManager + GameEngine perfetti)  
✅ **Compatibilità 100%** con versione pygame

**Ready for production!** 🚀

---

**Document Version**: v1.0  
**Last Updated**: 2026-02-13  
**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Author**: System Analysis (verified against both branches)
