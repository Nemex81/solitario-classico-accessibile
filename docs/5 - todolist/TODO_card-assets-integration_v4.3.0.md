---
type: todo
feature: card-assets-integration
version: v4.3.0
status: COMPLETED
plan_ref: docs/3 - coding plans/PLAN_card-assets-integration_v4.3.0.md
agent: Agent-Plan
date: 2026-04-08
---

# TODO â€” card-assets-integration v4.3.0

Piano di riferimento completo (fonte di veritÃ ):
[docs/3 - coding plans/PLAN_card-assets-integration_v4.3.0.md](../3%20-%20coding%20plans/PLAN_card-assets-integration_v4.3.0.md)

---

## Istruzioni per Agent-Code

1. Implementa le fasi **nell'ordine indicato** (1 â†’ 2 â†’ 3 â†’ 4).
2. Dopo ogni fase esegui **nell'ordine**: `py_compile` â†’ `mypy --strict` â†’ `pytest` (suite
   indicata per la fase).
3. Effettua un **commit atomico** dopo la validazione riuscita di ogni fase.
4. **Spunta le checkbox** di tutte le operazioni completate in questo file prima di passare
   alla fase successiva.
5. Non passare alla fase successiva se anche un solo test o controllo statico fallisce.

---

## Fase 1 â€” Fix path carte francesi + mapping napoletano in `CardImageCache`

**File**: `src/infrastructure/ui/card_image_cache.py`

### Operazioni

- [x] 1.1 Fix path: cambia `"carte francesi"` â†’ `"carte_francesi"` in `_load_source()`
- [x] 1.2 Aggiungi costanti di modulo: `_NAPOL_RANK_POS`, `_NAPOL_SUIT_OFFSET`,
  `_NAPOL_SEQ_TO_NOME`, `_NAPOL_SUIT_CASE_EXCEPTIONS` (prima della classe)
- [x] 1.3 Aggiungi parametro `deck_type: str = "french"` a `__init__`; inizializza
  `self._deck_type`, `self._back_source`, `self._back_cache`
- [x] 1.4 Aggiungi metodo privato `_load_source_napoletane(rank, suit) -> object | None`
  con calcolo seq, nome, eccezione case seme, caricamento `wx.Image`
- [x] 1.5 Modifica `_load_source`: routing `deck_type == "neapolitan"` â†’
  `_load_source_napoletane`, altrimenti logica francesi esistente
- [x] 1.6 Aggiungi metodo `get_back_bitmap(width, height) -> object | None` (cache +
  caricamento `41_Carte_Napoletane_retro.jpg`)
- [x] 1.7 Aggiorna `invalidate_size_cache`: aggiungere `self._back_cache.clear()`

### Test (in `tests/unit/test_card_image_cache.py`)

- [x] 1.T1 `test_french_path_uses_underscore` â€” path contiene `carte_francesi`
- [x] 1.T2 `test_load_source_routes_to_napoletane` â€” routing a `_load_source_napoletane`
- [x] 1.T3 `test_napoletane_seq_bastoni_asso` â€” seq=1, filename `1_Asso_di_bastoni.jpg`
- [x] 1.T4 `test_napoletane_seq_coppe_re` â€” Re di coppe â†’ `20_Dieci_di_coppe.jpg`
- [x] 1.T5 `test_napoletane_case_exception_bastoni_dieci` â€” Re di bastoni â†’
  `10_Dieci_di_Bastoni.jpg` (B maiuscolo)
- [x] 1.T6 `test_get_back_bitmap_french_returns_none` â€” `deck_type="french"` â†’ `None`
- [x] 1.T7 `test_get_back_bitmap_napoletane_file_missing_returns_none` â€” file assente â†’ `None`
- [x] 1.T8 `test_invalidate_clears_back_cache` â€” `invalidate_size_cache()` svuota
  `_back_cache`

### Validazione Fase 1

- [x] `python -m py_compile src/infrastructure/ui/card_image_cache.py` â€” exit 0
- [x] `mypy src/infrastructure/ui/card_image_cache.py --strict` â€” exit 0
- [x] `pytest tests/unit/test_card_image_cache.py -v` â€” 100% pass

### Commit Fase 1

- [x] Commit:
  `fix(infrastructure): fix path carte francesi e aggiungi supporto carte napoletane in CardImageCache`

