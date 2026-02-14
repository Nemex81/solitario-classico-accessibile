# 📋 Piano Implementazione Bug #68 - Async Rematch Dialog Pattern

> **NOTA**: Questo documento è stato sostituito dalla soluzione definitiva.  
> Vedi: `PLAN_BUG68_async_rematch_dialog.md` per implementazione completa.

---

## 📊 Status

**Stato**: OBSOLETO (sostituito)  
**Piano Corrente**: [`PLAN_BUG68_async_rematch_dialog.md`](./PLAN_BUG68_async_rematch_dialog.md)  
**Versione**: v1.0 (deprecato)  
**Data Deprecazione**: 2026-02-15

---

## Cronologia Evoluzione

### v2.4.3 - Interim Fix (Questo Piano - OBSOLETO)

**Problema**: `AttributeError: 'SolitarioWxApp' object has no attribute 'CallAfter'`

**Soluzione Applicata**:
- Sostituito `self.app.CallAfter()` con `wx.CallAfter()` (API corretta)
- 3 modifiche in `acs_wx.py` (linee 637, 648, 831)
- Documentazione aggiornata su usage corretto

**Limitazioni**:
- ✅ Risolve crash AttributeError
- ❌ Non risolve finestra vuota decline rematch (race condition)
- ❌ Pattern inconsistente (ESC/N async, rematch sincrono + workaround)
- ❌ Richiede `wx.CallAfter()` manuale in acs_wx.py

### v2.5.0 - Async Dialog Pattern (Piano Definitivo)

**Problema Root Cause**: Dialog rematch sincrono in `GameEngine.end_game()`

**Soluzione Definitiva**:
1. Aggiunto `show_rematch_prompt_async()` in `DialogManager`
2. Refactored `GameEngine.end_game()` per usare async dialog
3. Rimosso workaround `wx.CallAfter()` da `acs_wx.py`

**Benefici**:
- ✅ Risolve crash AttributeError
- ✅ Risolve finestra vuota decline rematch
- ✅ Pattern consistente (TUTTI i dialog async)
- ✅ Nessun workaround necessario
- ✅ Codice più pulito, meno commenti "CRITICAL"

---

## Migrazione

Se hai già applicato il fix v2.4.3 (CallAfter workaround):

1. **Leggi piano definitivo**: [`PLAN_BUG68_async_rematch_dialog.md`](./PLAN_BUG68_async_rematch_dialog.md)
2. **Applica 3 commit**:
   - COMMIT 1: Add `show_rematch_prompt_async()` in DialogManager
   - COMMIT 2: Refactor `GameEngine.end_game()` async pattern
   - COMMIT 3: Remove `wx.CallAfter()` workaround in acs_wx.py
3. **Testing**: 6 test case manuali (vedi piano definitivo)

---

## Link Rapidi

- **Piano Definitivo**: [`PLAN_BUG68_async_rematch_dialog.md`](./PLAN_BUG68_async_rematch_dialog.md)
- **Issue GitHub**: [#68 - Rematch flow crash](https://github.com/Nemex81/solitario-classico-accessibile/issues/68)
- **Branch**: `copilot/refactor-difficulty-options-system`
- **Files Coinvolti**:
  - `src/application/dialog_manager.py`
  - `src/application/game_engine.py`
  - `acs_wx.py`

---

## Documentazione Storica (v2.4.3 - Deprecata)

<details>
<summary>Espandi per vedere piano interim (OBSOLETO)</summary>

### Problema Originale

```python
# acs_wx.py - linea 637 (BUGGY)
self.app.CallAfter(self.start_gameplay)  # ❌ AttributeError!
```

**Causa**: wxPython 4.1.1 non ha metodo `CallAfter()` su `wx.App`

### Fix Interim (v2.4.3)

```python
# acs_wx.py - linea 637 (FIXED)
wx.CallAfter(self.start_gameplay)  # ✅ API corretta
```

**Risultato**:
- Crash eliminato
- Finestra vuota decline rematch persisteva (race condition)

### Limitazioni Fix Interim

| Aspetto | v2.4.3 (Interim) | v2.5.0 (Definitivo) |
|---------|------------------|---------------------|
| **Crash AttributeError** | ✅ Risolto | ✅ Risolto |
| **Finestra vuota decline** | ❌ Presente | ✅ Risolto |
| **Pattern consistency** | ❌ Inconsistente | ✅ Consistente |
| **Workaround needed** | ✅ Sì (CallAfter) | ❌ No |
| **Code complexity** | Media | Bassa |

</details>

---

**Per implementazione corrente, vedi**: [`PLAN_BUG68_async_rematch_dialog.md`](./PLAN_BUG68_async_rematch_dialog.md)
