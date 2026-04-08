---
feature: gameplay-card-images
type: plan
agent: Agent-Plan
status: READY
version: v4.1.0
design_ref: docs/2 - projects/DESIGN_gameplay-visual-ui.md
date: 2026-04-08
---

# PLAN: Gameplay Card Images — v4.1.0

## Executive Summary

| Attributo | Valore |
|-----------|--------|
| Tipo | Feature — rendering immagini reali carte da gioco |
| Priorita | Alta |
| Branch | `feature/gameplay-card-images` |
| Versione target | v4.1.0 |
| Design di riferimento | [DESIGN_gameplay-visual-ui.md](../2%20-%20projects/DESIGN_gameplay-visual-ui.md) (status: REVIEWED, v4.1.0) |
| Fasi totali | 5 (Fase 0 — Fase 4) |
| Base | v4.0.0 completato (CardRenderer testuale, GameplayPanel dual-mode, BoardLayoutManager) |

---

## Problema e Obiettivo

### Problema

La finestra di gameplay v4.0.0 disegna le carte come rettangoli colorati con testo (simboli Unicode) invece di usare le immagini fotografiche reali presenti in `assets/img/carte francesi/`. Le 46 immagini esistono ma non sono mai caricate ne usate dal codebase. L'interfaccia non assomiglia a un solitaire classico e non e riconoscibile da giocatori vedenti o ipovedenti.

### Obiettivo

Integrare il sistema di immagini (`CardImageCache`) nel pipeline di rendering esistente:
- Le carte scoperte vengono disegnate usando le immagini `.jpg` reali
- Lo sfondo del tavolo usa `Sfondo tavolo verde.jpg`
- Le 6 carte mancanti usano il fallback testuale gia implementato
- Il dorso rimane procedurale (pattern a rombi) per coerenza grafica
- Il tema Alto Contrasto continua ad usare il rendering testuale (massima leggibilita)

---

## File Coinvolti

### Nuovi file (CREATE)

| File | Descrizione |
|------|-------------|
| `src/infrastructure/ui/card_image_cache.py` | CardImageCache — carica/scala/cachea le immagini carte JPEG, invalida su ridimensionamento |
| `tests/unit/test_card_image_cache.py` | Unit test per CardImageCache con mock filesystem |

### File modificati (MODIFY)

| File | Modifiche |
|------|-----------|
| `src/infrastructure/ui/visual_theme.py` | Aggiungere `use_card_images: bool` a ThemeProperties; aggiornare i 3 temi (Standard: True, AltoContrasto: False, Grande: True) |
| `src/infrastructure/ui/card_renderer.py` | Aggiungere parametro opzionale `bitmap` a `draw_card()`; implementare `draw_card_image()` con `dc.DrawBitmap()`, bordi sovrimposti |
| `src/infrastructure/ui/gameplay_panel.py` | Istanziare `CardImageCache`; disegnare sfondo fotografico; passare bitmap a `draw_card()` |
| `tests/unit/test_card_renderer.py` | Aggiungere test per `draw_card()` con bitmap mock e senza bitmap (fallback) |
| `tests/unit/test_visual_theme.py` | Aggiungere test per `use_card_images` nei 3 temi |

### File non modificati

- Tutto il domain layer
- `board_layout_manager.py` — l'aspect ratio 5:7 e compatibile con le immagini reali
- `board_state.py`, `gameplay_controller.py`

---

## Dipendenze tra Fasi

```
Fase 0 (CardImageCache — nuovo componente)
  |
  v
Fase 1 (ThemeProperties + use_card_images)
  |
  v
Fase 2 (CardRenderer — supporto bitmap)
  |
  v
Fase 3 (GameplayPanel — integrazione finale)
  |
  v
Fase 4 (Test integrazione e validazione)
```

---

## Fasi Sequenziali

### Fase 0 — CardImageCache

**Scopo**: componente che carica, scala e cachea le immagini delle carte da `assets/img/carte francesi/`.

**File coinvolti**:
- CREATE: `src/infrastructure/ui/card_image_cache.py`
- CREATE: `tests/unit/test_card_image_cache.py`

**Regole di naming**:
- File immagine: `{rank_num}-{suit}.jpg` — es. `1-cuori.jpg`, `11-fiori.jpg`
- Mapping `CardView.rank` → `rank_num`:
  - `"A"` → `"1"`
  - `"2"` ... `"10"` → stessa stringa
  - `"J"` → `"11"`, `"Q"` → `"12"`, `"K"` → `"13"`
