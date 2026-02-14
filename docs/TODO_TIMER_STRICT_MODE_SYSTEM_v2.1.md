# 📋 TODO – Timer Strict Mode System Integration (v2.1)
Branch: copilot/remove-pygame-migrate-wxpython
Tipo: REFACTOR
Priorità: HIGH
Stato: IN PROGRESS

## 📖 Riferimento Documentazione Obbligatorio
**LEGGERE PRIMA DI OGNI FASE**:
`docs/IMPLEMENTATION_TIMER_STRICT_MODE_SYSTEM_v2.1.md`

Questo TODO è solo un sommario operativo. Il piano completo contiene:
- Analisi architetturale completa
- Pattern dettagliati con esempi di codice
- Common pitfalls da evitare
- Validation checklist per ogni commit

## 🎯 Obiettivo Implementazione

Integrazione sistemica e validazione del pattern deferred UI transitions (`self.app.CallAfter()`) stabilito in v2.0.9:
• Audit completo del codebase per identificare tutti gli usi di `wx.CallAfter()`
• Validazione consistency pattern in tutti i file critici
• Documentazione estensiva inline e in docstrings
• Zero breaking changes - solo refactoring e documentazione

**Impatto**: Garantisce manutenibilità futura e previene regressioni del pattern `self.app.CallAfter()`.

## 📂 File Coinvolti

### 🔴 Priorità CRITICA
- `test.py` → MODIFY (documentazione + validation)
- `src/infrastructure/ui/view_manager.py` → MODIFY (validation anti-patterns)

### 🟡 Priorità MEDIA
- `src/application/gameplay_controller.py` → AUDIT + possibile MODIFY
- `src/application/options_controller.py` → AUDIT
- `src/application/dialog_manager.py` → AUDIT

### 🟢 Priorità BASSA
- `docs/ARCHITECTURE.md` → UPDATE/CREATE
- `README.md` → UPDATE
- `CHANGELOG.md` → UPDATE (v2.1 entry)

## 🛠 Checklist Implementazione (6 Commit Atomici)

### Commit 1: Audit e Analisi
- [ ] Search globale `wx.CallAfter` in tutti i file
- [ ] Search globale `CallAfter` (senza wx. prefix)
- [ ] Categorizzare per contesto (UI transitions vs altro)
- [ ] Identificare inconsistenze pattern
- [ ] Documentare findings per commit successivi
- [ ] **NO CODE CHANGES** - solo analisi

**Commit Message Template**:
```
docs(v2.1): audit complete codebase for wx.CallAfter usage patterns
```

### Commit 2: Validazione test.py
- [ ] Verificare TUTTE le transizioni usano `self.app.CallAfter()`
- [ ] Aggiungere commenti header pattern-explaining:
  ```python
  # CRITICAL PATTERN (v2.0.9): Use self.app.CallAfter() for deferred UI transitions
  # Reason: wx.CallAfter() depends on wx.GetApp() which can return None
  # Direct instance method ensures reliability
  ```
- [ ] Aggiornare docstrings metodi con version history:
  - `show_abandon_game_dialog()`
  - `handle_game_ended()`
  - `_handle_game_over_by_timeout()`
  - `_safe_abandon_to_menu()`
  - `_safe_decline_to_menu()`
  - `_safe_timeout_to_menu()`
- [ ] **NO LOGIC CHANGES** - solo documentazione

**Commit Message Template**:
```
refactor(v2.1): validate and document deferred UI pattern in test.py
```

### Commit 3: Validazione view_manager.py
- [ ] Verificare ASSENZA di `wx.SafeYield()` (rimosso v2.0.8)
- [ ] Aggiungere/aggiornare commenti inline:
  ```python
  # NO wx.SafeYield() - Hide() and Show() are synchronous operations
  # SafeYield causes RuntimeError (nested event loop) - removed v2.0.8
  ```
- [ ] Aggiornare docstring `show_panel()` con note architetturali
- [ ] **NO LOGIC CHANGES**

**Commit Message Template**:
```
refactor(v2.1): validate ViewManager panel swap pattern consistency
```

### Commit 4: Audit Application Layer
- [ ] Audit `gameplay_controller.py` per `wx.CallAfter`
- [ ] Audit `options_controller.py` per `wx.CallAfter`
- [ ] Audit `dialog_manager.py` per `wx.CallAfter`
- [ ] Se trovato in contesto UI → sostituire con `self.app.CallAfter()`
- [ ] Se trovato in altro contesto → documentare e valutare
- [ ] Aggiungere commenti esplicativi dove applicabile

**Commit Message Template**:
```
refactor(v2.1): ensure deferred UI pattern consistency in application layer
```

