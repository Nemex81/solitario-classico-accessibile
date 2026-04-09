---
type: todo
feature: cx-freeze-setup
version: v4.5.0
status: COMPLETED
plan_ref: docs/3 - coding plans/PLAN_cx-freeze-setup_v4.5.0.md
agent: Agent-Plan
date: 2026-04-09
---

# TODO — cx-freeze-setup v4.5.0

Piano di riferimento completo:
[docs/3 - coding plans/PLAN_cx-freeze-setup_v4.5.0.md](../3%20-%20coding%20plans/PLAN_cx-freeze-setup_v4.5.0.md)

---

## Fase 1 — Crea setup.py

- [x] definire `build_exe_options` per packages, excludes e include_files
- [x] configurare `Executable` per `acs_wx.py`
- [x] allineare output a `dist/solitario-classico`

## Fase 2 — Valida build

- [x] eseguire `py_compile setup.py`
- [x] eseguire `python setup.py build_exe`
- [x] verificare `dist/solitario-classico/solitario.exe`

## Fase 3 — Documentazione

- [x] aggiornare `CHANGELOG.md`
- [x] segnare questo TODO come completato