- Suit: il nome e gia il nome file (`"cuori"`, `"fiori"`, `"picche"`, `"quadri"`)

**Interfaccia pubblica**:
```python
class CardImageCache:
    def __init__(self, assets_base_path: str | os.PathLike[str]) -> None: ...

    def get_bitmap(
        self,
        rank: str,
        suit: str,
        width: int,
        height: int,
    ) -> wx.Bitmap | None:
        """Ritorna il bitmap scalato, o None se l'immagine non esiste."""

    def get_background_bitmap(
        self,
        width: int,
        height: int,
    ) -> wx.Bitmap | None:
        """Ritorna bitmap sfondo tavolo scalato alle dimensioni panel."""

    def invalidate_size_cache(self) -> None:
        """Invalida i bitmap scalati (chiamato su EVT_SIZE). Le sorgenti restano in RAM."""
```

**Operazioni interne**:
1. `_load_source(rank, suit)`: carica `wx.Image` da disco, la mette in `_sources`; ritorna None se manca
2. `get_bitmap`: cerca in `_cache[(rank, suit, width, height)]`; se non c'e, chiama `_load_source` e scala con `wx.IMAGE_QUALITY_HIGH`, poi mette in cache
3. `invalidate_size_cache`: svuota solo le entry con chiave `(rank, suit, width, height)` — non `_sources`
4. Carte mancanti (6): `_load_source` ritorna None, `get_bitmap` ritorna None, log DEBUG "Immagine carta non trovata: {rank}-{suit}"

**Immagini mancanti conosciute**: `5-quadri`, `7-cuori`, `8-cuori`, `9-fiori`, `9-picche`, `9-quadri`

**Test**:
- `get_bitmap` con immagine esistente (mock `wx.Image`): ritorna bitmap
- `get_bitmap` con carta mancante: ritorna None
- `get_bitmap` seconda chiamata: cache hit (Image.Scale non chiamata di nuovo)
- `invalidate_size_cache`: dopo invalidazione, `get_bitmap` richiama Scale
- `get_background_bitmap`: stesso comportamento di `get_bitmap` per lo sfondo

**Commit**: `feat(presentation): aggiungi CardImageCache per immagini carte`

---

### Fase 1 — ThemeProperties: flag `use_card_images`

**Scopo**: aggiungere il flag `use_card_images` a `ThemeProperties` per controllare se il rendering usa immagini o fallback testuale.

**File coinvolti**:
- MODIFY: `src/infrastructure/ui/visual_theme.py`
- MODIFY: `tests/unit/test_visual_theme.py`

**Operazioni**:
1. Aggiungere `use_card_images: bool` a `ThemeProperties` dataclass (dopo `card_scale`)
2. Aggiornare `THEME_STANDARD`: `use_card_images=True`
3. Aggiornare `THEME_ALTO_CONTRASTO`: `use_card_images=False` (massima leggibilita su sfondo nero)
4. Aggiornare `THEME_GRANDE`: `use_card_images=True` (immagini grande formato)
5. Verificare `mypy src/infrastructure/ui/visual_theme.py --strict` zero errori

**Test aggiuntivi**:
- `THEME_STANDARD.use_card_images == True`
- `THEME_ALTO_CONTRASTO.use_card_images == False`
- `THEME_GRANDE.use_card_images == True`

**Commit**: `feat(presentation): aggiungi use_card_images a ThemeProperties`

---

### Fase 2 — CardRenderer: supporto bitmap opzionale

**Scopo**: estendere `CardRenderer.draw_card()` per disegnare un `wx.Bitmap` quando disponibile, mantenendo il fallback testuale per carte mancanti e per il tema Alto Contrasto.

**File coinvolti**:
- MODIFY: `src/infrastructure/ui/card_renderer.py`
- MODIFY: `tests/unit/test_card_renderer.py`

**Operazioni**:
1. Aggiungere parametro `bitmap: wx.Bitmap | None = None` a `draw_card()`
2. Aggiungere metodo privato `_draw_face_image(dc, bitmap, x, y, width, height)`:
   - Usa `dc.DrawBitmap(bitmap, x, y)` per disegnare l'immagine scalata
   - NON disegna rank/suit testuale quando usa l'immagine
3. Modificare `draw_card()`:
   - Se `card.face_up and bitmap is not None`: chiama `_draw_face_image()`
   - Altrimenti (bitmap None o carta coperta): usa logica esistente (`_draw_face` o `_draw_back`)
   - Bordi di highlight e selezione vengono sempre sovrimposti (invariati)
