    # PLAN Revisione Sistema Audio Centralizzato (v3.4.x)

**Branch:** `supporto-audio-centralizzato`
**Versione Target:** v3.4.1 → v3.5.0
**Tipo:** Feature / Bugfix
**Priorità:** CRITICAL → HIGH
**Stato:** DRAFT (READY)

---

## 🎯 Executive Summary

L'audit del 23 Febbraio 2026 ha evidenziato che il nuovo sistema audio centralizzato è stato implementato correttamente ma integrato soltanto al 5 % nel codice applicativo. L'infrastruttura (AudioManager, SoundCache, SoundMixer, audio_events) funziona perfettamente, ma la quasi totalità dei controller non emette eventi audio.

**Aggiornamento 20:29 CET:** durante la revisione troviamo tre gap rispetto al piano iniziale e le stime temporali sono state ricalibrate. Il totale stimato rimane ~23.5 ore, con redistribuzione interna tra le fasi (vedi sezione "Fasi del lavoro" per i dettagli corrette).

Questo piano descrive una revisione completa dell'integrazione: tutti gli eventi di gameplay, UI, dialoghi, menu, timer, ambient e loop dovranno generare suoni, con panning dove applicabile, e gestire le configurazioni opzionali previste dal design.

Al termine, il sistema audio sarà operativo al 100 % e pronto per un rilascio di produzione.

---

## 🔍 Scope

- Aggiunta e mappatura completa degli `AudioEvent` nei controller dell'application layer
- Estensione dei manager (`GamePlayController`, `OptionsWindowController`, `DialogManager`, ecc.) per supportare `AudioManager`
- Creazione/aggiornamento di componenti mancanti (MainMenuController, MixerController, focus handler, etc.)
- Avvio loop ambient/musica e gestione pause su perdita focus
- Aggiornamento di configurazione, DI container e test
- Documentazione dell'architettura e aggiornamenti API

**Non incluso:** modifiche all'infrastruttura audio stessa (già completa), redesign del mixer o del motore audio.

---

## 🛠️ Fasi del lavoro

### Fase 1 – Core gameplay (v3.4.1 MVP)
1. Helper `_map_pile_to_index()` in `GamePlayController` — **PREREQUISITO** per panning
2. Panning fix: aggiornare chiamate esistenti CARD_MOVE/STOCK_DRAW
3. Eventi navigazione: 16 metodi `UI_NAVIGATE`
   - 4 frecce (`_cursor_up/down/left/right`)
   - 7 pile base (`_nav_pile_base` 0‑6)
   - 3 pile speciali (`_nav_pile_semi`, `_nav_pile_scarti`, `_nav_pile_mazzo`)
   - 2 altri comandi (`_cursor_tab`, `_cursor_home`, `_cursor/end`)
4. Selezione (`CARD_SELECT`) e cancellazione (`UI_CANCEL`)
5. Boundary hit detection (`TABLEAU_BUMPER`)
6. Victory (`GAME_WON`) in end_game() + collegamento da `engine.on_game_ended`
7. Test unitari e integration per tutti i punti precedenti

### Fase 2 – Dialoghi e Input
1. Refactor `SolitarioDialogManager` per eventi apertura (`MIXER_OPENED`/`UI_NAVIGATE`) e chiusura (`UI_SELECT`/`UI_CANCEL`) in tutti i metodi sincroni/asincroni
2. **Skip InputHandler** (deprecato v1.7.x, attività solo documentale)
3. Integrare `AudioManager` in `OptionsWindowController` e aggiungere eventi
4. Test unitari per dialoghi e OptionsWindowController

<!-- stima rimossa per automazione -->

### Fase 3 – Menu & Mixer
0. **Verificare esistenza di `MainMenuController`** o crearne uno da zero (verificare o creare)**
1. Aggiungere audio a `OptionsWindowController.navigate_up/down`, `modify_current_option`, `close_window`
2. Creare/aggiornare `MainMenuController` con audio navigation/select/cancel
3. Implementare `MixerController` accessibile (tasto M) con audio + TTS feedback
4. Boundary hit anche per fine corsa in controller

<!-- stima rimossa per automazione -->

### Fase 4 – Timer & Loop Ambient/Music
1. ~~Verifica registrazione callback timer~~ **(già implementato in `game_engine.py` v3.4.2, linee 383–397)**
   - Eseguire **test di integrazione** per `TIMER_WARNING`/`TIMER_EXPIRED`
2. Avviare `AMBIENT_LOOP` dopo `AudioManager.initialize()` in `acs_wx.py` 
- Bind evento `wx.EVT_ACTIVATE` per pause/resume loop
4. Aggiornare `audio_config.json` per eventi opzionali e loader
- Test di integrazione focus e timer

<!-- stima rimossa per automazione -->

### Fase 5 – Finitura e rilascio
1. Aggiornare `docs/API.md`, `ARCHITECTURE.md` e README con i nuovi dettagli
2. Eseguire mypy/flake8, assicurare coverage ≥ 90 %
3. Aggiornare CHANGELOG con requisiti di rilascio
4. Validazione finale e merge

<!-- stima rimossa per automazione -->

---


## 🔧 Gap Risolti

### Gap #1: Timer callbacks già implementati
Le funzioni `_on_timer_warning` e `_on_timer_expired` sono presenti in `game_engine.py` (v3.4.2, linee 383–397). La Fase 4 è quindi ridotta a test di integrazione.

### Gap #2: CARD_MOVE senza panning
Nel controller l'evento CARD_MOVE veniva emesso con `source_pile=None` e `destination_pile=None`. Occorre inserire helper di mappatura nella Fase 1.

### Gap #3: MainMenuController mancante
Il file non esiste nel branch; la Fase 3 include ora una verifica preliminare e potenziale creazione.

## 📋 File Coinvolti

- `src/application/gameplay_controller.py`
- `src/application/input_handler.py`
- `src/application/dialog_manager.py`
- `src/application/options_controller.py`
- `src/application/*` (controller menu, mixer)
- `src/application/game_engine.py` (registrazione callbacks)
- `src/infrastructure/audio/*` (nessuna modifica necessaria ma mantenere salute)
- `src/infrastructure/di_container.py`
- `src/infrastructure/ui/gameplay_panel.py`, `main_frame.py`, eventuali nuove UI
- `docs/API.md`, `docs/ARCHITECTURE.md`, README, config files
- `tests/unit/*` e `tests/integration/*` – vari file da creare/aggiornare

---

## ✅ Criteri di completamento

- Tutti gli `AudioEventType` hanno almeno un punto di emissione nel codice di gioco o UI
- I test coprono ogni evento con mock di `AudioManager`/`play_event` (coverage ≥ 90 %) e non generano falsi positivi
- Meccanismo panning funziona (gli indici passati rispettano mappa pile)
- Loop ambient/musica si avviano in startup e si pongono in pausa al focus out
- Configurazione opzionale funziona senza errori
- Documentazione aggiornata e linkata correttamente
- Merge su `main` consentito solo quando Fase 1 è stata completata o chiaramente spiegato il disclaimer nel README

---

## ↪ Workflow

Seguire il protocollo TODO-Gate: leggere questo PLAN prima di ogni commit, aggiornare `docs/TODO.md` dopo ogni fase completata, e creare commit atomici con messaggi convenzionali.

---

*Versione 1.0 – 23 Febbraio 2026*