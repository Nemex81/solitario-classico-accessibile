---
feature: gameplay-visual-ui
type: plan
agent: Agent-Plan
status: REVIEWED
version: v4.0.0
design_ref: docs/2 - projects/DESIGN_gameplay-visual-ui.md
date: 2026-04-08
note: Rendering testuale completato. Esteso da PLAN_gameplay-card-images_v4.1.0.md per supporto immagini reali.
---

# PLAN: Gameplay Visual UI — v4.0.0

## Executive Summary

| Attributo | Valore |
|-----------|--------|
| Tipo | Feature — nuova funzionalita visiva + accessibilita |
| Priorita | Alta |
| Branch | `feature/gameplay-visual-ui` |
| Versione target | v4.0.0 |
| Design di riferimento | [DESIGN_gameplay-visual-ui.md](../2%20-%20projects/DESIGN_gameplay-visual-ui.md) (status: REVIEWED) |
| Fasi totali | 9 (Fase 0 — Fase 8) |

---

## Problema e Obiettivo

### Problema

La finestra di gameplay del Solitario Classico Accessibile e attualmente una interfaccia puramente audio/testuale. L'assenza di qualsiasi rendering visivo rende il gioco inutilizzabile per giocatori vedenti e ipovedenti, limitando drasticamente la base di utenti. Inoltre, `GamePlayController._vocalizza()` usa `pygame.time.wait()` che blocca il thread UI — un difetto che impedirebbe il funzionamento del rendering visivo e che viola gia la Clean Architecture (dipendenza pygame nel layer Application).

### Obiettivo

Introdurre una **board visiva dual-mode** che:

- Renderizza le 13 pile del solitario Klondike (7 tableau, 4 foundation, stock, waste) con carte disegnate, cursore evidenziato e selezione distinta
- Opera in due modalita: `audio_only` (default, comportamento attuale intatto) e `visual` (rendering completo)
- Garantisce zero regressione per utenti non vedenti: tutti i 60+ comandi tastiera, tutti gli annunci TTS e tutti i suoni restano identici
- Supporta 3 temi visivi (Standard, Alto Contrasto, Grande) per ipovedenti
- Mantiene piena accessibilita NVDA tramite info-zone off-screen parallela al rendering

---

## File Coinvolti

### Nuovi file (CREATE)

| File | Descrizione |
|------|-------------|
| `src/application/board_state.py` | BoardState DTO e CardView dataclass — strato di confine tra application e presentation |
| `src/infrastructure/ui/card_renderer.py` | CardRenderer — disegna singola carta (fronte/dorso, highlight, selezione) tramite wx.DC |
| `src/infrastructure/ui/board_layout_manager.py` | BoardLayoutManager — calcola posizioni responsive di tutte le pile su EVT_SIZE |
| `src/infrastructure/ui/visual_theme.py` | VisualTheme — 3 temi (Standard, AltoContrasto, Grande) con proprieta colori e font |
| `tests/unit/test_board_state.py` | Unit test per BoardState e CardView |
| `tests/unit/test_card_renderer.py` | Unit test per CardRenderer con mock wx.DC |
| `tests/unit/test_board_layout_manager.py` | Unit test per BoardLayoutManager: calcoli posizionali |
| `tests/unit/test_visual_theme.py` | Unit test per selezione e proprieta dei 3 temi |

### File modificati (MODIFY)

| File | Modifiche principali |
|------|----------------------|
| `src/application/gameplay_controller.py` | Rimozione `pygame.time.wait()` e import pygame; aggiunta callback `on_board_changed`; metodo `_build_board_state()`; invocazione callback dopo ogni azione |
| `src/domain/services/game_settings.py` | Aggiunta impostazioni `display_mode` (str, default `"audio_only"`) e `visual_theme` (str, default `"standard"`) |
| `src/infrastructure/ui/gameplay_panel.py` | Ristrutturazione completa: dual-mode, EVT_PAINT, dirty-rect, info-zone NVDA off-screen, F3 toggle, blink timer |
| `src/infrastructure/ui/wx_frame.py` | Min size portato a 900x650 |
| `src/infrastructure/ui/options_dialog.py` | Aggiunta selettori tema visivo e modalita display |
| `src/infrastructure/ui/basic_panel.py` | Eventuali adattamenti per dual-mode (da verificare durante Fase 6) |

