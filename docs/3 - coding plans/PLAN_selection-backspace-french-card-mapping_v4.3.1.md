---
type: plan
feature: selection-backspace-french-card-mapping
agent: Agent-Plan
status: READY
version: v4.3.1
design_ref: docs/2 - projects/DESIGN_selection-backspace-french-card-mapping_v4.3.1.md
date: 2026-04-10
---

# PLAN: Backspace annulla selezione + Annuncio vocale + Fix mapping immagini francesi

## 1. Executive Summary

| Campo | Valore |
|---|---|
| Tipo | Bugfix + UX improvement |
| Priorità | High |
| Branch suggerito | fix/selection-backspace-french-cards-v4.3.1 |
| Versione target | v4.3.1 |
| Commit attesi | 3 (uno per fase atomica) |

Tre correzioni correlate all'interazione tastiera e al rendering visivo:
1. Rimappatura CANCEL_SELECTION da Delete a Backspace (Delete è distruttivo nella navigazione NVDA).
2. Aggiunta annuncio vocale esplicito quando la selezione viene annullata.
3. Fix del passaggio rank/suit come enum al posto di stringa in `gameplay_panel.py`, che causa fallimento silenzioso del caricamento immagini per Asso, Jack, Regina, Re.

---

## 2. Problema e Obiettivo

### Problema A — Tasto Delete inadatto con NVDA

Il tasto Delete attiva `_cancel_selection()` in tutti i contesti di gameplay.
Con NVDA attivo su Windows, Delete è usato per leggere il carattere corrente
nella virtual cursor o per eliminare testo nei campi editabili.
Questo crea conflitti di input. Backspace (WXK_BACK / pygame.K_BACKSPACE)
non è usato da NVDA in modalità applicazione ed è più intuitivo per "tornare indietro".

### Problema B — Nessun annuncio vocale su annulla selezione

`_cancel_selection()` esegue `engine.clear_selection()` e riproduce `UI_CANCEL` audio,
ma non chiama `self._vocalizza(...)`. L'utente NVDA non riceve conferma testuale
dell'azione, non sa se la selezione è stata effettivamente rimossa.

### Problema C — Enum Rank/Suit passati come stringa alla cache immagini

In `gameplay_panel.py` linea 251:
```python
bitmap = cache.get_bitmap(card.rank, card.suit, cw, ch)
```
`card.rank` è `Optional[Rank]` (enum) e `card.suit` è `Optional[Suit]` (enum).
La firma di `CardImageCache.get_bitmap` si aspetta stringhe. Quando viene chiamata
`rank.strip().upper()` su un enum, si ottiene `AttributeError` (mancanza del metodo
`.strip()`) gestito silenziosamente, oppure nessuna corrispondenza nella `_RANK_MAP`.
Risultato: le immagini di Asso, J, Q, K non vengono caricate.

**Obiettivo**: correggere i tre difetti in modo atomico e committable separatamente,
mantenendo backward compatibility con le API esistenti.

---

## 3. File coinvolti

### Fase 1 — Input/Selection (Delete → Backspace + annuncio vocale)

| Operazione | File | Motivo |
|---|---|---|
| MODIFY | `src/application/gameplay_controller.py` | 3 occorrenze: pygame_mapping (riga 266), wx_dispatch (riga 1292), help_text (riga 907) |
| MODIFY | `src/application/input_handler.py` | 1 occorrenza: key_bindings riga 157 |

### Fase 2 — Card Image Mapping

| Operazione | File | Motivo |
|---|---|---|
| MODIFY | `src/infrastructure/ui/gameplay_panel.py` | Conversione enum→stringa prima di chiamare `cache.get_bitmap()` |

### Fase 3 — Test/Validation

| Operazione | File | Motivo |
|---|---|---|
| MODIFY | `tests/unit/test_card_image_cache.py` | Aggiungere test per rank italiani (Asso, Jack, Regina, Re) passati come stringa |
| CREATE | `tests/unit/test_input_handler_backspace.py` | Unit test: CANCEL_SELECTION ora su K_BACKSPACE, non K_DELETE |
| MODIFY | `tests/unit/application/test_input_handler_audio.py` | Allineare test esistente su CANCEL_SELECTION al nuovo tasto |

