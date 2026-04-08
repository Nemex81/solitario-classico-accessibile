---
type: design
feature: card-assets-integration
version: v4.3.0
status: REVIEWED
agent: Agent-Design
date: 2026-04-08
---

# DESIGN: Card Assets Integration v4.3.0

## 1. Idea in 3 righe

`CardImageCache` punta a una directory inesistente (`carte francesi` con spazio) e non supporta il mazzo napoletano, rendendo inutilizzabili 86 file JPEG di asset già presenti su disco. Questa feature corregge il path per le carte francesi, estende la cache per risolvere correttamente i filename del mazzo napoletano (naming sequenziale cross-seme), porta la bitmap del dorso napoletano in `draw_card()` e prepara `GameplayPanel` a reinizializzare la cache quando cambia il tipo di mazzo — tutto senza rompere il fallback testuale per le carte francesi mancanti.

---

## 2. Attori e Concetti

### Attori software coinvolti

- **`CardImageCache`** (`src/infrastructure/ui/card_image_cache.py`): componente infrastructure responsabile di lazy-load, scaling e invalidation delle bitmap. Attualmente hardcoded a `"carte francesi"` (path errato) e ignora il mazzo napoletano.
- **`CardRenderer`** (`src/infrastructure/ui/card_renderer.py`): riceve bitmap faccia in `draw_card(bitmap=...)` ma non accetta bitmap dorso; `_draw_back()` è sempre procedurale.
- **`GameplayPanel`** (`src/infrastructure/ui/gameplay_panel.py`): presentation-layer che istanzia `CardImageCache` tramite `_get_image_cache()` e passa le bitmap al renderer in `_on_paint()`.
- **`ThemeProperties`** (`src/infrastructure/ui/visual_theme.py`): espone `use_card_images: bool` che pilota il branch immagini vs testuale.
- **`GameSettings`** (`src/application/game_settings.py`): espone `deck_type: str` con valori `"french"` | `"neapolitan"`.
- **`BoardState` DTO**: trasporta lo stato delle pile verso il presentation-layer; ogni oggetto `card` ha `rank`, `suit`, `face_up`.

### Asset coinvolti

| Directory | Contenuto | Naming |
|-----------|-----------|--------|
| `assets/img/carte_francesi/` | 46 JPEG (6 mancanti) | `{rank_num}-{suit}.jpg` |
| `assets/img/carte_napoletane/` | 40 JPEG + 1 dorso | `{seq}_{Nome}_di_{Seme}.jpg` |

Carte francesi mancanti: `5-quadri`, `7-cuori`, `8-cuori`, `9-fiori`, `9-picche`, `9-quadri` → gestite dal fallback testuale già esistente.

### Concetti chiave

- **Path mismatch**: la directory fisica usa underscore (`carte_francesi`), `_load_source()` cerca con spazio (`carte francesi`). Fix atomico a 1 riga.
- **Naming sequenziale napoletano**: i file usano un indice sequenziale cross-seme (1-10 bastoni, 11-20 coppe, 21-30 denari, 31-40 spade). Il mapping richiede `offset_seme + posizione_rank`.
- **Dorso immagine vs procedurale**: il mazzo napoletano include `41_Carte_Napoletane_retro.jpg`; il mazzo francese usa dorso procedurale. `draw_card()` deve accettare entrambi.
- **Cache invalidation per deck_type**: se l'utente cambia mazzo a runtime, la cache deve essere reinizializzata con il nuovo `deck_type`.

---

## 3. Flussi Concettuali

### 3.1 Flusso attuale (rotto per francesi, assente per napoletane)

```
GameplayPanel._on_paint()
  └─ _get_image_cache()
       └─ CardImageCache.__init__()
            └─ base_path = "assets/img/carte francesi/"  ← path errato
                                                            (directory non trovata)

  └─ cache.get_bitmap(rank, suit, w, h)
       └─ _load_source(rank, suit)
            └─ path = "assets/img/carte francesi/{rank}-{suit}.jpg"
                 └─ FileNotFoundError → fallback testuale
                    [tutte le 46 carte cadono in fallback]

  └─ CardRenderer.draw_card(dc, card, bitmap=bmp, ...)
       ├─ face_up → _draw_face_image(dc, bitmap, ...)
       └─ face_down → _draw_back(dc, ...)  ← sempre procedurale
```

### 3.2 Flusso proposto (§1 + §2 + §3 + §4)