### File non modificati (confermati intatti)

- `src/domain/**` — modifiche minime: solo `src/domain/services/game_settings.py` (aggiunta 2 attributi opzionali con default)
- `src/application/game_engine.py` — nessuna modifica
- `src/application/cursor_manager.py` — nessuna modifica
- `src/application/selection_manager.py` — nessuna modifica

---

## Dipendenze tra Fasi

```
Fase 0 (prerequisito pygame)
  |
  v
Fase 1 (BoardState DTO)
  |
  v
Fase 2 (observer on_board_changed)  ─────┐
  |                                       |
  v                                       |
Fase 3 (VisualTheme)                      |
  |                                       |
  v                                       |
Fase 4 (CardRenderer)                     |
  |                                       |
  v                                       |
Fase 5 (BoardLayoutManager)               |
  |                                       |
  v                                       |
Fase 6 (GameplayPanel dual-mode) ←────────┘
  |
  v
Fase 7 (Frame resize + opzioni)
  |
  v
Fase 8 (test integrazione + validazione)
```

---

## Fasi Sequenziali

### Fase 0 — Prerequisito: Rimozione `pygame.time.wait()`

**Scopo**: eliminare il blocco del thread UI e rimuovere la dipendenza pygame dal layer Application (violazione Clean Architecture).

**File coinvolti**:
- MODIFY: `src/application/gameplay_controller.py`

**Operazioni**:
1. Identificare tutte le occorrenze di `pygame.time.wait()` nei metodi `_vocalizza()` e `_speak_with_hint()`
2. **ELIMINARE** le righe `pygame.time.wait(100)` e `pygame.time.wait(200)` senza sostituzione (`wx.CallLater` è asincrono e semanticamente incompatibile con uno sleep sincrono: il TTS nativo wxPython/SAPI5 gestisce i propri tempi)
3. Rimuovere `from pygame.locals import KMOD_SHIFT, KMOD_CTRL` (non più usati dopo la migrazione a `handle_wx_key_event()`)
4. **NON rimuovere** `import pygame` dalla riga principale né le costanti `pygame.K_xxx` in `_build_commands()`: questo metodo è il legacy pygame handler e può restare per compatibilità; `handle_wx_key_event()` è già il metodo nativo wx utilizzato dalla UI e non dipende da `_build_commands()`
5. Aggiungere il metodo `set_on_board_changed(callback: Callable[[BoardState], None] | None) -> None` come attributo `self._on_board_changed_callback` (per Fase 2)

**Nota architetturale** (`_build_commands()` vs `handle_wx_key_event()`):
- `handle_wx_key_event()` è il metodo nativo wx già completo con if/elif diretti — è ciò che la UI usa attualmente
- `_build_commands()` è il legacy handler pygame con `pygame.K_xxx` — non è chiamato da wxPython e può restare invariato
- Pertanto **`import pygame` rimane** per non rompere `_build_commands()`; solo `KMOD_SHIFT/KMOD_CTRL` e i `pygame.time.wait()` vengono rimossi

**Test di validazione**:
- Tutti i comandi tastiera funzionano senza blocco UI percepibile
- L'ordine degli annunci TTS è identico a prima
- `grep -n "KMOD_SHIFT\|KMOD_CTRL\|pygame.time.wait" src/application/gameplay_controller.py` restituisce zero occorrenze

**Commit**: `refactor(application): rimuovi pygame.time.wait e KMOD in gameplay_controller`

---

### Fase 1 — BoardState DTO e CardView

**Scopo**: creare il contratto di dati tra application layer e presentation layer, rispettando la Clean Architecture (il presentation non importa domain.Card).