### Fase 4 — Docs Sync

| Operazione | File | Motivo |
|---|---|---|
| MODIFY | `docs/API.md` | Aggiornare sezione keyboard mapping: Delete → Backspace |
| MODIFY | `CHANGELOG.md` | Aggiungere entrate v4.3.1 nelle sezioni Fixed/Changed |

---

## 4. Fasi sequenziali

### Fase 1 — Rimappatura Delete → Backspace + annuncio vocale

**Commit atomico:** `fix(input): rimappa CANCEL_SELECTION da Delete a Backspace con annuncio vocale`

#### 1a. `src/application/input_handler.py`

Riga 157 — sostituire:
```python
self.key_bindings[(pygame.K_DELETE, False, False)] = GameCommand.CANCEL_SELECTION
```
con:
```python
self.key_bindings[(pygame.K_BACKSPACE, False, False)] = GameCommand.CANCEL_SELECTION
```

#### 1b. `src/application/gameplay_controller.py` — pygame mapping

Riga 266 — sostituire:
```python
pygame.K_DELETE: self._cancel_selection,
```
con:
```python
pygame.K_BACKSPACE: self._cancel_selection,
```

#### 1c. `src/application/gameplay_controller.py` — wx dispatch

Riga 1292 — sostituire:
```python
elif key_code == wx.WXK_DELETE:
    self._cancel_selection()
```
con:
```python
elif key_code == wx.WXK_BACK:
    self._cancel_selection()
```

> Nota: `wx.WXK_BACK` è il codice wxPython per il tasto Backspace.

#### 1d. `src/application/gameplay_controller.py` — help text

Riga 907 — sostituire:
```
CANC: annulla selezione.
```
con:
```
Backspace: annulla selezione.
```

#### 1e. `src/application/gameplay_controller.py` — annuncio vocale

Nel metodo `_cancel_selection()` (riga 781), aggiungere chiamata vocale dopo
`engine.clear_selection()`. Il metodo diventa:
```python
def _cancel_selection(self) -> None:
    """BACKSPACE: Cancel current card selection."""
    self.engine.clear_selection()
    self._vocalizza("Selezione annullata.", interrupt=True)
    # AUDIO
    if self._audio:
        try:
            from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
            self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_CANCEL))
        except Exception:
            pass
```

#### 1f. `src/application/gameplay_controller.py` — docstring docstring

Riga 782 — sostituire:
```python
"""DELETE: Cancel current card selection."""
```
con:
```python
"""BACKSPACE: Cancel current card selection with vocal announcement."""
```

---

### Fase 2 — Fix mapping immagini carte francesi

**Commit atomico:** `fix(ui): converti Rank/Suit enum a stringa prima di chiamare card_image_cache`

#### 2a. `src/infrastructure/ui/gameplay_panel.py`

Riga 251 — sostituire:
```python
bitmap = cache.get_bitmap(card.rank, card.suit, cw, ch)
```
con:
```python
rank_str: str = (
    card.rank.name_it if card.rank is not None else str(card._valore)
)
suit_str: str = (
    card.suit.name_it if card.suit is not None else str(card._seme)
)
bitmap = cache.get_bitmap(rank_str, suit_str, cw, ch)
```

**Razionale**: `Rank.ACE.name_it` → `"Asso"`, `Rank.JACK.name_it` → `"Jack"`,
`Rank.QUEEN.name_it` → `"Regina"`, `Rank.KING.name_it` → `"Re"`.
Questi nomi italiani sono già presenti nella `_RANK_MAP` di `card_image_cache.py`
(vedi chiavi `"ASSO"`, `"JACK"`, `"REGINA"`, `"RE"`).
Per i rank numerici (2–10), `name_it` restituisce la stringa numerica diretta.
Il fallback `card._valore` copre il legacy interface.

