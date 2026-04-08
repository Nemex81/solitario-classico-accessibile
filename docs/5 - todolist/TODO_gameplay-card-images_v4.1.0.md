---
feature: gameplay-card-images
type: todo
agent: Agent-Plan
status: READY
version: v4.1.0
plan_ref: docs/3 - coding plans/PLAN_gameplay-card-images_v4.1.0.md
date: 2026-04-08
---

# TODO: Gameplay Card Images — v4.1.0

Piano di riferimento: [PLAN_gameplay-card-images_v4.1.0.md](../3%20-%20coding%20plans/PLAN_gameplay-card-images_v4.1.0.md)

---

## Istruzioni per Agent-Code

Implementa le fasi nell'ordine indicato. Ogni fase deve essere:
1. Completamente implementata (file creati/modificati come da PLAN)
2. Compilata senza errori (`python -m py_compile`)
3. Type-checked (`mypy --strict` sui file modificati)
4. Testata (eseguire i test della fase corrente)
5. Committata con il messaggio indicato nel PLAN
6. Spunta la checkbox corrispondente in questo file

Non procedere alla fase successiva finche la fase corrente non e completa e committata.

---

## Checklist Fasi

### [x] Fase 0 — CardImageCache

**File**: `src/infrastructure/ui/card_image_cache.py`, `tests/unit/test_card_image_cache.py`

- [x] Creare classe `CardImageCache` con `__init__(self, assets_base_path: str | os.PathLike[str])`
- [x] Implementare attributi: `_base_path: Path`, `_sources: dict[tuple[str,str], wx.Image | None]`, `_cache: dict[tuple[str,str,int,int], wx.Bitmap]`, `_bg_source: wx.Image | None`, `_bg_cache: dict[tuple[int,int], wx.Bitmap]`
- [x] Implementare `_rank_to_num(rank: str) -> str`: A→1, 2-10→stessa, J→11, Q→12, K→13
- [x] Implementare `_load_source(rank, suit) -> wx.Image | None`: carica dal file, logga DEBUG se mancante
- [x] Implementare `get_bitmap(rank, suit, width, height) -> wx.Bitmap | None`: cache-first, lazy load, scale HIGH
- [x] Implementare `get_background_bitmap(width, height) -> wx.Bitmap | None`: carica `Sfondo tavolo verde.jpg`, cache
- [x] Implementare `invalidate_size_cache()`: svuota `_cache` e `_bg_cache`, mantiene `_sources`
- [x] Scrivere `tests/unit/test_card_image_cache.py` con mock `wx.Image` e filesystem
- [x] `mypy src/infrastructure/ui/card_image_cache.py --strict` — zero errori
- [x] `pytest tests/unit/test_card_image_cache.py` — tutti green, coverage >= 85%
- [x] Commit: `feat(presentation): aggiungi CardImageCache per immagini carte`

---

### [x] Fase 1 — ThemeProperties: flag `use_card_images`

**File**: `src/infrastructure/ui/visual_theme.py`, `tests/unit/test_visual_theme.py`

- [x] Aggiungere campo `use_card_images: bool` a `ThemeProperties` dataclass (campo con default per backward compat)
- [x] Aggiornare `THEME_STANDARD`: aggiungere `use_card_images=True`
- [x] Aggiornare `THEME_ALTO_CONTRASTO`: aggiungere `use_card_images=False`
- [x] Aggiornare `THEME_GRANDE`: aggiungere `use_card_images=True`
- [x] Aggiungere 3 test in `test_visual_theme.py`: verifica `use_card_images` per ciascun tema
- [x] `mypy src/infrastructure/ui/visual_theme.py --strict` — zero errori
- [x] `pytest tests/unit/test_visual_theme.py` — tutti green
- [x] Commit: `feat(presentation): aggiungi use_card_images a ThemeProperties`

---

### [x] Fase 2 — CardRenderer: supporto bitmap

**File**: `src/infrastructure/ui/card_renderer.py`, `tests/unit/test_card_renderer.py`

