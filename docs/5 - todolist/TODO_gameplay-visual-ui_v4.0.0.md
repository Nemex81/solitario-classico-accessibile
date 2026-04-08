---
feature: gameplay-visual-ui
type: todo
agent: Agent-Plan
status: in_progress
version: v4.0.0
plan_ref: docs/3 - coding plans/PLAN_gameplay-visual-ui_v4.0.0.md
date: 2026-04-08
---

# TODO: Gameplay Visual UI — v4.0.0

Piano di riferimento completo: [PLAN_gameplay-visual-ui_v4.0.0.md](../3%20-%20coding%20plans/PLAN_gameplay-visual-ui_v4.0.0.md)

---

## Istruzioni per Agent-Code

Implementa le fasi nell'ordine indicato. Ogni fase deve essere:
1. Completamente implementata (file creati/modificati come da PLAN)
2. Compilata senza errori (`python -m py_compile`)
3. Type-checked (`mypy --strict` sui file modificati)
4. Testata (eseguire i test della fase corrente)
5. Committata con il messaggio indicato nel PLAN
6. Spuntata la checkbox corrispondente in questo file

Non procedere alla fase successiva finche la fase corrente non e completa e committata.

---

## Checklist Fasi

### [ ] Fase 0 — Prerequisito: Rimozione `pygame.time.wait()`

**File**: `src/application/gameplay_controller.py`

- [ ] Identificare tutte le occorrenze di `pygame.time.wait()` nei metodi `_vocalizza()` e `_speak_with_hint()`
- [ ] **ELIMINARE** le righe `pygame.time.wait()` senza sostituzione (il TTS SAPI5 gestisce i propri tempi; `wx.CallLater` è asincrono e incompatibile)
- [ ] Rimuovere `from pygame.locals import KMOD_SHIFT, KMOD_CTRL` (non più usati)
- [ ] **NON toccare** `import pygame` né `pygame.K_xxx` in `_build_commands()` (legacy handler, non usato da wxPython)
- [ ] Verificare `grep -n "KMOD_SHIFT\|KMOD_CTRL\|pygame.time.wait" src/application/gameplay_controller.py` — zero occorrenze
- [ ] Eseguire tutti i test esistenti: nessuna regressione
- [ ] Commit: `refactor(application): sostituisci pygame.time.wait con wx.CallLater`

---

### [ ] Fase 1 — BoardState DTO e CardView

**File**: `src/application/board_state.py`, `tests/unit/test_board_state.py`

- [ ] Creare `CardView` (NamedTuple o frozen dataclass) con: rank, suit, face_up, suit_color
- [ ] Creare `BoardState` dataclass con: piles (13 liste), cursor_pile_idx, cursor_card_idx, selection_active, selected_pile_idx, selected_cards, game_over
- [ ] Aggiungere type hints completi
- [ ] Scrivere `tests/unit/test_board_state.py` con coverage >= 85%
- [ ] `pytest tests/unit/test_board_state.py` — tutti green
- [ ] Commit: `feat(application): aggiungi BoardState DTO e CardView`

---

### [ ] Fase 2 — Observer callback `on_board_changed`

**File**: `src/application/gameplay_controller.py`

- [ ] Aggiungere attributo `_on_board_changed_callback` con tipo `Callable[[BoardState], None] | None`
- [ ] Implementare `set_on_board_changed(callback)` metodo pubblico
- [ ] Implementare `_build_board_state() -> BoardState` che legge da GameEngine, CursorManager, SelectionManager
- [ ] Invocare callback (tramite `_notify_board_changed()`) dopo ogni azione in `handle_wx_key_event()`
- [ ] Test: mock callback invocata correttamente su keypress
- [ ] Test: `_build_board_state()` produce BoardState coerente con stato gioco noto
- [ ] `mypy src/application/gameplay_controller.py --strict` — zero errori
- [ ] Commit: `feat(application): aggiungi observer on_board_changed`

---

