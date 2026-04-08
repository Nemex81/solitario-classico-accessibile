---
type: plan
feature: card-assets-integration
version: v4.3.0
status: READY
agent: Agent-Plan
date: 2026-04-08
design_ref: docs/2 - projects/DESIGN_card-assets-integration_v4.3.0.md
---

# PLAN — card-assets-integration v4.3.0

## 1. Executive Summary

| Campo        | Valore                                                  |
|--------------|---------------------------------------------------------|
| Tipo         | Feature + Fix (infrastructure + presentation)           |
| Priorità     | Alta — prerequisito per rendering carte napoletane      |
| Branch       | `feat/card-assets-integration-v4.3.0`                  |
| Versione     | v4.3.0                                                  |
| Design ref   | `docs/2 - projects/DESIGN_card-assets-integration_v4.3.0.md` |
| Agente       | Agent-Code (implementazione), Agent-Plan (questo piano) |

---

## 2. Problema e Obiettivo

### Problema

Il sistema di rendering carte ha due difetti bloccanti:

- Il path verso le immagini carte francesi contiene uno spazio (`"carte francesi"`) invece di un
  underscore (`"carte_francesi"`), causando file-not-found a runtime.
- Non esiste alcun meccanismo per caricare le immagini delle carte napoletane né per
  visualizzare il dorso del mazzo napoletano durante il gioco.

### Obiettivo

1. Fix immediato del path errato in `CardImageCache._load_source()`.
2. Aggiungere il supporto al mazzo napoletano in `CardImageCache` (mapping rank/suit →
   filename JPEG, caricamento dorso).
3. Estendere `CardRenderer.draw_card()` con il parametro `back_bitmap` per usare un'immagine
   reale come dorso invece del disegno procedurale.
4. Aggiornare `GameplayPanel` per istanziare la cache con il `deck_type` corretto e passare
   il `back_bitmap` al renderer.

---

## 3. File coinvolti

| Operazione | File                                                  |
|------------|-------------------------------------------------------|
| MODIFY     | `src/infrastructure/ui/card_image_cache.py`           |
| MODIFY     | `src/infrastructure/ui/card_renderer.py`              |
| MODIFY     | `src/infrastructure/ui/gameplay_panel.py`             |
| MODIFY     | `tests/unit/test_card_image_cache.py`                 |
| MODIFY     | `tests/unit/test_card_renderer.py`                    |

---

## 4. Fasi implementative

### Fase 1 — Fix path carte francesi + mapping napoletano in `CardImageCache`

**File**: `src/infrastructure/ui/card_image_cache.py`

**Operazioni atomiche**:

1. **Fix path** (singola riga): cambia `"carte francesi"` → `"carte_francesi"` in
   `_load_source()`.

2. **Aggiungi costanti di modulo** (prima della definizione della classe `CardImageCache`):

   ```python
   _NAPOL_RANK_POS: dict[str, int] = {
       "Asso": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
       "Regina": 8, "Cavallo": 9, "Re": 10,
   }
   _NAPOL_SUIT_OFFSET: dict[str, int] = {
       "bastoni": 0, "coppe": 10, "denari": 20, "spade": 30,
   }
   _NAPOL_SEQ_TO_NOME: dict[int, str] = {
       1: "Asso", 2: "Due", 3: "Tre", 4: "Quattro", 5: "Cinque",
       6: "Sei", 7: "Sette", 8: "Otto", 9: "Nove", 10: "Dieci",
   }
   # Eccezione naming: seq=10 → seme "Bastoni" (maiuscolo) invece di "bastoni"
   _NAPOL_SUIT_CASE_EXCEPTIONS: dict[tuple[int, int], str] = {
       (10, 0): "Bastoni",   # 10_Dieci_di_Bastoni.jpg
   }
   ```

3. **Aggiungi parametro `deck_type`** a `__init__`:

   ```python
   def __init__(
       self,
       assets_base_path: str | os.PathLike[str],
       deck_type: str = "french",
   ) -> None:
       ...
       self._deck_type: str = deck_type
       self._back_source: object | None = None
       self._back_cache: dict[tuple[int, int], object] = {}
   ```

