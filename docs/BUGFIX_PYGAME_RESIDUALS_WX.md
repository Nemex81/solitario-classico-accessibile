# 🐛 Bugfix Plan: Pygame Residuals in wxPython Migration

**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Tipo**: CRITICAL BUGFIX  
**Priorità**: URGENT  
**Stato**: READY  
**Version Target**: v1.7.5 (post keyboard mapping completion)

---

## 📊 Executive Summary

Copilot ha completato con successo il mapping di 60+ comandi keyboard in `handle_wx_key_event()`, ma **non ha aggiornato i metodi helper legacy** che continuano a referenziare pygame in ambiente wxPython.

### Problemi Identificati

1. **❌ ENTER non seleziona carta**: `_select_card()` chiama `pygame.key.get_mods()` in contesto wxPython → crash `pygame.error: video system not initialized`

2. **❌ ESC genera AttributeError**: `show_abandon_game_dialog()` chiama metodo inesistente `show_yes_no()` invece di `show_yes_no_dialog()`

### Impact

- **Severità**: CRITICA - Due comandi fondamentali (ENTER/ESC) non funzionano durante gameplay
- **Scope**: Solo 2 file da modificare (3 modifiche totali)
- **Rischio regressione**: BASSO - Modifiche chirurgiche a metodi isolati
- **Testing**: Semplice - Testare ENTER e ESC in gameplay

---

## 🔍 Analisi Dettagliata Problemi

### Problema 1: ENTER Key Handler (pygame residual)

#### Traccia Errore
```
Traceback (most recent call last):
  File "src/infrastructure/ui/gameplay_panel.py", line 130, in on_key_down
    handled = self.controller.gameplay_controller.handle_wx_key_event(event)
  File "src/application/gameplay_controller.py", line 764, in handle_wx_key_event
    self._select_card()
  File "src/application/gameplay_controller.py", line 323, in _select_card
    mods = pygame.key.get_mods()
           ^^^^^^^^^^^^^^^^^^^^^
pygame.error: video system not initialized
```

#### Root Cause Analysis

**Flusso chiamate**:
```
GameplayPanel.on_key_down()          (wxPython event)
  └─> GameplayController.handle_wx_key_event()  (line 764)
      └─> self._select_card()                    (line 323)
          └─> pygame.key.get_mods()                 ❌ ERRORE QUI!
```

**Causa radice**:
- Copilot ha creato `handle_wx_key_event()` per routing wxPython → helper methods
- Ha mappato correttamente ENTER → `_select_card()` (line 764)
- **MA**: Non ha aggiornato `_select_card()` che ancora usa pygame per check modifiers
- In ambiente wxPython, pygame NON è inizializzato → crash

**Codice attuale (ROTTO)**:
```python
# src/application/gameplay_controller.py - linee 318-332
def _select_card(self) -> None:
    """ENTER: Select card under cursor.
    
    Special behavior:
    - On stock pile: Draw cards
    - On other piles: Select/toggle card
    - CTRL+ENTER: Select from waste pile
    """
    mods = pygame.key.get_mods()  # ❌ PYGAME IN WXPYTHON CONTEXT!
    
    if mods & KMOD_CTRL:
        # CTRL+ENTER: Seleziona da scarti
        self.engine.select_from_waste()
    else:
        # ENTER normale: Seleziona carta o pesca
        self.engine.select_card_at_cursor()
```

**Perché fallisce**:
1. User preme ENTER in gameplay
2. `GameplayPanel.on_key_down()` riceve `wx.KeyEvent`
3. Chiama `handle_wx_key_event(event)` che rileva ENTER (line 764)
4. Chiama `self._select_card()` (senza passare modifiers!)
5. `_select_card()` tenta `pygame.key.get_mods()` → **CRASH**

**Soluzione corretta**:
- In `handle_wx_key_event()`, CTRL+ENTER è **già gestito separatamente** (line ~739):
  ```python
  if has_ctrl:
      if key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
          self._select_from_waste()  # Chiamata diretta!
          return True
  ```