- [x] Aggiungere parametro `bitmap: object | None = None` a firma `draw_card()`
- [x] Aggiungere metodo privato `_draw_face_image(dc, bitmap, x, y, width, height)`: chiama `dc.DrawBitmap(bitmap, x, y)` con try/except
- [x] Modificare `draw_card()`: se `card.face_up and bitmap is not None` → chiama `_draw_face_image`, altrimenti usa `_draw_face`
- [x] Verificare bordi highlight/selezione: sempre sovrimposti indipendentemente da immagine o testo
- [x] Verificare `_draw_back()` invariata (dorso sempre procedurale)
- [x] Scrivere test per `draw_card()` con bitmap mock (verifica che `DrawBitmap` venga chiamato)
- [x] Scrivere test per `draw_card()` senza bitmap (verifica fallback testuale)
- [x] Scrivere test per carta coperta con o senza bitmap (sempre `_draw_back`)
- [x] `mypy src/infrastructure/ui/card_renderer.py --strict` — zero errori
- [x] `pytest tests/unit/test_card_renderer.py` — tutti green, coverage >= 85%
- [x] Commit: `feat(presentation): estendi CardRenderer con supporto bitmap immagine`

---

### [x] Fase 3 — GameplayPanel: integrazione immagini

**File**: `src/infrastructure/ui/gameplay_panel.py`

- [x] Aggiungere import `CardImageCache` in cima al file
- [x] Aggiungere attributo `_image_cache: CardImageCache | None = None` in `__init__`
- [x] Aggiungere metodo `_get_image_cache() -> CardImageCache`: lazy init con path calcolato da `__file__`
- [x] In `_on_size()`: aggiungere `if self._image_cache: self._image_cache.invalidate_size_cache()`
- [x] In `_on_paint()`, quando `display_mode == visual`:
  - [x] Se `theme.use_card_images`: ottenere `bg_bmp` da cache, disegnare con `dc.DrawBitmap(bg_bmp, 0, 0)`
  - [x] Altrimenti: usare `dc.SetBackground` + `dc.Clear()` con `theme.bg_color` (comportamento attuale)
- [x] Nel loop rendering carte: se `theme.use_card_images and card.face_up`: ottenere `bitmap` da cache, passare a `draw_card()`
- [x] Se `not theme.use_card_images` o carta coperta: passare `bitmap=None`
- [x] `mypy src/infrastructure/ui/gameplay_panel.py --strict` — zero nuovi errori
- [x] `pytest tests/unit/ -m "not gui"` — tutti green, nessuna regressione
- [ ] Commit: `feat(presentation): integra CardImageCache in GameplayPanel`

---

### [ ] Fase 4 — Validazione e CHANGELOG

- [ ] `python -m py_compile src/infrastructure/ui/card_image_cache.py src/infrastructure/ui/card_renderer.py src/infrastructure/ui/gameplay_panel.py src/infrastructure/ui/visual_theme.py` — zero errori
- [ ] `mypy src/infrastructure/ui/ --strict` — zero errori di tipo
- [ ] `pylint --enable=cyclic-import src/infrastructure/ui/` — zero import ciclici
- [ ] `grep -r "print(" src/` — zero occorrenze
- [ ] `pytest tests/unit/ --cov=src -q` — coverage sopra soglia
- [ ] Test manuale: avviare `acs_wx.py`, selezionare tema Standard + modalita visual
  - [ ] Carte mostrano immagini fotografiche reali
  - [ ] 6 carte mancanti mostrano stile testuale
  - [ ] Sfondo e il tappeto verde fotografico
  - [ ] Ridimensionamento finestra: le immagini vengono aggiornate
  - [ ] Tema Alto Contrasto: nessuna immagine, rendering testuale ad alto contrasto
  - [ ] Tema Grande: immagini scala 1.5
  - [ ] Audio-only: nessuna modifica al comportamento (zero regressione)
- [ ] Aggiornare `CHANGELOG.md` sezione `[Unreleased]`
- [ ] Commit: `test: validazione integrazione card images v4.1.0`

---

## Riepilogo Avanzamento

| Fase | Descrizione | Stato |
|------|-------------|-------|
| Fase 0 | CardImageCache | [x] |
| Fase 1 | ThemeProperties use_card_images | [ ] |
| Fase 2 | CardRenderer bitmap support | [ ] |
| Fase 3 | GameplayPanel integrazione | [ ] |
| Fase 4 | Validazione e CHANGELOG | [ ] |
