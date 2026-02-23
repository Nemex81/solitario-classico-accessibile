📋 TODO – Revisione sistema audio centralizzato (v3.4.x)
Branch: supporto-audio-centralizzato
Tipo: Feature / Bugfix
Priorità: CRITICAL → HIGH
Stato: READY

---

📖 Piano di riferimento:
- [2 - projects/PLAN_revisione_audio_centralizzato.md](2%20-%20projects/PLAN_revisione_audio_centralizzato.md) (questo piano)

Obiettivo: completare l'integrazione di tutti gli eventi audio (gameplay, UI, dialoghi, menu, timer, ambient, music) affinché ogni azione generi un suono valido, rispettando il design del sistema audio centralizzato. Il lavoro è suddiviso in fasi incrementali; aggiornare questo TODO dopo ogni fase completata.

---

### Fase 1 – Core gameplay [7h totali]

#### 1.1 Helper (30 min) — PREREQUISITO
- [ ] Creare `_map_pile_to_index(pile) -> Optional[int]`
  - 0‑6 tableau, 7‑10 foundation, 11 waste, 12 stock

#### 1.2 Panning Fix (45 min)
- [ ] Aggiornare CARD_MOVE a passare indici reali
- [ ] Aggiungere source/destination anche a STOCK_DRAW
- [ ] Validare panning stereo in test

#### 1.3 Navigazione (2.5 h)
- [ ] 4 frecce: `_cursor_up/down/left/right` → `UI_NAVIGATE`
- [ ] 7 pile base: `_nav_pile_base(0..6)` → `UI_NAVIGATE`
- [ ] 3 pile speciali: `_nav_pile_semi`, `_nav_pile_scarti`, `_nav_pile_mazzo`
- [ ] 2 comandi addizionali: `_cursor_tab`, `_cursor_home`, `_cursor_end`

#### 1.4 Selezione (1 h)
- [ ] Evento `CARD_SELECT` in `_select_card()` (solo se success)
- [ ] Evento `UI_CANCEL` in `_cancel_selection()`
- [ ] Boundary hit (`TABLEAU_BUMPER`) quando non si muove cursor

#### 1.5 Victory (45 min)
- [ ] Aggiungere evento `GAME_WON` in callback di fine partita

#### 1.6 Test
- [x] Mock AudioManager e verifiche panning
- [x] Copertura evento per ognuno dei metodi precedenti

### Fase 2 – Dialoghi e Input
- [ ] Refactor `SolitarioDialogManager`: audio apertura/chiusura in tutti i metodi
- [ ] Documentare InputHandler come codice morto (TODO di refactor v3.5)
- [ ] Iniettare `AudioManager` in `OptionsWindowController`
- [ ] Aggiungere audio navigation/select/cancel in OptionsWindowController
- [ ] Test unitari per DialogManager, InputHandler, OptionsWindowController

### Fase 3 – Menu & Mixer
- [x] Integrare audio nel menu principale o creare `MainMenuController`
- [x] Implementare `MixerController` accessibile (tasto M) con audio/TTS
- [x] Boundary hit anche per fine corsa cursore
- [x] Test di comportamento menu e mixer

### Fase 4 – Timer & loop ambient/music [2h totali]

#### 4.1 Timer (SKIP: implementazione già esistente)
- [x] Callbacks `_on_timer_warning/expired` presenti in `game_engine.py` (v3.4.2)
- [x] Test integrazione `TIMER_WARNING` (30 min)
- [x] Test integrazione `TIMER_EXPIRED` (30 min)

#### 4.2 Ambient Loop (45 min)
- [x] Avviare `AMBIENT_LOOP` in `acs_wx.py` subito dopo init audio
- [x] Validare con test manuale/autom.

#### 4.3 Focus handling (30 min)
- [x] Bind `wx.EVT_ACTIVATE` per mettere in pausa/resume i loop
- [x] Test alt‑tab e perdita focus

#### 4.4 Config opzionali
- [x] Aggiornare `audio_config.json` per eventi opzionali
- [x] Verificare che loader filtri correttamente


### Fase 5 – Finitura & documentazione
- [ ] Aggiornare `API.md`, `ARCHITECTURE.md`, README
- [ ] Mypy/flake8 senza errori, coverage ≥ 90 %
- [ ] Aggiornare CHANGELOG e link del TODO
- [ ] Merge su main solo dopo Fase 1 o con disclaimer nel README

---

🗂️ File principali coinvolti
- `src/application/gameplay_controller.py` (16 metodi + helper panning)
- `src/application/input_handler.py` *(deprecato, nessuna modifica necessaria)*
- `src/application/dialog_manager.py`
- `src/application/options_controller.py`
- `src/application/*` (menu/mixer; verificare presenza `MainMenuController`)
- `src/application/game_engine.py` (GAME_WON, timer callbacks già presenti)
- `src/infrastructure/di_container.py`
- `src/infrastructure/ui/*` (gameplay_panel, main_frame, altri)
- `docs/API.md`, `docs/ARCHITECTURE.md`, README, config audio
- `tests/unit/*`, `tests/integration/*` (varie)

---

📋 Linee guida generali
- Incapsulare ogni chiamata audio in `if self._audio: try: ... except: pass`
- Usare panning quando possibile (pile index)
- Degradare graziosamente se audio disabilitato
- Aggiornare test prima di modificare il codice (TDD) quando possibile
- Documentare ogni nuovo evento e modifica API

---

*Autore: AI Assistant – 23 Febbraio 2026*
✅ Criteri di Completamento

L'implementazione è considerata completa quando:

- [ ] Tutte le checklist sopra sono spuntate
- [ ] Tutti i test passano
- [ ] Nessuna regressione funzionale
- [ ] Versione aggiornata coerentemente (SemVer)

---

📝 Aggiornamenti Obbligatori a Fine Implementazione

- [ ] Aggiornare `README.md` se la feature è visibile all'utente
- [ ] Aggiornare `CHANGELOG.md` con entry dettagliata
- [ ] Incrementare versione in modo coerente:
  - **PATCH** → bug fix
  - **MINOR** → nuova feature retrocompatibile
  - **MAJOR** → breaking change
- [ ] Commit con messaggio convenzionale
- [ ] Push su branch corretto

---

📌 Note

Questo TODO funge da cruscotto; il piano completo rimane la fonte di verità tecnica per ogni fase.

---

**Fine.**

Snello, consultabile in 30 secondi, zero fronzoli.
Il documento lungo resta come fonte di verità tecnica. Questo è il cruscotto operativo.