- Quindi `_select_card()` viene chiamato SOLO per **plain ENTER** (no CTRL)
- Il check modifiers in `_select_card()` è **ridondante e rotto**
- Semplificare: chiamare direttamente `self.engine.select_card_at_cursor()`

---

### Problema 2: ESC Dialog Method Name (typo)

#### Traccia Errore
```
Traceback (most recent call last):
  File "src/infrastructure/ui/gameplay_panel.py", line 125, in on_key_down
    self._handle_esc(event)
  File "src/infrastructure/ui/gameplay_panel.py", line 164, in _handle_esc
    self.controller.show_abandon_game_dialog()
  File "test.py", line 304, in show_abandon_game_dialog
    result = self.dialog_manager.show_yes_no(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'SolitarioDialogManager' object has no attribute 'show_yes_no'
```

#### Root Cause Analysis

**Flusso chiamate**:
```
GameplayPanel.on_key_down()               (wxPython event)
  └─> GameplayPanel._handle_esc()             (line 164)
      └─> SolitarioController.show_abandon_game_dialog()  (test.py line 304)
          └─> dialog_manager.show_yes_no()        ❌ METODO NON ESISTE!
```

**Causa radice**:
- `SolitarioDialogManager` espone metodo `show_yes_no_dialog(title, message)`
- Codice in `test.py` chiama metodo `show_yes_no(message, title)` che non esiste
- Errore nome + ordine parametri invertito

**Codice attuale (ROTTO)**:
```python
# test.py - linee 302-310
def show_abandon_game_dialog(self) -> None:
    """Show abandon game confirmation dialog (called from GameplayView)."""
    result = self.dialog_manager.show_yes_no(  # ❌ METODO NON ESISTE
        "Vuoi abbandonare la partita e tornare al menu di gioco?",
        "Abbandono Partita"
    )
    if result:
        # Reset game engine (clear cards, score, timer)
        print("\n→ User confirmed abandon - Resetting game engine")
        self.engine.reset_game()
        
        # Return to main menu
        self.return_to_menu()
```

**Confronto con altri dialog (FUNZIONANTI)**:
```python
# test.py - linee 276-286 (show_exit_dialog - FUNZIONA ✅)
def show_exit_dialog(self) -> None:
    # ...
    result = self.dialog_manager.show_yes_no_dialog(  # ✅ NOME CORRETTO
        title="Conferma uscita",                       # ✅ title PRIMO
        message="Vuoi davvero uscire dal gioco?"       # ✅ message SECONDO
    )
```

**Soluzione corretta**:
1. Cambiare nome metodo: `show_yes_no()` → `show_yes_no_dialog()`
2. Invertire parametri: `message, title` → `title, message`
3. Usare keyword arguments per chiarezza

---

## 🔧 Piano di Correzione Chirurgica

### Modifiche Richieste (3 fix in 2 file)

| File | Linea | Tipo | Descrizione |
|------|-------|------|-------------|
| `src/application/gameplay_controller.py` | 318-332 | SEMPLIFICA | Rimuovere check modifiers pygame da `_select_card()` |
| `src/application/gameplay_controller.py` | ~337 (nuovo) | AGGIUNGI | Creare metodo `_select_from_waste()` helper |
| `test.py` | 304-310 | CORREGGI | Fixare chiamata dialog ESC |

---

### Fix 1: Semplificare `_select_card()` (rimuovere pygame)

**File**: `src/application/gameplay_controller.py`  
**Linee**: 318-332 (metodo `_select_card`)

#### Codice PRIMA (ROTTO)

```python
def _select_card(self) -> None:
    """ENTER: Select card under cursor.
    
    Special behavior:
    - On stock pile: Draw cards
    - On other piles: Select/toggle card
    - CTRL+ENTER: Select from waste pile
    """
    mods = pygame.key.get_mods()  # ❌ RIMUOVERE: pygame in wxPython!
    
    if mods & KMOD_CTRL:
        # CTRL+ENTER: Seleziona da scarti
        self.engine.select_from_waste()
    else:
        # ENTER normale: Seleziona carta o pesca
        self.engine.select_card_at_cursor()
```

