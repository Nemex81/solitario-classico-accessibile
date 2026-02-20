# Piano di Correzione API.md v3.2.2 (Finale)

**Obiettivo**: Correggere 3 refusi residui dall'audit manuale, non risolti da Copilot nella v3.1.3.

**Versione Target**: v3.2.2 (NO INCREMENT - mantieni versioning corrente)

**File Target**: `docs/API.md`

**Workflow**: Locale con Copilot in VS Code

---

## 🔍 Context: Audit Post-Copilot v3.1.3

Copilot ha corretto i 5 fix dichiarati (format_timer_stats_detailed signature, create_profile param, save/record return types, list_profiles naming), ma **ha ignorato o parzialmente processato** le 3 correzioni aggiuntive segnalate dall'audit manuale:

1. **`ensure_guest_profile()` return type** → Rimasto `-> None` (corretto: `-> bool`)
2. **`record_session` param name** → Rimasto `outcome` (corretto: `session`)
3. **`format_end_reason(VICTORY_OVERTIME)` esempio** → Spostato in nuova sezione con valore ancora sbagliato `"Vittoria in overtime"` (corretto: `"Vittoria (oltre tempo)"`)

---

## 📋 Correzioni da Applicare

### FIX 1: `ensure_guest_profile()` return type

**Linea**: ~1325 (sezione ProfileService)  
**Severity**: 🔴 CRITICAL (consumatori non possono gestire errori)

**Da:**
```markdown
#### `ensure_guest_profile() -> None`

Assicura che il profilo guest (`profile_000`) esista, creandolo se necessario.

**Esempio:**
```python
profile_service.ensure_guest_profile()
# Ora profile_000 esiste sicuramente
```
```

**A:**
```markdown
#### `ensure_guest_profile() -> bool`

Assicura che il profilo guest (`profile_000`) esista, creandolo se necessario.

**Ritorna:**
- `True` se il profilo guest esiste o è stato creato con successo
- `False` se la creazione fallisce (es. errore I/O)

**Esempio:**
```python
success = profile_service.ensure_guest_profile()
if not success:
    # Handle error: retry, fallback, notify user
    log.error("Failed to ensure guest profile")
```
```

**Rationale**:  
Il codice reale (`src/domain/services/profile_service.py` line ~260) ritorna `bool`:
```python
def ensure_guest_profile(self) -> bool:
    # ...
    return True  # or False on failure
```

Documentare `-> None` è fuorviante per consumatori che vogliono gestire errori di creazione.

---

### FIX 2: `record_session` nome parametro

**Linea**: ~1220 (firma metodo) + ~1250 (esempio)  
**Severity**: 🟡 MEDIUM (rompe keyword arguments)

**Da (firma):**
```markdown
#### `record_session(outcome: SessionOutcome) -> bool`
```

**A (firma):**
```markdown
#### `record_session(session: SessionOutcome) -> bool`
```

**Da (esempio):**
```python
outcome = SessionOutcome.create_new(
    profile_id=profile_service.active_profile.profile_id,
    end_reason=EndReason.VICTORY,
    is_victory=True,
    elapsed_time=180.5,
    # ...
)

success = profile_service.record_session(outcome)
```

**A (esempio):**
```python
session = SessionOutcome.create_new(
    profile_id=profile_service.active_profile.profile_id,
    end_reason=EndReason.VICTORY,
    is_victory=True,
    elapsed_time=180.5,
    # ...
)

success = profile_service.record_session(session)
```

**Rationale**:  
Il parametro reale si chiama `session` (`src/domain/services/profile_service.py` line 154):
```python
def record_session(self, session: SessionOutcome) -> bool:
```

Usare `outcome` nell'esempio funziona per chiamate **posizionali** ma rompe **keyword arguments**:
```python
# ❌ ERRORE con documentazione attuale
profile_service.record_session(outcome=obj)
# → TypeError: got unexpected keyword argument 'outcome'

# ✅ CORRETTO con parametro reale
profile_service.record_session(session=obj)
```

---

### FIX 3: `format_end_reason(VICTORY_OVERTIME)` esempio output

**Linea**: ~938 (sezione Enum e Costanti → EndReason → blocco esempio VICTORY_OVERTIME)  
**Severity**: 🟢 LOW (confonde utenti NVDA ma non rompe codice)

**Da:**
```python
# Formattazione automatica
formatter.format_end_reason(outcome.end_reason)
# Output: "Vittoria in overtime"
```

**A:**
```python
# Formattazione automatica
formatter.format_end_reason(outcome.end_reason)
# Output: "Vittoria (oltre tempo)"
```

**Rationale**:  
Il dizionario in `src/presentation/formatters/stats_formatter.py` (line 141) mappa:
```python
EndReason.VICTORY_OVERTIME: "Vittoria (oltre tempo)",
```

L'output TTS reale è `"Vittoria (oltre tempo)"`, non `"Vittoria in overtime"`. L'esempio documentale deve rispecchiare il testo che gli utenti NVDA ascoltano realmente.

**Nota storica**: Copilot nel commit precedente ha corretto un inline comment errato nella sezione helper methods, ma ha **aggiunto** questo nuovo blocco esempio con lo stesso valore sbagliato → refuso spostato, non risolto.

---

## 🎯 Istruzioni per Copilot (VS Code)

