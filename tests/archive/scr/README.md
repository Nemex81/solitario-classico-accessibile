# Archived Legacy Tests (scr Package)

**Archived Date**: 19 Febbraio 2026 (v3.2.1)  
**Reason**: Package structure migration (`scr` → `src` in Clean Architecture refactoring)  
**Copertura**: funzionalità ora coperta dai test di integrazione

---

## Archived Files

- `test_distribuisci_carte_deck_switching.py` — Deck switching logic (now in `test_game_engine_flow.py`)
- `test_game_engine_f3_f5.py` — F3/F5 key bindings (now in `test_game_controller.py`)
- `test_king_to_empty_base_pile.py` — King move validation (now in `test_move_validator.py`)

---

## Note sulla migrazione

Questi test facevano riferimento alla vecchia struttura del pacchetto `scr`. Dopo la migrazione dell'architettura pulita:
- Pacchetto rinominato: `scr` → `src`
- GameState module removed (functionality split into GameTable + services)
- Test coverage maintained via integration tests in `tests/integration/`

**Status**: ARCHIVED (not deleted) for historical reference.

**Ultima versione funzionante**: v3.1.x (prima della rimozione del pacchetto scr)