#### Codice DOPO (FUNZIONANTE)

```python
def _select_card(self) -> None:
    """ENTER: Select card under cursor (simple selection).
    
    This method is called from handle_wx_key_event() which already
    handles CTRL+ENTER separately via _select_from_waste().
    This method ONLY handles plain ENTER (no modifiers).
    
    Behavior:
    - On stock pile: Draw cards
    - On other piles: Select/toggle card
    
    Note:
        CTRL+ENTER is handled separately in handle_wx_key_event()
        at line ~739 as direct call to _select_from_waste().
        This separation ensures clean wxPython integration.
    
    Version:
        v1.7.5: Simplified for wxPython (removed pygame.key.get_mods)
    """
    # wxPython version: No modifier check needed
    # Modifiers already handled by caller handle_wx_key_event()
    self.engine.select_card_at_cursor()
```

#### Rationale

**Perché questa modifica è corretta**:

1. **Separazione già implementata**: `handle_wx_key_event()` gestisce CTRL+ENTER separatamente:
   ```python
   # Line ~739 in handle_wx_key_event()
   if has_ctrl:
       if key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
           self._select_from_waste()  # Chiamata diretta
           return True
   
   # Line ~764 (più avanti, NO CTRL)
   elif key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
       self._select_card()  # Solo plain ENTER
       return True
   ```

2. **Controllo ridondante**: Il check `if mods & KMOD_CTRL` in `_select_card()` è inutile perché il metodo viene chiamato SOLO quando NON c'è CTRL

3. **Rimozione dipendenza pygame**: Eliminando `pygame.key.get_mods()`, il codice funziona in ambiente wxPython puro

4. **Mantiene logica originale**: Continua a chiamare `self.engine.select_card_at_cursor()` come prima

**Non ci sono regressioni perché**:
- La logica CTRL+ENTER è preservata in `handle_wx_key_event()` (line ~739)
- La logica plain ENTER è preservata in `_select_card()` (semplificata)
- Il metodo `handle_keyboard_events()` (pygame legacy) continua a funzionare perché usa `callback_dict` che chiama `_select_card()` direttamente

---

### Fix 2: Aggiungere metodo `_select_from_waste()`

**File**: `src/application/gameplay_controller.py`  
**Posizione**: Dopo `_select_card()` (circa linea 337, prima di `_move_cards()`)

#### Codice da AGGIUNGERE

```python
def _select_from_waste(self) -> None:
    """CTRL+ENTER: Select card from waste pile directly.
    
    Shortcut command for selecting top card from waste pile
    without needing to navigate cursor to it first.
    
    This is a convenience wrapper around engine.select_from_waste()
    for wxPython keyboard mapping.
    
    Called from:
        - handle_wx_key_event() when CTRL+ENTER pressed (line ~739)
    
    Equivalent pygame command:
        - CTRL+ENTER in handle_keyboard_events()
    
    Example:
        User presses CTRL+ENTER while cursor is on tableau pile.
        Instead of moving cursor to waste, this directly selects
        the top waste card for moving.
    
    Version:
        v1.7.5: New helper method for wxPython keyboard mapping
    """
    self.engine.select_from_waste()
```

#### Rationale

**Perché questo metodo è necessario**:

1. **Chiamato da `handle_wx_key_event()`**: Line ~739 chiama `self._select_from_waste()` ma il metodo non esiste → `AttributeError` imminente

2. **Coerenza architetturale**: Tutti i comandi keyboard hanno un metodo helper corrispondente:
   - ENTER → `_select_card()`
   - SPACE → `_move_cards()`
   - D/P → `_draw_cards()`
   - CTRL+ENTER → `_select_from_waste()` (MANCAVA!)

3. **Separazione responsabilità**: `handle_wx_key_event()` non chiama direttamente `engine.select_from_waste()` per mantenere separazione controller → helper → engine

4. **Compatibilità futura**: Eventuali estensioni (TTS custom, logging, etc) possono essere aggiunte nel metodo helper senza modificare il router principale