### Opzione A: Copilot Chat (Consigliata)

Apri Copilot Chat in VS Code e incolla:

```
Applica le seguenti 3 correzioni al file docs/API.md:

FIX 1 (line ~1325):
- Sostituisci `ensure_guest_profile() -> None` con `-> bool`
- Aggiungi dopo la descrizione:
  **Ritorna:**
  - `True` se il profilo guest esiste o è stato creato con successo
  - `False` se la creazione fallisce (es. errore I/O)
- Sostituisci esempio:
  DA: profile_service.ensure_guest_profile()
  A: success = profile_service.ensure_guest_profile()
      if not success:
          log.error("Failed to ensure guest profile")

FIX 2 (line ~1220 e ~1250):
- Sostituisci `record_session(outcome: SessionOutcome)` con `(session: SessionOutcome)`
- Nell'esempio sotto, sostituisci tutte le occorrenze di variabile `outcome` con `session`

FIX 3 (line ~938):
- Sostituisci `# Output: "Vittoria in overtime"` con `# Output: "Vittoria (oltre tempo)"`

NON modificare altro. NON incrementare versione. Solo questi 3 fix.
```

---

### Opzione B: Copilot Edits (Inline)

1. Apri `docs/API.md` in VS Code
2. Vai a line ~1325 → seleziona blocco `ensure_guest_profile()`
3. Prompt Copilot: *"Cambia return type a bool e aggiungi sezione Ritorna con True/False. Esempio con success variable e error handling."*
4. Vai a line ~1220 → seleziona firma `record_session`
5. Prompt Copilot: *"Cambia parametro outcome in session"*
6. Vai a line ~1250 → seleziona esempio `record_session`
7. Prompt Copilot: *"Rinomina variabile outcome in session in tutto l'esempio"*
8. Vai a line ~938 → seleziona commento output
9. Prompt Copilot: *"Cambia output a: Vittoria (oltre tempo)"*

---

### Opzione C: Manuale (Più Veloce)

Se Copilot non interpreta correttamente, applica direttamente:
- Cerca `ensure_guest_profile() -> None` → sostituisci con blocco FIX 1 completo
- Cerca `record_session(outcome:` → sostituisci con `session:`
- Cerca tutte le occorrenze di `outcome = SessionOutcome.create_new` dopo `record_session` → cambia in `session`
- Cerca `"Vittoria in overtime"` nel blocco EndReason → sostituisci con `"Vittoria (oltre tempo)"`

---

## ✅ Validation Checklist

Dopo applicazione, verifica in VS Code:

**Search (CTRL+F) in docs/API.md:**

1. Cerca `ensure_guest_profile() -> bool` → deve trovare 1 match (line ~1325)
2. Cerca `record_session(session:` → deve trovare 1 match (line ~1220)
3. Cerca `Vittoria (oltre tempo)` → deve trovare ≥2 match (helper + EndReason example)

**Verifica residui errati rimossi:**

4. Cerca `ensure_guest_profile() -> None` → deve trovare 0 match
5. Cerca `record_session(outcome:` → deve trovare 0 match
6. Cerca `"Vittoria in overtime"` → deve trovare 0 match

**Verifica versione intatta:**

7. Cerca `Versione API Corrente: v3.2.2` → deve esistere in header (~line 7)
8. Cerca `Document Version: 3.2.2` → deve esistere in footer (~line 1450)

**Success Criteria:**
- ✅ 3/3 fix applicati correttamente
- ✅ 3/3 residui errati rimossi
- ✅ Versione rimasta v3.2.2 (NO increment)

---

## 📊 Verifica Cross-Reference (Opzionale ma Consigliata)

Prima di applicare, conferma signature reali:

**In VS Code, apri e cerca:**

1. File: `src/domain/services/profile_service.py`  
   Cerca: `def ensure_guest_profile`  
   Expected: `-> bool` (~line 260)

2. File: `src/domain/services/profile_service.py`  
   Cerca: `def record_session`  
   Expected: `session: SessionOutcome` (~line 154)

3. File: `src/presentation/formatters/stats_formatter.py`  
   Cerca: `VICTORY_OVERTIME:`  
   Expected: `"Vittoria (oltre tempo)"` (~line 141)

Se uno dei 3 non matcha → **STOP**, il codice è stato modificato, rivalida piano.

---

## 📦 Deliverables

**File modificato:**
- `docs/API.md` (3 sezioni modificate: ~8 linee totali)

**Versioning:**
- **NO increment**: rimane `v3.2.2`
- **NO nuovo changelog**: queste sono correzioni post-implementazione v3.2.2

**Testing:**
- Validation checklist (8 check sopra)
- Preview API.md in VS Code Markdown preview

---

## 🚀 Workflow Consigliato

1. ✅ **Salva questo piano** (già fatto se stai leggendo)
2. 🔧 **Applica fix** (Opzione A/B/C sopra)
3. ✅ **Esegui validation** (8-point checklist)
4. 💾 **Stage e commit** (quando pronto per push)

**Stima totale**: 3-5 minuti (2 min Copilot Chat + 3 min validation).

---

## 📝 Note per Copilot

- "Solo questi 3 fix, non modificare altro"
- "Non incrementare versione"
- "Non aggiungere changelog"
- "Mantieni formattazione markdown esistente"
