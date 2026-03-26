<!-- markdownlint-disable MD029 MD031 MD032 MD040 MD060 -->

# docs_manager — Skill operativa per la gestione documenti

Questa skill definisce le istruzioni operative che gli agenti eseguono
quando interagiscono con la struttura docs/ del progetto.

Non è documentazione passiva: è il protocollo di azione che l'agente
esegue direttamente come runtime AI. Funziona esattamente come
Agent-Welcome.md non è documentazione dell'agente benvenuto ma è
l'agente benvenuto.

---

## Path del sistema

I path canonici del sistema di tracciamento documenti sono l'unica
fonte di verità. Tutti gli agenti li leggono da questa sezione.
Nessun path letterale deve essere codificato nelle istruzioni degli agenti.

```
Template framework:   .github/templates/
Template utente:      docs/1 - templates/
Progetti:             docs/2 - projects/
Piani:                docs/3 - coding plans/
Reports:              docs/4 - reports/
Tasks:                docs/5 - todolist/
Coordinatore:         docs/TODO.md
```

---

## Distinzione tra le due cartelle templates

**`.github/templates/`** — Template del framework.
Contengono i modelli operativi usati dalla skill per generare nuovi file
nei percorsi docs/. Gli agenti leggono questi template ma non vi scrivono mai.
Gestiti esclusivamente da Agent-FrameworkDocs tramite framework-unlock.

**`docs/1 - templates/`** — Template personali dell'utente.
Contengono modelli specifici del progetto, creati e gestiti dall'utente.
Gli agenti non vi scrivono mai template framework.
Il contenuto esistente non viene mai sovrascritto dal bootstrap
o da qualsiasi operazione automatica degli agenti.

---

## Convenzione naming file — Per tipo di documento

Ogni tipo di documento ha una convenzione specifica. Non esiste una convenzione universale: il naming è semantico per il tipo.

| Tipo | Convenzione | Cartella | Motivazione |
|------|-------------|----------|-------------|
| DESIGN | `DESIGN_<feature>.md` | `docs/2 - projects/` | Documento di analisi che evolve in-place; senza versione perché è la sorgente autoritative per ogni feature. |
| PLAN | `PLAN_<feature>_vX.Y.Z.md` | `docs/3 - coding plans/` | Legato a un target release specifico; versione + feature combinati assicurano tracciabilità per ogni tag. |
| TODO task | `TODO_<feature>_vX.Y.Z.md` | `docs/5 - todolist/` | Operatico per-task; versione perché legato al PLAN di destinazione che ha versione. |
| REPORT | `REPORT_<tipo>_AAAA-MM-GG.md` | `docs/4 - reports/` | Documento punto-nel-tempo (es. coverage, validation); data perché è evidence storica non versionata. |
| README | `README.md` | In ogni cartella | Readme folders, nessuna versione. |

**Regola generale:** Nessun file viene mai sovrascritto: se il path esiste già, segnalare il conflitto all'utente (vedi sezione Regola additiva).

---

## Come salvare un documento

Per ciascun tipo di documento, seguire questa sequenza:

**1. Leggere il template corrispondente da `.github/templates/`**

| Tipo | Template |
|------|----------|
| design | `.github/templates/design.md` |
| coding_plan | `.github/templates/coding_plan.md` |
| report | `.github/templates/report.md` |
| todo_task | `.github/templates/todo_task.md` |

**2. Sostituire tutti i placeholder `{{...}}` con i valori reali.**
Nessun placeholder deve rimanere nel file finale.

**3. Salvare nella cartella corretta con naming normalizzato:**

| Tipo | Destinazione |
|------|-------------|
| design | `docs/2 - projects/` |
| coding_plan | `docs/3 - coding plans/` |
| report | `docs/4 - reports/` |
| todo_task | `docs/5 - todolist/` |

**4. Aggiornare `docs/TODO.md`** aggiungendo il link relativo
   nella sezione corretta (vedi sezione successiva).

---

## Aggiornamento coordinatore

Il file coordinatore operativo è sempre `docs/TODO.md`.

Regole per l'aggiornamento:

- Aggiungere in append nella sezione corretta:
  - design → sezione `### Progetti`
  - coding_plan → sezione `### Piani`
  - report → sezione `### Reports`
  - todo_task → sezione `### Tasks`
- Verificare **prima** che il path relativo non sia già presente
  nella sezione: la chiave di unicità è il **path relativo del file**,
  non il titolo
- Se il path è già presente: non aggiungere nulla (operazione idempotente)
- Non ricreare mai `docs/TODO.md` da zero dopo il bootstrap iniziale
- Il file `.github/templates/todo_coordinator.md` viene usato
  solo per la creazione iniziale al bootstrap; dopo non viene mai riletto

---

## Regola additiva

Gli agenti non sovrascrivono mai file esistenti.

