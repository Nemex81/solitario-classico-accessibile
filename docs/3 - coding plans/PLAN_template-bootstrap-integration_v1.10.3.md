---
feature: template-bootstrap-integration
type: plan
agent: Agent-Plan
status: READY
version: v1.10.3
design_ref: docs/2 - projects/DESIGN_framework-template-bootstrap.md
date: 2026-03-28
---

# Plan: Template Bootstrap Integration v1.10.3

## Executive Summary

Rendere operativo il design di integrazione tra template framework, template utente e bootstrap Agent-Welcome, senza rompere la separazione gia esistente tra .github/templates e docs/1 - templates.

1. **Gap di copertura template framework**: mancano template canonici per API, ARCHITECTURE e CHANGELOG, mentre i file presenti in docs/1 - templates sono example/template utente e non sorgenti runtime affidabili.
2. **Bootstrap Agent-Welcome incompleto**: l'OP-3 oggi crea la struttura docs ma non i documenti core progetto ne un livello di istruzioni progetto dedicato.
3. **Contratto runtime assente**: non esiste ancora una skill o una sezione operativa che colleghi template canonici, file target e comportamento additivo del bootstrap.
4. **Template TODO example disallineato**: il template example TODO non riflette il modello duale coordinatore piu TODO task gia canonico nel framework.

**Obiettivo:** portare il framework a uno stato in cui Agent-Welcome possa inizializzare in modo coerente la documentazione core del progetto, i template framework coprano i documenti realmente bootstrapabili e i template utente restino compatibili ma non autoritativi.