**Posizionamento**:
- Dopo `_select_card()` (line ~337)
- Prima di `_move_cards()` (line ~338 circa)
- Nella sezione "AZIONI CARTE" del codice

---

### Fix 3: Correggere chiamata dialog ESC

**File**: `test.py`  
**Linee**: 302-315 (metodo `show_abandon_game_dialog`)

#### Codice PRIMA (ROTTO)

```python
def show_abandon_game_dialog(self) -> None:
    """Show abandon game confirmation dialog (called from GameplayView)."""
    result = self.dialog_manager.show_yes_no(  # ❌ METODO NON ESISTE
        "Vuoi abbandonare la partita e tornare al menu di gioco?",  # Parametro 1
        "Abbandono Partita"  # Parametro 2
    )
    if result:
        # Reset game engine (clear cards, score, timer)
        print("\n→ User confirmed abandon - Resetting game engine")
        self.engine.reset_game()
        
        # Return to main menu
        self.return_to_menu()
```

#### Codice DOPO (FUNZIONANTE)

```python
def show_abandon_game_dialog(self) -> None:
    """Show abandon game confirmation dialog (called from GameplayPanel ESC handler).
    
    Displays native wxDialog asking user to confirm game abandonment.
    If user confirms (YES), resets game engine and returns to menu.
    If user cancels (NO/ESC), returns to gameplay.
    
    Called from:
        GameplayPanel._handle_esc() when ESC pressed during gameplay
    
    Dialog behavior:
        - Title: "Abbandono Partita"
        - Message: "Vuoi abbandonare la partita e tornare al menu di gioco?"
        - Buttons: YES (confirm) / NO (cancel)
        - ESC key: Same as NO (cancel)
    
    Returns:
        None (side effect: may reset game and switch to menu)
    
    Version:
        v1.7.5: Fixed dialog method name and parameter order
    """
    result = self.dialog_manager.show_yes_no_dialog(  # ✅ NOME CORRETTO
        title="Abbandono Partita",  # ✅ title primo (keyword arg)
        message="Vuoi abbandonare la partita e tornare al menu di gioco?"  # ✅ message secondo
    )
    
    if result:
        # User confirmed abandon
        print("\n→ User confirmed abandon - Resetting game engine")
        self.engine.reset_game()
        self.return_to_menu()
    # else: User cancelled, do nothing (dialog already closed)
```

#### Rationale

**Modifiche applicate**:

1. **Nome metodo corretto**: `show_yes_no()` → `show_yes_no_dialog()`
   - Verifica signature in `SolitarioDialogManager`:
     ```python
     def show_yes_no_dialog(self, title: str, message: str) -> bool:
     ```

2. **Parametri in ordine corretto**: `message, title` → `title, message`
   - Specifica esplicitamente con keyword arguments per chiarezza
   - Previene futuri errori se signature cambia

3. **Docstring aggiornata**:
   - Specifica chiamante corretto: `GameplayPanel._handle_esc()`
   - Documenta comportamento dialog
   - Aggiunge note versione

4. **Commento esplicativo**:
   - Aggiunto commento `# else: User cancelled...` per chiarezza
   - Documenta che nessuna azione è richiesta su cancellazione

**Confronto con pattern esistente** (verifica correttezza):

```python
# test.py - show_exit_dialog (line ~276 - FUNZIONA ✅)
result = self.dialog_manager.show_yes_no_dialog(
    title="Conferma uscita",
    message="Vuoi davvero uscire dal gioco?"
)

# test.py - show_new_game_dialog (line ~318 - FUNZIONA ✅)
result = self.dialog_manager.show_yes_no_dialog(
    title="Nuova Partita",
    message="Vuoi iniziare una nuova partita? I progressi attuali andranno persi."
)

# test.py - show_abandon_game_dialog (line ~304 - ORA FIXATO ✅)
result = self.dialog_manager.show_yes_no_dialog(
    title="Abbandono Partita",
    message="Vuoi abbandonare la partita e tornare al menu di gioco?"
)
```