### [ ] Fase 3 — VisualTheme e configurazione temi

**File**: `src/infrastructure/ui/visual_theme.py`, `tests/unit/test_visual_theme.py`

- [ ] Creare `ThemeProperties` dataclass con tutti i campi (bg_color, card_bg, card_back, text_red, text_black, border_color, cursor_color, selection_color, border_width, cursor_width, font_size_base, card_scale)
- [ ] Definire `THEME_STANDARD` (sfondo verde, font 14pt, scale 1.0)
- [ ] Definire `THEME_ALTO_CONTRASTO` (sfondo nero, cursore giallo, bordi 3px, font 16pt)
- [ ] Definire `THEME_GRANDE` (come standard, scale 1.5, font 21pt)
- [ ] Implementare `get_theme(name: str) -> ThemeProperties` con fallback STANDARD
- [ ] Scrivere `tests/unit/test_visual_theme.py` con coverage >= 90%
- [ ] `pytest tests/unit/test_visual_theme.py` — tutti green
- [ ] Commit: `feat(presentation): aggiungi sistema temi visuali`

---

### [ ] Fase 4 — CardRenderer

**File**: `src/infrastructure/ui/card_renderer.py`, `tests/unit/test_card_renderer.py`

- [ ] Creare classe `CardRenderer` con metodo `draw_card(dc, card, x, y, width, height, theme, highlighted, selected)`
- [ ] Implementare rendering carta scoperta (sfondo, rank testo, simbolo seme Unicode, colore)
- [ ] Implementare rendering dorso carta coperta
- [ ] Implementare bordo highlight cursore (se `highlighted=True`)
- [ ] Implementare bordo selezione (se `selected=True`)
- [ ] Implementare helper `_draw_border()` e `_draw_suit_symbol()`
- [ ] Scrivere `tests/unit/test_card_renderer.py` con coverage >= 85%
- [ ] `mypy src/infrastructure/ui/card_renderer.py --strict` — zero errori
- [ ] `pytest tests/unit/test_card_renderer.py` — tutti green
- [ ] Commit: `feat(presentation): aggiungi CardRenderer`

---

### [ ] Fase 5 — BoardLayoutManager

**File**: `src/infrastructure/ui/board_layout_manager.py`, `tests/unit/test_board_layout_manager.py`

- [ ] Creare `PileGeometry` dataclass con: x, y, card_width, card_height, fan_offset_face_up, fan_offset_face_down
- [ ] Creare classe `BoardLayoutManager` con metodo `calculate_layout(panel_width, panel_height, theme) -> dict[int, PileGeometry]`
- [ ] Calcoli: card_width proporzionale a panel_width, aspect ratio 2.5:3.5, margini proporzionali
- [ ] Layout zona superiore: stock(11), waste(12), foundation 0-3 (idx 7-10)
- [ ] Layout zona inferiore: tableau 0-6 (idx 0-6)
- [ ] `fan_offset_face_down = card_height // 5`, `fan_offset_face_up = card_height // 3`
- [ ] Metodo `get_card_rect(pile_idx, card_idx, pile) -> tuple[int,int,int,int] | None`
- [ ] Scrivere `tests/unit/test_board_layout_manager.py` (puri Python, nessuna dipendenza wx) con coverage >= 85%
- [ ] `pytest tests/unit/test_board_layout_manager.py` — tutti green
- [ ] Commit: `feat(presentation): aggiungi BoardLayoutManager`

---

### [ ] Fase 6 — GameplayPanel ristrutturato (dual-mode)

**File**: `src/infrastructure/ui/gameplay_panel.py`, eventualmente `src/infrastructure/ui/basic_panel.py`

