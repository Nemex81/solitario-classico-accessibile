---
type: plan
feature: cx-freeze-setup
version: v4.5.0
status: READY
agent: Agent-Plan
date: 2026-04-09
design_ref: docs/2 - projects/DESIGN_cx-freeze-setup_v4.5.0.md
---

# PLAN — cx-freeze-setup v4.5.0

## 1. Executive Summary

- Tipo: packaging/build enablement
- Priorità: alta
- Obiettivo: creare `setup.py` root compatibile con `cx_Freeze` e verificare la generazione dell’eseguibile Windows.

---

## 2. Problema e Obiettivo

### Problema

Lo script di release invoca `setup.py build_exe`, ma `setup.py` non esiste e quindi il build dell’eseguibile è impossibile.

### Obiettivo

1. Creare `setup.py` con configurazione `cx_Freeze` per `acs_wx.py`.
2. Includere asset, sound pack e file JSON di configurazione.
3. Verificare che `python setup.py build_exe` produca `dist/solitario-classico/solitario.exe`.
4. Aggiornare il changelog e il TODO del task.

---

## 3. File coinvolti

- ADD `setup.py`
- MODIFY `CHANGELOG.md`
- MODIFY `docs/TODO.md`
- MODIFY `docs/5 - todolist/TODO_cx-freeze-setup_v4.5.0.md`

---

## 4. Fasi implementative

### Fase 1 — Implementazione setup.py

- leggere versione e metadati base dal repository
- definire `build_exe_options` per packages, includes, excludes e include_files
- configurare `Executable('acs_wx.py', base='Win32GUI', target_name='solitario.exe')`
- impostare `build_exe='dist/solitario-classico'`

### Fase 2 — Validazione build

- eseguire `py_compile` sul nuovo `setup.py`
- eseguire `python setup.py build_exe`
- verificare presenza di `dist/solitario-classico/solitario.exe`

### Fase 3 — Documentazione

- aggiornare `CHANGELOG.md` in `[Unreleased]`
- segnare il TODO del task come completato

---

## 5. Rischi

- path runtime diversi tra codice frozen e codice eseguito da sorgente
- hidden imports di `wx`, `pygame` o `accessible_output2` non catturati automaticamente
- build lento o rumoroso per dipendenze native Windows

---

## 6. Validazione prevista

- `py_compile setup.py`
- `python setup.py build_exe`
- controllo presenza artefatto `dist/solitario-classico/solitario.exe`