Se un file con lo stesso path esiste già:

1. Non sovrascrivere
2. Segnalare il conflitto all'utente con questo formato:

```
CONFLITTO FILE
──────────────────────────────────────────
Path: <path del file>
Il file esiste già. Scegli:
  [R] Rinomina con suffisso (es. _v2)
  [S] Salta — mantieni il file esistente
  [O] Sovrascrivi — perdi il contenuto attuale
──────────────────────────────────────────
```

3. Attendere la decisione dell'utente prima di procedere

---

## Bootstrap struttura docs/

Il bootstrap crea le cartelle mancanti e aggiunge un README orientativo
in ciascuna. Operazione **strettamente additiva** — mai distruttiva.
Il comportamento è sempre lo stesso indipendentemente dallo stato iniziale
del progetto: che sia un progetto nuovo o esistente, il bootstrap
lavora solo su ciò che manca.

### Sequenza bootstrap

Per ciascuna cartella nel sistema (nell'ordine):
`docs/1 - templates/`, `docs/2 - projects/`, `docs/3 - coding plans/`,
`docs/4 - reports/`, `docs/5 - todolist/`

```
1. Se la cartella non esiste: crearla
2. Se README.md non esiste nella cartella:
   a. Leggere .github/templates/readme_folder.md
   b. Sostituire i 6 placeholder con i valori specifici per quella cartella
      (vedi tabella sotto)
   c. Scrivere README.md nella cartella
3. Se la cartella o il README esiste già: non toccare nulla
```

Per `docs/TODO.md`:
```
1. Se non esiste:
   a. Leggere .github/templates/todo_coordinator.md
   b. Sostituire {{DATA}} con la data corrente, {{AGENTE}} con il nome agente
   c. Scrivere docs/TODO.md
2. Se esiste già: non toccare
```

### Valori placeholder README per cartella

| Cartella | NOME_CARTELLA | SCOPO | AGENTE_SCRITTURA | AGENTE_LETTURA | CONVENZIONE_NAMING |
|----------|---------------|-------|------------------|----------------|-------------------|
| `docs/1 - templates` | docs/1 - templates | Template personali del progetto | — (utente) | Agent-Plan, Agent-Code | `TEMPLATE_*.md` |
| `docs/2 - projects` | docs/2 - projects | Documenti DESIGN prodotti da Agent-Design | Agent-Design | Agent-Plan | `DESIGN_<feature>.md` |
| `docs/3 - coding plans` | docs/3 - coding plans | Piani di implementazione prodotti da Agent-Plan | Agent-Plan | Agent-Code | `PLAN_<feature>_vX.Y.Z.md` |
| `docs/4 - reports` | docs/4 - reports | Report copertura e validazione gate, output CI | Agent-Validate | Agent-Docs | `REPORT_<tipo>_<data>.md` |
| `docs/5 - todolist` | docs/5 - todolist | Checklist operative per feature in sviluppo | Agent-Plan | Agent-Code | `TODO_<feature>_vX.Y.Z.md` |

---

## File temporanei (esclusi dal sistema di tracking)

I seguenti file sono generati durante operazioni agenti ma NON vengono tracciati dal sistema:

- `findings.md` (generato da Agent-Analyze come report draft, non committed)
- File `.tmp_*` o suffisso `_draft_` (file di lavoro temporanei)

Esclusi dal coordinatore: questi file non vengono mai linkati in `docs/TODO.md` e non entrano nel bootstrap structure.

### Contenuto `{{ISTRUZIONI_SPECIFICHE}}` per `docs/1 - templates/`

```
Questa cartella contiene i template personali del progetto.
Non contiene template del framework (quelli sono in .github/templates/).

Per aggiungere un template personale:
1. Crea un file .md con nome TEMPLATE_*.md
2. Documenta i placeholder nel file stesso
3. Per referenziarlo nel ciclo automatizzato: indicane il nome
   nel PLAN o TODO della feature che lo utilizza

Il bootstrap non sovrascrive mai il contenuto di questa cartella.
```

Per tutte le altre cartelle, usare come `{{ISTRUZIONI_SPECIFICHE}}` il contenuto
della colonna SCOPO esteso con il nome della convenzione naming.

---

## Riferimento rapido

| Azione | Template | Destinazione |
|--------|----------|--------------|
| Nuovo design | `.github/templates/design.md` | `docs/2 - projects/` |
| Nuovo piano | `.github/templates/coding_plan.md` | `docs/3 - coding plans/` |
| Nuovo report | `.github/templates/report.md` | `docs/4 - reports/` |
| Nuovo task | `.github/templates/todo_task.md` | `docs/5 - todolist/` |
| README cartella | `.github/templates/readme_folder.md` | cartella specifica |
| Coordinatore | `.github/templates/todo_coordinator.md` | `docs/TODO.md` (solo bootstrap) |
