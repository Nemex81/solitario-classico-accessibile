---
type: design
feature: tableau-adaptive-layout
version: v4.2.0
status: DONE
agent: Agent-Design
date: 2026-04-08
---

# DESIGN: Tableau Adaptive Layout

## 1. Idea in 3 righe

`BoardLayoutManager.calculate_layout()` calcola `fan_offset_face_up` e `fan_offset_face_down` come frazioni fisse dell'altezza della carta, senza conoscere quante carte sono presenti nelle pile tableau. Questo causa overflow verticale: con 13 carte scoperte nella pila più lunga a fine partita, le carte escono oltre il bordo inferiore del panel. La soluzione introduce `calculate_adaptive_tableau_layout()`, che scala proporzionalmente gli offset per ogni pila quando il contenuto supera l'altezza disponibile, mantenendo la firma pubblica invariata e zero dipendenze wx.

---

## 2. Attori e Concetti

### Attori software coinvolti

- **`BoardLayoutManager`** (`src/infrastructure/ui/board_layout_manager.py`): componente presentation/infrastructure che calcola la geometria pixel di tutte e 13 le pile; pure-Python senza dipendenze wx; da estendere con il nuovo metodo adattivo.
- **`PileGeometry`** (`src/infrastructure/ui/board_layout_manager.py`): frozen dataclass che incapsula `x`, `y`, `card_width`, `card_height`, `fan_offset_face_up`, `fan_offset_face_down`; immutabile — le modifiche richiedono `dataclasses.replace()`.
- **`GameplayPanel`** (`src/infrastructure/ui/gameplay_panel.py`): panel wx presentation-layer che chiama `calculate_layout()` in `_on_paint()` e recupera le profondità delle pile dallo stato corrente del board per passarle al nuovo metodo adattivo.
- **`BoardState` DTO**: oggetto che trasporta lo stato corrente delle pile dall'application verso il presentation-layer, incluso il numero di carte coperte e scoperte per ogni pila tableau.

### Concetti chiave

- **Fan overflow**: condizione in cui la coordinata `y` dell'ultima carta di una pila tableau supera `panel_height`. Si verifica quando `bottom_zone_y + (n_fd * fan_offset_face_down) + (n_fu * fan_offset_face_up) + card_height > panel_height`.
- **Offset adattivo per-pila**: valore `fan_offset_face_up` e `fan_offset_face_down` calcolato individualmente per ogni pila in funzione della sua profondità, anziché fisso per tutte.
- **Scaling proporzionale**: riduzione uniforme di entrambi gli offset (mantenendo il rapporto `face_up / face_down ≈ 3 : 1`) fino a rientrare nel panel height, con floor ai minimi garantiti.
- **Minimi garantiti**: `fan_offset_face_down ≥ 2 px`, `fan_offset_face_up ≥ 4 px`; sotto questi valori le carte si sovrappongono troppo per essere percepite visivamente.
- **`dataclasses.replace()`**: meccanismo standard per produrre un nuovo `PileGeometry` a partire da uno esistente modificando solo i campi degli offset; rispetta l'immutabilità del frozen dataclass.

---

## 3. Flussi Concettuali

### 3.1 Flusso attuale (con overflow)

```
GameplayPanel._on_paint()
  └─ BoardLayoutManager.calculate_layout(w, h, theme)
       ├─ fan_face_up  = card_h // 3        ← fisso
       ├─ fan_face_down = max(4, card_h//5) ← fisso
       └─ layout[0..6] → PileGeometry con offset uniformi

  └─ GameRenderer.draw_tableau(layout, board_state)
       └─ card_y = pile.y + fd_count*fan_down + fu_count*fan_up
                                              ↑ può superare panel_height
```

### 3.2 Flusso proposto (layout adattivo)

