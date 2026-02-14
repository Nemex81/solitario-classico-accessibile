# 📋 TODO – wx.CallAfter MainLoop Assertion Fix (v2.0.5)

**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Tipo**: FIX (CRITICAL)  
**Priorità**: HIGH (P0 - Blocks release)  
**Stato**: READY

---

## 📖 Riferimento Documentazione

**OBBLIGATORIO** consultare prima di qualsiasi modifica:

📄 **`docs/FIX_WX_CALLAFTER_MAINLOOP_ASSERTION.md`** (Piano completo)

Questo file TODO è solo un sommario operativo da consultare e aggiornare durante ogni fase dell'implementazione.  
Il piano completo contiene:
- Root cause analysis dettagliata
- Timeline del problema
- Confronto wx.CallAfter vs wx.CallLater
- Test cases completi (10 tests)
- Commit message pre-scritto

---

## 🎯 Obiettivo Implementazione

**Problema**: App si blocca dopo ESC abandon con errore `AssertionError: No wx.App created yet`

**Soluzione**: Sostituire `wx.CallAfter()` con `wx.CallLater(10, ...)` in tutte le transizioni deferite

**Impatto**: 
- Elimina hang su transizioni panel (ESC, rematch, timeout)
- Delay 10ms impercettibile (~1 frame @ 60fps)
- Affidabilità 100% in tutte le fasi app lifecycle

---

## 📂 File Coinvolti

- `test.py` → **MODIFY** (4 linee cambiate)
- `CHANGELOG.md` → **UPDATE** (v2.0.5)
- `docs/FIX_WX_CALLAFTER_MAINLOOP_ASSERTION.md` → **RENAME** (→ completed-)

---

## 🛠 Checklist Implementazione

### Modifiche Codice (test.py)

- [ ] **Linea ~371**: `show_abandon_game_dialog()`
  - Cambia: `wx.CallAfter(self._safe_abandon_to_menu)`
  - In: `wx.CallLater(10, self._safe_abandon_to_menu)`

- [ ] **Linea ~460**: `handle_game_ended()` - rematch branch
  - Cambia: `wx.CallAfter(self.start_gameplay)`
  - In: `wx.CallLater(10, self.start_gameplay)`

- [ ] **Linea ~463**: `handle_game_ended()` - decline branch
  - Cambia: `wx.CallAfter(self._safe_decline_to_menu)`
  - In: `wx.CallLater(10, self._safe_decline_to_menu)`

- [ ] **Linea ~600**: `_handle_game_over_by_timeout()`
  - Cambia: `wx.CallAfter(self._safe_timeout_to_menu)`
  - In: `wx.CallLater(10, self._safe_timeout_to_menu)`

### Testing (4 Critical + 4 Regression)

#### Critical Tests
- [ ] **Test #1**: ESC abandon → Menu shows (no hang, no AssertionError)
- [ ] **Test #2**: Victory decline → Menu shows
- [ ] **Test #3**: Victory rematch → New game starts
- [ ] **Test #4**: Timeout strict → Menu shows (auto transition)

#### Regression Tests
- [ ] **RT #1**: Menu navigation works
- [ ] **RT #2**: All 80+ keyboard commands work
- [ ] **RT #3**: Options dialog works
- [ ] **RT #4**: Exit flows (ESC menu, button, ALT+F4) work

### Documentation

- [ ] Update `CHANGELOG.md` with v2.0.5 section
- [ ] Update version string in test.py docstring
- [ ] Rename `FIX_WX_CALLAFTER_MAINLOOP_ASSERTION.md` → `completed-`

---

## ✅ Criteri di Completamento

L'implementazione è considerata completa quando:

- [ ] Tutte le 4 linee modificate (search/replace eseguito)
- [ ] Tutti gli 8 test passano (4 critical + 4 regression)
- [ ] Nessun `AssertionError` nei log
- [ ] Nessun hang/freeze dopo transizioni
- [ ] CHANGELOG.md aggiornato con v2.0.5
- [ ] Versione incrementata (v2.0.4 → v2.0.5 PATCH)
- [ ] Commit con messaggio da piano completo
- [ ] Documentazione marcata come completed

---

## 📝 Aggiornamenti Obbligatori a Fine Implementazione

- [ ] `CHANGELOG.md`: Aggiungere sezione v2.0.5 con fix dettagli
- [ ] `test.py`: Docstring versione → "v2.0.5 (CRITICAL bugfix - wx.CallAfter assertion)"
- [ ] Commit message: Usare template da piano completo (linee 653-696)
- [ ] Push: `git push origin copilot/remove-pygame-migrate-wxpython`
- [ ] Move doc: `git mv docs/FIX_WX_CALLAFTER_MAINLOOP_ASSERTION.md docs/completed-FIX_WX_CALLAFTER_MAINLOOP_ASSERTION.md`

---

## 📌 Note

**PATTERN DA APPLICARE**:
```python
# TROVA
wx.CallAfter(metodo)

# SOSTITUISCI CON
wx.CallLater(10, metodo)
```

**MOTIVO**: `wx.CallAfter()` fallisce con `AssertionError: No wx.App created yet` perché `wx.App.Get()` ritorna `None` durante fasi init/transition. `wx.CallLater(10)` usa timer system (no dipendenza da `wx.App.Get()`), quindi funziona sempre.

**DELAY 10ms**: Impercettibile (~1 frame @ 60fps), garantisce MainLoop attivo e wx.App registrato.

**NET CHANGE**: 4 linee modificate, 0 linee aggiunte/rimosse. Minimal impact, maximum fix.

---

**Fine TODO**

Consultare piano completo per dettagli tecnici, rationale, e test completi.
