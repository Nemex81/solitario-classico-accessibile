# 📋 TODO – Async Rematch Dialog Pattern (v2.5.0)

**Branch**: `copilot/refactor-difficulty-options-system`  
**Tipo**: REFACTORING + BUGFIX  
**Priorità**: HIGH  
**Stato**: READY  
**Issue**: [#68 - Rematch flow crash + finestra vuota](https://github.com/Nemex81/solitario-classico-accessibile/issues/68)

---

## 📚 ⚠️ Riferimento Documentazione OBBLIGATORIO

**Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente**:

📄 **Piano Completo**: [`docs/PLAN_BUG68_async_rematch_dialog.md`](./PLAN_BUG68_async_rematch_dialog.md)

Questo file TODO è solo un **sommario operativo** da consultare e aggiornare durante ogni fase dell'implementazione.

Il piano completo contiene:
- ✅ Analisi root cause (dialog sincrono vs asincrono)
- ✅ Architettura target con diagrammi
- ✅ Codice completo per ogni commit
- ✅ Testing strategy con 6 test case
- ✅ Common pitfalls e troubleshooting
- ✅ Istruzioni step-by-step dettagliate

---

## 🎯 Obiettivo Implementazione

**Cosa**: Convertire dialog rematch da pattern sincrono (ShowModal) a pattern asincrono (Show + callback).

**Perché**: 
- Elimina workaround `wx.CallAfter()` in `acs_wx.py`
- Risolve Bug #68 residuo (finestra vuota decline rematch)
- Pattern consistente con ESC/N (tutti dialog async)

**Impatto**:
- ✅ Callback `on_game_ended()` riceve contesto UI stabile
- ✅ Codice più pulito, meno commenti "CRITICAL"
- ✅ Future-proof per nuovi dialog confirmation

---

## 📝 Strategia Implementazione

### ⚠️ IMPORTANTE - Approccio Incrementale

**Copilot DEVE procedere con codifica**:
1. ✅ **Incrementale**: Un commit alla volta, mai tutto insieme
2. ✅ **Sequenziale**: COMMIT 1 → test → COMMIT 2 → test → COMMIT 3
3. ✅ **Consultazione piano**: Leggere sezione specifica prima di ogni commit
4. ✅ **Atomicità**: Ogni commit deve compilare e non rompere funzionalità

**Pattern corretto**:
```
COMMIT 1 (DialogManager) → Push → Test sintassi
  ↓
COMMIT 2 (GameEngine) → Push → Test sintassi  
  ↓
COMMIT 3 (acs_wx.py) → Push → Test funzionale completo
```

**Anti-pattern da EVITARE**:
```
❌ Modificare tutti e 3 i file insieme
❌ Commit unico con 3 file
❌ Implementare senza leggere piano
❌ Saltare test intermedi
```

---

## 📚 Riferimenti Piano per Ogni Commit

### COMMIT 1: DialogManager
**Sezione Piano**: "COMMIT 1: Add show_rematch_prompt_async() to DialogManager"  
**File**: `src/application/dialog_manager.py`  
**Azione**: Aggiungere metodo dopo linea 261  
**Codice Completo**: Vedi piano linee ~230-310

### COMMIT 2: GameEngine
**Sezione Piano**: "COMMIT 2: Refactor GameEngine.end_game() to use async rematch dialog"  
**File**: `src/application/game_engine.py`  
**Azione**: Sostituire linee 898-933  
**Codice Completo**: Vedi piano linee ~340-480

### COMMIT 3: acs_wx.py
**Sezione Piano**: "COMMIT 3: Remove wx.CallAfter workaround from acs_wx.py"  
**File**: `acs_wx.py`  
**Azione**: Rimuovere CallAfter linee 637, 648 + aggiornare docs  
**Codice Completo**: Vedi piano linee ~500-680

---

## 📂 File Coinvolti

| File | Azione | Commit | Linee |
|------|--------|--------|-------|
| `src/application/dialog_manager.py` | CREATE | 1 | +40 (nuovo metodo) |
| `src/application/game_engine.py` | MODIFY | 2 | ~35 (sostituire Step 7-8) |
| `acs_wx.py` | MODIFY | 3 | ~50 (rimuovere CallAfter + docs) |

---

## 🛠 Checklist Implementazione

### COMMIT 1: DialogManager (⚠️ Leggere piano prima di implementare)
- [ ] 📚 Letto sezione "COMMIT 1" nel piano completo
- [ ] Aperto file `src/application/dialog_manager.py`
- [ ] Trovato linea 261 (dopo `show_exit_app_prompt_async`)
- [ ] Copiato metodo `show_rematch_prompt_async()` dal piano
- [ ] Verificato docstring completo in italiano
- [ ] Verificato fallback `if not self.is_available`
- [ ] Test sintassi: `python -m py_compile src/application/dialog_manager.py`
- [ ] Commit con messaggio: `feat(dialogs): add show_rematch_prompt_async() method`
- [ ] Push branch

### COMMIT 2: GameEngine (⚠️ Leggere piano prima di implementare)
- [ ] 📚 Letto sezione "COMMIT 2" nel piano completo
- [ ] Aperto file `src/application/game_engine.py`
- [ ] Trovato linee 898-933 (Step 6-8 in `end_game()`)
- [ ] Rimosso `wants_rematch = False`
- [ ] Rimosso `wants_rematch = self.dialogs.show_yes_no(...)`
- [ ] Aggiunto nested callback `on_rematch_result()`
- [ ] Aggiunto chiamata `show_rematch_prompt_async(on_rematch_result)`
- [ ] Aggiornato Step 7 comment: "Async Rematch Prompt (v2.5.0)"
- [ ] Test sintassi: `python -m py_compile src/application/game_engine.py`
- [ ] Commit con messaggio: `refactor(engine): use async rematch dialog in end_game()`
- [ ] Push branch

### COMMIT 3: acs_wx.py (⚠️ Leggere piano prima di implementare)
- [ ] 📚 Letto sezione "COMMIT 3" nel piano completo
- [ ] Aperto file `acs_wx.py`
- [ ] **Modifica 1**: Linea 637 - Rimosso `wx.CallAfter(self.start_gameplay)` → `self.start_gameplay()`
- [ ] **Modifica 2**: Linea 648 - Rimosso `wx.CallAfter(self._safe_return_to_main_menu)` → `self._safe_return_to_main_menu()`
- [ ] **Modifica 3**: Aggiornato docstring `handle_game_ended()` (linea ~595)
- [ ] **Modifica 4**: Sostituito "DEFERRED PATTERN" con "ASYNC DIALOG PATTERN" (linee 455-486)
- [ ] Aggiornato print statements: "Starting rematch..." / "Returning to main menu..."
- [ ] Test sintassi: `python -m py_compile acs_wx.py`
- [ ] Commit con messaggio: `fix(app): remove wx.CallAfter workaround (Bug #68 final)`
- [ ] Push branch

---

## 🧪 Testing Strategy (⚠️ Sezione completa nel piano)

### Test Immediato Post-COMMIT 3
```bash
python acs_wx.py

# Test Case 1: Accept Rematch
N → CTRL+ALT+W → INVIO → YES (INVIO)
Expected: Nuova partita, console log "Starting rematch..." (NO "Scheduling deferred")

# Test Case 2: Decline Rematch (Bug #68 risolto)
N → CTRL+ALT+W → INVIO → TAB → INVIO (NO)
Expected: Menu VISIBILE immediatamente, console log "Returning to main menu..."
```

### Test Completi (Vedi piano per dettagli)
- [ ] Test Case 1: Accept rematch (async flow)
- [ ] Test Case 2: Decline rematch (Bug #68 risolto) ⭐ CRITICO
- [ ] Test Case 3: Multiple rematch sequence
- [ ] Test Case 4: ESC abandon (no regression)
- [ ] Test Case 5: N new game (no regression)
- [ ] Test Case 6: Fallback without dialogs

---

## ✅ Criteri di Completamento

### Funzionali
- [ ] Nessun crash AttributeError
- [ ] Menu visibile dopo decline rematch (Bug #68 risolto)
- [ ] Rematch accept funziona senza CallAfter logs
- [ ] ESC abandon no regression
- [ ] N new game no regression

### Tecnici
- [ ] Tutti e 3 i commit compilano senza errori
- [ ] Nessun nuovo warning in console
- [ ] Console log consistente ("Starting/Returning", NO "Scheduling")
- [ ] `grep -n "wx.CallAfter.*handle_game_ended" acs_wx.py` ritorna 0 risultati

### Code Quality
- [ ] Pattern async consistente (TUTTI i dialog usano `*_async()`)
- [ ] Documentazione inline aggiornata (no "CRITICAL" su timing)
- [ ] Docstring completi con esempio usage
- [ ] Version history aggiornato in ogni file

---

## 📝 Aggiornamenti Obbligatori a Fine Implementazione

- [ ] Chiudere Issue #68 con riferimento ai 3 commit
- [ ] Aggiornare `CHANGELOG.md` con entry v2.5.0
- [ ] Tag version (se merge in main): `git tag v2.5.0`
- [ ] Commit message finale segue Conventional Commits

---

## 📌 Note Operative

### Verifica Rapida Post-Implementazione
```bash
# Sintassi (tutti e 3 i file)
python -m py_compile src/application/dialog_manager.py
python -m py_compile src/application/game_engine.py
python -m py_compile acs_wx.py

# Grep per verificare rimozione CallAfter
grep -n "wx.CallAfter" acs_wx.py | grep -E "(637|648)"
# Expected: Nessun match

# Test funzionale immediato
python acs_wx.py
N → CTRL+ALT+W → INVIO → NO
# Expected: Menu visibile, nessun crash
```

### Troubleshooting Rapido (Dettagli completi nel piano)

| Problema | Causa Probabile | Soluzione |
|----------|-----------------|------------|
| AttributeError su `show_rematch_prompt_async` | COMMIT 1 non applicato | Verificare dialog_manager.py, controllare nome metodo |
| Menu vuoto dopo decline | COMMIT 3 non completo | Verificare linea 648, `_safe_return_to_main_menu()` diretto |
| Crash su accept rematch | Panel hiding mancante | Verificare `start_gameplay()` linee 268-273 |
| Callback non invocato | COMMIT 2 sintassi errata | Verificare nested callback definito, passaggio a `show_*_async` |

### Link Utili
- **Piano Completo**: [`docs/PLAN_BUG68_async_rematch_dialog.md`](./PLAN_BUG68_async_rematch_dialog.md)
- **Piano Interim (Deprecato)**: [`docs/PLAN_BUG68_wx_CallAfter_fix.md`](./PLAN_BUG68_wx_CallAfter_fix.md)
- **Issue GitHub**: [#68](https://github.com/Nemex81/solitario-classico-accessibile/issues/68)
- **Branch**: `copilot/refactor-difficulty-options-system`

---

## ⚠️ Promemoria per Copilot

### PRIMA DI OGNI COMMIT:
1. 📚 **Leggere sezione specifica nel piano completo**
2. 🔍 **Verificare numero linee corrette** (possono cambiare tra commit)
3. 📝 **Copiare codice esatto dal piano** (non improvvisare)
4. ✅ **Test sintassi immediatamente dopo modifica**
5. 📦 **Commit atomico con messaggio conventional**

### DOPO OGNI COMMIT:
1. 🚀 **Push branch** (per backup incrementale)
2. 📋 **Spuntare checklist in questo TODO**
3. 🔎 **Verificare GitHub Actions** (se configurate)
4. ➡️ **Passare al commit successivo SOLO se test OK**

### SE QUALCOSA VA STORTO:
1. 🛑 **STOP - Non procedere al commit successivo**
2. 📚 **Rileggere sezione Troubleshooting nel piano**
3. 👁️ **Confrontare codice con piano (diff)**
4. ❓ **Chiedere chiarimenti se necessario**

---

**Fine TODO Operativo**

**Versione**: v1.0  
**Data Creazione**: 2026-02-15  
**Autore**: AI Assistant + Nemex81  
**Ultima Modifica**: 2026-02-15  
**Stato**: ⭕ READY

🚀 **Pronto per implementazione incrementale!**
