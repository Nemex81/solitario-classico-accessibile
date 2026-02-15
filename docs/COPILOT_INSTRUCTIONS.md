# 🤖 Copilot - Istruzioni Implementazione Scoring System v2.0

## 🎯 Obiettivo

Implementare il **Scoring System v2.0** per il progetto Solitario Accessibile.

Si tratta di una **reimplementazione completa** del sistema di punteggio con:
- Formula deterministico (order-independent)
- Config esterna JSON (no hardcoded)
- Victory bonus composite bilanciato
- Protezioni anti-exploit (abbandoni = 0 bonus)
- Rounding policy con safety invariants
- Accessibilità TTS con warnings configurabili

---

## 📚 Documentazione da Consultare

### Piano Completo (OBBLIGATORIO)
📝 **[docs/SCORING_SYSTEM_V2.md](docs/SCORING_SYSTEM_V2.md)**

Contiene:
- Formule matematiche complete
- Invarianti e constraint
- Test strategy dettagliata
- Rationale per ogni decisione
- Boundary conditions
- Esempi codice

⚠️ **Consulta SEMPRE questa specifica prima di codificare ogni commit.**

### TODO Operativo (Tracking)
✅ **[TODO_SCORING_V2.md](TODO_SCORING_V2.md)**

Contiene:
- Checklist spuntabili per ogni commit
- File da modificare
- Sub-task granulari
- Test critici richiesti
- Status commit

⚠️ **Aggiorna questo file spuntando i checkbox dopo ogni modifica completata.**

---

## 🔄 Workflow Incrementale

Segui questo processo per **ogni commit**:

### 1️⃣ Consulta Documentazione
```
1. Apri docs/SCORING_SYSTEM_V2.md
2. Leggi sezione relativa al commit corrente
3. Comprendi formule, invarianti, edge case
```

### 2️⃣ Consulta TODO
```
1. Apri TODO_SCORING_V2.md
2. Identifica commit da implementare (es. "Commit 1: Extend ScoreEventType")
3. Leggi checklist file coinvolti + sub-task
```

### 3️⃣ Implementa Codice
```
1. Modifica file indicati nel TODO
2. Implementa logica seguendo specifica in docs/SCORING_SYSTEM_V2.md
3. Scrivi/aggiorna test richiesti (inclusi test CRITICAL)
4. Run test: pytest tests/ -v
5. Verifica tutti test passano
```

### 4️⃣ Aggiorna TODO
```
1. Apri TODO_SCORING_V2.md
2. Spunta [x] tutti checkbox completati per questo commit
3. Aggiorna "Status commit X" da ❌ NOT STARTED a ✅ DONE
```

### 5️⃣ Commit
```
1. git add <files modificati>
2. git commit -m "<conventional commit message>"
   Esempio: "feat(scoring): implement STOCK_DRAW progressive penalty"
3. Verifica commit atomico e self-contained
```

### 6️⃣ Ripeti per Commit Successivo
```
Torna a step 1 per il commit successivo.
Ripeti fino a completare tutti 9 commit.
```

---

## 📌 Ordine Commit (9 totali)

### Phase 1: Core Scoring Logic
1. **Commit 1**: Extend ScoreEventType + update ScoringConfig
2. **Commit 2**: Implement STOCK_DRAW penalty progressive
3. **Commit 3**: Update time bonus (v2.0 values) + _safe_truncate()
4. **Commit 4**: Implement quality factors (time/move/recycle)
5. **Commit 5**: Implement composite victory bonus
6. **Commit 6**: Update calculate_final_score() + persist quality_multiplier

### Phase 2: Config Externalization
7. **Commit 7**: Create config JSON + loader
8. **Commit 8**: Integrate loader into GameEngine

### Phase 3: TTS Transparency
9. **Commit 9**: Implement formatters + warnings

---

## ⚠️ Regole Critiche

### 🔴 SEMPRE
- Consulta `docs/SCORING_SYSTEM_V2.md` prima di codificare
- Implementa test **CRITICAL** marcati nel TODO (boundary, safety, determinism)
- Verifica tutti test passano prima di committare
- Aggiorna TODO spuntando checkbox completati
- Commit atomici (un concetto logico per commit)
- Conventional commit messages (`feat`, `fix`, `test`, `refactor`)

### 🟢 MAI
- Saltare commit (seguire ordine 1→2→3...9)
- Committare codice con test falliti
- Modificare file non previsti nel TODO per quel commit
- Inventare logica non documentata in specifica
- Dimenticare di aggiornare TODO dopo implementazione

---

## ✅ Completamento

L'implementazione è completa quando:

- [ ] Tutti 9 commit completati
- [ ] Tutti checkbox in `TODO_SCORING_V2.md` spuntati
- [ ] Test coverage ≥95% su `ScoringService`
- [ ] Test deterministici (commutativity, bias) passano
- [ ] Nessuna regressione funzionale
- [ ] `CHANGELOG.md` aggiornato
- [ ] `README.md` aggiornato
- [ ] Version bumped a v2.6.0

---

## 🚀 Inizia Ora

**Prossimo step**:
```
1. Apri docs/SCORING_SYSTEM_V2.md → Leggi sezione "Implementation Plan > Commit 1"
2. Apri TODO_SCORING_V2.md → Leggi checklist "Commit 1: Extend ScoreEventType"
3. Inizia implementazione modificando src/domain/models/scoring.py
4. procedi in modo incrementale e implementando le fasi consecutivamente seguendo la codumentazione all'inizio di ogni fase.
```

**Buon lavoro!** 💪
