---
feature: framework-template-bootstrap
agent: Agent-Design
status: REVIEWED
version: v1.10.3
date: 2026-03-28
---

# DESIGN — Integrazione Template Framework e Bootstrap Agent-Welcome

## Idea in 3 righe

Il repository ha gia due ecosistemi di template distinti: template canonici del framework in .github/templates e template/example utente in docs/1 - templates. La bozza di partenza coglie correttamente il gap di copertura, ma va ristrutturata per evitare di trasformare i template utente in sorgenti operative del framework. Il target corretto e un bootstrap documentale additivo, con ownership esplicita, compatibile con Agent-Welcome e con il sistema TODO gia attivo.

## Attori e Concetti

### Attori

- Agent-Welcome: inizializza il progetto, genera il project-profile e puo bootstrapparne la documentazione core.
- Agent-FrameworkDocs: unico owner dei template framework in .github/templates e della documentazione framework in .github/.
- Agent-Docs: owner della documentazione tecnica di progetto in root e validatore di coerenza documentale.
- docs_manager.skill.md: skill che governa bootstrap docs, naming, coordinatore e regola additiva.
- Utente: puo mantenere template personali in docs/1 - templates senza che gli agenti li assumano come sorgente canonica.

### Concetti Chiave

#### Template framework

- Cosa sono: modelli canonici, minimali e machine-friendly usati dagli agenti come sorgente operativa.
- Path: .github/templates.
- Regola: letti dagli agenti, scritti solo da Agent-FrameworkDocs.

#### Template utente

- Cosa sono: esempi, reference template o modelli personalizzati del progetto.
- Path: docs/1 - templates.
- Regola: non devono essere consumati come sorgente primaria dal framework.

#### Bootstrap documentale core

- Cosa e: generazione additiva dei file base del progetto documentale.
- File target: docs/API.md, docs/ARCHITECTURE.md, CHANGELOG.md ed eventuale file di istruzioni progetto dedicato.
- Regola: nessuna sovrascrittura implicita; ogni conflitto va esplicitato.

#### Istruzioni progetto dedicate

- Cosa sono: livello di specializzazione progetto separato dalle istruzioni globali del framework.
- Path candidato: .github/instructions/project.instructions.md.
- Regola: sostituiscono l'idea di rigenerare .github/copilot-instructions.md durante il setup.

#### Sistema TODO

- Cosa e: modello duale gia canonico nel repository.
- Componenti: docs/TODO.md come coordinatore persistente; docs/5 - todolist/TODO_feature_vX.Y.Z.md come TODO operativo per task.
- Regola: i template TODO example vanno adattati a questo modello, non introdurre uno standard parallelo.

## Flussi Concettuali

### Flusso 1 — Normalizzazione template

1. Agent-FrameworkDocs legge i template example in docs/1 - templates come materiale di riferimento, non come input operativo diretto.
2. Da questi example estrae i corrispondenti template canonici per il framework solo dove esiste un bisogno runtime reale.
3. I template framework nuovi vengono progettati in forma sintetica, con placeholder chiari e senza contenuto tutoriale esteso.
4. I template example in docs/1 - templates vengono mantenuti come wrapper utente, con riferimenti espliciti al template canonico corrispondente.

### Flusso 2 — Bootstrap Agent-Welcome

1. Agent-Welcome completa OP-1 sul profilo progetto e, se richiesto, propone il bootstrap documentale.
2. Il bootstrap avviene a livelli:
   - livello base: struttura docs e coordinatore
   - livello core: docs/API.md, docs/ARCHITECTURE.md, CHANGELOG.md
   - livello progetto: eventuale file project.instructions.md
3. Se un file target esiste gia, il bootstrap resta additivo e chiede una decisione esplicita all'utente.
4. Il risultato viene riportato in formato accessibile e i nuovi documenti vengono collegati al coordinatore docs quando applicabile.

### Flusso 3 — Gestione template TODO

1. Il framework continua a considerare canonici .github/templates/todo_coordinator.md e .github/templates/todo_task.md.
2. TEMPLATE_example_TODO.md viene reinterpretato come esempio allineato al modello coordinatore piu TODO task.
3. Agent-Welcome non genera un terzo formato TODO; si limita a bootstrap della struttura e, se richiesto in futuro, a creare esempi utente compatibili.

## Decisioni Architetturali

### Decisione 1 — Separazione forte tra .github/templates e docs/1 - templates

