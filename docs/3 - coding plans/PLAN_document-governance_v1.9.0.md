---
type: plan
feature: document-governance
agent: Agent-Plan
status: READY
version: v1.9.0
design_ref: docs/2 - projects/DESIGN_document-governance.md
date: 2026-03-26
---

# PLAN — Document Governance v1.9.0

## Executive Summary

- Tipo: framework architecture
- Priorita': alta
- Stato: READY
- Versione target: v1.9.0
- Data: 2026-03-26
- Scope: `.github/` per regole e agenti, `docs/` per struttura e artefatti documentali
- Obiettivo: rendere sistemico l'uso delle cartelle documentali senza centralizzare tutta la scrittura su `Agent-Docs`

## Problema e Obiettivo

### Problema

La struttura documentale del repository e' cresciuta in modo utile ma non ancora completamente sistemico. Esistono gia' convenzioni, template e una suddivisione parziale delle responsabilita', ma mancano ancora quattro elementi chiave:

1. ownership esplicita per tipo di artefatto
2. separazione netta tra coordinamento documentale e persistenza dei file
3. trattamento coerente dei TODO specifici per implementazione
4. integrazione strutturale di nuove cartelle come `docs/4 - reports/` e `docs/5 - todolist/`

Nel modello attuale emergono alcune tensioni:

- `Agent-Plan` e `Agent-Code` lavorano su `docs/TODO.md` come file operativo
- `Agent-Docs` e' gia' owner della documentazione tecnica root ma non del repository documentale complessivo
- skill e convenzioni documentali risultano parzialmente sovrapposte
- alcune cartelle previste dal modello non sono ancora presenti fisicamente o non sono rese obbligatorie dal workflow

### Obiettivo

Definire e implementare un modello documentale in cui:

1. ogni agente specialista possiede i propri artefatti
2. `Agent-Docs` governa struttura, naming, linking e coerenza del sistema documentale
3. i TODO per singola implementazione sono file dedicati e non piu' concetti impliciti
4. `docs/TODO.md` viene progressivamente riallineato a un ruolo di coordinamento persistente

## Modello Target

### Ownership documentale

- `Agent-Design` possiede `docs/2 - projects/` e i documenti `DESIGN_*`
- `Agent-Plan` possiede `docs/3 - coding plans/` e crea i TODO per-task
- `Agent-Validate` possiede `docs/4 - reports/`
- `Agent-Code` puo' aggiornare solo il TODO del task attivo
- `Agent-Docs` possiede i documenti tecnici di root e coordina la validazione strutturale del sistema documentale

### Ruolo di `docs/TODO.md`

Nel target finale `docs/TODO.md` non deve essere la checklist di dettaglio del task, ma un indice persistente dei lavori attivi. Fino alla migrazione completa resta utilizzabile come appoggio operativo, ma il modello strutturale approvato prevede che i TODO specifici stiano in file dedicati.

### Ruolo di `docs/5 - todolist/`

`docs/5 - todolist/` e' la cartella canonica che contiene i singoli TODO specifici per implementazione. Ogni file rappresenta un task o una iniziativa implementativa, con checklist, link al piano di riferimento e stato aggiornabile durante l'esecuzione.

### Ruolo di `Agent-Docs`

`Agent-Docs` non diventa writer unico di `docs/`. Il suo ruolo target e' questo:

- validare naming, path e frontmatter
- verificare link tra design, piani, TODO e report
- mantenere la coerenza tra documentazione tecnica di root e artefatti di progetto
- coordinare il repository documentale senza sostituirsi agli agenti specialisti nella produzione dei loro documenti

## File Coinvolti

### Da introdurre o rendere canonici

- `docs/4 - reports/` — nuova cartella per report di validazione
- `docs/5 - todolist/` — nuova cartella per TODO specifici per task
- `.github/skills/docs_manager.skill.md` oppure evoluzione canonica di `docs_manager`
- eventuali template dedicati a report e todo-task

### Da aggiornare in una futura implementazione

- `.github/agents/Agent-Docs.md`
- `.github/agents/Agent-Plan.md`
- `.github/agents/Agent-Design.md`
- `.github/agents/Agent-Validate.md`
- `.github/agents/Agent-Code.md`
- `.github/skills/document-template.skill.md`
- eventuale skill `docs_manager`
- `docs/TODO.md`
- eventuali script di validazione come `scripts/validate_gates.py`

## Fasi Sequenziali

### Fase 1 — Chiusura del contratto documentale

