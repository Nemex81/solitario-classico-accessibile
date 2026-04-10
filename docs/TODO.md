<!-- markdownlint-disable MD012 -->

# Coordinatore Documenti Attivi

<!--
COORDINATORE DOCUMENTI ATTIVI
tipo: todo_coordinator
data_creazione: 2026-03-26
agente: Agent-Plan / Agent-Docs
stato: attivo

Questo file è il coordinatore persistente del sistema documentale.
NON è una checklist di task: è l'indice dei lavori attivi.
Per i TODO specifici di implementazione: docs/5 - todolist/
Per aggiornamento e struttura: .github/skills/docs_manager.skill.md
-->

## Priorità Corrente

<!-- Task attivi con priorità massima — espansi qui per visibilità immediata -->

- ~~[TODO_cx-freeze-setup_v4.5.0.md](5%20-%20todolist/TODO_cx-freeze-setup_v4.5.0.md)~~
  Piano: [PLAN_cx-freeze-setup_v4.5.0.md](3%20-%20coding%20plans/PLAN_cx-freeze-setup_v4.5.0.md)
  Stato: COMPLETED — setup.py root creato e build cx_Freeze verificato (v4.5.0)

- **[ATTIVO — PRIORITARIO]** [TODO_options-tabs-layout_v4.4.0.md](5%20-%20todolist/TODO_options-tabs-layout_v4.4.0.md)
  Piano: [PLAN_options-tabs-layout_v4.4.0.md](3%20-%20coding%20plans/PLAN_options-tabs-layout_v4.4.0.md)
  Stato: ACTIVE — refactor finestra opzioni con notebook a tab, focus NVDA e grouping logico (v4.4.0)

- **[ATTIVO — PRIORITARIO]** [TODO_card-assets-integration_v4.3.0.md](5%20-%20todolist/TODO_card-assets-integration_v4.3.0.md)
  Piano: [PLAN_card-assets-integration_v4.3.0.md](3%20-%20coding%20plans/PLAN_card-assets-integration_v4.3.0.md)
  Stato: ACTIVE — fix path francesi + carte napoletane + back_bitmap, 4 fasi (v4.3.0)

- **[ATTIVO]** [TODO_gameplay-card-images_v4.1.0.md](5%20-%20todolist/TODO_gameplay-card-images_v4.1.0.md)
  Piano: [PLAN_gameplay-card-images_v4.1.0.md](3%20-%20coding%20plans/PLAN_gameplay-card-images_v4.1.0.md)
  Stato: Fase 0 in avvio — immagini reali carte francesi, 5 fasi (v4.1.0)

- ~~[TODO_gameplay-visual-ui_v4.0.0.md](5%20-%20todolist/TODO_gameplay-visual-ui_v4.0.0.md)~~ *(completato — rendering testuale v4.0.0)*

---

## Metadati

tipo: todo_coordinator
data_creazione: 2026-03-26
stato: attivo

## Progetti

<!-- Link relativi ai file attivi in docs/2 - projects/ -->

- [DESIGN_audio_system.md](2%20-%20projects/DESIGN_audio_system.md) — sistema audio (completato)
- [DESIGN_cx-freeze-setup_v4.5.0.md](2%20-%20projects/DESIGN_cx-freeze-setup_v4.5.0.md) — packaging Windows con setup.py e cx_Freeze (REVIEWED)
- [DESIGN_cx-freeze-frozen-runtime.md](2%20-%20projects/DESIGN_cx-freeze-frozen-runtime.md) — correttivo runtime/avvio frozen cx_Freeze (DRAFT)
- [DESIGN_selection-backspace-french-card-mapping_v4.3.1.md](2%20-%20projects/DESIGN_selection-backspace-french-card-mapping_v4.3.1.md) — backspace per annullamento selezione, replacement descrittivo e mapping carte francesi (DRAFT)
- [DESIGN_options-tabs-layout_v4.4.0.md](2%20-%20projects/DESIGN_options-tabs-layout_v4.4.0.md) — refactor dialogo opzioni con tab accessibili e grouping logico (REVIEWED)
- [DESIGN_framework-template-bootstrap.md](2%20-%20projects/DESIGN_framework-template-bootstrap.md) — integrazione template framework e bootstrap Agent-Welcome (reviewed)
- [DESIGN_gameplay-visual-ui.md](2%20-%20projects/DESIGN_gameplay-visual-ui.md) — supporto visivo finestra gameplay (reviewed)
- [DESIGN_tableau-adaptive-layout_v4.2.0.md](2%20-%20projects/DESIGN_tableau-adaptive-layout_v4.2.0.md) — layout adattivo tableau: overflow verticale carte (REVIEWED)

## Piani

<!-- Link relativi ai file attivi in docs/3 - coding plans/ -->