---

## Fase 2 â€” Estendi `CardRenderer` con parametro `back_bitmap`

**File**: `src/infrastructure/ui/card_renderer.py`

### Operazioni

- [x] 2.1 Aggiungere parametro `back_bitmap: object | None = None` alla firma di `draw_card()`
  (dopo il parametro `bitmap`)
- [x] 2.2 Nel ramo `not card.face_up`: se `back_bitmap is not None` â†’ chiamare
  `_draw_face_image(dc, back_bitmap, ...)`, altrimenti `_draw_back(...)` (fallback)

### Test (in `tests/unit/test_card_renderer.py`)

- [x] 2.T1 `test_draw_card_back_uses_back_bitmap_when_provided` â€” carta coperta +
  `back_bitmap` mock â†’ `DrawBitmap` chiamato
- [x] 2.T2 `test_draw_card_back_uses_procedural_when_no_back_bitmap` â€” carta coperta senza
  `back_bitmap` â†’ `_draw_back` chiamato

### Validazione Fase 2

- [x] `python -m py_compile src/infrastructure/ui/card_renderer.py` â€” exit 0
- [x] `mypy src/infrastructure/ui/card_renderer.py --strict` â€” exit 0
- [x] `pytest tests/unit/test_card_renderer.py -v` â€” 100% pass

### Commit Fase 2

- [x] Commit:
  `feat(presentation): aggiungi supporto back_bitmap a CardRenderer.draw_card`

---

## Fase 3 â€” Aggiorna `GameplayPanel` per cache deck-type-aware e dorso

**File**: `src/infrastructure/ui/gameplay_panel.py`

### Pre-operazione (lettura contesto)

- [x] 3.0 Leggere `_on_paint()` in `gameplay_panel.py`: annotare struttura `board_state` e
  punto di accesso a `deck_type`

### Operazioni

- [x] 3.1 Aggiungere `self._current_deck_type: str = ""` in `__init__`
- [x] 3.2 Modificare `_get_image_cache()`: aggiungere parametro `deck_type: str = "french"`;
  reinizializzare cache se `None` o se `deck_type != self._current_deck_type`
- [x] 3.3 In `_on_paint()`: determinare `deck_type` da `board_state.deck_type` o
  `self._settings.deck_type` (default `"french"` se assente)
- [x] 3.4 Aggiornare call site `_get_image_cache()` per passare `deck_type`
- [x] 3.5 Nel loop rendering carte face-down: ottenere
  `back_bmp = cache.get_back_bitmap(card_w, card_h)` e passare
  `renderer.draw_card(..., back_bitmap=back_bmp)`

### Validazione Fase 3

- [x] `python -m py_compile src/infrastructure/ui/gameplay_panel.py` â€” exit 0
- [x] `mypy src/infrastructure/ui/gameplay_panel.py --strict` â€” exit 0
- [x] `pytest tests/unit/presentation/ -v` â€” 100% pass (suite regressione)

### Commit Fase 3

- [x] Commit:
  `feat(presentation): aggiorna GameplayPanel per cache deck-type-aware e dorso napoletano`

---

## Fase 4 â€” Validazione finale e CHANGELOG

### Operazioni

- [x] 4.1 Compilazione statica completa (tutti e tre i file modificati) â€” exit 0
- [x] 4.2 `mypy` completo sui tre file â€” exit 0
- [x] 4.3 `pytest tests/unit/test_card_image_cache.py tests/unit/test_card_renderer.py
  tests/unit/presentation/test_gameplay_visual_wiring.py -v` â€” 100% pass
- [x] 4.4 Aggiornare `CHANGELOG.md` sezione `[Unreleased]`:
  - **Fixed**: path `carte_francesi` corretto in `CardImageCache`
  - **Added**: supporto carte napoletane in `CardImageCache` (`deck_type="neapolitan"`)
  - **Added**: `get_back_bitmap()` in `CardImageCache`
  - **Added**: parametro `back_bitmap` a `CardRenderer.draw_card()`
  - **Added**: `GameplayPanel` deck-type-aware con dorso immagine reale

### Commit Fase 4

- [x] Commit:
  `fix+test(infrastructure/presentation): validazione card-assets-integration v4.3.0`

