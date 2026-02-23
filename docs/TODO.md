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

### Fase 1 – Core gameplay (v3.4.1 MVP)
- [ ] Implementare `_map_pile_to_index()` helper in `GamePlayController`
- [ ] CARD_MOVE con panning (source/destination index)
- [ ] Eventi navigazione cursore (`_cursor_up/down/left/right`, `_nav_pile_base`)
- [ ] Eventi CARD_SELECT e UI_CANCEL
- [ ] Boundary hit detection (`TABLEAU_BUMPER`)
- [ ] Victory detection callback `_on_game_won` + collegamento
- [ ] Aggiornare test unitari/integration per gli eventi

### Fase 2 – Dialoghi e Input
- [ ] Refactor `SolitarioDialogManager`: audio apertura/chiusura in tutti i metodi
- [ ] Documentare InputHandler come codice morto (TODO di refactor v3.5)
- [ ] Iniettare `AudioManager` in `OptionsWindowController`
- [ ] Aggiungere audio navigation/select/cancel in OptionsWindowController
- [ ] Test unitari per DialogManager, InputHandler, OptionsWindowController

### Fase 3 – Menu & Mixer
- [ ] Integrare audio nel menu principale o creare `MainMenuController`
- [ ] Implementare `MixerController` accessibile (tasto M) con audio/TTS
- [ ] Boundary hit anche per fine corsa cursore
- [ ] Test di comportamento menu e mixer

### Fase 4 – Timer & loop ambient/music
- [ ] Verificare timer callbacks in GamePlayController/engine
- [ ] Avviare `AMBIENT_LOOP` all'inizializzazione in `acs_wx.py`
- [ ] Bind `wx.EVT_ACTIVATE` per pause/resume loop
- [ ] Gestire eventi opzionali tramite `audio_config.json`
- [ ] Test integrati focus e timer audio

### Fase 5 – Finitura & documentazione
- [ ] Aggiornare `API.md`, `ARCHITECTURE.md`, README
- [ ] Mypy/flake8 senza errori, coverage ≥ 90 %
- [ ] Aggiornare CHANGELOG e link del TODO
- [ ] Merge su main solo dopo Fase 1 o con disclaimer nel README

---

🗂️ File principali coinvolti
- `src/application/gameplay_controller.py`
- `src/application/input_handler.py`
- `src/application/dialog_manager.py`
- `src/application/options_controller.py`
- `src/application/*` (menu, mixer)
- `src/application/game_engine.py`
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
