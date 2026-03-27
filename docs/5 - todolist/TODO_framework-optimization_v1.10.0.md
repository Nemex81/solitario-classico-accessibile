---
type: todo
feature: Framework Optimization — Coerenza sistema documenti e protocolli Orchestrator
status: COMPLETED
version: v1.10.0
plan_ref: docs/3 - coding plans/PLAN_framework-optimization_v1.10.0.md
date: 2026-03-26
---

# TODO: Framework Optimization v1.10.0

Implementazione del Piano framework-optimization_v1.10.0: allineamento naming documenti, estensione Orchestrator Fase 0, skill error-recovery.

## Fasi

### Fase 1 — Allineamento naming e routing

- [x] Tabella naming in `docs_manager.skill.md` con motivazioni per tipo (DESIGN, PLAN, TODO, REPORT)
- [x] Correggi tabella bootstrap: `DESIGN_<feature>.md` (senza versione), `TODO_<feature>_vX.Y.Z.md` (con versione)
- [x] Aggiungi sezione "File temporanei" in `docs_manager.skill.md` (esclude findings.md)
- [x] Estendi Fase 0 Agent-Orchestrator: punti 2a, 2b, 2c per ripresa robusta
- [x] Aggiorna Fase 2 prompt: istruzioni aggiornamento coordinatore
- [x] Aggiorna Fase 3 prompt: istruzioni aggiornamento coordinatore (Piani + Tasks)
- [x] Aggiungi `docs_manager.skill.md` a "Riferimenti Skills" Agent-Design, Agent-Plan, Agent-Orchestrator
- [x] Aggiorna tabella skills README.md

**Commit Message Fase 1:**
```
docs(framework): allinea naming docs_manager.skill.md, estendi Fase 0 Orchestrator
```

### Fase 2 — Error recovery skill

- [x] Crea `error-recovery.skill.md` (max 2 tentativi, escalata, no riprova dopo fallimento)
- [x] Aggiungi `error-recovery.skill.md` a "Riferimenti Skills" Agent-Orchestrator
- [x] Aggiungi a inventario "Skills presenti" README.md
- [x] Aggiungi a tabella agenti-skills Agent-Orchestrator

**Commit Message Fase 2:**
```
docs(framework): crea error-recovery.skill.md (max 2 tentativi, escalata)
```

### Fase 3 — Gate minimale Fase 6

- [x] Aggiungi gate informale Fase 6: verifica che almeno 1 di [API.md, ARCHITECTURE.md, CHANGELOG.md] sia modificato
- [x] Eslint checks: none (documentale)

**Commit Message Fase 3:**
```
docs(framework): aggiungi gate informale Fase 6 Orchestrator
```

## Risultati

Tutte le modifiche applicate. **Integrazione logica completa** tra:
- Convenzioni naming (unified authority: docs_manager.skill.md)
- Routing skills (docs_manager referenziato da Design, Plan, Orchestrator)
- Ripresa sessione (Fase 0 esplicitamente disaccoppiata da TODO.md)
- Error recovery (procedura standardizzata 2 tentativi + escalata)

## Prossimi step

1. Commit e push delle modifiche
2. Aggiornamento FRAMEWORK_CHANGELOG.md per v1.10.0

