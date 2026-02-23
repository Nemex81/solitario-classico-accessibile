
📋 TODO – Correzione sistema audio e mapping eventi (v3.4.1)
Branch: supporto-audio-centralizzato
Tipo: BUGFIX + Refactor
Priorità: HIGH
Stato: READY

---

📖 Piani di riferimento:
- [2 - projects/PLAN_audio_system_v3.4.1.md](2%20-%20projects/PLAN_audio_system_v3.4.1.md)   (documentazione implementazione generale)
- [3 - coding plans/PLAN_audio_system_fix_v3.4.1.md](3%20-%20coding%20plans/PLAN_audio_system_fix_v3.4.1.md)   (piano corrrettivo dettagliato)


Obiettivo: risolvere il problema dei suoni non riprodotti correggendo il mapping dei file audio e rimuovendo la logica random non utilizzata. L'implementazione segua questo ordine:

1. applicare le modifiche al codice (`sound_cache.py` & `audio_manager.py`) come da piano
2. eseguire type check e validazioni rapide
3. aggiungere i test unitari che confermino la correzione
4. verificare copertura e comportamento

Aggiornare il TODO dopo ogni fase con riferimento alla documentazione pertinente.

**Nuovo requisito:** Inserire anche task per migliorare il supporto timer audio.
- Modificare `TimerManager` per callback `expired_callback`
- Integrare un `TimerManager` nel `GameEngine` con audio events
- Aggiornare `DIContainer.get_timer_manager` con parametri callback
- Creare test per audio events sui timer

File coinvolti:
- src/infrastructure/audio/sound_cache.py
- src/infrastructure/audio/audio_manager.py
- src/application/timer_manager.py
- src/application/game_engine.py
- src/infrastructure/di_container.py
- docs/2 - projects/DESIGN_audio_system.md
- docs/3 - coding plans/PLAN_audio_system_fix_v3.4.1.md
- tests/infrastructure/audio/test_sound_cache.py  (da creare)
- tests/infrastructure/audio/test_audio_manager.py  (da creare)
- tests/unit/application/test_timer_manager.py  (da creare)
- tests/integration/test_timer_integration.py  (aggiornare)

Checklist fasi:
- [x] Aggiorna mapping EVENT_TO_FILES e type hints in SoundCache
- [x] Rimuovi codice random e aggiungi logging in AudioManager.play_event
- [x] Aggiungi sezione "Gestione Suoni per Evento" al design (fatto)
- [x] Scrivi test unitari per SoundCache e AudioManager
- [x] Esegui mypy e flake8 su src/infrastructure/audio
- [x] Esegui script di verifica asset e validazione musicale
- [x] Test manuale funzionale (elenco checklist Step 6 nel piano)
- [x] Commit e push modifiche con messaggio convenzionale

- [x] **BUG #1:** Eliminare metodo duplicato `resume_all_loops()` in `audio_manager.py`
Criteri di completamento:
- Nessun warning "Sound asset missing" al lancio
- SoundCache.get() non restituisce liste
- AudioManager.play_event() non importa/usa random
- Copertura di test ≥ 85 % per il package audio
- Documentazione aggiornata e design coerente

**Note operative:**
- Inserire i nuovi test prima di modificare codice per seguire flusso TDD se preferito.
- Aggiornare questo TODO dopo ogni commit spuntando la fase corrispondente.


---

🎯 Obiettivo Implementazione

🔧 **Attività in corso (da completare prima di test di integrazione)**

- [x] Recuperare `AudioManager` dal `DIContainer` all'avvio dell'app
- [x] Chiamare `initialize()` sul `AudioManager`
- [x] Passare l'istanza a `GamePlayController` (e altri controller audio-aware)
- [x] Aggiungere binding nel container o in `acs_wx.py` per gestire il ciclo di vita
- [x] Modificare `InputHandler` per emettere AudioEvent su navigazione/boundary
- [x] Aggiungere supporto audio in `DialogManager` (opzionale ma raccomandato)
- [x] Aggiunti test unitari InputHandler/DialogManager audio



- Aggiungere sistema audio modulare a 5 bus indipendenti usando pygame.mixer.
- Centralizzare effetti sonori per gioco, UI, ambient, musica, voice con panning spaziale.
- Fornire mixer accessibile, preferenze persistenti e degradazione graziosa.

---

🔊 **Mappatura Eventi → File Audio, Varianti e Opzioni**

**Strategia di Mapping e Gestione Varianti**

1. Mappatura esplicita: Ogni `AudioEventType` è mappato a una o più path di file WAV (solo WAV, no OGG/MP3) nella struttura `assets/sounds/default/`.
   - La mappatura è definita in una struttura Python (dict) e documentata qui e nel DESIGN.
   - Esempio: `CARD_MOVE` → `["gameplay/card_move_1.wav", "gameplay/card_move_2.wav"]`
2. Varianti: *(deprecated)* in v3.4.1 la selezione casuale è stata rimossa; ogni evento ha un unico file per pack.
3. Bus assignment: Ogni evento è assegnato a un bus (`Gameplay`, `UI`, `Ambient`, `Music`, `Voice`) secondo tabella seguente.
4. Eventi opzionali: Alcuni eventi (es. `TIMER_WARNING`, `TIMER_EXPIRED`, `MIXER_OPENED`) sono disattivabili via config JSON (`audio_config.json`).
5. Degradazione: Se un file manca, warning nel log e nessun crash. Se nessuna variante disponibile, l'evento è silenziato.