**File coinvolti**:
- CREATE: `src/application/board_state.py`
- CREATE: `tests/unit/test_board_state.py`

**Operazioni**:
1. Definire `CardView` come `NamedTuple` o `@dataclass(frozen=True)`:
   - `rank: str` — es. "A", "2", "10", "J", "Q", "K"
   - `suit: str` — es. "cuori", "quadri", "fiori", "picche"
   - `face_up: bool`
   - `suit_color: str` — "red" o "black"
2. Definire `BoardState` come `@dataclass`:
   - `piles: list[list[CardView]]` — 13 liste (indici 0-6 tableau, 7-10 foundation, 11 waste/scarti, 12 stock/mazzo)
   - `cursor_pile_idx: int`
   - `cursor_card_idx: int`
   - `selection_active: bool`
   - `selected_pile_idx: int | None`
   - `selected_cards: list[CardView] | None`
   - `game_over: bool`
3. Aggiungere type hints completi e docstring per ogni classe

**Test**:
- Costruzione BoardState con dati validi
- Comportamento con `selected_cards=None` e `selected_pile_idx=None`
- Immutabilita di CardView se implementata come `frozen=True`
- Coverage: >= 85% su `board_state.py`

**Commit**: `feat(application): aggiungi BoardState DTO e CardView`

---

### Fase 2 — Observer callback `on_board_changed`

**Scopo**: introdurre il canale di notifica dal controller al panel senza dipendenze cicliche.

**File coinvolti**:
- MODIFY: `src/application/gameplay_controller.py`

**Operazioni**:
1. Aggiungere attributo `_on_board_changed_callback: Callable[[BoardState], None] | None = None`
2. Aggiungere metodo pubblico `set_on_board_changed(callback: Callable[[BoardState], None]) -> None`
3. Implementare metodo privato `_build_board_state() -> BoardState`:
   - Legge `GameEngine.get_table()` (o equivalente) per ottenere lo stato delle 13 pile
   - Converte ogni `Card` di dominio in `CardView` (rank, suit, face_up, suit_color)
   - Legge posizione cursore da `CursorManager`
   - Legge stato selezione da `SelectionManager`
   - Costruisce e restituisce `BoardState`
4. Invocare `_notify_board_changed()` (wrapper che controlla se la callback e registrata) dopo ogni azione che modifica lo stato:
   - `handle_wx_key_event()` gia centralizzato — aggiungere invocazione al termine

**Test**:
- Mock callback registrata: verificare che venga invocata dopo ogni azione
- `_build_board_state()`: verificare struttura BoardState prodotta con stato di gioco noto
- BoardState con selezione attiva e selezione inattiva

**Commit**: `feat(application): aggiungi observer on_board_changed`

---

### Fase 3 — VisualTheme e configurazione temi

**Scopo**: incapsulare le proprieta visive dei 3 temi in un oggetto coeso, evitando valori magici sparsi nel codice di rendering.

**File coinvolti**:
- CREATE: `src/infrastructure/ui/visual_theme.py`
- CREATE: `tests/unit/test_visual_theme.py`

**Operazioni**:
1. Definire `@dataclass` o `TypedDict` `ThemeProperties`:
   - `bg_color: tuple[int,int,int]` — colore sfondo board
   - `card_bg: tuple[int,int,int]` — colore sfondo carta scoperta
   - `card_back: tuple[int,int,int]` — colore dorso carta coperta
   - `text_red: tuple[int,int,int]` — colore testo seme rosso
   - `text_black: tuple[int,int,int]` — colore testo seme nero
   - `border_color: tuple[int,int,int]` — colore bordo carta normale
   - `cursor_color: tuple[int,int,int]` — colore bordo cursore
   - `selection_color: tuple[int,int,int]` — colore bordo selezione
   - `border_width: int` — spessore bordo carta
   - `cursor_width: int` — spessore bordo cursore
   - `font_size_base: int` — dimensione font rank (pt)
   - `card_scale: float` — moltiplicatore dimensione carta (1.0 standard, 1.5 grande)