```
GameplayPanel._on_paint()
  └─ _get_image_cache()   [§4]
       ├─ deck_type = settings.deck_type
       ├─ se deck_type != _current_deck_type:
       │    reinizializza _image_cache con nuovo deck_type
       └─ CardImageCache(deck_type=deck_type)

  └─ CardImageCache.get_bitmap(rank, suit, w, h)   [§1 + §2]
       ├─ deck_type == "french":
       │    _load_source(rank, suit)
       │      path = "assets/img/carte_francesi/{rank}-{suit}.jpg"  ← fix §1
       │      → bitmap o None (fallback)
       └─ deck_type == "neapolitan":
            _load_source_napoletane(rank, suit)
              seq = offset[suit] + pos[rank]
              nome = RANK_NAMES[rank]   (es. "Asso", "Due", "Re")
              seme = suit.capitalize()  (es. "Bastoni", "Coppe")
              path = "assets/img/carte_napoletane/{seq}_{nome}_di_{seme}.jpg"
              → bitmap o None (fallback)

  └─ CardImageCache.get_back_bitmap(w, h)   [§2]
       ├─ deck_type == "neapolitan":
       │    path = "assets/img/carte_napoletane/41_Carte_Napoletane_retro.jpg"
       └─ deck_type == "french":
            → None (dorso procedurale)

  └─ CardRenderer.draw_card(dc, card, bitmap=bmp, back_bitmap=back_bmp, ...)   [§3]
       ├─ face_up  → _draw_face_image(dc, bitmap, ...)   [invariato]
       └─ face_down:
            ├─ back_bitmap is not None → _draw_face_image(dc, back_bitmap, ...)
            └─ back_bitmap is None    → _draw_back(dc, ...)  [backward compat]
```

### 3.3 Mapping napoletano (dettaglio)

```
SUIT_OFFSET = {"bastoni": 0, "coppe": 10, "denari": 20, "spade": 30}

RANK_POSITION = {
    "Asso": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "Regina": 8, "Cavallo": 9, "Re": 10
}

RANK_NAMES = {
    "Asso": "Asso", "2": "Due", "3": "Tre", "4": "Quattro", "5": "Cinque",
    "6": "Sei", "7": "Sette", "Regina": "Regina", "Cavallo": "Cavallo", "Re": "Re"
}

Esempi:
  Asso di bastoni → seq=1  → "1_Asso_di_Bastoni.jpg"
  Re   di bastoni → seq=10 → "10_Re_di_Bastoni.jpg"
  Asso di coppe   → seq=11 → "11_Asso_di_Coppe.jpg"
  Re   di spade   → seq=40 → "40_Re_di_Spade.jpg"
```

NOTA: il case esatto dei filename (es. `Spade` vs `spade`) deve essere verificato
sui file fisici prima dell'implementazione, poiché Windows è case-insensitive ma Linux
(CI) non lo è.

---

## 4. Decisioni Architetturali

### §1 — Fix path carte francesi

**Decisione**: correggere `"carte francesi"` → `"carte_francesi"` nella costante/stringa
di `CardImageCache._load_source()`.

**Motivazione**: modifica atomica a 1 riga, zero rischio regressione. Sblocca
immediatamente 40 carte funzionanti (le 46 meno le 6 mancanti che restano in fallback).

**File**: `src/infrastructure/ui/card_image_cache.py`

---

### §2 — Estensione CardImageCache per mazzo napoletano

**Decisione**: aggiungere `deck_type: str = "french"` al costruttore e delegare
la risoluzione del path a metodi privati separati per tipo di mazzo.

Struttura pubblica modificata:

```python
class CardImageCache:
    def __init__(self, deck_type: str = "french") -> None: ...

    # già presente — invariata per french, invariata per external callers
    def get_bitmap(self, rank: str, suit: str, width: int, height: int) -> object | None: ...

    # nuovo
    def get_back_bitmap(self, width: int, height: int) -> object | None: ...

    # privati
    def _load_source(self, rank: str, suit: str) -> object | None: ...           # french
    def _load_source_napoletane(self, rank: str, suit: str) -> object | None: ...  # napoletane
```

**Motivazione**: separare i due branch di naming in metodi privati distinti mantiene
`get_bitmap()` come unico punto di accesso pubblico, evita branching nella firma pubblica
e permette test unitari indipendenti per il mazzo napoletano.

**Backward compat**: default `deck_type="french"` — tutti i caller esistenti che
istanziano `CardImageCache()` senza argomenti continuano a funzionare.

---

### §3 — Estensione CardRenderer per dorso immagine

