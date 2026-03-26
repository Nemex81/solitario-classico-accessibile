---
feature: E2E Resilience — Gate semantici, rollback procedure, coverage SOT
agent: Agent-Plan
status: DRAFT
version: v1.11.0
date: 2026-03-26
---

# Plan: E2E Resilience v1.11.0

## Executive Summary

Rafforzamento del ciclo E2E del framework su quattro aree operative, escludendo esplicitamente la gestione timeout/stallo dei subagenti.

1. **Gate semantici mancanti tra Analyze, Design e Plan**: l'Orchestrator verifica struttura documentale ma non la qualita minima dell'input ne lo stato richiesto per avanzare.
2. **Smoke test CLI non esplicitato**: gli script di gate esistono, ma l'Orchestrator non verifica in apertura che siano realmente disponibili nell'ambiente corrente.
3. **Rollback E2E non definito**: manca una procedura standard quando una fase successiva fallisce dopo commit parziali gia creati.
4. **Coverage threshold senza source of truth unica**: il valore 85% e duplicato in piu file operativi e documentali, con rischio di drift.

**Obiettivo:** rendere il ciclo E2E piu robusto e coerente senza introdurre nuove feature di prodotto, centralizzando la soglia coverage, formalizzando i gate semantici, aggiungendo una procedura di rollback e inserendo un controllo bootstrap leggero sugli script CLI.

**Versione target:** v1.11.0  
**Priorita:** Alta  
**Scope escluso:** nessuna implementazione di timeout o watchdog per subagenti in questa iterazione.

---

## Problema e Obiettivo

### Problemi confermati o riformulati

1. **Gate semantici assenti**
   - I findings di Agent-Analyze non hanno un gate minimo di completezza prima della Fase 2.
   - Il DESIGN non viene verificato tecnicamente come `REVIEWED` prima di avviare Agent-Plan.
   - Il PLAN non ha una precondizione formale collegata allo stato del DESIGN approvato.

2. **Prerequisiti CLI non verificati in bootstrap**
   - `validate_gates.py` e `detect_agent.py` esistono e funzionano.
   - Manca pero un check iniziale esplicito nell'Orchestrator che blocchi subito il workflow se i gate CLI non sono disponibili.

3. **Rollback E2E assente**
   - Il framework gestisce retry di subagente ma non il caso "commit gia fatto, fase successiva fallita".
   - Non esiste una procedura condivisa per scegliere tra revert, reset soft o stop operativo.

4. **Coverage threshold duplicata**
   - Il valore `85` compare in Orchestrator, Agent-Validate, instructions, CI e script locali.
   - `pyproject.toml` e il luogo naturale per diventare la source of truth, ma oggi non governa il `fail_under`.

### Obiettivi strategici

1. Introdurre una **source of truth unica** per la coverage minima.
2. Formalizzare **gate semantici minimi** tra Analyze, Design e Plan.
3. Definire una **procedura rollback/revert** usabile nel ciclo E2E.
4. Aggiungere uno **smoke test CLI** leggero all'avvio dell'Orchestrator.
5. Lasciare fuori da questa iterazione i timeout dei subagenti, per evitare complessita prematura.

---

## File coinvolti

### CREATE

- `.github/skills/semantic-gate.skill.md` — criteri minimi per findings strutturati e enforcement stati DESIGN/PLAN.
- `.github/skills/rollback-procedure.skill.md` — procedura standard di revert/rollback E2E.

### MODIFY

- `pyproject.toml`
  - aggiungere `fail_under = 85` nella configurazione coverage.

- `.github/agents/Agent-Orchestrator.md`
  - aggiungere bootstrap check CLI in Fase 0.
  - introdurre gate semantico su findings in Fase 1.
  - aggiungere precondizione DESIGN `REVIEWED` prima della Fase 3.
  - referenziare `semantic-gate.skill.md` e `rollback-procedure.skill.md`.
  - documentare il comportamento da seguire in caso di fallimento post-commit.

- `.github/agents/Agent-Git.md`
  - aggiungere procedura operativa di revert con conferma esplicita.

- `.github/agents/Agent-Validate.md`
  - chiarire che la soglia minima e configurata centralmente in `pyproject.toml`.

- `.github/skills/git-execution.skill.md`
  - estendere la matrice autorizzazioni con operazioni di revert/rollback per Agent-Git.

- `.github/skills/README.md`
  - aggiungere `semantic-gate.skill.md` e `rollback-procedure.skill.md`.
  - aggiornare la tabella agenti-skill.

- `.github/instructions/workflow-standard.instructions.md`
  - rimuovere il flag coverage hardcoded dai comandi operativi, demandando la soglia alla configurazione centrale.

- `.github/agents/Agent-Code.md`
  - allineare il comando coverage alla source of truth centralizzata se oggi e hardcoded.

- `.github/workflows/ci.yml`
  - rimuovere `--cov-fail-under=85` se la soglia viene letta da configurazione coverage.

- `scripts/ci-local-validate.py`
  - rimuovere la soglia hardcoded dai comandi pytest.

- `scripts/create-project-files.py`
  - aggiornare eventuali template generati che riportano la soglia coverage in forma hardcoded.

- `.github/copilot-instructions.md`
  - mantenere il riferimento al target coverage, ma allinearlo alla source of truth in `pyproject.toml`.