Obiettivo: definire in modo esplicito il modello target senza toccare ancora la logica del workflow.

Output attesi:

- decisione confermata sul fatto che `docs/5 - todolist/` ospita i TODO per singola implementazione
- decisione confermata sul fatto che `Agent-Docs` e' coordinatore/validatore e non writer unico
- definizione del ruolo transitorio di `docs/TODO.md`

### Fase 2 — Unificazione delle regole documentali

Obiettivo: eliminare o assorbire le sovrapposizioni tra skill e template documentali.

Attivita':

- fondere o deprecare le regole duplicate tra `document-template.skill.md` e `docs_manager`
- dichiarare un'unica sorgente canonica per naming, frontmatter, path e responsabilita'
- chiarire il formato dei TODO per-task e del coordinatore root

### Fase 3 — Formalizzazione dell'ownership negli agenti

Obiettivo: fare in modo che gli agenti sappiano con chiarezza dove scrivere e dove non scrivere.

Attivita':

- assegnare ad `Agent-Design` la responsabilita' di `docs/2 - projects/`
- assegnare ad `Agent-Plan` la responsabilita' di `docs/3 - coding plans/` e della creazione dei TODO per-task
- assegnare ad `Agent-Validate` la responsabilita' di `docs/4 - reports/`
- limitare `Agent-Code` all'aggiornamento del solo TODO attivo
- estendere `Agent-Docs` alla validazione strutturale del repository documentale

### Fase 4 — Bootstrap fisico della struttura

Obiettivo: rendere sempre presenti le cartelle previste dal modello, evitando dipendenze da bootstrap opzionali.

Attivita':

- creare `docs/4 - reports/`
- creare `docs/5 - todolist/`
- introdurre eventuali file placeholder se necessari
- allineare i template disponibili alle cartelle reali

### Fase 5 — Migrazione controllata del flusso TODO

Obiettivo: spostare il lavoro operativo dai TODO root ai TODO per-task senza rompere il workflow in corso.

Attivita':

- mantenere temporaneamente `docs/TODO.md` come file coordinato o ponte
- creare TODO specifici per le nuove implementazioni nel formato definitivo
- aggiornare i riferimenti nei piani futuri verso `docs/5 - todolist/`
- evitare migrazioni distruttive dei file legacy finche' il nuovo flusso non e' stabile

### Fase 6 — Validazione e gate

Obiettivo: fare in modo che il framework non si limiti a dichiarare la struttura, ma la faccia rispettare.

Attivita':

- aggiornare i gate documentali e gli script di validazione
- controllare esistenza cartelle, naming e frontmatter
- validare i collegamenti tra progetto, piano, TODO e report

## Rischi e Vincoli

### Rischi principali

1. doppio contratto semantico tra `docs/TODO.md` e i futuri TODO per-task
2. sovrapposizione tra skill documentali con regole incompatibili
3. introduzione di nuove cartelle senza aggiornare i gate di validazione
4. estensione eccessiva di `Agent-Docs` fino a trasformarlo in collo di bottiglia

### Vincoli progettuali

- evitare modifiche premature ai file del framework senza un contratto architetturale consolidato
- mantenere compatibilita' con i documenti legacy gia' presenti
- non forzare da subito la rinomina dei file esistenti se non necessario
- preservare l'autonomia operativa degli agenti specialisti

## Gate Decisionali

Prima dell'implementazione effettiva devono essere considerati chiusi questi gate:

1. `docs/5 - todolist/` e' confermata come cartella dei TODO specifici per task
2. `docs/TODO.md` e' confermato come coordinatore persistente o file ponte transitorio
3. `Agent-Docs` e' confermato come coordinatore/validatore e non come writer unico
4. esiste una sola sorgente canonica per le regole documentali
5. i gate automatici verranno estesi alle nuove cartelle documentali

## Test Plan

### Verifiche documentali

- verificare che ogni agente indirizzi gli artefatti nel path corretto
- verificare che i TODO per implementazione nascano come file autonomi
- verificare che `docs/TODO.md` non venga piu' usato come checklist di dettaglio nel modello finale
- verificare che `Agent-Docs` non produca artefatti di task ma li validi

### Verifiche di coerenza

- controllare che i piani puntino ai TODO corretti
- controllare che i report siano collegabili al piano o al task di origine
- controllare che i template documentali non abbiano piu' regole in conflitto

## Stato di Approvazione

Questo piano e' stato discusso, validato e approvato in chat come base per la futura implementazione del modello documentale strutturale.