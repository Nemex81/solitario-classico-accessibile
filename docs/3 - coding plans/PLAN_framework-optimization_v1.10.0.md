---
type: plan
feature: Framework Optimization — Coerenza sistema documenti e protocolli Orchestrator
agent: Agent-Plan
status: COMPLETED
version: v1.10.0
date: 2026-03-26
---

# Plan: Framework Optimization v1.10.0

## Executive Summary

Consolidamento del sistema di gestione documenti e protocolli dell'Orchestratore per risolvere due problemi operativi:

1. **Conflitto naming:** `docs_manager.skill.md` prescrive una convenzione universale (`AAAA-MM-GG_slug.md`) che contraddice le convenzioni specifiche già implementate in `document-template.skill.md` (DESIGN_*, PLAN_*, ecc.)
2. **Mancanza di tracciamento stato macchina:** L'Orchestratore nella Fase 0 non ha un protocollo esplicito per riprendere sessioni interrotte; affida l'inferenza dello stato alle spunte dei TODO, che non cattura correttamente il caso in cui un PLAN sia in stato DRAFT ma senza TODO generato ancora.
3. **Gestione errori inconsistente:** Quando un subagente fallisce, l'Orchestratore ha solo istruzioni generiche ("riprova con contesto più dettagliato"). Non c'è una procedura standardizzata di retry e escalata.

**Obiettivo:** Allineare tre skill critiche (`docs_manager`, `error-recovery` new, protocolli Orchestratore) per garantire coerenza tra l'intenzione documentale (authority di naming) e l'implementazione operativa (referenze skill negli agenti).

**Branch:** `feature/framework-optimizer-v1.10.0`  
**Versione target:** v1.10.0  
**Priorità:** Alta (risolve incoerenze architetturali, non aggiunge features nuove)

---

## Problema e Obiettivo

### Stato attuale

1. **docs_manager.skill.md** (riga 51): "Convenzione naming file" prescrive format universale `AAAA-MM-GG_slug-descrittivo.md`
2. **document-template.skill.md**: definisce convenzioni specifiche per tipo (`DESIGN_<feature>.md`, `PLAN_<feature>_vX.Y.Z.md`)
3. **Skills/README.md tabella agenti-skills**: mostra che Agent-Design e Agent-Plan referenziano `document-template` ma NON `docs_manager`
4. **Agent-Orchestrator.md Fase 0**: legge TODO.md per inferire stato sessione; non ha protocollo esplicito per il caso "PLAN in DRAFT ma senza TODO task generato"
5. **Agent-Orchestrator.md**: referenzia `docs_manager` nelle regole invarianti (riga 100) ma non nella sezione "Riferimenti Skills"
6. **Error recovery**: Orchestratore ha solo "riprova con contesto più dettagliato"; nessuna skill di standardizzazione

### Conseguenze operative

- Agenti non sanno di dover aggiornare `docs/TODO.md` quando salvano DESIGN/PLAN (Agent-Design e Agent-Plan non referenziano `docs_manager`)
- Se un'operazione Agent-Analyze o Agent-Design fallisce, non c'è procedura standardizzata di retry — Orchestratore decide ad hoc
- Bootstrap documenti funziona ma la semantica del naming rimane ambigua fra "universale" vs "per-tipo"

### Obiettivi strategici

1. **Singola authority per naming:** `docs_manager.skill.md` dichiara esplicitamente la convenzion per ogni tipo di documento, con motivazione
2. **Coerenza routing:** Agent-Design, Agent-Plan e Orchestrator referenziano `docs_manager` e sanno aggiornare il coordinatore
3. **Ripresa sessione robusta:** Orchestratore Fase 0 ha protocollo esplicito per identificare stato tasks anche in assenza di TODO task (fallback a lettura DESIGN/PLAN stato)
4. **Error recovery standardizzato:** Skill `error-recovery.skill.md` definisce max 2 tentativi, formato escalata, regola di conferma

---

## File coinvolti

### CREATE

- `.github/skills/error-recovery.skill.md` — Procedura standardizzata retry + escalata (30 righe max)

### MODIFY

- `.github/skills/docs_manager.skill.md`:
  - Tabella naming (riga ~51): allinea convenzioni con motivazione per tipo
  - Tabella bootstrap (riga ~167): correggi DESIGN versioning
  - Nuova sezione "File temporanei": esclude findings.md da tracking
  