- `.github/AGENTS.md`
  - aggiornare l'overview coverage/gate per riflettere la nuova SOT e le nuove skill.

### DELETE

- Nessuna eliminazione file prevista.

---

## Fasi sequenziali

### Fase 1 — Coverage Single Source of Truth

**Obiettivo:** centralizzare la soglia minima coverage in `pyproject.toml` e rimuovere il drift operativo.

Sequenza:

1. Aggiorna `pyproject.toml` con `fail_under = 85`.
2. Rimuovi `--cov-fail-under=85` dai comandi operativi in CI e validazione locale.
3. Aggiorna le instructions e gli agenti che oggi riportano la soglia come parametro CLI hardcoded.
4. Allinea la documentazione interna spiegando che il valore resta 85%, ma la fonte di verita e `pyproject.toml`.

Commit suggerito:
`chore(framework): centralizza coverage fail_under in pyproject.toml`

### Fase 2 — Gate Semantici Analyze → Design → Plan

**Obiettivo:** evitare avanzamenti formalmente validi ma semanticamente deboli.

Sequenza:

1. Crea `.github/skills/semantic-gate.skill.md` con:
   - sezioni minime attese nei findings;
   - criteri minimi di completezza;
   - controllo stato `REVIEWED` del DESIGN prima del planning;
   - controllo stato `READY` del PLAN prima della codifica.
2. Aggiorna `.github/agents/Agent-Orchestrator.md` per applicare la skill in Fase 1, 2 e 3.
3. Esplicita il blocco del workflow quando i prerequisiti semantici non sono rispettati.
4. Aggiorna `.github/skills/README.md` con la nuova skill.

Commit suggerito:
`docs(framework): aggiungi gate semantici tra analyze design e plan`

### Fase 3 — Procedura Rollback / Revert E2E

**Obiettivo:** gestire in modo controllato i fallimenti dopo commit parziali.

Sequenza:

1. Crea `.github/skills/rollback-procedure.skill.md`.
2. Aggiungi in `.github/agents/Agent-Orchestrator.md` una sezione dedicata al caso "fase successiva fallita dopo commit".
3. Estendi `.github/agents/Agent-Git.md` con una operazione di revert esplicita.
4. Allinea `.github/skills/git-execution.skill.md` e `.github/skills/README.md`.

Commit suggerito:
`docs(framework): definisci procedura rollback e revert e2e`

### Fase 4 — Smoke Test CLI all'avvio Orchestrator

**Obiettivo:** fallire presto e in modo leggibile se gli script di gate non sono disponibili.

Sequenza:

1. Aggiungi Step 0 in Fase 0 di `.github/agents/Agent-Orchestrator.md`.
2. Esegui `python scripts/validate_gates.py --help` come smoke test senza effetti collaterali.
3. In caso di errore, blocca il workflow con messaggio operativo chiaro.

Commit suggerito:
`docs(framework): aggiungi smoke test cli in bootstrap orchestrator`

---

## Test Plan

1. Verifica configurazione coverage:
   - `pytest -m "not gui" --cov=src -q`
   - confermare che il fail under sia letto da configurazione e non da flag CLI.

2. Verifica gate documentali e semantici:
   - `python scripts/validate_gates.py --help`
   - `python scripts/validate_gates.py --check-all`
   - grep mirato su `Agent-Orchestrator.md` per i nuovi riferimenti a `semantic-gate` e `rollback-procedure`.

3. Verifica documentazione framework:
   - controllo link e riferimenti skill in `.github/skills/README.md`, `.github/AGENTS.md`, `.github/copilot-instructions.md`.

4. Verifica rollback documentato:
   - presenza di percorso esplicito in `Agent-Orchestrator.md` e `Agent-Git.md`.

---

## Dependencies

- Fase 1 puo essere implementata indipendentemente dalle altre ed e la migliore candidata per iniziare.
- Fase 2 dipende solo dalla creazione della nuova skill e dall'aggiornamento dell'Orchestrator.
- Fase 3 dipende da Agent-Git e dalla matrice `git-execution`.
- Fase 4 e indipendente e puo essere eseguita in parallelo a Fase 2 o a valle.

---

## Risk & Constraints

### Accessibilita

- Impatto nullo su UI runtime.
- I file Markdown devono restare leggibili da screen reader, con headings puliti e liste lineari.

### Compatibilita

- Nessuna rottura funzionale attesa se le modifiche restano documentali/configurative.
- La centralizzazione coverage richiede allineamento accurato tra CI, script e instructions per evitare divergenze temporanee.

### Vincoli espliciti

- **Escluso** dalla presente iterazione ogni meccanismo di timeout/stallo dei subagenti.
- Nessun file legacy viene eliminato; si aggiorna solo il coordinatore `docs/TODO.md`.

---

## Approvals & Validation

Prima dell'implementazione:

- [ ] Confermata l'esclusione del problema 6 dalla presente iterazione
- [ ] Confermato `pyproject.toml` come source of truth coverage
- [ ] Confermata l'introduzione delle nuove skill `semantic-gate` e `rollback-procedure`

Prima del commit finale di ciascuna fase:

- [ ] Nessun riferimento coverage hardcoded rimasto nei percorsi operativi target
- [ ] Orchestrator aggiornato con gate semantici e smoke test CLI
- [ ] Agent-Git aggiornato con procedura di revert esplicita
- [ ] Coordinatore `docs/TODO.md` allineato ai lavori attivi reali
