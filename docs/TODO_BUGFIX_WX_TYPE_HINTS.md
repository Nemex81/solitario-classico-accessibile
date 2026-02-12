# TODO: Bugfix wxPython Type Hints & Parameter Naming

**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Issue**: #59 (Post-implementation bugfixes)  
**Versione Target**: v1.7.1 (PATCH)  
**Piano Completo**: [`docs/BUGFIX_WX_TYPE_HINTS_PARAMETER_NAMING.md`](./BUGFIX_WX_TYPE_HINTS_PARAMETER_NAMING.md)  
**Stima Totale**: 30 minuti (3 commit × 10 min)

---

## 🐛 Bug Identificati

### Bug #1: `wx.ButtonEvent` Non Esiste
**Errore**: `AttributeError: module 'wx' has no attribute 'ButtonEvent'`  
**File**: `src/infrastructure/ui/menu_view.py`  
**Fix**: Sostituire `wx.ButtonEvent` → `wx.CommandEvent`

### Bug #2: Parameter Naming Inconsistente
**Errore**: `TypeError: unexpected keyword argument 'parent'`  
**File**: `src/application/game_engine.py`  
**Fix**: Cambiare `parent=` → `parent_frame=`

---

## 📦 COMMIT 1: Fix Type Hints menu_view.py (10 min)

### Modifiche

**File**: `src/infrastructure/ui/menu_view.py`

- [ ] **Linea ~147**: Cambia `wx.ButtonEvent` → `wx.CommandEvent` in `on_play_click()`
- [ ] **Aggiungi** docstring args: `event: Command event from button (wx.EVT_BUTTON)`
- [ ] **Linea ~158**: Cambia `wx.ButtonEvent` → `wx.CommandEvent` in `on_options_click()`
- [ ] **Aggiungi** docstring args: `event: Command event from button (wx.EVT_BUTTON)`
- [ ] **Linea ~169**: Cambia `wx.ButtonEvent` → `wx.CommandEvent` in `on_exit_click()`
- [ ] **Aggiungi** docstring args: `event: Command event from button (wx.EVT_BUTTON)`

### Testing

- [ ] Verifica import: `python -c "from src.infrastructure.ui.menu_view import MenuView; print('✓ OK')"`
- [ ] Nessun `AttributeError`
- [ ] Grep verifica: `grep -n "wx.ButtonEvent" src/infrastructure/ui/menu_view.py` → 0 risultati

### Commit

```bash
git add src/infrastructure/ui/menu_view.py
git commit -m "fix(ui): Replace wx.ButtonEvent with wx.CommandEvent in menu_view.py

CRITICAL FIX: wx.ButtonEvent does not exist in wxPython.
Button events use wx.CommandEvent (base class for command widgets).

Fixed methods:
- on_play_click(): wx.ButtonEvent → wx.CommandEvent
- on_options_click(): wx.ButtonEvent → wx.CommandEvent  
- on_exit_click(): wx.ButtonEvent → wx.CommandEvent

References: Issue #59 bugfix"
```

---

## 📦 COMMIT 2: Fix Parameter Naming game_engine.py (10 min)

### Modifiche

**File**: `src/application/game_engine.py`

- [ ] **Linea ~241**: Cambia `WxDialogProvider(parent=parent_window)` → `WxDialogProvider(parent_frame=parent_window)`

**Context** (dentro metodo `GameEngine.create()`):
```python
# PRIMA (❌ ERRATO)
dialog_provider = WxDialogProvider(parent=parent_window)

# DOPO (✅ CORRETTO)
dialog_provider = WxDialogProvider(parent_frame=parent_window)
```

### Testing

- [ ] Verifica import: `python -c "from src.application.game_engine import GameEngine; print('✓ OK')"`
- [ ] Verifica factory: `python -c "from src.application.game_engine import GameEngine; GameEngine.create(use_native_dialogs=True); print('✓ OK')"`
- [ ] Nessun `TypeError`
- [ ] Grep verifica: `grep -n "WxDialogProvider(parent=" src/` → 0 risultati

