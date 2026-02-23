
📋 TODO – Fix DependencyContainer.get_audio_manager (v3.4.0)
Branch: supporto-audio-centralizzato
Tipo: BUGFIX
Priorità: CRITICAL
Stato: READY

---

📖 Piano di riferimento:
[2 - projects/PLAN_fix_dependencycontainer_audio_manager_v3.4.0.md](2%20-%20projects/PLAN_fix_dependencycontainer_audio_manager_v3.4.0.md)

Obiettivo: Correggere il crash all’avvio implementando il metodo `get_audio_manager` in DependencyContainer secondo Clean Architecture, con lazy loading e singleton.

File coinvolti:
- src/infrastructure/di/dependency_container.py
- docs/API.md
- docs/TODO.md
- tests/infrastructure/test_dependency_container.py

Checklist fasi:
- [ ] Aggiungi metodo get_audio_manager in DependencyContainer
- [ ] Aggiorna/crea test unitario per risoluzione audio_manager
- [ ] Aggiorna docs/API.md con firma pubblica
- [ ] Test end-to-end: avvio app senza crash

Criteri di completamento:
- App avviabile senza errori
- Test unitari e integrazione passano
- Documentazione aggiornata

**Esempio workflow reale:**
```
Fase 1: Dipendenze/Assets
→ Implementa + Commit + Aggiorna TODO ✅

Fase 2: AudioEvent dataclass...
→ Rileggi piano completo sezione Fase 2
→ Implementa + Commit + Aggiorna TODO ✅

... fino a Fase 9
```

---

🎯 Obiettivo Implementazione

🔧 **Attività in corso (da completare prima di test di integrazione)**

- [ ] Recuperare `AudioManager` dal `DIContainer` all'avvio dell'app
- [ ] Chiamare `initialize()` sul `AudioManager`
- [ ] Passare l'istanza a `GamePlayController` (e altri controller audio-aware)
- [ ] Aggiungere binding nel container o in `acs_wx.py` per gestire il ciclo di vita



- Aggiungere sistema audio modulare a 5 bus indipendenti usando pygame.mixer.
- Centralizzare effetti sonori per gioco, UI, ambient, musica, voice con panning spaziale.
- Fornire mixer accessibile, preferenze persistenti e degradazione graziosa.

---

🔊 **Mappatura Eventi → File Audio, Varianti e Opzioni**

**Strategia di Mapping e Gestione Varianti**

1. Mappatura esplicita: Ogni `AudioEventType` è mappato a una o più path di file WAV (solo WAV, no OGG/MP3) nella struttura `assets/sounds/default/`.
   - La mappatura è definita in una struttura Python (dict) e documentata qui e nel DESIGN.
   - Esempio: `CARD_MOVE` → `["gameplay/card_move_1.wav", "gameplay/card_move_2.wav"]`
2. Varianti: Se una lista di file è associata a un evento, la selezione è randomica tra le varianti disponibili (anti-ripetitività).
3. Bus assignment: Ogni evento è assegnato a un bus (`Gameplay`, `UI`, `Ambient`, `Music`, `Voice`) secondo tabella seguente.
4. Eventi opzionali: Alcuni eventi (es. `TIMER_WARNING`, `TIMER_EXPIRED`, `MIXER_OPENED`) sono disattivabili via config JSON (`audio_config.json`).
5. Degradazione: Se un file manca, warning nel log e nessun crash. Se nessuna variante disponibile, l'evento è silenziato.

**Tabella Mapping Eventi → File e Bus**

| AudioEventType         | File(s) WAV (relativo a assets/sounds/default/)         | Bus        | Varianti | Note |
|-----------------------|--------------------------------------------------------|------------|----------|------|
| CARD_MOVE             | gameplay/card_move_1.wav, ..._2.wav, ..._3.wav         | Gameplay   | Sì (3)   | Random |
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
