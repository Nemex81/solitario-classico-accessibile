### Piano di Correzione Incoerenze Documentazione/Codice (Correction Plan)

### Obiettivo
Allineare istruzioni operative, documentazione tecnica e codice reale del progetto, eliminando le incoerenze rilevate su architettura, logging, API docs, policy toolchain e controlli automatici.

### Ambito
- File di governance e istruzioni: `.github/copilot-instructions.md`
- Documentazione tecnica: `docs/API.md`, `docs/ARCHITECTURE.md`, `docs/TESTING.md`, `CHANGELOG.md`
- Configurazioni qualità: `mypy.ini`, `pytest.ini`, `.pre-commit-config.yaml`
- Codice con violazioni note: `src/domain/**`, `src/infrastructure/ui/wx_frame.py`, `src/infrastructure/storage/score_storage.py`

---

## Stato attuale (sintesi)

### Coerenze confermate
- `ProfileService.create_profile(name, is_guest)` presente e usata coerentemente.
- Gestione `EndReason.VICTORY` / `EndReason.VICTORY_OVERTIME` implementata.
- Dualità contatori pescata (`draw_count` e `stock_draw_count`) presente.
- Uso di `pile.get_card_count()` al posto di `pile.count()` nel codice corrente.

### Incoerenze da correggere
- Regole architetturali dichiarate come “strict” ma violate nel codice (Domain con dipendenze Infrastructure).
- Regola “no wx fuori infrastructure.ui” non allineata allo stato reale.
- Regola “mai print” violata in runtime.
- Drift documentale in `docs/API.md` e `docs/ARCHITECTURE.md`.
- Policy di verifica (mypy/coverage/versione Python) non uniforme tra istruzioni e config reali.

---

## Strategia di correzione

### Fase 1 — P0 (Bloccanti)

1. Allineamento API immediato
- Aggiornare `docs/API.md` per:
  - `ProfileService.ensure_guest_profile` con return type `bool`.
  - Terminologia overtime coerente con formatter reale.
- Output atteso: nessun mismatch firma/ritorno tra API docs e codice.

2. Decisione architetturale esplicita (strict vs transitional)
- Definire una decisione ufficiale:
  - Opzione A: mantenere regola strict e pianificare refactor graduale.
  - Opzione B: dichiarare regola transitional con debt tracking.
- Aggiornare in modo coerente `.github/copilot-instructions.md` e `docs/ARCHITECTURE.md`.
- Output atteso: nessuna contraddizione tra regole dichiarate e stato attuale.

3. Rimozione `print()` runtime
- Sostituire i `print()` noti con `game_logger` semantico in:
  - `src/infrastructure/ui/wx_frame.py`
  - `src/infrastructure/storage/score_storage.py`
- Output atteso: zero `print(` nel codice di produzione (esclusi eventuali script esplicitamente autorizzati).

### Fase 2 — P1 (Consolidamento)

4. Pulizia `docs/ARCHITECTURE.md`
- Correggere path/simboli obsoleti, riallineare struttura cartelle e riferimenti layer.
- Verificare riferimenti a file realmente esistenti in `src/`.
- Output atteso: documentazione architetturale navigabile e aderente al repository.

5. Uniformare policy qualità/toolchain
- Portare a coerenza:
  - Versione Python (`pyproject.toml`, `mypy.ini`, istruzioni).
  - Target coverage e gate (`pytest.ini`, docs testing, istruzioni).
- Output atteso: una sola fonte di verità per versioning e quality gate.

### Fase 3 — P2 (Prevenzione regressioni)

6. Automazione enforcement regole
- Estendere `.pre-commit-config.yaml` (o CI) con controlli minimi:
  - ban `print()` in `src/`
  - check coerenza docs/API su firme pubbliche ad alto rischio
  - quality gate coverage coerente
  - controllo import-layers (se adottata policy strict)
- Output atteso: incoerenze intercettate automaticamente prima del merge.

7. Miglioramento accessibilità coerente
- Audit dialog wx per uniformare acceleratori (`&`) e focus/chiusura ESC.
- Output atteso: comportamento tastiera e screen reader consistente.

---

## Piano operativo dettagliato

### Step 1 — Document baseline
- Creare ticket/issue per ciascun mismatch P0/P1/P2.
- Collegare ogni ticket a file e simboli precisi.

### Step 2 — Correzioni P0 a batch piccoli
- Batch A: solo `docs/API.md`.
- Batch B: solo logging (`print` -> `game_logger`).
- Batch C: allineamento regole architetturali in docs/istruzioni.

### Step 3 — Correzioni P1
- Aggiornare `docs/ARCHITECTURE.md` e policy toolchain.
- Eseguire verifica link e cross-reference docs.

### Step 4 — Hardening P2
- Aggiungere/aggiornare controlli pre-commit/CI.
- Eseguire dry-run locale dei controlli.

### Step 5 — Chiusura
- Aggiornare `CHANGELOG.md` sezione `[Unreleased]` con `Fixed`/`Changed`.
- Verifica finale “codice + docs + policy” sincronizzati.

---

## Matrice Priorità

- P0: drift API, contraddizioni regole core, `print()` in produzione.
- P1: pulizia architettura docs e uniformità toolchain.
- P2: automazione enforcement e rifiniture accessibilità.

---

## Verifica e accettazione

### Check tecnici
1. Ricerca `print(` in `src/` con risultato vuoto (salvo eccezioni deliberate e documentate).
2. Nessun mismatch tra firme pubbliche in `src/domain/services/profile_service.py` e `docs/API.md`.
3. `docs/ARCHITECTURE.md` senza riferimenti a file inesistenti.
4. Policy Python/coverage coerente tra:
   - `.github/copilot-instructions.md`
   - `mypy.ini`
   - `pytest.ini`
   - `docs/TESTING.md`

### Check qualità
- Test unitari/integration pass.
- Coverage conforme al gate scelto e dichiarato.
- Nessuna regressione su flussi principali di gioco/profili.

---

## Rischi e mitigazioni

- Rischio: bloccare sviluppo imponendo subito regole strict non ancora rifattorizzate.
  - Mitigazione: approccio transitional con milestone e debt register.

- Rischio: aggiornare docs senza enforce automatico.
  - Mitigazione: introdurre controlli pre-commit/CI nella Fase 3.

- Rischio: mismatch terminologico (overtime, naming API) ricorrente.
  - Mitigazione: creare glossario minimo in `docs/ARCHITECTURE.md` e usarlo in API docs.

---

## Deliverable finali
- Documento istruzioni aggiornato e non contraddittorio.
- API e Architecture docs allineate al codice reale.
- Logging runtime conforme (no `print()` in produzione).
- Pipeline qualità coerente e verificabile.
- Entry in `CHANGELOG.md` per tracciabilità delle correzioni.
