---
type: plan
feature: tableau-adaptive-layout
version: v4.2.0
status: DONE
design: docs/2 - projects/DESIGN_tableau-adaptive-layout_v4.2.0.md
agent: Agent-Plan
date: 2026-04-08
---

# PLAN: Tableau Adaptive Layout — v4.2.0

## 1. Executive Summary

| Campo | Valore |
|---|---|
| Tipo | Feature — nuova funzionalità non breaking |
| Priorità | Alta (regressione visiva: overflow carte tableau in partite avanzate) |
| Branch | `feature/tableau-adaptive-layout-v4.2.0` |
| Versione target | v4.2.0 |
| Design di riferimento | [DESIGN_tableau-adaptive-layout_v4.2.0.md](../2%20-%20projects/DESIGN_tableau-adaptive-layout_v4.2.0.md) |
| Commit atomici | 3 (uno per file modificato) |

---

## 2. Problema e Obiettivo

### Problema

`BoardLayoutManager.calculate_layout()` calcola `fan_offset_face_up` e `fan_offset_face_down` come frazioni fisse dell'altezza della carta, senza tenere conto del numero di carte presenti in ogni pila tableau. Con 13 carte scoperte nella pila più lunga in una partita avanzata, l'ultima carta esce oltre il bordo inferiore del panel (`panel_height` superato), rendendo il rendering visivo compromesso.

### Obiettivo

Aggiungere `BoardLayoutManager.calculate_adaptive_tableau_layout()` — metodo pubblico, pure-Python, zero import wx — che riceve il layout base, le profondità delle pile (0-6) e l'altezza del panel, e restituisce un dizionario `dict[int, PileGeometry]` con offset fan scalati proporzionalmente (rapporto 3:1 face_up/face_down) per garantire che tutte le carte restino entro `panel_height`. Integrare la chiamata in `GameplayPanel._on_paint()` dopo `calculate_layout()`.

### Invarianti garantite

- Firma di `calculate_layout()` invariata (test esistenti non si rompono).
- `PileGeometry` rimane frozen dataclass; ogni modifica usa `dataclasses.replace()`.
- `BoardLayoutManager` rimane pure-Python (zero dipendenze wx).
- `pile.x` e `pile.y` identici al layout base per tutte le pile.
- `fan_offset_face_down ≥ 2 px`, `fan_offset_face_up ≥ 4 px` (floor garantiti).

---

## 3. File Coinvolti

| File | Operazione | Note |
|---|---|---|
| `src/infrastructure/ui/board_layout_manager.py` | MODIFY | Aggiungere metodo `calculate_adaptive_tableau_layout()` e costanti `MIN_FD`, `MIN_FU` |
| `tests/unit/test_board_layout_manager.py` | MODIFY | Aggiungere 5 test: 2 obbligatori + 3 edge case |
| `src/infrastructure/ui/gameplay_panel.py` | MODIFY | Integrare chiamata metodo adattivo in `_on_paint()` dopo `calculate_layout()` |

---

## 4. Fasi Sequenziali

### Fase 1 — `BoardLayoutManager.calculate_adaptive_tableau_layout()` + test unitari

**File modificati:**

- `src/infrastructure/ui/board_layout_manager.py` (MODIFY)
- `tests/unit/test_board_layout_manager.py` (MODIFY)

**Descrizione:**

Aggiungere in coda alla classe `BoardLayoutManager` il metodo pubblico `calculate_adaptive_tableau_layout()`.

**Algoritmo (da DESIGN §3.3):**

Per ogni pila `i` in 0-6:

1. Recupera `(n_fd, n_fu) = pile_depths.get(i, (0, 0))`.
2. Calcola `needed = geom.y + n_fd * geom.fan_offset_face_down + n_fu * geom.fan_offset_face_up + geom.card_height`.
3. Se `needed <= panel_height`: nessuna modifica, usa geometria base.
4. Altrimenti:
   - `available_h = max(0, panel_height - geom.y - geom.card_height)`
   - `total_units = n_fd * 1 + n_fu * 3`  (rapporto 1:3)
   - Se `total_units == 0`: usa geometria base.
   - `unit = available_h / total_units`
   - `new_fd = max(MIN_FD, int(unit * 1))`
   - `new_fu = max(MIN_FU, int(unit * 3))`
   - Produce `dataclasses.replace(geom, fan_offset_face_down=new_fd, fan_offset_face_up=new_fu)`.
5. Pile 7-12: copia invariata da `base_layout`.

**Costanti da aggiungere (a livello di modulo o di classe):**

```python
MIN_FD: int = 2   # fan_offset_face_down minimo garantito
MIN_FU: int = 4   # fan_offset_face_up minimo garantito
```

**Firma pubblica (da DESIGN §5):**

```python
def calculate_adaptive_tableau_layout(
    self,
    base_layout: dict[int, PileGeometry],
    pile_depths: dict[int, tuple[int, int]],
    panel_height: int,
) -> dict[int, PileGeometry]:
    ...
```

**Raises:** `ValueError` se `base_layout` non contiene tutte le chiavi 0-12.

**Test da aggiungere in `tests/unit/test_board_layout_manager.py`:**

- `test_adaptive_layout_cards_within_panel_height` — scenario peggiore: pila 6 con (7, 13); verifica che l'altezza occupata di ogni pila non superi `panel_height`.
- `test_adaptive_layout_y_top_unchanged` — verifica che `adapted[i].y == base_layout[i].y` per tutte le pile 0-6 dopo l'adattamento.
- `test_adaptive_layout_no_overflow_not_modified` — nessuna pila in overflow: gli offset adattivi devono essere identici a quelli base.
- `test_adaptive_layout_minimum_offsets_enforced` — `panel_height` molto piccolo: `fan_offset_face_down ≥ 2` e `fan_offset_face_up ≥ 4` garantiti.
- `test_adaptive_layout_non_tableau_piles_unchanged` — pile 7-12: `PileGeometry` identica al layout base.