### Commit 5: Documentazione Architetturale
- [ ] Creare/aggiornare sezione in `docs/ARCHITECTURE.md`:
  - "Deferred UI Transitions Pattern"
  - Decision tree: quando usare `self.app.CallAfter()`
  - Best practices con esempi codice
  - Anti-patterns da evitare (wx.CallAfter, wx.SafeYield)
- [ ] Aggiornare `README.md` con riferimenti pattern
- [ ] Link a version history rilevante

**Commit Message Template**:
```
docs(v2.1): add architectural documentation for deferred UI pattern
```

### Commit 6: Aggiornamento CHANGELOG e README
- [ ] Aggiungere sezione completa v2.1 in `CHANGELOG.md`:
  - Tutti i commit precedenti con dettagli
  - Release highlights
  - Breaking changes: NONE (internal refactoring)
- [ ] Aggiornare `README.md` versione corrente
- [ ] Incrementare version number a 2.1

**Commit Message Template**:
```
chore(release): prepare v2.1 - Timer Strict Mode system integration
```

## ✅ Criteri di Completamento

L'implementazione v2.1 è completa quando:

### Tecnico
- [ ] Zero istanze `wx.CallAfter()` in contesti UI transition
- [ ] Tutte transizioni UI usano `self.app.CallAfter()`
- [ ] Nessun `wx.SafeYield()` nel codebase
- [ ] Documentazione completa e aggiornata
- [ ] Consistency verificata in tutti i layer

### Funzionale
- [ ] Tutte transizioni UI funzionano senza crash
- [ ] Nessun hang o nested event loop
- [ ] Timer STRICT mode termina partita correttamente
- [ ] ESC abandon game funziona in tutti i contesti
- [ ] Victory/Defeat rematch flow robusto

### Qualitativo
- [ ] Codice più leggibile e manutenibile
- [ ] Pattern architetturale chiaro e consistente
- [ ] Commenti inline esplicativi ovunque
- [ ] Docstrings complete con version history
- [ ] Documentazione tecnica accessibile

## 📝 Aggiornamenti Obbligatori

- [x] README.md (commit 5 e 6)
- [x] CHANGELOG.md (commit 6 - entry completa v2.1)
- [x] ARCHITECTURE.md (commit 5 - nuovo/aggiornato)
- [x] Version increment: MINOR (2.0.9 → 2.1)
  - Rationale: Refactoring interno estensivo + documentazione
  - NO breaking changes
  - Mantiene backward compatibility

## 🧪 Testing Manuale Richiesto

Dopo OGNI commit, testare scenari critici:

### Scenario 1: ESC Abandon Game
```
1. python test.py
2. Nuova Partita
3. ESC → Conferma "Sì"
Expected: Menu appare istantaneamente, nessun crash
```

### Scenario 2: Victory Decline Rematch
```
1. Completa partita (vittoria)
2. Dialog rematch → "No"
Expected: Menu appare istantaneamente
```

### Scenario 3: Timer STRICT Expiration
```
1. Abilita timer STRICT (se config disponibile)
2. Lascia scadere timer
Expected: Menu appare automaticamente dopo timeout
```

## 📌 Note Importanti

### Pattern da Seguire Rigorosamente
```python
# ✅ CORRECT - Direct instance method
self.app.CallAfter(self._deferred_callback)

# ❌ WRONG - Global function (wx.GetApp() lookup)
wx.CallAfter(self._deferred_callback)

# ❌ WRONG - Causes nested event loop crash
wx.SafeYield()
```

### Decision Tree
**Quando usare `self.app.CallAfter()`**:
- Tutte le transizioni UI (panel swaps)
- Tutti i callback differiti da event handlers
- Qualsiasi operazione che modifica lo stato UI da contesto asincrono

**Quando NON usare**:
- Operazioni sincrone dirette
- Logic pura senza side effects UI
- Calcoli e validazioni

### Common Pitfalls
1. NON usare `wx.CallAfter()` - sempre `self.app.CallAfter()`
2. NON aggiungere `wx.SafeYield()` - causa nested loops
3. NON chiamare panel swap direttamente da event handler
4. SEMPRE resettare state prima di show_panel()

## 🔗 Link Riferimenti Rapidi

- Piano Completo: `docs/IMPLEMENTATION_TIMER_STRICT_MODE_SYSTEM_v2.1.md`
- ARCHITECTURE: `docs/ARCHITECTURE.md` (da creare/aggiornare)
- Version History: v2.0.3 → v2.0.9 documentata nel piano
- Branch: `copilot/remove-pygame-migrate-wxpython`

---

**Fine TODO - Consultare sempre il piano completo per dettagli tecnici**