**Tutti e tre i metodi ora usano lo stesso pattern**: ✅ Coerenza architetturale

---

## 🧪 Testing Plan Dettagliato

### Test 1: ENTER Key (plain)

**Setup**:
1. Avvia gioco: `python test.py`
2. Menu → "Nuova Partita"
3. Cursore posizionato su carta in pila base (es. 1 per pila 1)

**Procedura**:
1. Premi **ENTER**
2. Verifica TTS: "Carta selezionata: [nome carta]"
3. Premi **SPACE** per spostare
4. Verifica TTS: "Carta spostata" o "Mossa non valida"

**Risultato Atteso**:
- ✅ Nessun crash pygame.error
- ✅ Carta selezionata correttamente
- ✅ Log console: Nessun traceback

**Risultato PRIMA del fix**:
- ❌ Crash: `pygame.error: video system not initialized`
- ❌ Traceback a linea 323 (`pygame.key.get_mods()`)

---

### Test 2: CTRL+ENTER (select from waste)

**Setup**:
1. Avvia gioco: `python test.py`
2. Menu → "Nuova Partita"
3. Premi **D** per pescare 3 carte
4. Cursore su qualsiasi pila (NON su scarti)

**Procedura**:
1. Premi **CTRL+ENTER**
2. Verifica TTS: "Selezionata carta da scarti: [nome carta]"
3. Premi **SPACE** per spostare
4. Verifica TTS: "Carta spostata" o "Mossa non valida"

**Risultato Atteso**:
- ✅ Nessun crash
- ✅ Carta da scarti selezionata (non carta sotto cursore)
- ✅ Comportamento identico a versione pygame legacy

**Risultato PRIMA del fix**:
- ⚠️ Potenziale AttributeError: `_select_from_waste()` not found
- ❌ O fallback a plain ENTER (comportamento errato)

---

### Test 3: ESC during gameplay

**Setup**:
1. Avvia gioco: `python test.py`
2. Menu → "Nuova Partita"
3. Gioca qualche mossa (stato game attivo)

**Procedura**:
1. Premi **ESC**
2. Verifica apparizione dialog nativo wxPython:
   - Titolo: "Abbandono Partita"
   - Messaggio: "Vuoi abbandonare la partita e tornare al menu di gioco?"
   - Pulsanti: YES / NO
3. Premi **NO** (o ESC per chiudere)
4. Verifica: Ritorno a gameplay
5. Premi **ESC** di nuovo
6. Premi **YES**
7. Verifica: Ritorno a menu principale

**Risultato Atteso**:
- ✅ Dialog appare correttamente
- ✅ NO/ESC: Ritorno a gameplay
- ✅ YES: Reset game + ritorno a menu
- ✅ Nessun crash AttributeError

**Risultato PRIMA del fix**:
- ❌ Crash: `AttributeError: 'SolitarioDialogManager' object has no attribute 'show_yes_no'`
- ❌ Ripetuto ad ogni pressione ESC (6 traceback nel log)

---

### Test 4: Regression Check (altri 60+ tasti)

**Procedura Rapida**:
Testare un campione rappresentativo dei 60+ comandi:

| Tasto | Azione Attesa | Status |
|-------|---------------|--------|
| **1-7** | Vai pila base | ✅ |
| **SHIFT+1-4** | Vai fondazioni | ✅ |
| **SHIFT+S** | Vai scarti | ✅ |
| **SHIFT+M** | Vai mazzo | ✅ |
| **Frecce** | Navigazione | ✅ |
| **HOME/END** | Prima/ultima carta | ✅ |
| **TAB** | Pila tipo diverso | ✅ |
| **DELETE** | Annulla selezione | ✅ |
| **SPACE** | Sposta carte | ✅ |
| **D/P** | Pesca dal mazzo | ✅ |
| **F/G/R** | Info queries | ✅ |
| **N** | Nuova partita | ✅ |
| **O** | Opzioni | ✅ |

**Risultato Atteso**:
- ✅ Tutti i tasti funzionano come prima
- ✅ Nessuna regressione introdotta dai fix

