---
feature: Template Bootstrap Integration
type: todo
status: COMPLETED
version: v1.10.3
plan_ref: docs/3 - coding plans/PLAN_template-bootstrap-integration_v1.10.3.md
date: 2026-03-28
---

# TODO: Template Bootstrap Integration v1.10.3

Implementazione del piano `PLAN_template-bootstrap-integration_v1.10.3.md`: template canonici per bootstrap documentale core, contratto operativo Agent-Welcome e riallineamento template/example utente.

## Fasi

### Fase 1 — Canonical Template Layer

- [x] Crea `.github/templates/api.md`
- [x] Crea `.github/templates/architecture.md`
- [x] Crea `.github/templates/changelog.md`
- [x] Crea `.github/templates/project.instructions.md`
- [x] Crea `.github/templates/copilot-instructions.md`
- [x] Aggiorna `.github/templates/README.md`

**Commit Message Fase 1:**

```text
docs(framework): aggiungi template canonici per bootstrap documentale core
```

### Fase 2 — Runtime Contract for Bootstrap

- [x] Crea oppure integra la skill bootstrap documentale core
- [x] Definisci mapping template -> file target
- [x] Formalizza gestione conflitti e idempotenza
- [x] Allinea il confine con `docs_manager.skill.md`

**Commit Message Fase 2:**

```text
docs(framework): formalizza contratto bootstrap documentale core
```

### Fase 3 — Estensione Agent-Welcome

- [x] Aggiorna `Agent-Welcome.md` con fase bootstrap documenti core
- [x] Aggiungi i livelli di bootstrap espliciti
- [x] Punta le istruzioni progetto a `.github/instructions/project.instructions.md`
- [x] Escludi la rigenerazione di `.github/copilot-instructions.md`

**Commit Message Fase 3:**

```text
docs(framework): estende Agent-Welcome con bootstrap documentale core
```

### Fase 4 — Rimozione Template di Sistema da docs/1 - templates

- [x] Elimina `docs/1 - templates/TEMPLATE_COPILOT_INSTRUCTIONS.md`
- [x] Elimina `docs/1 - templates/TEMPLATE_example_API.md`
- [x] Elimina `docs/1 - templates/TEMPLATE_example_ARCHITECTURE.md`
- [x] Elimina `docs/1 - templates/TEMPLATE_example_CHANGELOG.md`
- [x] Elimina `docs/1 - templates/TEMPLATE_example_TODO.md`
- [x] Elimina `docs/1 - templates/TEMPLATE_example_DESIGN_DOCUMENT.md`
- [x] Elimina `docs/1 - templates/TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md`
- [x] Verifica che `docs/1 - templates/` non contenga altri file del framework
- [x] Aggiorna il README di `docs/1 - templates/` se presente

**Commit Message Fase 4:**

```text
docs(project): rimuovi template di sistema da docs/1 - templates
```

### Fase 5 — Framework Documentation Sync

- [x] Aggiorna `.github/AGENTS.md`
- [x] Aggiorna `.github/copilot-instructions.md` solo dove strettamente necessario
- [x] Verifica i riferimenti incrociati tra skill, template e agenti

**Commit Message Fase 5:**

```text
docs(framework): sincronizza documentazione del bootstrap template
```

## Vincoli espliciti

- [x] Attivare lo sblocco framework prima di modificare `.github/**`
- [x] Mantenere additivo il bootstrap: nessun overwrite implicito
- [x] Non introdurre un formato TODO alternativo al modello corrente
- [x] Non usare `.github/copilot-instructions.md` come output del bootstrap progetto

## Prossimi step

1. Task completato: mantenere questo file come storico di implementazione.
2. Allineare eventuali release framework future tramite `#framework-release`.