**Commit atomico:**

```bash
git add src/infrastructure/ui/board_layout_manager.py tests/unit/test_board_layout_manager.py
git commit -m "feat(infrastructure): add calculate_adaptive_tableau_layout to BoardLayoutManager

Adds proportional fan-offset scaling per-pile to prevent vertical overflow.
Invariants: MIN_FD=2, MIN_FU=4, ratio 3:1 face_up/face_down.
Uses dataclasses.replace() — PileGeometry remains frozen.
Test coverage: 5 unit tests including edge cases (empty pile, single card, all face-down)."
```

---

### Fase 2 — Integrazione in `GameplayPanel._on_paint()`

**File modificati:**

- `src/infrastructure/ui/gameplay_panel.py` (MODIFY)

**Descrizione:**

Dopo la chiamata esistente a `calculate_layout()` in `_on_paint()`, aggiungere la chiamata a `calculate_adaptive_tableau_layout()`:

```python
# Esistente — invariato
base_layout = self._layout_manager.calculate_layout(panel_w, panel_h, self._theme)

# --- NUOVO BLOCCO ---
pile_depths = {
    i: (
        len([c for c in board_state.piles[i] if not c.face_up]),
        len([c for c in board_state.piles[i] if c.face_up]),
    )
    for i in range(7)
}
layout = self._layout_manager.calculate_adaptive_tableau_layout(
    base_layout, pile_depths, panel_h
)
# --- FINE NUOVO BLOCCO ---

# Uso di layout (adattivo) per tutto il rendering successivo
```

**Nota**: verificare che la variabile `board_state` sia già disponibile nello scope di `_on_paint()` al punto di integrazione. Se è recuperata tramite `self._board_state` o parametro, adattare il riferimento di conseguenza senza modificare la firma del metodo.

**Commit atomico:**

```bash
git add src/infrastructure/ui/gameplay_panel.py
git commit -m "feat(presentation): integrate adaptive tableau layout in GameplayPanel._on_paint

Calls calculate_adaptive_tableau_layout after calculate_layout.
Extracts pile_depths from board_state.piles[0..6].
All subsequent rendering uses the adapted layout — no overflow guaranteed."
```

---

### Fase 3 — Pre-commit checklist completa

**Descrizione:**

Eseguire la sequenza di validazione obbligatoria definita in `workflow-standard.instructions.md` prima di ogni push/merge.

**Comandi da eseguire (in ordine):**

```bash
# 1. Compilazione sintattica
python -m py_compile src/infrastructure/ui/board_layout_manager.py
python -m py_compile src/infrastructure/ui/gameplay_panel.py

# 2. Type checking strict
mypy src/ --strict

# 3. Lint import ciclici
pylint --enable=cyclic-import src/

# 4. Zero print() in src/
grep -r "print(" src/

# 5. Coverage (soglia da pyproject.toml)
pytest --cov=src tests/unit/test_board_layout_manager.py -v

# 6. Suite completa
pytest --cov=src -v
```

**Soglia coverage**: come definita in `pyproject.toml` (verificare sezione `[tool.pytest.ini_options]` o `[tool.coverage.report]`).

**Commit atomico per la checklist**:

Non previsto: la Fase 3 è una validazione pre-push, non produce file aggiuntivi.

---

## 5. Test Plan

### Unit test (Fase 1)

| Test | File | Obiettivo |
|---|---|---|
| `test_adaptive_layout_cards_within_panel_height` | `tests/unit/test_board_layout_manager.py` | Overflow impossibile dopo adattamento — scenario peggiore |
| `test_adaptive_layout_y_top_unchanged` | `tests/unit/test_board_layout_manager.py` | Coordinate `y` invariate |
| `test_adaptive_layout_no_overflow_not_modified` | `tests/unit/test_board_layout_manager.py` | Nessuna modifica inutile se non c'è overflow |
| `test_adaptive_layout_minimum_offsets_enforced` | `tests/unit/test_board_layout_manager.py` | Floor MIN_FD=2, MIN_FU=4 garantiti anche con panel degenere |
| `test_adaptive_layout_non_tableau_piles_unchanged` | `tests/unit/test_board_layout_manager.py` | Pile 7-12 identiche al base layout |

### Test di integrazione (Fase 2)

Verifica manuale: avviare la partita, portare una o più pile tableau a profondità elevata (es. 10+ carte scoperte), verificare che il rendering non esca oltre il bordo inferiore del panel. Non è previsto un test automatizzato di integrazione wx (richiede fixture grafica pesante).

### Regressione

I test esistenti su `calculate_layout()` non devono essere modificati e devono passare senza errori prima e dopo entrambe le fasi.

---

## 6. Note Operative per Agent-Code

- Lavorare sempre su un branch dedicato (`feature/tableau-adaptive-layout-v4.2.0`), mai su `main`.
- Rispettare l'ordine delle fasi: Fase 1 (metodo + test) prima di Fase 2 (integrazione).
- Dopo Fase 1, eseguire `pytest tests/unit/test_board_layout_manager.py` prima di procedere.
- Non rompere test esistenti: rileggere la suite corrente in `test_board_layout_manager.py` prima di modificare il file.
- Usare `dataclasses.replace()` — mai assegnazione diretta ai campi di `PileGeometry`.
- Zero import `wx` in `board_layout_manager.py`.
- Type hints obbligatori su tutti i parametri e return type del nuovo metodo.