**Decisione**: aggiungere `back_bitmap: object | None = None` come parametro keyword
opzionale a `draw_card()`.

Firma pubblica proposta:

```python
def draw_card(
    self,
    dc: object,
    card: object,
    x: int,
    y: int,
    width: int,
    height: int,
    bitmap: object | None = None,
    back_bitmap: object | None = None,
    selected: bool = False,
) -> None: ...
```

**Motivazione**: parametro opzionale con default `None` garantisce zero breaking change
per i caller esistenti. Il branch `face_down` riutilizza `_draw_face_image()` già
esistente anziché duplicare logica di rendering.

**File**: `src/infrastructure/ui/card_renderer.py`

---

### §4 — Aggiornamento GameplayPanel

**Decisione**: tracciare il `deck_type` corrente con un attributo privato e
reinizializzare la cache solo quando cambia.

Modifiche a `GameplayPanel`:

```python
# nuovo attributo
_current_deck_type: str = ""

# _get_image_cache() aggiornato (pseudocodice)
def _get_image_cache(self) -> CardImageCache:
    deck_type = self._settings.deck_type
    if self._image_cache is None or deck_type != self._current_deck_type:
        self._image_cache = CardImageCache(deck_type=deck_type)
        self._current_deck_type = deck_type
    return self._image_cache
```

In `_on_paint()`:
- Ottenere `back_bmp` da `cache.get_back_bitmap(card_w, card_h)` una sola volta
  per frame prima del loop di rendering.
- Passare `back_bitmap=back_bmp` a ogni chiamata `draw_card()` per carte `face_down`.

**Source di `deck_type`**: `self._settings.deck_type` (via `GameSettings`) — già
accessibile nell'application layer, evita dipendenze aggiuntive.

**File**: `src/infrastructure/ui/gameplay_panel.py`

---

### Sfondo alternativo (fuori scope v4.3.0)

`Sfondo Tavolo 400x600.jpg` è presente in `assets/img/` ma non integrato.
Nessuna modifica in questa versione: `get_background_bitmap()` continua a usare
`Sfondo tavolo verde.jpg` come default. Una futura versione potrà aggiungere
`bg_name: str | None = None` a `get_background_bitmap()` per renderlo configurabile.

---

## 5. Interfacce pubbliche modificate

| Classe | Metodo/Attributo | Modifica |
|--------|------------------|----------|
| `CardImageCache` | `__init__(deck_type: str = "french")` | Nuovo parametro opzionale |
| `CardImageCache` | `get_back_bitmap(width: int, height: int) -> object \| None` | Nuovo metodo pubblico |
| `CardRenderer` | `draw_card(..., back_bitmap: object \| None = None)` | Nuovo parametro keyword opzionale |
| `GameplayPanel` | `_current_deck_type: str` | Nuovo attributo privato |
| `GameplayPanel` | `_get_image_cache()` | Logic update: reinit on deck_type change |

Tutti i parametri aggiunti sono opzionali con default invariante → **zero breaking changes**.

---

## 6. Rischi e Mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| Case sensitivity filename napoletani (CI Linux) | Media | Medio | Verificare su file fisici prima di implementare; usare mapping constants centralizzato |
| 6 carte francesi mancanti | Certa | Basso | Fallback testuale già presente e funzionante |
| Reinit cache a ogni frame se `deck_type` non cambia | Bassa | Basso | Check `deck_type != _current_deck_type` evita reinit superflui |
| `get_back_bitmap()` carica da disco a ogni chiamata | Media | Medio | La bitmap del dorso va inclusa nella stessa cache interna (keyed su `"__back__"`) |
| `back_bitmap` passato a carte face-up per errore | Bassa | Nullo | Il branch `face_up` ignora `back_bitmap` — nessun effetto collaterale |

---

## 7. Scope vs Out-of-scope

### In scope (v4.3.0)

- Fix path `carte francesi` → `carte_francesi`
- `CardImageCache`: supporto mazzo napoletano + `get_back_bitmap()`
- `CardRenderer`: parametro `back_bitmap` in `draw_card()`
- `GameplayPanel`: reinit cache on deck_type change + pass `back_bmp` ai renderer calls
- Test unitari per mapping napoletano e `get_back_bitmap()`

### Out of scope (documentato per future versioni)

- Sfondo alternativo `Sfondo Tavolo 400x600.jpg` (futura `get_background_bitmap(bg_name=...)`)
- Generazione dei 6 JPEG mancanti per il mazzo francese
- Animazioni flip carta
- Selezione tema visivo dinamica a runtime
