---
type: todo
feature: tableau-adaptive-layout
version: v4.2.0
status: CLOSED
plan: docs/3 - coding plans/PLAN_tableau-adaptive-layout_v4.2.0.md
agent: Agent-Plan
date: 2026-04-08
---

# TODO: Tableau Adaptive Layout — v4.2.0

Piano completo: [PLAN_tableau-adaptive-layout_v4.2.0.md](../3%20-%20coding%20plans/PLAN_tableau-adaptive-layout_v4.2.0.md)

---

## Istruzioni per Agent-Code

Eseguire le fasi in ordine sequenziale. Ogni fase termina con un commit atomico autonomo.
Prima di iniziare la Fase 2, verificare che tutti i test della Fase 1 passino (`pytest tests/unit/test_board_layout_manager.py -v`).
Non rompere test esistenti: `calculate_layout()` e i suoi test restano invariati.

---

## Checklist Fasi

### Fase 1 — `BoardLayoutManager.calculate_adaptive_tableau_layout()` + test unitari

**File:** `src/infrastructure/ui/board_layout_manager.py` + `tests/unit/test_board_layout_manager.py`

- [x] Aggiungere costanti `MIN_FD = 2` e `MIN_FU = 4` a livello di modulo o classe
- [x] Implementare `calculate_adaptive_tableau_layout(self, base_layout, pile_depths, panel_height)` con firma e docstring da DESIGN §5
- [x] Algoritmo scaling proporzionale (rapporto 1:3 face_down:face_up) con clamp ai minimi
- [x] Sollevare `ValueError` se `base_layout` non contiene le chiavi 0-12
- [x] Usare `dataclasses.replace()` per ogni `PileGeometry` modificata
- [x] Zero import `wx` nel file
- [x] Type hints completi su parametri e return type
- [x] Test `test_adaptive_layout_cards_within_panel_height` aggiunto e passante
- [x] Test `test_adaptive_layout_y_top_unchanged` aggiunto e passante
- [x] Test `test_adaptive_layout_no_overflow_not_modified` aggiunto e passante
- [x] Test `test_adaptive_layout_minimum_offsets_enforced` aggiunto e passante
- [x] Test `test_adaptive_layout_non_tableau_piles_unchanged` aggiunto e passante
- [x] `pytest tests/unit/test_board_layout_manager.py -v` — tutti i test PASS (nuovi + esistenti)
- [x] Commit atomico Fase 1 eseguito

---

### Fase 2 — Integrazione in `GameplayPanel._on_paint()`

**File:** `src/infrastructure/ui/gameplay_panel.py`

- [x] Localizzare il punto di chiamata a `calculate_layout()` in `_on_paint()`
- [x] Verificare che `board_state` (o `self._board_state`) sia disponibile nello scope
- [x] Costruire `pile_depths` come `dict[int, tuple[int, int]]` per i = 0..6
- [x] Chiamare `calculate_adaptive_tableau_layout(base_layout, pile_depths, panel_h)` e assegnare a `layout`
- [x] Sostituire tutti i riferimenti successivi al layout base con `layout` (adattivo)
- [x] Verificare che il rendering successivo al blocco usi la variabile `layout` aggiornata
- [x] `pytest` — 34/34 PASS, nessuna regressione
- [x] Commit atomico Fase 2 eseguito (fix test wiring incluso)

---

### Fase 3 — Pre-commit checklist completa

**Verifica finale prima del push**

- [x] `python -m py_compile src/infrastructure/ui/board_layout_manager.py` — OK
- [x] `python -m py_compile src/infrastructure/ui/gameplay_panel.py` — OK
- [x] `mypy src/ --strict` — zero errori di tipo
- [x] `pylint --enable=cyclic-import src/` — zero import ciclici
- [x] `grep -r "print(" src/` — zero occorrenze
- [x] `pytest --cov=src -v` — tutti i test PASS, soglia coverage rispettata (pyproject.toml)
- [x] `python scripts/validate_gates.py --check-all` — gate OK (warn legacy non correlato)

---

## Log Avanzamento

| Data | Fase | Azione | Esito |
|---|---|---|---|
| 2026-04-08 | — | PLAN e TODO creati da Agent-Plan | PRONTO |