**Versione target:** v1.10.3  
**Priorita:** Alta  
**Prerequisito operativo:** le fasi che modificano .github/** richiedono sblocco esplicito del framework tramite il percorso previsto dal framework guard.

---

## Problema e Obiettivo

### Problemi confermati

1. **Doppio ecosistema non integrato**
   - .github/templates contiene i template canonici letti dagli agenti.
   - docs/1 - templates contiene template/example utente.
   - Manca il ponte operativo che definisce quali example generano quali template canonici e quali file target vengono bootstrapati.

2. **Document bootstrap parziale**
   - Agent-Welcome bootstrapa cartelle docs e coordinatore, ma non docs/API.md, docs/ARCHITECTURE.md e CHANGELOG.md.
   - Il setup iniziale del progetto resta quindi strutturalmente incompleto rispetto ai documenti core effettivamente usati dal repository.

3. **Tema copilot-instructions architetturalmente ambiguo**
   - L'idea di usare TEMPLATE_COPILOT_INSTRUCTIONS.md per rigenerare .github/copilot-instructions.md e incompatibile con il ruolo di quel file come nucleo framework.
   - Serve un file di istruzioni progetto dedicato, separato dalle istruzioni globali del framework.

4. **TODO example fuori contratto**
   - Il sistema attuale prevede docs/TODO.md come coordinatore persistente e docs/5 - todolist/TODO_feature_vX.Y.Z.md come TODO operativo.
   - Un template TODO alternativo non deve introdurre uno standard concorrente.

### Obiettivi strategici

1. Introdurre template framework canonici per i documenti core bootstrapabili.
2. Formalizzare il bootstrap documentale core di Agent-Welcome come fase esplicita e additiva.
3. Separare le istruzioni progetto dalle istruzioni globali del framework.
4. Riallineare i template example utente ai template framework corrispondenti.
5. Preservare il sistema TODO gia in uso senza introdurre formati paralleli.

---

## File coinvolti

### CREATE

- `.github/templates/api.md`
  - template canonico per bootstrap di `docs/API.md`.

- `.github/templates/architecture.md`
  - template canonico per bootstrap di `docs/ARCHITECTURE.md`.

- `.github/templates/changelog.md`
  - template canonico per bootstrap di `CHANGELOG.md`.

- `.github/templates/project.instructions.md`
  - template canonico per un file di istruzioni progetto dedicato, destinato a `.github/instructions/project.instructions.md`.

- `.github/skills/project-doc-bootstrap.skill.md`
  - sezione o skill operativa che definisce mapping template -> file target, placeholder minimi, gestione conflitti e livelli di bootstrap.

- `.github/templates/copilot-instructions.md`
  - template canonico neutro e riutilizzabile, copia della struttura di `.github/copilot-instructions.md` con tre placeholder espliciti: `{{NOME_PROGETTO}}` nel titolo h1, `{{VERSIONE_FRAMEWORK}}` accanto alla versione framework, `{{PROFILO_UTENTE}}` nella sezione Profilo Utente. Scopo: ripristino del file root su richiesta esplicita dell'utente tramite Agent-Welcome, mai automaticamente. Non e un template da compilare durante il bootstrap progetto standard.

### MODIFY

- `.github/agents/Agent-Welcome.md`
  - aggiungere una fase dedicata al bootstrap documentale core.
  - esplicitare i livelli di bootstrap: struttura, documenti core, istruzioni progetto.
  - dichiarare comportamento additivo e gestione conflitti.

- `.github/skills/docs_manager.skill.md`
  - integrare oppure referenziare il nuovo contratto di bootstrap documentale core.
  - chiarire il confine tra bootstrap struttura docs e bootstrap documenti core.

- `.github/templates/README.md`
  - documentare i nuovi template canonici, l'owner e l'agente consumatore.

- `.github/AGENTS.md`
  - aggiornare la descrizione di Agent-Welcome e del sistema template/bootstrap.

- `.github/copilot-instructions.md`
  - aggiornare i riferimenti solo se necessario per descrivere il nuovo file di istruzioni progetto dedicato, senza renderlo sorgente bootstrapabile da Agent-Welcome.

- `docs/1 - templates/TEMPLATE_COPILOT_INSTRUCTIONS.md`
  - convertirlo in example/wrapper coerente con il nuovo template framework `project.instructions.md`.
  - rimuovere le istruzioni che suggeriscono la copia diretta in `.github/copilot-instructions.md` come percorso standard del framework.

- `docs/1 - templates/TEMPLATE_example_API.md`
  - riallinearlo al template framework `api.md` e al ruolo di `docs/API.md`.

- `docs/1 - templates/TEMPLATE_example_ARCHITECTURE.md`
  - riallinearlo al template framework `architecture.md` e al ruolo di `docs/ARCHITECTURE.md`.

- `docs/1 - templates/TEMPLATE_example_CHANGELOG.md`
  - riallinearlo al template framework `changelog.md` e alla policy Keep a Changelog del progetto.

- `docs/1 - templates/TEMPLATE_example_TODO.md`
  - riallinearlo al sistema coordinatore piu TODO task, evitando un terzo formato operativo.

- `docs/TODO.md`
  - aggiornare il coordinatore con i nuovi artefatti di plan e todo del lavoro attivo.

### DELETE

- `docs/1 - templates/TEMPLATE_COPILOT_INSTRUCTIONS.md`
- `docs/1 - templates/TEMPLATE_example_API.md`
- `docs/1 - templates/TEMPLATE_example_ARCHITECTURE.md`
- `docs/1 - templates/TEMPLATE_example_CHANGELOG.md`
- `docs/1 - templates/TEMPLATE_example_TODO.md`
- `docs/1 - templates/TEMPLATE_example_DESIGN_DOCUMENT.md`
- `docs/1 - templates/TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md`

---

## Fasi sequenziali

### Fase 1 — Canonical Template Layer

**Obiettivo:** coprire in .github/templates i documenti core che Agent-Welcome dovra bootstrapare.

Sequenza:

1. Creare i template canonici `api.md`, `architecture.md`, `changelog.md` e `project.instructions.md` in `.github/templates/`.
2. Creare `.github/templates/copilot-instructions.md` come template neutro con i tre placeholder `{{NOME_PROGETTO}}`, `{{VERSIONE_FRAMEWORK}}` e `{{PROFILO_UTENTE}}`, speculare alla struttura attuale del file root ma privo di contenuto specifico del progetto corrente.
3. Rendere i template minimali, placeholder-driven e allineati ai file target reali del repository.
4. Aggiornare `.github/templates/README.md` con ownership, scopo e consumatore.
5. Verificare che nessun template nuovo duplichi il ruolo di `todo_coordinator.md` o `todo_task.md`.

Commit suggerito:
`docs(framework): aggiungi template canonici per bootstrap documentale core`

### Fase 2 — Runtime Contract for Bootstrap

**Obiettivo:** introdurre un contratto operativo esplicito tra template framework, file target e comportamento Agent-Welcome.

Sequenza:

1. Creare `project-doc-bootstrap.skill.md` oppure integrare una sezione dedicata in `docs_manager.skill.md`.
2. Definire livelli di bootstrap:
   - struttura docs
   - documenti core
   - istruzioni progetto
3. Formalizzare le regole di conflitto: no overwrite implicito, prompt esplicito, idempotenza.
4. Dichiarare placeholder obbligatori e mapping template -> destinazione.

Commit suggerito:
`docs(framework): formalizza contratto bootstrap documentale core`

### Fase 3 — Estensione Agent-Welcome

**Obiettivo:** rendere Agent-Welcome capace di bootstrap documentale completo, in modo guidato e compatibile con il framework guard.

Sequenza:

1. Aggiornare `Agent-Welcome.md` con una fase successiva al bootstrap struttura docs.
2. Offrire una scelta esplicita tra:
   - solo struttura docs
   - struttura piu documenti core
   - struttura piu documenti core piu istruzioni progetto
3. Esplicitare il file target delle istruzioni progetto come `.github/instructions/project.instructions.md`.
4. Documentare che `.github/copilot-instructions.md` non viene rigenerato dal bootstrap progetto.
5. Documentare la competenza di ripristino di `.github/copilot-instructions.md`: Agent-Welcome, su richiesta esplicita dell'utente, legge `project-profile.md`, compila i tre placeholder del template `copilot-instructions.md` e sovrascrive il file root. Questa operazione e separata dal bootstrap progetto standard, richiede conferma esplicita e non viene mai eseguita automaticamente.

Commit suggerito:
`docs(framework): estende Agent-Welcome con bootstrap documentale core`

### Fase 4 — Rimozione Template di Sistema da docs/1 - templates

**Obiettivo:** liberare `docs/1 - templates/` dai template di sistema del framework e riservare lo spazio ai template personalizzati dell'utente relativi allo sviluppo della propria applicazione.

Sequenza:

1. Eliminare i seguenti file da `docs/1 - templates/`: `TEMPLATE_COPILOT_INSTRUCTIONS.md`, `TEMPLATE_example_API.md`, `TEMPLATE_example_ARCHITECTURE.md`, `TEMPLATE_example_CHANGELOG.md`, `TEMPLATE_example_TODO.md`, `TEMPLATE_example_DESIGN_DOCUMENT.md`, `TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md`.
2. Verificare che dopo la rimozione `docs/1 - templates/` non contenga altri file di pertinenza del framework o degli agenti.
3. Aggiornare il README della cartella se presente, per dichiarare che lo spazio e riservato ai template personalizzati dell'utente e non viene mai letto dagli agenti del framework come sorgente primaria.

Commit suggerito:
`docs(project): rimuovi template di sistema da docs/1 - templates`

### Fase 5 — Framework Documentation Sync

**Obiettivo:** aggiornare la documentazione quadro del framework una volta implementato il nuovo modello.

Sequenza:

1. Aggiornare `.github/AGENTS.md` con il nuovo bootstrap documentale di Agent-Welcome.
2. Aggiornare `.github/copilot-instructions.md` solo per descrivere il nuovo assetto, senza spostare ownership o responsabilita.
3. Verificare i riferimenti incrociati tra skill, template e agenti.

Commit suggerito:
`docs(framework): sincronizza documentazione del bootstrap template`

---

## Test Plan

1. Verifica template framework:
   - controllo manuale dei placeholder nei nuovi file in `.github/templates/`
   - verifica coerenza con `.github/templates/README.md`

2. Verifica contratto bootstrap:
   - controllo riferimenti in `Agent-Welcome.md`, `docs_manager.skill.md` o `project-doc-bootstrap.skill.md`
   - verifica esplicita dei mapping template -> file target

3. Verifica pulizia cartella utente: verifica che `docs/1 - templates/` non contenga piu file di pertinenza del framework o degli agenti dopo l'esecuzione della Fase 4; verifica che il README della cartella dichiari esplicitamente lo spazio come riservato ai template personalizzati dell'utente

4. Verifica integrita coordinatore:
   - `docs/TODO.md` deve contenere i link ai nuovi artefatti attivi
   - nessun duplicato del path relativo nelle sezioni Piani e Tasks

5. Verifica vincoli framework:
   - nessuna proposta di bootstrap diretto di `.github/copilot-instructions.md`
   - ogni modifica su `.github/**` resta esplicitamente soggetta a framework guard

---

## Dependencies

- La Fase 1 e prerequisito diretto della Fase 2 e della Fase 4.
- La Fase 2 e prerequisito diretto della Fase 3.
- La Fase 5 va eseguita solo dopo il completamento sostanziale delle Fasi 1-4.
- L'implementazione effettiva delle Fasi 1-5 richiede sblocco del framework per le scritture su `.github/**`.

---

## Risk & Constraints

### Accessibilita

- I nuovi documenti devono rimanere lineari, scansionabili da screen reader e senza tabelle complesse evitabili.
- I messaggi di bootstrap proposti da Agent-Welcome devono restare brevi e con scelte esplicite.

### Compatibilita

- Nessun file utente in `docs/1 - templates/` deve diventare implicitamente sorgente autoritativa del framework.
- Il sistema TODO esistente non va alterato nella sua architettura duale.

### Vincoli espliciti

- `.github/copilot-instructions.md` non deve essere trattato come output del bootstrap progetto.
- Nessuna sovrascrittura implicita di file esistenti in docs o .github.
- Il framework guard resta attivo per tutte le modifiche .github fuori dalle eccezioni gia previste.

---

## Approvals & Validation

Prima dell'implementazione:

- [x] DESIGN `framework-template-bootstrap` considerato revisionato e idoneo alla pianificazione
- [x] Confermato che il target e il bootstrap documentale core, non la rigenerazione del nucleo framework
- [x] Confermato che il sistema TODO esistente resta canonico

Prima del commit finale di ciascuna fase:

- [ ] Template canonici nuovi coerenti con i file target reali
- [ ] Skill o sezione bootstrap aggiornata con mapping e gestione conflitti
- [ ] Agent-Welcome aggiornato con flusso bootstrap esplicito
- [ ] Template/example utente riallineati senza diventare autoritativi
- [ ] Documentazione framework sincronizzata