```
GameplayPanel._on_paint()
  ├─ base_layout = BoardLayoutManager.calculate_layout(w, h, theme)
  │    [invariata — test esistenti preservati]
  │
  ├─ pile_depths = {i: (n_face_down[i], n_face_up[i]) for i in 0..6}
  │    [estratto da board_state corrente]
  │
  └─ adapted_layout = BoardLayoutManager.calculate_adaptive_tableau_layout(
         base_layout, pile_depths, panel_height
     )
       ├─ Per ogni pila i = 0..6:
       │    ├─ Calcola total_height(i) con offset base
       │    ├─ Se overflow → scala offset proporzionalmente
       │    └─ Clamp ai minimi garantiti
       └─ Restituisce dict[int, PileGeometry] con override solo pile 0-6;
          pile 7-12 (foundation, waste, stock) invariate

  └─ GameRenderer.draw_tableau(adapted_layout, board_state)
       └─ card_y ≤ panel_height garantito
```

### 3.3 Algoritmo di scaling (pseudocodice)

```
function adaptive_offsets(n_fd, n_fu, base_fd, base_fu, available_h):
    needed = n_fd * base_fd + n_fu * base_fu + card_height
    if needed <= available_h:
        return (base_fd, base_fu)        # nessun adattamento necessario

    # Spazio disponibile per il solo fan (esclusa altezza carta in cima)
    fan_space = max(0, available_h - card_height)

    # Mantieni rapporto 3:1 tra face_up e face_down
    # total_units = n_fd * 1 + n_fu * 3  (proporzionale ai base)
    total_units = n_fd * 1 + n_fu * 3
    if total_units == 0:
        return (base_fd, base_fu)

    unit = fan_space / total_units
    new_fd = max(MIN_FD, int(unit * 1))
    new_fu = max(MIN_FU, int(unit * 3))
    return (new_fd, new_fu)
```

dove `MIN_FD = 2`, `MIN_FU = 4`.

---

## 4. Decisioni Architetturali

### 4.1 Nuovo metodo in `BoardLayoutManager`, firma `calculate_layout` invariata

**Decisione**: aggiungere `calculate_adaptive_tableau_layout()` come metodo pubblico distinto, senza modificare `calculate_layout()`.

**Motivazione**: i test esistenti su `calculate_layout` restano validi senza modifiche. La separazione delle responsabilità è netta: `calculate_layout` produce il layout base geometricamente corretto (proporzionale al panel), `calculate_adaptive_tableau_layout` lo corregge in funzione del contenuto dinamico delle pile.

**Alternativa scartata**: modificare `calculate_layout` aggiungendo `pile_depths` come parametro opzionale. Scartata perché avrebbe reso la firma più fragile e avrebbe mescolato la logica di layout geometrico con la logica di adattamento ai dati di runtime.

### 4.2 Input `pile_depths` solo per le pile tableau (0-6)

**Decisione**: il parametro `pile_depths: dict[int, tuple[int, int]]` contiene solo le pile 0-6; le pile 7-12 non partecipano all'adattamento (sono stacked senza fan).

**Motivazione**: riflette la realtà del gioco — solo le pile tableau hanno fan verticale e possono causare overflow. Semplifica l'interfaccia e riduce l'accoppiamento con il board state.

### 4.3 Immutabilità di `PileGeometry` via `dataclasses.replace()`

**Decisione**: non rendere `PileGeometry` mutabile; usare `dataclasses.replace()` per produrre nuove istanze con offset modificati.

**Motivazione**: preserva la semantica di valore (value object) e la thread safety. Previene side-effect indesiderati su oggetti condivisi tra chiamate successive.

### 4.4 `BoardLayoutManager` rimane pure-Python (no wx)

**Decisione**: il nuovo metodo non importa né usa `wx` in nessuna forma.

**Motivazione**: mantiene la piena testabilità unitaria senza fixture wx. Rispetta il pattern già stabilito nella classe (zero dipendenze wx nella docstring di modulo).

### 4.5 Layer di appartenenza: Infrastructure/Presentation

**Decisione**: `BoardLayoutManager` appartiene al layer infrastructure (sotto-cartella `ui`), non al domain.

**Motivazione**: gestisce coordinate pixel e geometria schermo — responsabilità di presentazione tecnica, non regola di dominio. Non dipende da `src/domain` e non deve farlo. La dipendenza è unidirezionale: `GameplayPanel` (presentation) usa `BoardLayoutManager` (infrastructure/ui).

---

## 5. Contratto API

### Firma pubblica