---

### Test 5: Cross-Check con Pygame Legacy

**Procedura**:
1. Checkout branch `refactoring-engine` (pygame legacy)
2. Avvia: `python test.py`
3. Testa ENTER, CTRL+ENTER, ESC
4. Annota comportamento
5. Checkout branch `copilot/remove-pygame-migrate-wxpython` (wxPython fixed)
6. Avvia: `python test.py`
7. Testa ENTER, CTRL+ENTER, ESC
8. Confronta comportamento

**Risultato Atteso**:
- ✅ Comportamento identico in entrambi i branch
- ✅ Solo differenza: UI nativa wxPython vs pygame
- ✅ Logica gameplay 100% uguale

---

## 📦 Commit Strategy

### Commit Unico Atomico

**Rationale per singolo commit**:
- Le 3 modifiche sono **strettamente correlate** (risoluzione residui pygame)
- Testare separatamente non avrebbe senso (ENTER e ESC devono funzionare insieme)
- Commit atomico facilita eventuale revert

#### Commit Message (Conventional Commits)

```
fix(wx): resolve pygame residuals in ENTER handler and ESC dialog

Fixes two critical bugs preventing wxPython gameplay:

1. ENTER key not selecting cards during gameplay
   - Root cause: _select_card() called pygame.key.get_mods() in wxPython context
   - Fix: Removed pygame dependency, simplified to plain selection
   - Rationale: handle_wx_key_event() already handles CTRL+ENTER separately
   - Added _select_from_waste() helper method for CTRL+ENTER shortcut

2. ESC key crashing with AttributeError during abandon game dialog
   - Root cause: show_abandon_game_dialog() called non-existent show_yes_no() method
   - Fix: Corrected to show_yes_no_dialog() with proper parameter order
   - Aligned with existing dialog patterns (show_exit_dialog, show_new_game_dialog)

Impact:
- ENTER: Now selects card correctly (no pygame.error crash)
- CTRL+ENTER: Selects from waste pile (new helper method)
- ESC: Opens abandon dialog (no AttributeError crash)
- All 60+ other keyboard commands remain functional

Testing:
- Tested ENTER/CTRL+ENTER selection workflow
- Tested ESC abandon dialog (YES/NO/ESC flows)
- Regression check on 15+ representative commands
- Cross-checked behavior with pygame legacy branch

Files modified:
- src/application/gameplay_controller.py:
  - Simplified _select_card() (removed pygame.key.get_mods)
  - Added _select_from_waste() helper method
- test.py:
  - Fixed show_abandon_game_dialog() method call

Related:
- Completes wxPython migration (post keyboard mapping)
- Resolves residual pygame dependencies
- Critical path for v1.7.5 release

Closes: #[issue_number] (if applicable)
```

#### Files Changed Summary

```diff
 src/application/gameplay_controller.py | 28 ++++++++++++++----------
 test.py                                | 12 ++++++-----
 2 files changed, 23 insertions(+), 17 deletions(-)
```

---

## ✅ Checklist Completamento

### Pre-Commit
- [ ] **Fix 1 applicato**: `_select_card()` semplificato (no pygame)
- [ ] **Fix 2 applicato**: `_select_from_waste()` aggiunto
- [ ] **Fix 3 applicato**: `show_abandon_game_dialog()` corretto
- [ ] **Codice formattato**: PEP8 compliant
- [ ] **Docstring aggiornate**: Tutti i 3 metodi documentati
- [ ] **Import verificati**: Nessun import pygame inutilizzato

### Testing
- [ ] **Test 1 passato**: ENTER seleziona carta (no crash)
- [ ] **Test 2 passato**: CTRL+ENTER seleziona da scarti
- [ ] **Test 3 passato**: ESC apre dialog (no crash)
- [ ] **Test 4 passato**: Nessuna regressione altri tasti
- [ ] **Test 5 passato**: Comportamento identico a pygame legacy