2. Implementare i 3 temi predefiniti come costanti o factory:
   - `THEME_STANDARD`: sfondo verde tavolo (0,100,0), carte bianche, font 14pt, scale 1.0
   - `THEME_ALTO_CONTRASTO`: sfondo nero, bordi bianchi 3px, cursore giallo fluorescente (255,255,0), font 16pt
   - `THEME_GRANDE`: come Standard ma scale 1.5, font 21pt, bordi 2px
3. Funzione `get_theme(name: str) -> ThemeProperties` con fallback su STANDARD

**Test**:
- `get_theme("standard")` restituisce `THEME_STANDARD`
- `get_theme("alto_contrasto")` restituisce `THEME_ALTO_CONTRASTO`
- `get_theme("grande")` restituisce `THEME_GRANDE`
- `get_theme("sconosciuto")` restituisce `THEME_STANDARD` (fallback)
- Proprieta dei temi: verifica valori critici (cursor_color alto contrasto = giallo)

**Commit**: `feat(presentation): aggiungi sistema temi visuali`

---

### Fase 4 — CardRenderer

**Scopo**: componente che incapsula il disegno di una singola carta su wx.DC, separando la logica di rendering dalla logica di layout.

**File coinvolti**:
- CREATE: `src/infrastructure/ui/card_renderer.py`
- CREATE: `tests/unit/test_card_renderer.py`

**Operazioni**:
1. Creare classe `CardRenderer`:
   - Metodo principale: `draw_card(dc: wx.DC, card: CardView, x: int, y: int, width: int, height: int, theme: ThemeProperties, highlighted: bool = False, selected: bool = False) -> None`
   - Per carta `face_up=True`: sfondo `card_bg`, rank in alto a sinistra, simbolo seme Unicode centrato, colore testo da `suit_color`
   - Per carta `face_up=False`: sfondo `card_back`, pattern dorso uniforme (es. linee diagonali o colore pieno + bordo interno)
   - Bordo normale: `border_color`, spessore `border_width`
   - Se `highlighted=True`: bordo aggiuntivo `cursor_color`, spessore `cursor_width` (sovrapposto al bordo normale)
   - Se `selected=True`: bordo aggiuntivo `selection_color`, spessore `cursor_width`
   - I simboli seme Unicode: cuori=♥, quadri=♦, fiori=♣, picche=♠
2. Metodo helper privato `_draw_border(dc, x, y, w, h, color, width)` per evitare duplicazione
3. Metodo helper privato `_draw_suit_symbol(dc, suit, x, y, w, h, color)` per simbolo centrato

**Considerazioni di test** (wx richiede display attivo):
- I test devono usare `wx.MemoryDC` con `wx.Bitmap` in un test case che inizializza `wx.App`
- Alternativa: factoring delle operazioni dc in modo testabile isolando i calcoli da wx

**Test**:
- `draw_card` su carta scoperta: verifica che le chiamate dc siano effettuate senza eccezioni
- `draw_card` su carta coperta: idem
- `highlighted=True`: verifica che il bordo highlight venga disegnato
- `selected=True`: idem per selezione
- Coverage: >= 85% su `card_renderer.py`

**Commit**: `feat(presentation): aggiungi CardRenderer`

---

### Fase 5 — BoardLayoutManager

**Scopo**: calcolare in modo responsive le posizioni e dimensioni di tutte le pile sul panel, separando la geometria dalla logica di rendering.

**File coinvolti**:
- CREATE: `src/infrastructure/ui/board_layout_manager.py`
- CREATE: `tests/unit/test_board_layout_manager.py`

**Operazioni**:
1. Definire `@dataclass` `PileGeometry`:
   - `x: int`, `y: int` — posizione in alto a sinistra della pila
   - `card_width: int`, `card_height: int` — dimensioni carta
   - `fan_offset_face_up: int` — offset verticale carte scoperte
   - `fan_offset_face_down: int` — offset verticale carte coperte