- `.github/agents/Agent-Orchestrator.md`:
  - Sezione "Riferimenti Skills" (dopo riga 90): aggiungi `docs_manager.skill.md`
  - Fase 0 punto 2: amplia con punto 2b che identifica primo TODO non spuntato
  - Fase 0 punto 2: aggiungi comportamento esplicito per caso "no TODO attivi" (fallback a DESIGN/PLAN stato)
  - Fase 6: aggiungi gate minimale su `git diff` per verificare che almeno uno di [API.md, ARCHITECTURE.md, CHANGELOG.md] sia modificato
  
- `.github/agents/Agent-Design.md`:
  - Sezione "Riferimenti Skills": aggiungi `docs_manager.skill.md`
  
- `.github/agents/Agent-Plan.md`:
  - Sezione "Riferimenti Skills": aggiungi `docs_manager.skill.md`
  
- `.github/skills/README.md`:
  - Sezione "Skills presenti": aggiungi entry per `error-recovery.skill.md`
  - Tabella agenti-skills: aggiungi `docs_manager` a Agent-Design, Agent-Plan, Agent-Orchestrator; aggiungi `error-recovery` a Agent-Orchestrator

### DELETE

- Nessuno

---

## Fasi sequenziali

### Fase 1 — Allineamento naming e routing (Task 1 + Task 2 C-bis)

**Obiettivo:** Risolvere conflitto naming e integrare `docs_manager` negli agenti  
**Durata:** Low complexity  
**Atomic:** Sì

Sequenza:
1. Modifica `.github/skills/docs_manager.skill.md`:
   - Sostituisci sezione "Convenzione naming file" (riga 51) con tabella esplicita di convenzioni per tipo + motivazione per ciascuna
   - Correggi tabella bootstrap (riga 167): `DESIGN_<feature>.md` (senza versione), `TODO_<feature>_vX.Y.Z.md` (aggiorna se attualmente diverso)
   - Aggiungi sezione "File temporanei" che esclude findings.md
   
2. Modifica `.github/agents/Agent-Orchestrator.md`:
   - Aggiungi `docs_manager.skill.md` a "Riferimenti Skills"
   - Estendi Fase 0 punto 2:
     - Punto 2a (esistente): leggi `docs/TODO.md`
     - Punto 2b (NEW): se esiste `docs/5 - todolist/TODO_<feature>_vX.Y.Z.md` con fasi non spuntate, primo task è "ripresa dal TODO attivo"
     - Punto 2c (NEW): se NON esiste TODO att attivo, controlla `docs/2 - projects/` e `docs/3 - coding plans/` per DESIGN o PLAN in stato DRAFT/READY prima di dichiarare "nessun task in corso"
     - Punto 3 (esistente): dopo questi step, esegui `detect_agent.py`
   - Aggiorna report stato iniziale per riflettere i tre path di discovery
   - Aggiungi `docs_manager.skill.md` a Fase 2 e Fase 3 prompt: istruzioni esplicite che il file salvato va comunicato al coordinatore
   
3. Modifica `.github/agents/Agent-Design.md`:
   - Aggiungi `docs_manager.skill.md` a "Riferimenti Skills"
   - Aggiungi nota nel deliverable: "Al salvataggio di DESIGN_<feature>.md, aggiorna `docs/TODO.md` sezione ### Progetti con link relativo (vedi `docs_manager.skill.md` Step 4)"
   
4. Modifica `.github/agents/Agent-Plan.md`:
   - Aggiungi `docs_manager.skill.md` a "Riferimenti Skills"
   - Aggiungi nota nel deliverable: "Al salvataggio di PLAN e TODO task, aggiorna `docs/TODO.md` sezioni ### Piani e ### Tasks con link relativi (vedi `docs_manager.skill.md` Step 4)"
   
5. Modifica `.github/skills/README.md`:
   - Tabella agenti-skills: aggiungi `docs_manager` a Agent-Design, Agent-Plan, Agent-Orchestrator

Commit: "docs(framework): allinea convenzioni naming in docs_manager.skill.md, integra routing docs_manager in Agent-Design/Plan/Orchestrator"

### Fase 2 — Error recovery skill (Task 3)

**Obiettivo:** Standardizzare procedura retry + escalata negli subagenti  
**Durata:** Very low complexity  
**Atomic:** Sì

Sequenza:
1. Crea `.github/skills/error-recovery.skill.md` con:
   - Dichiarazione authority: quando un subagente fallisce nella esecuzione di un task, segui questa procedura
   - Max 2 tentativi: primo tentativo con istruzioni originali, secondo con context incrementale ("Il tuo primo tentativo ha fallito perché X. Riprova con...")
   - Dopo 2 fallimenti: non riprova autonomamente. Escalata standard: "Ho tentato 2 volte di <task> senza successo. Errori: <log>. Richiedo conferma: proseguo comunque, salto il task, o ritento manualmente?"
   - Niente di più (max 25-30 righe)