### Commit

```bash
git add src/application/game_engine.py
git commit -m "fix(engine): Fix WxDialogProvider parameter naming to match COMMIT 2 pattern

CRITICAL FIX: WxDialogProvider constructor expects 'parent_frame', not 'parent'.
Align with hs_deckmanager pattern.

Fixed:
- game_engine.py line ~241: parent= → parent_frame=

References: Issue #59 bugfix, COMMIT 2 pattern"
```

---

## 📦 COMMIT 3: Verify & Update Docs (10 min)

### Verifica gameplay_view.py

- [ ] Esegui: `grep -n "wx.ButtonEvent" src/infrastructure/ui/gameplay_view.py`
- [ ] **Se trova occorrenze**: Applica fix `wx.ButtonEvent` → `wx.CommandEvent`
- [ ] **Se nessuna occorrenza**: Skip file (nota in commit message)

### Verifica Completa Progetto

- [ ] Esegui: `grep -rn "wx.ButtonEvent" src/` → **0 risultati attesi**
- [ ] Esegui: `grep -rn "WxDialogProvider(parent=" src/` → **0 risultati attesi**
- [ ] Tutte le chiamate usano `parent_frame=`

### Aggiornamento CHANGELOG.md (OBBLIGATORIO)

**File**: `CHANGELOG.md`

- [ ] **Aggiungi** nuova sezione sopra `[1.7.0]`:

```markdown
## [1.7.1] - 2026-02-12

### Fixed
- **CRITICAL**: Fixed `AttributeError: module 'wx' has no attribute 'ButtonEvent'` in `menu_view.py`
  - Replaced incorrect `wx.ButtonEvent` type hints with `wx.CommandEvent`
  - Button events in wxPython use `wx.CommandEvent` base class
  - Affected methods: `on_play_click()`, `on_options_click()`, `on_exit_click()`
  
- **CRITICAL**: Fixed `TypeError: unexpected keyword argument 'parent'` in `game_engine.py`
  - Changed `WxDialogProvider(parent=...)` to `WxDialogProvider(parent_frame=...)`
  - Aligned parameter naming with hs_deckmanager pattern (COMMIT 2)

### Technical
- Enhanced docstrings with explicit event type specification
- Verified project-wide consistency for wxPython event type hints

### References
- Issue #59: Post-implementation bugfixes
- wxPython docs: https://docs.wxpython.org/events_summary.html
```

### Verifica README.md (Opzionale)

- [ ] Apri `README.md`
- [ ] Verifica sezione "Requisiti Sistema"
- [ ] Verifica sezione "Installazione"
- [ ] **Se accurato**: Nessuna modifica necessaria
- [ ] **Se obsoleto**: Aggiorna (poco probabile per bugfix)

### Testing Completo App

- [ ] Esegui: `python test.py`
- [ ] App si avvia senza crash
- [ ] Menu principale visibile
- [ ] TAB naviga pulsanti
- [ ] ENTER su "Gioca" → Gameplay inizia
- [ ] H → Comandi mostrati
- [ ] ESC → Dialog conferma abbandono
- [ ] Conferma Sì → Ritorno menu
- [ ] ENTER su "Esci" → Dialog conferma uscita

### Commit

```bash
git add CHANGELOG.md
git add README.md  # se modificato
git add src/infrastructure/ui/gameplay_view.py  # se modificato

git commit -m "docs: Update CHANGELOG for v1.7.1 bugfix release

Post-implementation bugfixes for Issue #59.

Version: v1.7.0 → v1.7.1 (PATCH increment)

Fixed:
1. wx.ButtonEvent → wx.CommandEvent (menu_view.py)
2. parent= → parent_frame= (game_engine.py)

Verified:
- gameplay_view.py: No issues found
- Project-wide consistency validated
- Full app testing: OK

References: Issue #59 bugfix"
```

---