- [ ] Aggiungere attributi: `_display_mode`, `_board_state`, `_card_renderer`, `_layout_manager`, `_current_theme`, `_blink_timer`, `_cursor_blink_on`, `_nvda_info_zone`
- [ ] Creare `_nvda_info_zone` (wx.StaticText) posizionato a (-10000, -10000)
- [ ] Bind EVT_PAINT -> `_on_paint`; EVT_SIZE -> `_on_size`; EVT_TIMER -> `_on_blink_timer`
- [ ] Implementare handler `_on_paint`: skip in audio_only, rendering completo in visual con AutoBufferedPaintDC
- [ ] Implementare handler `_on_size`: ricalcolo layout + Refresh
- [ ] Implementare callback `_on_board_changed()`: aggiorna board_state, info-zone, accessible name, Refresh()
- [ ] Implementare `_build_nvda_text()`: testo leggibile per NVDA
- [ ] Intercettare F3 in EVT_CHAR_HOOK: toggle display_mode, annuncio vocale, NON event.Skip()
- [ ] Blink timer: Start(500) in visual, Stop() in audio_only
- [ ] Registrare callback su controller in `set_controller()` o equivalente
- [ ] `mypy src/infrastructure/ui/gameplay_panel.py --strict` — zero errori
- [ ] Test: dual-mode toggle, callback aggiornamento, info-zone contenuto
- [ ] Commit: `feat(presentation): ristruttura GameplayPanel con dual-mode visivo`

---

### [ ] Fase 7 — Resize frame e integrazione opzioni

**File**: `src/infrastructure/ui/wx_frame.py`, `src/domain/services/game_settings.py`, `src/infrastructure/ui/options_dialog.py`

- [ ] `wx_frame.py`: portare min size a (900, 650); verificare RESIZE_BORDER abilitato
- [ ] `game_settings.py`: aggiungere `display_mode: str = "audio_only"` con validazione
- [ ] `game_settings.py`: aggiungere `visual_theme: str = "standard"` con validazione
- [ ] `game_settings.py`: backward compat — uso `.get(key, default)` per ogni nuova chiave
- [ ] `options_dialog.py`: aggiungere selettore modalita display (RadioBox o Choice)
- [ ] `options_dialog.py`: aggiungere selettore tema visivo (Choice: Standard, Alto Contrasto, Grande)
- [ ] Test: salvataggio/caricamento impostazioni persiste tra sessioni
- [ ] `mypy src/domain/services/game_settings.py --strict` — zero errori
- [ ] Commit: `feat(presentation): resize frame e opzioni tema visivo`

---

### [ ] Fase 8 — Test integrazione e validazione accessibilita

- [ ] Test end-to-end: keypress -> controller -> board_state -> panel -> render
- [ ] Regression test: 60+ comandi tastiera funzionano in entrambe le modalita
- [ ] Test audio_only: zero rendering, annunci TTS identici alla versione pre-feature
- [ ] Test modalita visual: rendering avviene, info-zone NVDA aggiornata
- [ ] Checklist pre-commit completa:
  - [ ] `python -m py_compile src/**/*.py` — zero errori
  - [ ] `mypy src/ --strict` — zero errori di tipo
  - [ ] `pylint --enable=cyclic-import` — zero import ciclici
  - [ ] `grep -r "print(" src/` — zero occorrenze
  - [ ] `pytest --cov=src` — coverage sopra soglia
  - [ ] `grep -rn "pygame.time.wait" src/` — zero occorrenze
- [ ] Commit: `test: validazione integrazione gameplay visual UI`

---

## Riepilogo Avanzamento

| Fase | Descrizione | Stato |
|------|-------------|-------|
| Fase 0 | Rimozione pygame.time.wait() | [ ] |
| Fase 1 | BoardState DTO e CardView | [ ] |
| Fase 2 | Observer on_board_changed | [ ] |
| Fase 3 | VisualTheme | [ ] |
| Fase 4 | CardRenderer | [ ] |
| Fase 5 | BoardLayoutManager | [ ] |
| Fase 6 | GameplayPanel dual-mode | [ ] |
| Fase 7 | Frame resize + opzioni | [ ] |
| Fase 8 | Test integrazione | [ ] |