```python
def calculate_adaptive_tableau_layout(
    self,
    base_layout: dict[int, PileGeometry],
    pile_depths: dict[int, tuple[int, int]],
    panel_height: int,
) -> dict[int, PileGeometry]:
    """Return layout with per-pile adaptive fan offsets for tableau piles 0-6.

    For each tableau pile, computes the minimum fan offsets (face-up and
    face-down) that keep all cards within *panel_height*, scaling
    proportionally when the base offsets would cause overflow.
    Piles 7-12 (foundation, waste, stock) are returned unchanged from
    *base_layout*.

    Args:
        base_layout: Output of :meth:`calculate_layout`; used as the
            geometric baseline (x, y, card dimensions, base offsets).
        pile_depths: Mapping from pile index 0-6 to a
            ``(n_face_down, n_face_up)`` tuple representing the number of
            face-down and face-up cards currently in that tableau pile.
            Missing keys are treated as ``(0, 0)``.
        panel_height: Current panel height in pixels; defines the lower
            bound within which all cards must remain.

    Returns:
        A new mapping of pile index (0-12) to :class:`PileGeometry`.
        For tableau piles (0-6) the ``fan_offset_face_up`` and
        ``fan_offset_face_down`` fields may differ from *base_layout*.
        For all other piles (7-12) the geometry is identical to
        *base_layout*.

    Raises:
        ValueError: If *base_layout* does not contain all pile indices 0-12.

    Post-conditions:
        - For every pile i in 0-6 with (n_fd, n_fu) = pile_depths.get(i, (0,0)):
              pile_y + n_fd * fan_offset_face_down + n_fu * fan_offset_face_up
              + card_height <= panel_height
          (guaranteed only when panel_height >= card_height + MIN_FD + MIN_FU;
           if panel_height is degenerate the minimums are still applied)
        - fan_offset_face_down >= 2  (MIN_FD)
        - fan_offset_face_up   >= 4  (MIN_FU)
        - pile.x and pile.y are unchanged vs base_layout for all piles
        - pile.card_width and pile.card_height are unchanged for all piles
    """
```

### Pre-condizioni

| Parametro | Vincolo |
|---|---|
| `base_layout` | Contiene esattamente le chiavi 0-12 |
| `pile_depths` | Valori `(n_fd, n_fu)` con entrambi ≥ 0; chiavi mancanti trattate come `(0, 0)` |
| `panel_height` | > 0 (valori degeneri clampati ai minimi garantiti) |

### Post-condizioni

- Per ogni pila `i` in 0-6: nessuna carta supera `panel_height`
- `fan_offset_face_down ≥ 2`, `fan_offset_face_up ≥ 4` per tutte le pile tableau adattate
- `pile.x`, `pile.y`, `pile.card_width`, `pile.card_height` identici a `base_layout` per tutte le pile

### Integrazione in `GameplayPanel._on_paint()`

```python
# Pseudocodice integrazione — dopo la chiamata esistente
base_layout = self._layout_manager.calculate_layout(
    panel_w, panel_h, self._theme
)
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
# Usa layout (adattivo) per tutto il rendering successivo
```

---

## 6. Impatto su test esistenti

### Test esistenti invariati

I test in `tests/unit/test_board_layout_manager.py` che coprono `calculate_layout()` **non si rompono** perché la firma di `calculate_layout` rimane immutata e nessun valore di ritorno viene modificato.

### Test aggiuntivi obbligatori (minimi)

#### `test_adaptive_layout_cards_within_panel_height`

**Obiettivo**: verificare che con un panel piccolo e molte carte in una pila, l'output di `calculate_adaptive_tableau_layout()` garantisca che l'altezza occupata da ogni pila non superi `panel_height`.

```python
def test_adaptive_layout_cards_within_panel_height() -> None:
    """All tableau cards must fit within panel_height after adaptation."""
    manager = BoardLayoutManager()
    theme = ThemeProperties()
    panel_w, panel_h = 800, 600
    base_layout = manager.calculate_layout(panel_w, panel_h, theme)

    # Pila 6 con 7 coperte + 13 scoperte = scenario peggiore
    pile_depths = {i: (0, 0) for i in range(7)}
    pile_depths[6] = (7, 13)

    adapted = manager.calculate_adaptive_tableau_layout(
        base_layout, pile_depths, panel_h
    )

    for pile_idx, (n_fd, n_fu) in pile_depths.items():
        geo = adapted[pile_idx]
        total_h = (
            geo.y
            + n_fd * geo.fan_offset_face_down
            + n_fu * geo.fan_offset_face_up
            + geo.card_height
        )
        assert total_h <= panel_h, (
            f"Pile {pile_idx}: total_h={total_h} > panel_h={panel_h}"
        )
```