4. `_draw_back()` rimane invariata: dorso sempre procedurale
5. `mypy src/infrastructure/ui/card_renderer.py --strict` zero errori

**Test aggiuntivi**:
- `draw_card()` con `bitmap` non-None: `dc.DrawBitmap` chiamato, `_draw_face` NON chiamato
- `draw_card()` con `bitmap=None`: fallback `_draw_face` chiamato (comportamento v4.0.0 invariato)
- Bordi highlight sovrimposti correttamente in entrambi i casi
- Carta coperta: `_draw_back` sempre chiamato indipendentemente da `bitmap`

**Commit**: `feat(presentation): estendi CardRenderer con supporto bitmap immagine`

---

### Fase 3 — GameplayPanel: integrazione sfondo + immagini

**Scopo**: collegare `CardImageCache` al pipeline di rendering in `GameplayPanel`.

**File coinvolti**:
- MODIFY: `src/infrastructure/ui/gameplay_panel.py`

**Operazioni**:
1. Aggiungere attributo `_image_cache: CardImageCache | None = None`
2. Aggiungere metodo `_get_image_cache() -> CardImageCache`:
   - Istanzia `CardImageCache` lazily alla prima chiamata (quando la dimensione e nota)
   - Usa il path `assets/img/carte francesi` relativo alla root del progetto
   - Il path assoluto si ricava con `Path(__file__).parent.parent.parent.parent.parent / "assets" / "img" / "carte francesi"`
3. In `_on_size()`: se `_image_cache` e istanziato, chiamare `_image_cache.invalidate_size_cache()`
4. In `_on_paint()`, dopo `dc.Clear()`:
   - Se `use_card_images` del tema corrente e True (o Standard/Grande):
     - Ottenere `bg_bmp = cache.get_background_bitmap(w, h)`
     - Se `bg_bmp is not None`: `dc.DrawBitmap(bg_bmp, 0, 0)` (primo layer)
     - Altrimenti: `dc.SetBackground(wx.Brush(wx.Colour(*theme.bg_color)))` + `dc.Clear()` (fallback colore)
5. Nel loop di rendering carte, per ogni carta pass `draw_card`:
   - Se `theme.use_card_images and card.face_up`:
     - `w_c, h_c = cw, ch` (dimensioni correnti della carta)
     - `bitmap = cache.get_bitmap(card.rank, card.suit, w_c, h_c)`
   - Altrimenti: `bitmap = None`
   - Chiamare `self._card_renderer.draw_card(dc, card, cx, cy, cw, ch, theme, highlighted, selected, bitmap=bitmap)`
6. `mypy src/infrastructure/ui/gameplay_panel.py --strict` zero errori

**Commit**: `feat(presentation): integra CardImageCache in GameplayPanel`

---

### Fase 4 — Test integrazione e validazione

**Scopo**: validare il funzionamento end-to-end del sistema immagini.

**Operazioni**:
1. Eseguire `pytest tests/unit/ -v` — tutti green, nessuna regressione
2. Eseguire `mypy src/infrastructure/ui/ --strict` — zero errori di tipo
3. Eseguire `python -m py_compile src/infrastructure/ui/card_image_cache.py src/infrastructure/ui/card_renderer.py src/infrastructure/ui/gameplay_panel.py src/infrastructure/ui/visual_theme.py` — zero errori
4. Test manuale (avvio applicazione):
   - Selezionare tema Standard e modalita visual: le carte mostrano immagini fotografiche reali
   - Le 6 carte mancanti mostrano stile testuale (diverso ma giocabile)
   - Il dorso e visibile con pattern a rombi
   - Lo sfondo e il tappeto verde fotografico
   - EVT_SIZE: le immagini vengono ridisegnate correttamente alla nuova dimensione
   - Tema Alto Contrasto: nessuna immagine, rendering testuale ad alto contrasto
   - Tema Grande: immagini scala 1.5 correttamente dimensionate
5. Aggiornare `CHANGELOG.md` sezione `[Unreleased]`:
   - Added: rendering immagini reali carte francesi in modalita visual
   - Fixed: fallback testuale per 6 carte senza immagine
6. Commit: `test: validazione integrazione card images v4.1.0`

---

## Checklist Pre-Commit (ogni fase)

- [ ] `python -m py_compile` sui file modificati — zero errori
- [ ] `mypy --strict` sui file modificati — zero errori di tipo
- [ ] `grep -r "print(" src/` — zero occorrenze
- [ ] `pytest tests/unit/ --cov=src/infrastructure/ui/` — coverage >= 85%