Scelta: mantenere la distinzione gia presente e rafforzarla come contratto architetturale.

Motivazione:

- e gia coerente con docs_manager.skill.md e con .github/templates/README.md
- evita che template example verbose o tutoriali diventino input fragile per gli agenti
- consente all'utente di avere template personalizzati senza alterare il runtime framework

### Decisione 2 — Nuovi template framework solo per documenti con consumo operativo reale

Scelta: introdurre in .github/templates i corrispettivi canonici per API, ARCHITECTURE e CHANGELOG; non introdurre un nuovo template TODO parallelo.

Motivazione:

- docs/API.md, docs/ARCHITECTURE.md e CHANGELOG.md sono file target stabili del ciclo documentale
- il sistema TODO ha gia template framework sufficienti
- si evita di moltiplicare standard concorrenti

### Decisione 3 — Non rigenerare .github/copilot-instructions.md dal bootstrap progetto

Scelta: sostituire l'uso diretto di TEMPLATE_COPILOT_INSTRUCTIONS.md con un template framework per istruzioni progetto dedicate, preferibilmente .github/instructions/project.instructions.md.

Motivazione:

- .github/copilot-instructions.md e un file di nucleo framework, non un artefatto di bootstrap progetto
- la sua rigenerazione da parte di Agent-Welcome entra in conflitto con framework guard e con la separazione framework/progetto
- un file project.instructions.md mantiene la stessa utilita pratica senza destabilizzare il framework

### Decisione 4 — Estensione di Agent-Welcome con un bootstrap documentale esplicito

Scelta: introdurre una fase dedicata, successiva al bootstrap struttura docs, per la generazione dei documenti core progetto.

Motivazione:

- l'attuale OP-3 copre la struttura ma non i documenti applicativi di base
- una fase esplicita rende il comportamento leggibile, confermabile e testabile
- riduce le ambiguita tra setup framework e setup documentazione progetto

### Decisione 5 — Skill dedicata o estensione strutturata di docs_manager

Scelta: gestire il bootstrap documentale core tramite una sezione esplicita di docs_manager.skill.md oppure tramite una nuova skill project-doc-bootstrap.skill.md.

Motivazione:

- serve un contratto runtime chiaro tra template canonici, file target e Agent-Welcome
- oggi il framework non contiene un workflow formale che consumi i template example richiesti
- la scelta va fatta privilegiando un solo punto di verita per naming, conflitti e comportamento additivo

Decisione derivata:

- se l'estensione di docs_manager resta leggibile e focalizzata, e preferibile evitare una nuova skill
- se il bootstrap core introduce troppa complessita, la skill separata e piu mantenibile

## Rischi e Vincoli

### Vincoli strutturali

- I path protetti sotto .github richiedono rispetto del framework guard; l'implementazione reale delle modifiche framework non puo essere considerata automatica finche non viene autorizzata.
- Il file .github/project-profile.md risulta ancora non inizializzato a livello di frontmatter; questo non blocca il design, ma rende il bootstrap teorico finche il setup non viene completato.
- Il repository contiene gia documentazione tecnica ricca e specifica; i nuovi template non devono semplificare eccessivamente il contratto gia in uso.

### Rischi principali

- Promuovere i template example a template framework senza normalizzazione introdurrebbe accoppiamento improprio tra documentazione utente e runtime agenti.
- Usare TEMPLATE_COPILOT_INSTRUCTIONS.md per rigenerare .github/copilot-instructions.md rischia regressioni framework e conflitti con le regole di protezione.
- Introdurre un nuovo template TODO framework parallelo romperebbe la coesione del sistema docs/TODO.md piu docs/5 - todolist/.

### Validazione della bozza di partenza

- Valida nell'intuizione: identifica correttamente il gap di integrazione tra template utente, framework e Agent-Welcome.
- Da correggere nel perimetro: il contenuto non va tradotto in una copia speculare dei file da docs/1 - templates a .github/templates.
- Da ottimizzare nel modello: bisogna distinguere template canonici, template example, bootstrap documentale core e istruzioni progetto dedicate.

## Coding plans correlati

- Contesto storico: docs/3 - coding plans/PLAN_document-governance_v1.9.0.md
- Contesto operativo parziale: docs/3 - coding plans/PLAN_framework-optimization_v1.10.0.md
- Piano dedicato da creare successivamente: PLAN_template-bootstrap-integration_v1.10.3.md