2. Modifica `.github/agents/Agent-Orchestrator.md`:
   - Sezione "Riferimenti Skills": aggiungi `error-recovery.skill.md`
   - Tutte le fasi che delegano subagenti: sostituisci "Se fallisce: riprova..." con "Applica `error-recovery.skill.md`"
   - Fase 2, 3, 4, 5: aggiorna istruzioni di retry per referenziare la skill anziché inline
   
3. Modifica `.github/skills/README.md`:
   - Sezione "Skills presenti": aggiungi voce per `error-recovery.skill.md` con descrizione
   - Tabella agenti-skills: aggiungi `error-recovery` a Agent-Orchestrator

Commit: "docs(framework): crea error-recovery.skill.md con procedura standardizzata retry (max 2 tentativi) e escalata"

### Fase 3 — Gate minimale Fase 6 (Task 3)

**Obiettivo:** Verificare che Agent-Docs abbia effettivamente modificato i file target  
**Durata:** Very low complexity  
**Atomic:** Sì

Sequenza:
1. Modifica `.github/agents/Agent-Orchestrator.md` Fase 6:
   - Dopo "Delega a Agent-Docs ...": aggiungi gate
     ```
     Gate di uscita (informale):
       git diff --name-only HEAD
       Almeno uno di [docs/API.md, docs/ARCHITECTURE.md, CHANGELOG.md] deve essere modificato.
       Se nessuno è modificato: segnala all'utente "Agent-Docs non ha modificato alcun file target.
       Verificare che il task sia effettivamente completato."
     ```

Commit: "docs(framework): aggiungi gate informale Fase 6 per validare modifiche Agent-Docs"

---

## Test Plan

### Unit + Integration Tests

**Goal:** Verificare che i file modificati rispettino struttura e sintassi attesa.

1. **Markup validation:**
   - `markdownlint .github/skills/error-recovery.skill.md` — deve passare con esclusioni standard
   - `markdownlint .github/agents/Agent-*.md` (Design, Plan, Orchestrator) — no new errors
   - `markdownlint .github/skills/README.md` — no new errors

2. **Sintassi YAML frontmatter (se applicabile):**
   - Agent-Orchestrator.md: no frontmatter modification (agent file)
   - Verificare struttura liste ("Riferimenti Skills", tabelle) con grep basics

3. **Coerenza interna:**
   - `grep -n "docs_manager" .github/agents/Agent-*.md` — Agent-Design, Agent-Plan, Agent-Orchestrator devono tutti referenziarla
   - `grep -n "error-recovery" .github/agents/Agent-Orchestrator.md` — deve occorrere in Fase 2, 3, 4, 5
   - `.github/skills/README.md`: conteggio righe tabella agenti-skills deve aumentare di 3 entry (docs_manager in 3 agenti, error-recovery in 1)

4. **Integrità link relativi:**
   - Todos di Test Plan rimangono minimali perché il piano è di refactor documentale, non di funzionalità nuove
   - CI passerà se markdownlint passa (no new errors) e grep finds non mostrano regressioni

---

## Dependencies

- Nessuna dipendenza tra Fase 1, Fase 2, Fase 3 (possono procedere in parallelo)
- Tutte le modifiche sono documentali e non generano build/test impatti
- No git operations richieste oltre al commit finale di ogni fase

---

## Risk & Constraints

### Accessibilità

- Nessun impact: modifiche sono solo documentali, non UI
- Verificare che i file .md rimangono screen reader friendly (heading hierarchy, link text, ecc.)

### Backward Compatibility

- Non c'è: agenti leggeranno le skill nuove dalla prima volta che vengono invocati
- Orchestrator con Fase 0 ampliata rimane retrocompatibile (fallback à vecchio comportamento se TODO.md assente)

### Performance

- No degradation: tutti gli step restano I/O read su file locali

### Forward Compatibility

- Struttura error-recovery.skill.md è designed per supportare future estensioni (numero max tentativi, formato escalata) senza rotture

---

## Approvals & Validation

Prima di commit:
- [ ] Tutti i `.md` passano markdownlint
- [ ] No regressioni di referenze interne (grep check)
- [ ] Tabella agenti-skills è coerente
- [ ] Frontmatter Orchestrator ammissibile (se reader YAML)