4. **Aggiungi metodo privato** `_load_source_napoletane(rank, suit) -> object | None`:

   ```python
   def _load_source_napoletane(self, rank: str, suit: str) -> object | None:
       rank_pos = _NAPOL_RANK_POS.get(rank)
       suit_offset = _NAPOL_SUIT_OFFSET.get(suit)
       if rank_pos is None or suit_offset is None:
           _log.debug("Rank/suit napoletano non riconosciuto: %s-%s", rank, suit)
           return None
       seq = suit_offset + rank_pos
       nome = _NAPOL_SEQ_TO_NOME[rank_pos]
       suit_in_file = _NAPOL_SUIT_CASE_EXCEPTIONS.get((rank_pos, suit_offset), suit)
       filename = f"{seq}_{nome}_di_{suit_in_file}.jpg"
       file_path = (
           self._base_path / "assets" / "img" / "carte_napoletane" / filename
       )
       if not file_path.exists():
           _log.debug("Immagine napoletana non trovata: %s", filename)
           return None
       try:
           import wx  # noqa: PLC0415
           img = wx.Image(str(file_path), wx.BITMAP_TYPE_JPEG)
           if not img.IsOk():
               _log.debug("Immagine napoletana non valida: %s", filename)
               return None
           return img  # type: ignore[no-any-return]
       except ImportError:
           return None
   ```

5. **Modifica `_load_source`** per routing per `deck_type`:

   ```python
   def _load_source(self, rank: str, suit: str) -> object | None:
       if self._deck_type == "neapolitan":
           return self._load_source_napoletane(rank, suit)
       # logica francesi esistente (con path fix underscore)
       ...
   ```

6. **Aggiungi `get_back_bitmap(width, height) -> object | None`**:

   ```python
   def get_back_bitmap(self, width: int, height: int) -> object | None:
       if self._deck_type != "neapolitan":
           return None
       back_key = (width, height)
       if back_key in self._back_cache:
           return self._back_cache[back_key]
       if self._back_source is None:
           back_path = (
               self._base_path / "assets" / "img" / "carte_napoletane"
               / "41_Carte_Napoletane_retro.jpg"
           )
           if not back_path.exists():
               _log.debug("Immagine dorso napoletano non trovata")
               return None
           try:
               import wx  # noqa: PLC0415
               img = wx.Image(str(back_path), wx.BITMAP_TYPE_JPEG)
               if not img.IsOk():
                   return None
               self._back_source = img
           except ImportError:
               return None
       if self._back_source is None:
           return None
       try:
           import wx  # noqa: PLC0415
           img = self._back_source.Copy()  # type: ignore[attr-defined]
           img.Rescale(width, height, wx.IMAGE_QUALITY_HIGH)
           bmp: object = wx.Bitmap(img)
           self._back_cache[back_key] = bmp
           return bmp
       except ImportError:
           return None
   ```

7. **Aggiorna `invalidate_size_cache`**: aggiungere `self._back_cache.clear()` nel corpo del
   metodo.

**Test da aggiungere** in `tests/unit/test_card_image_cache.py`:

| Test | Verifica |
|------|----------|
| `test_french_path_uses_underscore` | path costruito contiene `carte_francesi` (non `carte francesi`) |
| `test_load_source_routes_to_napoletane` | `_load_source` con `deck_type="neapolitan"` chiama `_load_source_napoletane` |
| `test_napoletane_seq_bastoni_asso` | Asso di bastoni → seq=1, filename `1_Asso_di_bastoni.jpg` |
| `test_napoletane_seq_coppe_re` | Re di coppe → seq=20, filename `20_Dieci_di_coppe.jpg` |
| `test_napoletane_case_exception_bastoni_dieci` | Re di bastoni → seq=10, filename `10_Dieci_di_Bastoni.jpg` (B maiuscolo) |
| `test_get_back_bitmap_french_returns_none` | `deck_type="french"` → `get_back_bitmap` restituisce `None` |
| `test_get_back_bitmap_napoletane_file_missing_returns_none` | `deck_type="neapolitan"`, file assente → `None` |
| `test_invalidate_clears_back_cache` | dopo inject in `_back_cache`, `invalidate_size_cache()` svuota il dizionario |

**Commit**:
```
fix(infrastructure): fix path carte francesi e aggiungi supporto carte napoletane in CardImageCache
```

---

### Fase 2 — Estendi `CardRenderer` con parametro `back_bitmap`

**File**: `src/infrastructure/ui/card_renderer.py`

**Operazioni atomiche**:

1. Aggiungere parametro `back_bitmap: object | None = None` alla firma di `draw_card()`
   (dopo il parametro `bitmap` esistente — backward-compatible grazie al default `None`).