---

### Fase 3 — Test / Validation

**Commit atomico:** `test: aggiungi test Backspace/annuncio vocale e rank italiani cache`

#### 3a. `tests/unit/test_card_image_cache.py`

Aggiungere test per verifica che i rank italiani (Asso, Jack, Regina, Re)
siano correttamente mappati dalla `_rank_to_num`:
```python
def test_rank_to_num_asso_it(self) -> None:
    assert FakeCardImageCache()._rank_to_num("Asso") == "1"

def test_rank_to_num_jack_it(self) -> None:
    assert FakeCardImageCache()._rank_to_num("Jack") == "11"

def test_rank_to_num_regina_it(self) -> None:
    assert FakeCardImageCache()._rank_to_num("Regina") == "12"

def test_rank_to_num_re_it(self) -> None:
    assert FakeCardImageCache()._rank_to_num("Re") == "13"
```

#### 3b. `tests/unit/application/test_input_handler_audio.py`

Verificare che il test esistente (riga 51) su `CANCEL_SELECTION` usi
`pygame.K_BACKSPACE` al posto di `pygame.K_DELETE`. Se il test costruisce
l'evento con `K_DELETE`, aggiornare la costruzione dell'evento.

#### 3c. Checklist validazione manuale

- Premere Backspace durante una selezione attiva → NVDA legge "Selezione annullata."
- Premere Delete durante gameplay → nessun effetto (non mappato)
- Aprire partita francese → Asso, J, Q, K mostrano immagine corretta
- Resize finestra → immagini riscalate correttamente

---

### Fase 4 — Docs Sync

**Commit atomico:** `docs: aggiorna API.md e CHANGELOG per v4.3.1`

#### 4a. `docs/API.md`

Nella sezione keyboard mapping, aggiornare:
- `Delete` → `Backspace` per CANCEL_SELECTION

#### 4b. `CHANGELOG.md`

Aggiungere sotto `[Unreleased]` o `[v4.3.1]`:
```markdown
### Fixed
- Rimappatura CANCEL_SELECTION da Delete a Backspace per compatibilità NVDA
- _cancel_selection ora vocalizza "Selezione annullata." via screen reader
- Correzione passaggio enum Rank/Suit come stringa italiana a CardImageCache:
  Asso, Jack, Regina, Re ora caricano correttamente l'immagine francese

### Changed
- gameplay_controller.py: docstring e help text aggiornati per Backspace
```

---

## 5. Test Plan

### Unit

| Test | File | Verifica |
|---|---|---|
| `test_rank_to_num_asso_it` | `test_card_image_cache.py` | "Asso" → "1" |
| `test_rank_to_num_jack_it` | `test_card_image_cache.py` | "Jack" → "11" |
| `test_rank_to_num_regina_it` | `test_card_image_cache.py` | "Regina" → "12" |
| `test_rank_to_num_re_it` | `test_card_image_cache.py` | "Re" → "13" |
| `test_backspace_cancel_selection` | `test_input_handler_backspace.py` | K_BACKSPACE → CANCEL_SELECTION |
| `test_delete_not_mapped` | `test_input_handler_backspace.py` | K_DELETE → None (non mappato) |
| Aggiornamento test esistente | `test_input_handler_audio.py` | CANCEL_SELECTION usa K_BACKSPACE |

### Integration / Validazione manuale

- Partita francese avviata: verifica visiva Asso/J/Q/K con immagini
- Selezione carta + Backspace: NVDA annuncia "Selezione annullata."
- Delete premuto: nessun effetto gameplay, NVDA non intercettato

### Pre-commit Checklist (da `workflow-standard.instructions.md`)

```bash
python -m py_compile src/application/gameplay_controller.py
python -m py_compile src/application/input_handler.py
python -m py_compile src/infrastructure/ui/gameplay_panel.py
mypy src/ --strict
grep -r "print(" src/     # deve restituire 0 occorrenze
pytest --cov=src
```