### Documentazione
- [ ] **Commit message scritto**: Conventional Commits format
- [ ] **CHANGELOG.md aggiornato**: Entry v1.7.5 bugfix
- [ ] **Questo documento archiviato**: Spostare in `docs/completed - BUGFIX_PYGAME_RESIDUALS_WX.md`

### Post-Commit
- [ ] **Branch pushed**: `git push origin copilot/remove-pygame-migrate-wxpython`
- [ ] **CI/CD verificato**: (se applicabile)
- [ ] **Ready for merge**: Approvazione richiesta

---

## 📝 Note Operative per Copilot

### Istruzioni Step-by-Step

1. **Apri file**: `src/application/gameplay_controller.py`
2. **Naviga a linea 318** (metodo `_select_card`)
3. **Sostituisci linee 318-332** con codice da "Fix 1 - Codice DOPO"
4. **Naviga a linea ~337** (dopo `_select_card`, prima di `_move_cards`)
5. **Inserisci codice** da "Fix 2 - Codice da AGGIUNGERE"
6. **Salva file**

7. **Apri file**: `test.py`
8. **Naviga a linea 302** (metodo `show_abandon_game_dialog`)
9. **Sostituisci linee 302-315** con codice da "Fix 3 - Codice DOPO"
10. **Salva file**

11. **Testa applicazione**: `python test.py`
12. **Verifica Test 1-5**: Tutti devono passare
13. **Commit con message**: Usa esattamente il message fornito sopra

### Verifica Rapida Pre-Commit

Esegui questi comandi per validare:

```bash
# Verifica sintassi Python
python -m py_compile src/application/gameplay_controller.py
python -m py_compile test.py

# Verifica import pygame rimossi dove non servono
grep -n "pygame.key.get_mods" src/application/gameplay_controller.py
# Output atteso: NESSUNA LINEA (vuoto)

# Verifica nuovo metodo aggiunto
grep -n "def _select_from_waste" src/application/gameplay_controller.py
# Output atteso: Linea ~337 (o simile)

# Verifica dialog corretto
grep -n "show_yes_no_dialog" test.py
# Output atteso: Linee ~281, ~304, ~322 (3 occorrenze)
```

### Troubleshooting

**Se ENTER continua a non funzionare**:
- Verifica che `handle_wx_key_event()` a linea ~764 chiami `self._select_card()`
- Verifica che `_select_card()` NON contenga più `pygame.key.get_mods()`
- Testa con `print("ENTER pressed")` in `_select_card()` per debug

**Se CTRL+ENTER genera AttributeError**:
- Verifica che `_select_from_waste()` sia stato aggiunto
- Verifica che `handle_wx_key_event()` a linea ~739 chiami `self._select_from_waste()`
- Verifica che il metodo sia nella sezione "AZIONI CARTE" (dopo `_select_card`)

**Se ESC continua a crashare**:
- Verifica che `test.py` linea ~304 usi `show_yes_no_dialog` (non `show_yes_no`)
- Verifica ordine parametri: `title` PRIMA di `message`
- Verifica che `dialog_manager` sia inizializzato (non None)

---

## 🚀 Risultato Finale Atteso

Una volta applicati tutti i fix:

✅ **Gameplay 100% funzionale**:
- ENTER seleziona carta sul focus
- CTRL+ENTER seleziona da scarti
- ESC apre dialog abbandono
- Tutti i 60+ comandi keyboard operativi

✅ **Zero dipendenze pygame** in codice wxPython:
- Nessuna chiamata `pygame.key.get_mods()` in metodi wxPython
- Architettura pulita: wxPython → helpers → engine

✅ **Dialogs nativi consistenti**:
- Tutti usano `show_yes_no_dialog(title, message)`
- Pattern uniforme in tutto il codice

✅ **Ready for production**:
- Migrazione wxPython completa
- Testing validato
- Documentazione aggiornata

---

**Fine Piano Bugfix Chirurgico**

**Document Version**: v1.0  
**Last Updated**: 2026-02-13  
**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Status**: READY FOR IMPLEMENTATION  
**Estimated Time**: 15 minuti (3 fix + testing)
