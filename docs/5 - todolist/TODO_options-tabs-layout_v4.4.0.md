---
type: todo
feature: options-tabs-layout
version: v4.4.0
status: COMPLETED
plan_ref: docs/3 - coding plans/PLAN_options-tabs-layout_v4.4.0.md
agent: Agent-Plan
date: 2026-04-09
---

# TODO — options-tabs-layout v4.4.0

Piano di riferimento completo:
[docs/3 - coding plans/PLAN_options-tabs-layout_v4.4.0.md](../3%20-%20coding%20plans/PLAN_options-tabs-layout_v4.4.0.md)

---

## Fase 1 — Riorganizza layout dialogo

- [x] creare `wx.Notebook` con tab Generale, Gameplay, Audio e Accessibilità, Visuale
- [x] spostare i controlli esistenti nei pannelli corretti
- [x] convertire il tema visivo a `wx.RadioBox`
- [x] aggiungere focus iniziale e cambio focus su cambio tab
- [x] mantenere pulsanti Salva/Annulla fuori dalle pagine notebook

## Fase 2 — Correggi stato e testi accessibili

- [x] aggiungere `draw_count` allo snapshot e restore del controller
- [x] aggiornare help text nel formatter ai comandi reali del dialogo wx
- [x] verificare binding eventi sul nuovo widget tema

## Fase 3 — Test e validazione

- [x] aggiungere smoke test per notebook e nuovi controlli
- [x] eseguire test opzioni dialogo e controller
- [x] verificare assenza di errori sui file modificati

## Fase 4 — Documentazione

- [x] aggiornare `CHANGELOG.md`
- [x] segnare questo TODO come completato
