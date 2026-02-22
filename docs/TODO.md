📋 TODO – Fix Pre-Merge Branch → main (v3.3.0)
Branch: sistema-log-categorizzati
Tipo: FIX
Priorità: HIGH
Stato: IN PROGRESS

---

📖 Riferimento Documentazione

Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:
`docs/2 - projects/PLAN_premerge_fixes_v3.3.0.md`

Questo file TODO è solo un sommario operativo da consultare e aggiornare durante ogni fase
dell'implementazione. Il piano completo contiene analisi, architettura, edge case e dettagli
tecnici — incluse le analisi di incoerenza e la fixture corretta per i test.

---

🤖 Istruzioni per Copilot Agent

Implementare le modifiche in modo **incrementale** su più commit atomici e logici.

**Workflow per ogni fase:**

1. **Leggi questo TODO** → Identifica il prossimo item da implementare
2. **Consulta piano completo** → Rivedi dettagli tecnici e edge case della fase
3. **Implementa modifiche** → Codifica solo la fase corrente (scope limitato)
4. **Commit atomico** → Messaggio conventional con scope chiaro
5. **Aggiorna questo TODO** → Spunta la checkbox completata
6. **RIPETI** → Passa all'item successivo (torna al punto 1)

⚠️ **REGOLE FONDAMENTALI:**

- ✅ **Un commit per task logico** (no mega-commit con tutto)
- ✅ **Dopo ogni commit**: aggiorna questo TODO spuntando checkbox
- ✅ **Prima di ogni task**: rileggi sezione pertinente nel piano completo
- ✅ **Approccio sequenziale**: il Pre-req Task 3 deve precedere i test
- ❌ **NO eseguire Task 3 senza aver applicato il Pre-req** (i test fallirebbero con TypeError)

---

🎯 Obiettivo Implementazione

Risolvere 4 problemi bloccanti o di qualità prima del merge del branch
`sistema-log-categorizzati` su `main` (release v3.3.0):

- Eliminare il conflitto di merge non risolto in `CHANGELOG.md` (marker Git ancora presenti)
- Allineare le docstring di `categorized_logger.py` alla versione corretta (`v3.3.0`)
- Abilitare la testabilità del wrapper `setup_logging()` aggiungendo il parametro `logs_dir`
- Creare i test unitari mancanti per il nuovo sistema logging categorizzato

---

📂 File Coinvolti

- `CHANGELOG.md` → MODIFY (risoluzione conflitto + pulizia testo v3.2.0 + link footer)
- `src/infrastructure/logging/categorized_logger.py` → MODIFY (docstring v3.2.0 → v3.3.0)
- `src/infrastructure/logging/logger_setup.py` → MODIFY (aggiungere param `logs_dir`)
- `tests/infrastructure/test_categorized_logger.py` → CREATE (5 test unitari CI-safe)

---

🛠 Checklist Implementazione

**Pre-requisito Task 3 — Firma setup_logging() (🔴 BLOCCANTE per i test)**

- [ ] Aggiungere `logs_dir: Path = LOGS_DIR` alla firma di `setup_logging()` in `logger_setup.py`
- [ ] Propagare `logs_dir` nella chiamata interna a `setup_categorized_logging()`

**Task 1 — Risoluzione conflitto CHANGELOG.md (🔴 BLOCCANTE)**

- [ ] Rimuovere i marker di conflitto (`<<<`, `===`, `>>>`) dalla sezione `[Unreleased]`
- [ ] Mantenere il blocco HEAD (versione più dettagliata)
- [ ] Rimuovere il testo `` (`v3.2.0` infrastruttura) `` dal bullet logging nel blocco HEAD
- [ ] Aggiornare link footer: aggiungere `[3.3.0]`, modificare `[Unreleased]` → al momento del merge
- [ ] Verifica `grep -n "^<<<\|^===\|^>>>" CHANGELOG.md` → 0 risultati

**Task 2 — Docstring versione categorized_logger.py (🟡 MINORE)**

- [ ] Sostituire `v3.2.0` → `v3.3.0` nel docstring del modulo (riga ~32)
- [ ] Sostituire `v3.2.0` → `v3.3.0` nel docstring di `setup_categorized_logging()` (riga ~88)

**Pre-requisito Task 3 — Firma setup_logging() (🔴 BLOCCANTE per i test)**

- [ ] Aggiungere `logs_dir: Path = LOGS_DIR` alla firma di `setup_logging()` in `logger_setup.py`
- [ ] Propagare `logs_dir` nella chiamata interna a `setup_categorized_logging()`

**Task 3 — Test unitari logging categorizzato (🟠 QUALITY)**

- [ ] Creare `tests/infrastructure/test_categorized_logger.py`
- [ ] Fixture `reset_logging`: cleanup sia prima che dopo ogni test (`_cleanup()` pre + post yield)
- [ ] `test_setup_creates_log_files_for_all_categories`
- [ ] `test_setup_idempotent_no_duplicate_handlers`
- [ ] `test_setup_sets_propagate_false_on_all_category_loggers`
- [ ] `test_setup_logging_wrapper_creates_same_files`
- [ ] `test_setup_suppresses_external_library_loggers`

**Testing**

- [ ] `pytest tests/infrastructure/test_categorized_logger.py -v` → 5 passed
- [ ] Smoke test `pytest -m "not gui"` senza regressioni
- [ ] Nessuna regressione su test esistenti

---

✅ Criteri di Completamento

L'implementazione è considerata completa quando:

- [ ] Tutte le checklist sopra sono spuntate
- [ ] `CHANGELOG.md` non contiene marker di conflitto
- [ ] `pytest tests/infrastructure/test_categorized_logger.py -v` → 5 passed
- [ ] `pytest -m "not gui"` → 0 regressioni
- [ ] PR aperta su `main` con titolo `feat: sistema logging categorizzato v3.3.0 (#XX)`

---

📝 Aggiornamenti Obbligatori a Fine Implementazione

- [ ] `CHANGELOG.md` link footer aggiornato con `[3.3.0]` e nuovo `[Unreleased]`
- [ ] Commit con messaggi convenzionali (vedi piano per i messaggi suggeriti per ogni task)
- [ ] PR body: linkare `PLAN_premerge_fixes_v3.3.0.md` e `DESIGN_categorized_logging.md`
- [ ] Aggiornare stato di questo TODO → `DONE`

---

📌 Note

- L'ordine di esecuzione è vincolante: **Task 1 e Task 2 sono indipendenti tra loro**
  ma il **Pre-req Task 3 deve sempre precedere Task 3**.
- Il pre-requisito (firma `setup_logging()`) deve essere committato separatamente
  dal file di test per mantenere la tracciabilità degli atomic commits.
- Zero import da `wx` nel file di test: è CI-safe senza Xvfb e senza `@pytest.mark.gui`.
- La fixture `reset_logging` usa `autouse=True` con cleanup pre+post yield per garantire
  isolamento anche con esecuzione in ordine arbitrario (`pytest-randomly`).
- Stima effort totale: ~35-45 minuti (dettaglio in piano completo, sezione "Stima effort").

---

**Fine.**

Snello, consultabile in 30 secondi, zero fronzoli.
Il documento lungo (`PLAN_premerge_fixes_v3.3.0.md`) è la fonte di verità tecnica.
Questo è il cruscotto operativo.
