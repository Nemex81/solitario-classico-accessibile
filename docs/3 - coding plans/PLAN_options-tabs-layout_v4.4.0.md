---
type: plan
feature: options-tabs-layout
version: v4.4.0
status: READY
agent: Agent-Plan
date: 2026-04-09
design_ref: docs/2 - projects/DESIGN_options-tabs-layout_v4.4.0.md
---

# PLAN — options-tabs-layout v4.4.0

## 1. Executive Summary

- Tipo: refactor UI accessibile + bugfix snapshot/controller
- Priorità: alta
- Target principale: `src/infrastructure/ui/options_dialog.py`
- Obiettivo: passare da layout lineare a `wx.Notebook` con quattro tab logiche, senza cambiare il contratto utente del dialogo.

---

## 2. Problema e Obiettivo

### Problema

La finestra opzioni contiene troppi controlli in un singolo flusso verticale, il tema visivo usa un widget incoerente rispetto agli altri, e il rollback del controller non ripristina `draw_count`.

### Obiettivo

1. Introdurre tab accessibili per categorie.
2. Conservare focus, ordine TAB e salvataggio live.
3. Correggere snapshot/restore del controller su `draw_count`.
4. Aggiornare l’help TTS del formatter ai comandi reali del dialogo wx.
5. Verificare il comportamento con test unitari e smoke test del dialogo.

---

## 3. File coinvolti

- MODIFY `src/infrastructure/ui/options_dialog.py`
- MODIFY `src/application/options_controller.py`
- MODIFY `src/presentation/options_formatter.py`
- MODIFY `tests/unit/presentation/test_options_dialog_audio.py`
- ADD `tests/unit/presentation/test_options_dialog_tabs.py`
- MODIFY `CHANGELOG.md`
- MODIFY `docs/TODO.md`
- MODIFY `docs/5 - todolist/TODO_options-tabs-layout_v4.4.0.md`

---

## 4. Fasi implementative

### Fase 1 — Refactor del dialogo

- Estrarre la costruzione delle pagine del notebook in helper privati.
- Creare notebook + quattro pannelli.
- Spostare i controlli nelle tab corrette.
- Convertire il tema visivo a `wx.RadioBox`.
- Aggiungere focus iniziale e gestione `EVT_NOTEBOOK_PAGE_CHANGED`.

### Fase 2 — Allineamento stato e formatter

- Correggere `_save_snapshot()` e `_restore_snapshot()` su `draw_count`.
- Aggiornare `OptionsFormatter.format_help_text()` ai comandi reali del dialogo wx.
- Verificare che non servano cambiamenti strutturali al controller.

### Fase 3 — Test

- Estendere i test del dialogo con verifiche su notebook, label tab, focus-map e nuovo widget tema.
- Eseguire i test del dialogo e quelli del controller opzioni rilevanti.

### Fase 4 — Sync docs

- Aggiornare `CHANGELOG.md` in `[Unreleased]`.
- Aggiornare il TODO per-task a completamento.

---

## 5. Rischi

- Focus NVDA sul cambio tab non automatico.
- Regressioni sui test che assumono l’esistenza di `visual_theme_choice`.
- Possibili riferimenti legacy a testi help ormai obsoleti.

---

## 6. Validazione prevista

- `py_compile` sui file modificati.
- test unit mirati per dialogo e controller opzioni.
- controllo errori su file toccati.