2. Nel ramo `not card.face_up`:
   - Se `back_bitmap is not None`: chiamare
     `self._draw_face_image(dc, back_bitmap, x, y, width, height)`
   - Altrimenti: chiamare `self._draw_back(dc, x, y, width, height)` (fallback procedurale
     invariato)

**Test da aggiungere** in `tests/unit/test_card_renderer.py`:

| Test | Verifica |
|------|----------|
| `test_draw_card_back_uses_back_bitmap_when_provided` | carta coperta + `back_bitmap` mock → `DrawBitmap` chiamato |
| `test_draw_card_back_uses_procedural_when_no_back_bitmap` | carta coperta senza `back_bitmap` → `_draw_back` chiamato |

**Commit**:
```
feat(presentation): aggiungi supporto back_bitmap a CardRenderer.draw_card
```

---

### Fase 3 — Aggiorna `GameplayPanel` per cache deck-type-aware e dorso

**File**: `src/infrastructure/ui/gameplay_panel.py`

**Pre-requisito**: leggere `_on_paint()` per capire la struttura di `board_state` e il punto
di accesso a `deck_type` prima di implementare.

**Operazioni atomiche**:

1. Aggiungere attributo `_current_deck_type: str = ""` in `__init__`.
2. Modificare `_get_image_cache()`:
   - Aggiungere parametro opzionale `deck_type: str = "french"`
   - Se `self._image_cache is None or deck_type != self._current_deck_type`:
     - `self._image_cache = CardImageCache(project_root, deck_type=deck_type)`
     - `self._current_deck_type = deck_type`
   - Restituire `self._image_cache`
3. In `_on_paint()`: determinare `deck_type` da `board_state` (attributo `deck_type` se
   presente) o da `self._settings.deck_type`; usare `"french"` come default sicuro se
   nessuna delle due fonti è disponibile.
4. Aggiornare il call site `_get_image_cache()` per passare `deck_type`.
5. Nel loop rendering carte face-down: ottenere
   `back_bmp = cache.get_back_bitmap(card_w, card_h)`
   e passarlo a `renderer.draw_card(..., back_bitmap=back_bmp)`.

**Test**: non sono richiesti test nuovi. Eseguire la suite di regressione:

```
pytest tests/unit/presentation/ -v
```

**Commit**:
```
feat(presentation): aggiorna GameplayPanel per cache deck-type-aware e dorso napoletano
```

---

### Fase 4 — Validazione finale e CHANGELOG

**Operazioni**:

1. Compilazione statica:
   ```
   python -m py_compile \
     src/infrastructure/ui/card_image_cache.py \
     src/infrastructure/ui/card_renderer.py \
     src/infrastructure/ui/gameplay_panel.py
   ```
2. Type checking:
   ```
   mypy \
     src/infrastructure/ui/card_image_cache.py \
     src/infrastructure/ui/card_renderer.py \
     src/infrastructure/ui/gameplay_panel.py \
     --strict
   ```
3. Test suite:
   ```
   pytest \
     tests/unit/test_card_image_cache.py \
     tests/unit/test_card_renderer.py \
     tests/unit/presentation/test_gameplay_visual_wiring.py \
     -v
   ```
4. Aggiornare `CHANGELOG.md` sezione `[Unreleased]` con le voci Added/Fixed/Changed.

**Commit**:
```
fix+test(infrastructure/presentation): validazione card-assets-integration v4.3.0
```

---

## 5. Test Plan

### Unit test

| Suite file                          | Fase | Nuovi test |
|-------------------------------------|------|------------|
| `tests/unit/test_card_image_cache.py` | 1  | 8          |
| `tests/unit/test_card_renderer.py`    | 2  | 2          |

### Regressione

| Suite                                              | Trigger            |
|----------------------------------------------------|--------------------|
| `tests/unit/presentation/test_gameplay_visual_wiring.py` | Fase 3 + Fase 4 |

### Soglia di completamento

Tutte le suite devono passare **100%** prima del commit di Fase 4.
`py_compile` e `mypy --strict` devono uscire con codice 0.

---

## Note tecniche

- L'import di `wx` dentro i metodi (`import wx  # noqa: PLC0415`) è intenzionale per
  mantenere la testabilità senza wxPython installato nell'ambiente CI.
- Le eccezioni naming (`_NAPOL_SUIT_CASE_EXCEPTIONS`) sono dizionari a livello di modulo per
  essere patchabili nei test senza istanziare la cache.
- Il parametro `back_bitmap` di `draw_card` ha default `None` per garantire backward
  compatibility con tutti i call site esistenti.