**Tabella Mapping Eventi → File e Bus**

| AudioEventType         | File(s) WAV (relativo a assets/sounds/default/)         | Bus        | Varianti | Note |
|-----------------------|--------------------------------------------------------|------------|----------|------|
| CARD_MOVE             | gameplay/card_move.wav                                  | Gameplay   | No       |       |
| CARD_SELECT           | gameplay/card_select.wav                               | Gameplay   | No       |       |
| CARD_DROP             | gameplay/card_drop.wav                                 | Gameplay   | No       |       |
| FOUNDATION_DROP       | gameplay/foundation_drop.wav                           | Gameplay   | No       |       |
| INVALID_MOVE          | gameplay/invalid_move.wav                              | Gameplay   | No       |       |
| TABLEAU_BUMPER        | gameplay/bumper.wav                                    | Gameplay   | No       |       |
| STOCK_DRAW            | gameplay/stock_draw.wav                                | Gameplay   | No       |       |
| WASTE_DROP            | gameplay/waste_drop.wav                                | Gameplay   | No       |       |
| UI_NAVIGATE           | ui/navigate.wav                                        | UI         | No       |       |
| UI_SELECT             | ui/select.wav                                          | UI         | No       |       |
| UI_CANCEL             | ui/cancel.wav                                          | UI         | No       |       |
| MIXER_OPENED          | ui/mixer_opened.wav                                    | UI         | No       | Opzionale |
| AMBIENT_LOOP          | ambient/room_loop.wav                                  | Ambient    | No       | Loop |
| MUSIC_LOOP            | music/music_loop.wav                                   | Music      | No       | Loop |
| GAME_WON              | voice/victory.wav                                      | Voice      | No       |       |
| TIMER_WARNING         | ui/navigate.wav                                        | UI         | No       | Opzionale |
| TIMER_EXPIRED         | ui/cancel.wav                                          | UI         | No       | Opzionale |

**Nota**: La lista completa e aggiornata dei file disponibili è mantenuta nel DESIGN e nel README. Eventuali nuovi eventi o varianti vanno aggiunti sia qui che nel mapping Python.

**Esempio di struttura mapping Python**

```python
EVENT_TO_FILES = {
  AudioEventType.CARD_MOVE: [
    "gameplay/card_move_1.wav",
    "gameplay/card_move_2.wav",
    "gameplay/card_move_3.wav",
  ],
  AudioEventType.CARD_SELECT: ["gameplay/card_select.wav"],
  # ... altri eventi ...
}
```

**Gestione Varianti**

- Se la lista associata a un evento contiene più file, la selezione è randomica (`random.choice`).
- Se la lista è vuota o tutti i file mancano, l'evento è silenziato (nessun errore).

**Eventi Opzionali e Configurazione**

- Gli eventi marcati come "Opzionale" possono essere abilitati/disabilitati dall'utente tramite `audio_config.json`.
- Il loader carica la config e filtra gli eventi disabilitati a runtime.

**Bus Assignment e Policy**

- Ogni evento è assegnato a un bus secondo la tabella sopra.
- I bus sono gestiti da `SoundMixer` e possono essere mutati/regolati indipendentemente.
- I bus loop (Ambient, Music) sono sospesi in pausa/focus out; i bus one-shot (Gameplay, UI, Voice) restano sempre attivi.

---

---

📂 File Coinvolti

- `requirements.txt` → MODIFY
- `assets/sounds/` → STRUCTURE/FILES (existing assets)
- `src/infrastructure/audio/*` → CREATE/MODIFY
- `src/infrastructure/config/audio_config_loader.py` → CREATE
- `src/infrastructure/di_container.py` → MODIFY
- `src/application/gameplay_controller.py` → MODIFY
- `src/application/input_handler.py` → MODIFY
- `src/presentation/dialogs/accessible_mixer_dialog.py` → CREATE
- `src/infrastructure/ui/main_frame.py` (o similare) → MODIFY
- `config/audio_config.json` → CREATE
- tests/unit/infrastructure/* → CREATE

---

🛠 Checklist Implementazione

**Logica / Dominio**
- [ ] Modifica modello / entità (AudioEvent)
- [ ] Aggiornamento servizi / use case
- [ ] Gestione edge case previsti

**Application / Controller**
- [ ] Nuovi metodi aggiunti (timer callbacks, mixer dialog)
- [ ] Metodi esistenti aggiornati (GamePlayController, InputHandler, DialogManager)
- [ ] Nessuna violazione Clean Architecture

**Infrastructure (se applicabile)**
- [ ] Persistenza aggiornata (config JSON)
- [ ] Eventi / handler modificati (DIContainer, AudioManager)

**Presentation / Accessibilità**
- [ ] Messaggi TTS in italiano chiaro
- [ ] Nessuna informazione solo visiva
- [ ] Comandi accessibili via tastiera (mixer, focus)

**Testing**
- [ ] Unit test creati / aggiornati
- [ ] Tutti i test esistenti passano
- [ ] Nessuna regressione rilevata

---

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
