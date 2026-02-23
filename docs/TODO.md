📋 TODO – Sistema audio centralizzato (v3.4.0)
Branch: supporto-audio-centralizzato
Tipo: FEATURE
Priorità: HIGH
Stato: READY

---

📖 Riferimento Documentazione
Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:
`docs/3 - coding plans/PLAN_audio_system_v3.4.0.md`

Questo file TODO è solo un sommario operativo da consultare e aggiornare durante ogni fase dell'implementazione.
Il piano completo contiene analisi, architettura, edge case e dettagli tecnici.

---

🤖 Istruzioni per Copilot Agent

Implementare le modifiche in modo **incrementale** su più commit atomici e logici.

**Workflow per ogni fase:**

1. **Leggi questo TODO** → Identifica la prossima fase da implementare
2. **Consulta piano completo** → Rivedi dettagli tecnici, architettura, edge case della fase
3. **Implementa modifiche** → Codifica solo la fase corrente (scope limitato)
4. **Commit atomico** → Messaggio conventional, scope chiaro, riferimento fase
5. **Aggiorna questo TODO** → Spunta checkbox completate per la fase
6. **Acquisisci info sommarie** → Rivedi stato globale prima di proseguire
7. **RIPETI** → Passa alla fase successiva (torna al punto 1)

⚠️ **REGOLE FONDAMENTALI:**

- ✅ **Un commit per fase logica** (no mega-commit con tutto)
- ✅ **Dopo ogni commit**: aggiorna questo TODO spuntando checkbox
- ✅ **Prima di ogni fase**: rileggi sezione pertinente nel piano completo
- ✅ **Approccio sequenziale**: fase → commit → aggiorna TODO → fase successiva
- ✅ **Commit message format**: `type(scope): description [Phase N/10]`
- ❌ **NO commit multipli senza aggiornare TODO** (perde tracciabilità)
- ❌ **NO implementazione completa in un colpo** (viola incrementalità)

**Esempio workflow reale:**
```
Fase 1: Dipendenze/Assets
→ Implementa + Commit + Aggiorna TODO ✅

Fase 2: AudioEvent dataclass...
→ Rileggi piano completo sezione Fase 2
→ Implementa + Commit + Aggiorna TODO ✅

... fino a Fase 10
```

---

🎯 Obiettivo Implementazione


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