- [PLAN_document-governance_v1.9.0.md](3%20-%20coding%20plans/PLAN_document-governance_v1.9.0.md) — governance documentale (in corso)
- [PLAN_cx-freeze-setup_v4.5.0.md](3%20-%20coding%20plans/PLAN_cx-freeze-setup_v4.5.0.md) — definizione setup.py e validazione build cx_Freeze (READY)
- [PLAN_options-tabs-layout_v4.4.0.md](3%20-%20coding%20plans/PLAN_options-tabs-layout_v4.4.0.md) — refactor finestra opzioni con notebook accessibile (READY)
- [PLAN_game-engine-refactoring_v3.6.0.md](3%20-%20coding%20plans/PLAN_game-engine-refactoring_v3.6.0.md) — refactoring engine (legacy)
- [PLAN_e2e-resilience_v1.10.0.md](3%20-%20coding%20plans/PLAN_e2e-resilience_v1.10.0.md) — gate semantici, rollback, coverage SOT (completed)
- [PLAN_template-bootstrap-integration_v1.10.3.md](3%20-%20coding%20plans/PLAN_template-bootstrap-integration_v1.10.3.md) — bootstrap documentale core e integrazione template framework (completed)
- [PLAN_scf-mcp-server_v1.0.0.md](3%20-%20coding%20plans/PLAN_scf-mcp-server_v1.0.0.md) — server MCP locale per esposizione runtime del framework SCF (ready)
- [PLAN_gameplay-visual-ui_v4.0.0.md](3%20-%20coding%20plans/PLAN_gameplay-visual-ui_v4.0.0.md) — piano implementazione visual UI gameplay (reviewed — completato)
- [PLAN_gameplay-card-images_v4.1.0.md](3%20-%20coding%20plans/PLAN_gameplay-card-images_v4.1.0.md) — immagini reali carte francesi **(ready — in avvio)**
- [PLAN_tableau-adaptive-layout_v4.2.0.md](3%20-%20coding%20plans/PLAN_tableau-adaptive-layout_v4.2.0.md) — layout adattivo tableau, scaling fan offset per-pila (DRAFT)
- [PLAN_card-assets-integration_v4.3.0.md](3%20-%20coding%20plans/PLAN_card-assets-integration_v4.3.0.md) — fix path carte francesi, carte napoletane, back_bitmap **(READY)**
- [PLAN_cx-freeze-frozen-runtime_v4.5.1.md](3%20-%20coding%20plans/PLAN_cx-freeze-frozen-runtime_v4.5.1.md) — correttivo avvio/runtime frozen cx_Freeze: bootstrap diagnostico, path resolver, hardening TTS/audio, DLL validation **(DRAFT)**
- **[NUOVO]** [PLAN_selection-backspace-french-card-mapping_v4.3.1.md](3%20-%20coding%20plans/PLAN_selection-backspace-french-card-mapping_v4.3.1.md) — Backspace annulla selezione + annuncio vocale + fix mapping immagini francesi **(DRAFT)**

## Reports

<!-- Link relativi ai file attivi in docs/4 - reports/ -->

- [REPORT_gate-validation_2026-03-26.md](4%20-%20reports/REPORT_gate-validation_2026-03-26.md) — validazione document governance v1.9.0

## Tasks

<!-- Link relativi ai file attivi in docs/5 - todolist/ -->

- [TODO_cx-freeze-setup_v4.5.0.md](5%20-%20todolist/TODO_cx-freeze-setup_v4.5.0.md) — packaging cx_Freeze con setup.py root (COMPLETED)
- [TODO_options-tabs-layout_v4.4.0.md](5%20-%20todolist/TODO_options-tabs-layout_v4.4.0.md) — refactor finestra opzioni con tab accessibili (ACTIVE)
- [TODO_gameplay-visual-ui_v4.0.0.md](5%20-%20todolist/TODO_gameplay-visual-ui_v4.0.0.md) — implementazione visual UI gameplay **(prioritario — in esecuzione)**
- [TODO_document-governance_v1.9.0.md](5%20-%20todolist/TODO_document-governance_v1.9.0.md) — governance documentale (in corso)
- [TODO_e2e-resilience_v1.10.0.md](5%20-%20todolist/TODO_e2e-resilience_v1.10.0.md) — e2e resilience (completed)
- [TODO_template-bootstrap-integration_v1.10.3.md](5%20-%20todolist/TODO_template-bootstrap-integration_v1.10.3.md) — implementazione bootstrap template/framework (completed)
- [TODO_scf-mcp-server_v1.0.0.md](5%20-%20todolist/TODO_scf-mcp-server_v1.0.0.md) — implementazione server MCP SCF (completed)
- [TODO_gameplay-visual-ui_v4.0.0.md](5%20-%20todolist/TODO_gameplay-visual-ui_v4.0.0.md) — implementazione visual UI gameplay (completato — rendering testuale)
- [TODO_gameplay-card-images_v4.1.0.md](5%20-%20todolist/TODO_gameplay-card-images_v4.1.0.md) — immagini reali carte francesi **(prioritario — in avvio)**
- [TODO_tableau-adaptive-layout_v4.2.0.md](5%20-%20todolist/TODO_tableau-adaptive-layout_v4.2.0.md) — layout adattivo tableau (ACTIVE — 3 fasi)
- [TODO_card-assets-integration_v4.3.0.md](5%20-%20todolist/TODO_card-assets-integration_v4.3.0.md) — fix path francesi + carte napoletane + back_bitmap **(ACTIVE — 4 fasi)**
- [TODO_cx-freeze-frozen-runtime_v4.5.1.md](5%20-%20todolist/TODO_cx-freeze-frozen-runtime_v4.5.1.md) — correttivo avvio frozen: diagnostica, path resolver, hardening TTS/audio, DLL SDL2 **(ACTIVE — 6 fasi)**
- **[NUOVO]** [TODO_selection-backspace-french-card-mapping_v4.3.1.md](5%20-%20todolist/TODO_selection-backspace-french-card-mapping_v4.3.1.md) — Backspace annulla selezione + annuncio vocale + fix mapping immagini francesi **(DRAFT — 4 fasi)**

## Stato Avanzamento

- [x] Struttura inizializzata (2026-03-26)