2. Creare classe `BoardLayoutManager`:
   - Metodo `calculate_layout(panel_width: int, panel_height: int, theme: ThemeProperties) -> dict[int, PileGeometry]`
   - Restituisce dizionario pile_idx -> PileGeometry per tutte e 13 le pile
   - Calcoli:
     - `card_width = int(panel_width / 9 * theme.card_scale)`
     - `card_height = int(card_width * 3.5 / 2.5)` (aspect ratio costante)
     - Margine orizzontale: `(panel_width - 7 * card_width) / 8`
     - Zona superiore (y=margin_top): waste/scarti (idx=11), stock/mazzo (idx=12), foundation 0-3 (idx=7-10)
     - Zona inferiore (y=zona_superiore_height + gap): tableau 0-6 (idx=0-6)
     - `fan_offset_face_down = card_height // 5`
     - `fan_offset_face_up = card_height // 3`
   - Metodo `get_pile_geometry(pile_idx: int) -> PileGeometry | None` (usa cache dell'ultimo calcolo)
   - Metodo `get_card_rect(pile_idx: int, card_idx: int, pile: list[CardView]) -> tuple[int,int,int,int] | None` — calcola rect (x,y,w,h) della singola carta nel fan

**Test** (puri Python, nessuna dipendenza wx):
- `calculate_layout(900, 650, THEME_STANDARD)`: verifica che 13 pile abbiano geometry non None
- Aspect ratio carte: `card_height / card_width` circa 1.4 (3.5/2.5)
- Posizioni non sovrapposte tra pile nella zona superiore
- Tema Grande con scale=1.5: carte piu grandi
- Coverage: >= 85% su `board_layout_manager.py`

**Commit**: `feat(presentation): aggiungi BoardLayoutManager`

---

### Fase 6 — GameplayPanel ristrutturato (dual-mode)

**Scopo**: integrare CardRenderer e BoardLayoutManager nel panel esistente, implementare il dual-mode e il canale NVDA off-screen.

**File coinvolti**:
- MODIFY: `src/infrastructure/ui/gameplay_panel.py`
- MODIFY (se necessario): `src/infrastructure/ui/basic_panel.py`

**Operazioni**:
1. Aggiungere attributi:
   - `_display_mode: str = "audio_only"` (property con setter che triggera refresh)
   - `_board_state: BoardState | None = None`
   - `_card_renderer: CardRenderer`
   - `_layout_manager: BoardLayoutManager`
   - `_current_theme: ThemeProperties`
   - `_blink_timer: wx.Timer`
   - `_cursor_blink_on: bool = True`
   - `_nvda_info_zone: wx.StaticText` — posizionato a (-10000, -10000)

2. Inizializzazione (`__init__`):
   - Creare `_card_renderer`, `_layout_manager` con tema default
   - Creare `_nvda_info_zone` con `wx.StaticText(self, label="", style=wx.NO_BORDER)`; `_nvda_info_zone.Move((-10000, -10000))`
   - Bind `EVT_PAINT` -> `_on_paint`
   - Bind `EVT_SIZE` -> `_on_size`
   - Creare `_blink_timer`, bind `EVT_TIMER` -> `_on_blink_timer`

3. Handler EVT_PAINT (`_on_paint`):
   - Se `_display_mode == "audio_only"`: return immediatamente (nessun rendering)
   - Se `_board_state is None`: disegna sfondo vuoto
   - Creare `wx.AutoBufferedPaintDC(self)`
   - Per ogni pila: chiamare `_layout_manager.get_pile_geometry(pile_idx)` -> iterare carte -> `_card_renderer.draw_card()`
   - `highlighted`: pile_idx == `board_state.cursor_pile_idx` e card_idx == `board_state.cursor_card_idx`; se blink_on=False, non disegnare highlight
   - `selected`: la carta e in `board_state.selected_cards`

4. Handler EVT_SIZE (`_on_size`):
   - Ricalcolare `_layout_manager.calculate_layout(new_width, new_height, _current_theme)`
   - `self.Refresh()`

5. Callback `_on_board_changed(board_state: BoardState)`:
   - Salvare `_board_state = board_state`
   - Aggiornare `_nvda_info_zone.SetLabel(_build_nvda_text(board_state))`
   - Aggiornare accessible name del panel: `self.SetName(f"Board solitario - Cursore su {_pile_name(board_state.cursor_pile_idx)}")`
   - Se `_display_mode == "visual"`: `self.Refresh()` (o dirty-rect ottimizzato se possibile)

6. Metodo `_build_nvda_text(board_state: BoardState) -> str`:
   - Costruisce stringa leggibile: "Pila tableau 3, carta: 7 di cuori scoperta, 2 carte coperte sotto."
   - Se selezione attiva: aggiunge "Selezione attiva: 10 di picche."

7. Toggle F3 in `on_key_down` (o EVT_CHAR_HOOK):
   - Prima del dispatch al controller, intercettare F3
   - Alternare `_display_mode` tra "audio_only" e "visual"
   - Annunciare la modalita: `controller.announce("Modalita visiva attivata")` o TTS diretto
   - NON chiamare `event.Skip()` per F3 (consumato)

8. Blink timer:
   - Avviare `_blink_timer.Start(500)` solo in modalita visual
   - `_on_blink_timer`: toggle `_cursor_blink_on`, invalidate solo rect cursore (dirty-rect)
   - Fermare il timer in modalita audio_only

9. Registrazione callback:
   - Nel metodo che riceve il controller (es. `set_controller()`): `controller.set_on_board_changed(self._on_board_changed)`

**Test**:
- Dual-mode: verifica che in audio_only EVT_PAINT non esegua rendering
- F3 toggle: verifica cambio display_mode
- Callback on_board_changed: verifica aggiornamento info-zone
- Info-zone: verifica contenuto testo con BoardState noto

**Commit**: `feat(presentation): ristruttura GameplayPanel con dual-mode visivo`

---

### Fase 7 — Resize frame e integrazione opzioni

**Scopo**: portare la finestra alla dimensione minima necessaria e permettere all'utente di configurare modalita e tema dalle opzioni.

**File coinvolti**:
- MODIFY: `src/infrastructure/ui/wx_frame.py`
- MODIFY: `src/domain/services/game_settings.py`
- MODIFY: `src/infrastructure/ui/options_dialog.py`

**Operazioni**:

`wx_frame.py`:
1. Trovare la chiamata `SetMinSize()` o il parametro di dimensione nel costruttore del frame
2. Portare min size a `(900, 650)` — da verificare il valore attuale
3. Verificare che `wx.RESIZE_BORDER` sia abilitato (il frame deve essere ridimensionabile)

`game_settings.py`:
1. Aggiungere campo `display_mode: str = "audio_only"` con validazione (valori ammessi: "audio_only", "visual")
2. Aggiungere campo `visual_theme: str = "standard"` con validazione (valori ammessi: "standard", "alto_contrasto", "grande")
3. Garantire backward compatibility: se la chiave non esiste nel file di configurazione, usare il default

`options_dialog.py`:
1. Aggiungere sezione "Modalita Display" con `wx.RadioBox` o `wx.Choice` per `display_mode`
2. Aggiungere sezione "Tema Visivo" con `wx.Choice` per `visual_theme` (opzioni: Standard, Alto Contrasto, Grande)
3. Collegare i controlli a `game_settings` in lettura e scrittura
4. Il cambio tema deve propagarsi al `GameplayPanel` tramite il controller o un canale dedicato

**Test integrazione**:
- Modifica display_mode persiste al riavvio
- Modifica visual_theme persiste al riavvio
- Frame ridimensionabile con min size 900x650

**Commit**: `feat(presentation): resize frame e opzioni tema visivo`

---

### Fase 8 — Test integrazione e validazione accessibilita

**Scopo**: garantire che il sistema integrato funzioni correttamente e che non esistano regressioni per utenti non vedenti.

**File coinvolti**:
- CREATE/MODIFY: test di integrazione in `tests/`

**Operazioni**:
1. Test end-to-end del flusso completo: keypress -> controller -> board_state -> panel -> rendering
2. Regression test tastiera: verificare che tutti i comandi mappati nel controller siano raggiungibili senza blocco UI
3. Test modalita audio_only: zero rendering, tutti gli annunci TTS identici alla versione pre-feature
4. Test modalita visual: rendering avviene, info-zone NVDA e aggiornata
5. Test toggle F3: alternanza corretta tra modalita
6. Test tema alto contrasto: proprieta visive corrette applicate al rendering
7. Verifica coverage: soglie su `board_state.py`, `card_renderer.py`, `board_layout_manager.py`

**Checklist validazione pre-commit**:
- [ ] `python -m py_compile src/**/*.py` — zero errori
- [ ] `mypy src/ --strict` — zero errori di tipo
- [ ] `pylint --enable=cyclic-import` — zero import ciclici
- [ ] `grep -r "print(" src/` — zero occorrenze
- [ ] `pytest --cov=src` — coverage sopra soglia
- [ ] `grep -rn "pygame.time.wait" src/` — zero occorrenze

**Commit**: `test: validazione integrazione gameplay visual UI`

---

## Test Plan

### Unit test (per componente)

| File test | Componente | Coverage target |
|-----------|------------|-----------------|
| `tests/unit/test_board_state.py` | `BoardState`, `CardView` | >= 85% |
| `tests/unit/test_card_renderer.py` | `CardRenderer` | >= 85% |
| `tests/unit/test_board_layout_manager.py` | `BoardLayoutManager`, `PileGeometry` | >= 85% |
| `tests/unit/test_visual_theme.py` | `VisualTheme`, `get_theme()` | >= 90% |

### Integration test

| Scenario | Componenti coinvolti |
|----------|----------------------|
| Keypress -> callback -> render | GamePlayController + GameplayPanel |
| Toggle F3 dual-mode | GameplayPanel |
| Profilo: salvataggio e caricamento display_mode e visual_theme | GameSettings + OptionsDialog |
| Resize: layout ricalcolato correttamente | GameplayPanel + BoardLayoutManager |

### Regression test

- Tutti i 60+ comandi tastiera devono funzionare identicamente in entrambe le modalita
- L'ordine e il contenuto degli annunci TTS non devono cambiare in modalita audio_only
- La sequenza new game -> play -> game over deve completarsi senza errori in entrambe le modalita

---

## Rischi Residui e Mitigazioni

| Rischio | Livello | Mitigazione |
|---------|---------|-------------|
| wx.DC non disponibile in ambiente headless (CI) | MEDIO | test card_renderer con wx.App inizializzata o skip in CI con marker `@pytest.mark.gui` |
| Blink timer attivo in audio_only per errore | BASSO | Fermare il timer esplicitamente nel setter di display_mode |
| Backward compat profilo utente | MEDIO | game_settings usa `.get(key, default)` per ogni nuova chiave |
| Performance rendering tableau profondi (10+ carte) | BASSO | dirty-rect limita ridisegno; nessun alpha blending |
| F3 intercettato da NVDA prima di wx | BASSO | Testare con NVDA attivo; alternativa: Ctrl+F3 o menu opzioni |

---

## Vincoli Architetturali Applicati

- **Clean Architecture**: CardRenderer e BoardLayoutManager vivono in `src/infrastructure/ui/`; BoardState e CardView in `src/application/`; il domain layer resta intatto
- **Zero breaking changes**: la modalita `audio_only` e il default; tutti i 60+ comandi tastiera invariati
- **Type hints obbligatori**: tutti i nuovi moduli usano type hints completi (standard `python.instructions.md`)
- **Zero print()**: nessun `print()` in `src/`; solo logging semantico
- **Accessibilita NVDA**: info-zone off-screen obbligatoria in modalita visual

---

## Stato Avanzamento

- [ ] Definito (DRAFT creato)
- [ ] In implementazione
- [ ] Test superati
- [ ] Chiuso