## ✅ Acceptance Criteria

### Funzionalità

- [ ] App si avvia senza `AttributeError`
- [ ] App si avvia senza `TypeError`
- [ ] Menu funzionante (TAB + ENTER)
- [ ] Gameplay si avvia correttamente
- [ ] Dialog modali funzionano
- [ ] Flow completo menu → gameplay → menu OK

### Code Quality

- [ ] Zero occorrenze `wx.ButtonEvent` nel progetto
- [ ] Tutte le chiamate `WxDialogProvider` usano `parent_frame=`
- [ ] Docstring aggiornate con tipo evento
- [ ] Commit messages descrittivi

### Documentazione

- [ ] CHANGELOG.md aggiornato con v1.7.1
- [ ] README.md verificato
- [ ] Reference Issue #59 in tutti i commit

### Testing

- [ ] Import validations: OK
- [ ] Factory method: OK
- [ ] App startup: OK
- [ ] Flow completo testato

---

## 🔍 Comandi Verifica Finali

```bash
# 1. Verifica wx.ButtonEvent (deve essere 0)
grep -rn "wx.ButtonEvent" src/

# 2. Verifica WxDialogProvider calls (tutte con parent_frame=)
grep -rn "WxDialogProvider(" src/ test.py

# 3. Import validations
python -c "from src.infrastructure.ui.menu_view import MenuView; print('✓ MenuView OK')"
python -c "from src.infrastructure.ui.gameplay_view import GameplayView; print('✓ GameplayView OK')"
python -c "from src.application.game_engine import GameEngine; print('✓ GameEngine OK')"

# 4. Factory method
python -c "from src.application.game_engine import GameEngine; GameEngine.create(use_native_dialogs=True); print('✓ Factory OK')"

# 5. Full app
python test.py

# 6. Commit log
git log --oneline -3

# 7. CHANGELOG version
head -20 CHANGELOG.md | grep "\[1.7.1\]"
```

---

## 🚀 Workflow per Copilot

### Pre-Implementazione

1. ✅ Consulta piano completo: `docs/BUGFIX_WX_TYPE_HINTS_PARAMETER_NAMING.md`
2. ✅ Leggi questo TODO per checklist rapida
3. ✅ Verifica branch: `copilot/remove-pygame-migrate-wxpython`

### Durante Implementazione

**Per ogni commit**:
1. ✅ Consulta sezione commit in piano completo
2. 🔨 Implementa modifiche (questo TODO)
3. 🧪 Esegui testing
4. ✅ Spunta checkbox
5. 📝 Commita
6. 🔄 Procedi al successivo

### Post-Implementazione

1. ✅ Esegui comandi verifica finali
2. ✅ Valida acceptance criteria
3. 🚀 Push branch
4. 📊 Commenta PR #59

---

## 📚 Reference Rapida: Type Hints wxPython

```python
import wx

# ✅ CORRETTO - Eventi pulsanti
def on_button_click(self, event: wx.CommandEvent) -> None:
    pass

# ✅ CORRETTO - Eventi tastiera
def on_key_down(self, event: wx.KeyEvent) -> None:
    pass

# ✅ CORRETTO - Eventi focus
def on_set_focus(self, event: wx.FocusEvent) -> None:
    pass

# ✅ CORRETTO - Eventi chiusura
def on_close(self, event: wx.CloseEvent) -> None:
    pass

# ✅ CORRETTO - Eventi timer
def on_timer(self, event: wx.TimerEvent) -> None:
    pass
```

**Documentazione**: https://docs.wxpython.org/events_summary.html

---

## 📞 Supporto

Se emergono problemi:
- **Consulta** piano completo per dettagli tecnici
- **Copia** traceback completo in commento PR
- **Verifica** pattern hs_deckmanager per naming

---

**Status**: ⏳ Pending Implementation  
**Progress**: 0/3 commits (0%)  
**Prossimo Step**: ➡️ COMMIT 1 (menu_view.py)
