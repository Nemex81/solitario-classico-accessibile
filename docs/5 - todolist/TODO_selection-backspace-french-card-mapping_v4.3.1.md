# TODO: selection-backspace-french-card-mapping v4.3.1

> Piano di riferimento: [PLAN_selection-backspace-french-card-mapping_v4.3.1.md](../3%20-%20coding%20plans/PLAN_selection-backspace-french-card-mapping_v4.3.1.md)
>
> Versione target: **v4.3.1**
> Branch: `fix/selection-backspace-french-cards-v4.3.1`
> Agente: Agent-Code

---

## Istruzioni per Agent-Code

Esegui le fasi nella sequenza indicata. Ogni fase termina con un commit atomico.
Dopo ogni commit, aggiorna la checklist segnando `[x]` sulle voci completate.
Non passare alla fase successiva se la pre-commit checklist della fase corrente
non è superata.

---

## Fase 1 — Input/Selection (Delete → Backspace + annuncio vocale)

**Commit atteso:** `fix(input): rimappa CANCEL_SELECTION da Delete a Backspace con annuncio vocale`

- [x] `src/application/input_handler.py`: `CANCEL_SELECTION` rimappato a `pygame.K_BACKSPACE`
- [x] `src/application/gameplay_controller.py`: `Backspace` reso tasto primario per annullare la selezione; `Delete` mantenuto come alias wx/pygame compatibile
- [x] `src/application/gameplay_controller.py` help e docstring `_cancel_selection()`: aggiornati da `CANC/DELETE` a `Backspace/BACKSPACE`
- [x] `src/presentation/game_formatter.py` e `src/domain/services/selection_manager.py`: messaggi utente riallineati a `Backspace`
- [x] `src/application/game_engine.py`: aggiunta sostituzione atomica della selezione con annuncio vocale descrittivo e rollback se la nuova selezione fallisce
- [x] Validazione: `py_compile` su file modificati + test mirati verdi

---

## Fase 2 — Card Image Mapping (asset francesi mancanti)

**Commit atteso:** `fix(ui): completa gli asset mancanti del mazzo francese`

- [x] Verificata la root cause reale: `BoardState` e `GameplayPanel` passavano già stringhe corrette; il problema era il set incompleto in `assets/img/carte_francesi`
- [x] Generati i 6 file mancanti: `5-quadri.jpg`, `7-cuori.jpg`, `8-cuori.jpg`, `9-fiori.jpg`, `9-picche.jpg`, `9-quadri.jpg`
- [x] Verifica visiva locale sulle carte rigenerate completata
- [x] `tests/unit/test_card_image_cache.py`: aggiunti test di presenza asset e mapping rank italiani

---

## Fase 3 — Test / Validation

**Commit atteso:** `test: aggiungi test Backspace/annuncio vocale e rank italiani cache`

- [x] `tests/unit/test_card_image_cache.py`: aggiunti 4 test rank italiani (`Asso`, `Jack`, `Regina`, `Re`)
- [x] `tests/unit/application/test_input_handler_audio.py`: aggiornato il test `CANCEL_SELECTION` a `K_BACKSPACE`
- [x] Creato `tests/unit/application/test_game_engine_selection_replacement.py` per verificare sostituzione selezione e rollback
- [x] Eseguiti test mirati sui file toccati: 55 passed, 0 failed
- [x] Nota validazione: `mypy` focalizzato non ha restituito esito utile prima della terminazione del terminale; nessun errore editor sui file modificati

---

## Fase 4 — Docs Sync

**Commit atteso:** `docs: aggiorna API.md e CHANGELOG per v4.3.1`

- [x] `docs/API.md`: aggiornata la voce keyboard mapping `CANCEL_SELECTION` → `Backspace`
- [x] `CHANGELOG.md`: aggiunta voce `[Unreleased]` con input, selection replacement e completamento asset francesi
- [x] `docs/5 - todolist/TODO_selection-backspace-french-card-mapping_v4.3.1.md`: riallineato alla root cause corretta e marcato completato

---

## Stato globale

- [x] Fase 1 completata
- [x] Fase 2 completata
- [x] Fase 3 completata
- [x] Fase 4 completata
- [x] PR / task CHIUSO