#### `test_adaptive_layout_y_top_unchanged`

**Obiettivo**: verificare che la coordinata `y` superiore di ogni pila tableau sia identica nel layout adattivo e nel layout base (l'allineamento del bordo superiore non deve mai cambiare).

```python
def test_adaptive_layout_y_top_unchanged() -> None:
    """Top-y of every tableau pile must be identical before and after adaptation."""
    manager = BoardLayoutManager()
    theme = ThemeProperties()
    panel_w, panel_h = 800, 600
    base_layout = manager.calculate_layout(panel_w, panel_h, theme)

    pile_depths = {i: (i + 1, i * 2 + 1) for i in range(7)}

    adapted = manager.calculate_adaptive_tableau_layout(
        base_layout, pile_depths, panel_h
    )

    for i in range(7):
        assert adapted[i].y == base_layout[i].y, (
            f"Pile {i}: y changed from {base_layout[i].y} to {adapted[i].y}"
        )
```

#### Test aggiuntivi consigliati

- `test_adaptive_layout_no_overflow_not_modified`: verifica che se nessuna pila è in overflow, gli offset adattivi siano uguali a quelli base (nessuna modifica inutile).
- `test_adaptive_layout_minimum_offsets_enforced`: verifica che con panel_height molto piccolo, `fan_offset_face_down ≥ 2` e `fan_offset_face_up ≥ 4` per tutte le pile adattate.
- `test_adaptive_layout_non_tableau_piles_unchanged`: verifica che le pile 7-12 nel layout adattivo abbiano geometria identica al layout base.

---

## 7. Impatto su NVDA / Accessibilità

Il layout adattivo **non modifica** le coordinate usate dal canale NVDA.

Le informazioni comunicate a NVDA (tramite `ScreenReader` / info-zone off-screen) sono derivate dallo stato logico del gioco (nome pila, rank, seme, coperta/scoperta) e non dalle coordinate pixel. `BoardLayoutManager` opera esclusivamente nel dominio pixel/presentazione; il canale TTS SAPI5 e il canale NVDA non dipendono da `PileGeometry`.

Conseguenza: nessuna modifica richiesta in `ScreenReader`, `screen_reader.py`, né nella info-zone wx. L'accessibilità audio-only per giocatori non vedenti è preservata integralmente.

---

## 8. Pattern Architetturale

### Layer di appartenenza

```
Presentation (GameplayPanel)
      │
      ▼
Infrastructure / UI  (BoardLayoutManager  ←  nuovo metodo qui)
      │
      ▼  [nessuna freccia verso il basso — no dipendenze domain]
Domain  [NON COINVOLTO]
```

### Invarianti Clean Architecture

- `BoardLayoutManager` non importa da `src/domain/` né da `src/application/`.
- `GameplayPanel` riceve `pile_depths` da `board_state` (già disponibile in `_on_paint`); nessun nuovo accoppiamento cross-layer introdotto.
- Il DTO `BoardState` (già esistente) trasporta i dati delle pile senza esporre entità domain.
- Pure-Python: testabilità unitaria completa senza mock wx.

### Rischi e Vincoli

| Rischio | Mitigazione |
|---|---|
| Panel height degenere (< card_height) | Clamp ai minimi garantiti MIN_FD/MIN_FU; non sollevare eccezioni |
| `pile_depths` con chiavi mancanti | Trattare come `(0, 0)`; documentato nella post-condizione |
| Performance: metodo chiamato ogni `_on_paint` | O(7) operazioni scalari; trascurabile rispetto al rendering wx |
| Regressione test esistenti | Firma `calculate_layout` invariata; nessun test esistente modificato |
| `PileGeometry` frozen (immutabile) | Usare `dataclasses.replace()` per ogni istanza modificata |
