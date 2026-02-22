# 🔊 Design Document - Sistema Audio Dinamico e Accessibile

> **FASE: CONCEPT & FLOW DESIGN**  
> Nessuna decisione tecnica implementativa qui - solo logica, flussi e architettura concettuale  
> Equivalente a "diagrammi di flusso sulla lavagna"

---

## 📌 Metadata

- **Data Inizio**: 2026-02-22
- **Stato**: FROZEN (pronto per PLAN)
- **Versione Target**: v3.4.0 (ipotesi)
- **Autore**: AI Assistant + Nemex81
- **Ultima Revisione**: 2026-02-22 (v1.2 — allineato a PLAN v1.1: panning, DRY JSON, domande risolte)

---

## 💡 L'Idea in 3 Righe

Aggiungere un sistema audio modulare a 5 bus indipendenti che funzioni come **display uditivo parallelo a NVDA**: dove NVDA descrive la struttura e il contenuto, l'audio descrive la topografia spaziale del tavolo e fornisce feedback emotivo immediato su ogni azione. Il sistema si integra nell'architettura Clean Architecture esistente tramite il pattern già consolidato di `DIContainer` + `ConfigLoader`, senza introdurre paradigmi nuovi e senza sovrapporsi alle responsabilità di `TtsProvider`.

---

## 🎭 Attori e Concetti

### Attori (Chi/Cosa Interagisce)

- **Giocatore non vedente**: Usa NVDA per le informazioni descrittive e l'audio per il feedback immediato spaziale/emotivo
- **GamePlayController**: Pubblica eventi audio dopo ogni azione validata dal motore di gioco (nota: classe reale è `GamePlayController` con capital P)
- **InputHandler**: Pubblica eventi audio per navigazione e bumper di fine corsa
- **DialogManager**: Pubblica eventi audio per apertura/chiusura dialoghi e selezioni UI
- **AudioManager**: Unico punto di ingresso al sistema audio, interpreta gli eventi e orchestra la riproduzione
- **SoundMixer**: Gestisce i 5 bus pygame.mixer con volumi e mute indipendenti
- **SoundCache**: Carica e mantiene i campioni WAV in RAM all'avvio
- **AudioConfigLoader**: Deserializza `config/audio_config.json` con fallback ai default
- **DIContainer**: Gestisce il ciclo di vita dell'AudioManager come singleton
- **NVDA / TtsProvider**: Sistema TTS separato, non gestisce audio PCM - le responsabilità non si sovrappongono mai

### Concetti Chiave (Cosa Esiste nel Sistema)

#### AudioEvent
- **Cos'è**: Dataclass immutabile che descrive un evento di gioco rilevante per il sistema audio
- **Stati possibili**: Creato (da un controller), Consumato (dall'AudioManager dopo la riproduzione)
- **Proprietà**:
  - `event_type` (stringa costante, es. `CARD_MOVE_SUCCESS`, `FOUNDATION_DROP`, `INVALID_MOVE`)
  - `source_pile` (indice intero della pila di partenza, opzionale)
  - `destination_pile` (indice intero della pila di destinazione, opzionale)
  - `context` (dizionario opzionale per informazioni aggiuntive future)
- **Nota**: I controller non conoscono il sistema audio internamente. Sanno solo che un'azione è avvenuta e creano l'evento descrittivo corrispondente.

#### AudioBus
- **Cos'è**: Un canale `pygame.mixer.Channel` dedicato con volume e stato mute indipendenti
- **Stati possibili**: Attivo, Silenziato (mute), In Pausa (loop sospesi)
- **Proprietà**:
  - Nome bus (gameplay / ui / ambient / music / voice)
  - Volume (intero 0-100, mappato a float 0.0-1.0 per pygame)
  - Flag mute (booleano)
  - Tipo contenuto (one-shot per gameplay/ui/voice, loop per ambient/music)
- **Bus definiti**:
  - **Gameplay**: Feedback delle azioni sulle carte (spostamento, giro, posizionamento)
  - **UI**: Suoni di navigazione menu, apertura dialoghi, conferma/annullamento
  - **Ambient**: Loop ambientali continui (brusio di sottofondo, fruscio carte)
  - **Music**: Colonna sonora in loop, priorità percettiva più bassa
  - **Voice**: Clip vocali campionate pre-registrate per eventi narrativamente rilevanti

#### SoundTimbre (Firma Sonora)
- **Cos'è**: Associazione tra categoria strutturale del tavolo e file audio corrispondente
- **Proprietà**:
  - `tableau`: Suono carta/legno - naturale, secco, attacco percussivo deciso
  - `foundation`: Suono cristallino/metallico - acuto, risonante brevemente, gratificante
  - `stock`: Suono plastico/sordo - basso, funzionale, neutro
  - `waste`: Suono plastico/sordo - identico o variante dello stock
  - `ui_navigate`: Neutro e discreto, non compete con il gameplay
  - `ui_confirm`: Tono positivo, corto
  - `ui_cancel`: Tono neutro/negativo, corto
  - `boundary_hit`: Thud smorzato, fisico - comunica il confine del tavolo

#### StereoPosition
- **Cos'è**: Valore float da -1.0 (estrema sinistra) a +1.0 (estrema destra) che rappresenta la posizione orizzontale di una pila nel campo stereo
- **Calcolo**: Formula lineare `panning = (pile_index / 12) * 2.0 - 1.0` su 13 indici di gioco (0-12)
- **Applicazione stereo**: Constant-power pan law — il volume percepito rimane uniforme su tutto lo spettro stereo. La formula lineare classica `(1.0 - pan) / 2.0` dimezza il volume al centro (left=0.5, right=0.5 per panning=0.0), inaccettabile per accessibilità (cfr. PLAN v1.1, Fix #1)
- **Mapping logico del tavolo (sinistra → destra)**:
  - Indici 0-6: Pile Tableau 1-7 (estrema sinistra al centro)
  - Indici 7-10: Fondazioni 1-4 (centro-destra all'estrema destra)
  - Indice 11: Stock / Mazzo coperto (destra)
  - Indice 12: Scarti / Waste (estrema destra)
- **Nota**: Il calcolo panning è **dinamico** in `AudioManager._get_panning_for_event()`. **Non** viene persistito in `audio_config.json` — memorizzare output computati violerebbe il principio DRY (cfr. PLAN v1.1, Fix #2, pattern `scoring_config.json`). La 14ª posizione concettuale (menu) non è usata nel gameplay loop.

#### SoundPack
- **Cos'è**: Raccolta coerente di file audio WAV che sostituisce in blocco tutti i suoni di gioco
- **Stati possibili**: Attivo (in uso), Installato (disponibile), Non installato
- **Proprietà**:
  - Nome pack (stringa, es. `default`, `retro`, `minimalist`)
  - Cartella base (`assets/sounds/<pack_name>/`)
  - Sottocartelle per bus: `gameplay/`, `ui/`, `ambient/`, `music/`, `voice/`
- **Comportamento**: Cambiare pack = cambiare solo la chiave `active_sound_pack` in JSON. Zero modifiche al codice.

#### AudioConfig
- **Cos'è**: Struttura dati deserializzata da `config/audio_config.json` con tutte le preferenze utente
- **Proprietà**: volumi per bus (0-100), stato mute per bus, pack attivo, mapping spaziale pile
- **Ciclo di vita**: Caricata all'init, aggiornata in memoria durante sessione, scritta su disco solo alla chiusura del mixer o del gioco

---

## 🎬 Scenari & Flussi

### Scenario 1: Spostamento Carta su Fondazione (Flusso Normale Principale)

**Punto di partenza**: Giocatore sposta una carta dalla Pila Tableau 3 alla Fondazione 2 con tasto Enter.

**Flusso**:

1. **GameplayController**: Invia comando al GameEngine, che valida la mossa
   → **GameEngine**: Restituisce esito SUCCESS con sorgente (Tableau 3, indice 2) e destinazione (Fondazione 2, indice 8)

2. **GameplayController**: Crea `AudioEvent(event_type=FOUNDATION_DROP, source_pile=2, destination_pile=8)`
   → **GameplayController**: Chiama `audio_manager.play_event(event)`

3. **AudioManager**: Riceve l'evento, consulta la mappa dei timbre
   → **AudioManager**: Destinazione è fondazione → seleziona timbre `foundation` (cristallino)

4. **AudioManager**: Calcola panning per destinazione (Fondazione 2, indice 8 su 12 posizioni totali)
   → **AudioManager**: `panning = (8/12) * 2.0 - 1.0 = +0.33` (centro-destra)

5. **AudioManager**: Recupera il volume del bus Gameplay dalla config, verifica che non sia mutato
   → **SoundCache**: Restituisce il buffer WAV pre-caricato per `foundation_drop.wav`

6. **SoundMixer**: Applica constant-power pan law: `set_volume(left=0.67, right=1.0)` sul canale Gameplay, riproduce buffer
   → (panning=+0.33 positivo → `left = 1.0 - 0.33 = 0.67`, `right = 1.0` — volume uniforme percepito)
   → **Output**: L'utente sente un tintinnio cristallino leggermente spostato a destra, al volume pieno

7. **NVDA**: (in parallelo, asincrono) Inizia a leggere la descrizione testuale della mossa
   → **Risultato**: L'audio arriva prima di NVDA, confermando la mossa mentre il TTS prepara la lettura

**Cosa cambia**: Il buffer audio raggiunge le cuffie in <50ms dall'azione. NVDA completa la lettura nel successivo ciclo.

---

### Scenario 2: Navigazione tra Pile (Bumper di Fine Corsa)

**Punto di partenza**: Giocatore è sulla Pila Tableau 1 (estrema sinistra) e preme freccia sinistra.

**Flusso**:

1. **InputHandler**: Riceve tasto freccia sinistra, verifica posizione corrente nel cursore di gioco
   → **InputHandler**: Posizione corrente è già alla Pila 1 (indice 0) - non c'è posizione precedente

2. **InputHandler**: Chiama `audio_manager.play_boundary_hit(direction='left')`
   → **AudioManager**: Seleziona suono `boundary_hit.wav`, nessun panning (centro), bus UI

3. **SoundMixer**: Riproduce thud smorzato con panning 0.0 (centro)
   → **Output**: L'utente percepisce il confine fisico del tavolo prima che NVDA lo segnali

**Cosa cambia**: Feedback immediato del bordo. NVDA non ha ancora parlato - il suono ha già comunicato l'informazione.

---

### Scenario 3: Apertura Mixer Accessibile

**Punto di partenza**: Giocatore preme il tasto rapido `M` durante una partita.

**Flusso**:

1. **InputHandler**: Intercetta tasto `M`, invia comando di apertura mixer
   → **DialogManager**: Avvia apertura menu modale mixer audio

2. **AudioManager**: Riceve chiamata `pause_all_loops()`
   → **SoundMixer**: I bus Ambient e Music vengono messi in pausa (loop sospesi)

3. **DialogManager**: Apre pannello modale mixer (navigabile da tastiera)
   → **ScreenReader (TTS)**: Annuncia il menu: *"Mixer Audio aperto. Bus: Gameplay 80%"*

4. **Giocatore**: Naviga tra i 5 bus con frecce su/giù, modifica il volume con frecce sinistra/destra
   → **AudioManager**: Per ogni modifica chiama `set_bus_volume(bus, new_volume)`
   → **ScreenReader (TTS)**: Annuncia immediatamente il nuovo valore: *"Volume Musica: 40%"*

5. **Giocatore**: Preme Escape per chiudere il mixer
   → **DialogManager**: Chiude menu modale
   → **AudioManager**: Chiama `resume_all_loops()` e `save_settings()`

**Cosa cambia**: Impostazioni aggiornate in memoria e su disco. I loop riprendono dal punto di interruzione.

---

### Scenario 4: Perdita di Focus della Finestra (Alt+Tab)

**Punto di partenza**: Giocatore passa a un'altra finestra con Alt+Tab durante una partita con musica attiva.

**Flusso**:

1. **Frame wxPython**: Genera evento `wx.EVT_ACTIVATE` con `GetActive() == False`
   → **Presentation Layer**: Handler registrato chiama `audio_manager.pause_all_loops()`

2. **AudioManager**: Sospende i bus Ambient e Music
   → **Output**: Silenzio (bus Gameplay e UI non hanno loop attivi, quindi già silenziosi)

3. **Giocatore**: Torna alla finestra del gioco
   → **Frame wxPython**: Evento `wx.EVT_ACTIVATE` con `GetActive() == True`
   → **Presentation Layer**: Handler chiama `audio_manager.resume_all_loops()`

4. **AudioManager**: Riprende i loop Ambient e Music
   → **Output**: L'ambiente sonoro torna operativo

**Nota**: La logica di binding `EVT_ACTIVATE` è responsabilità del Presentation Layer, non dell'AudioManager. L'AudioManager espone solo `pause_all_loops()` / `resume_all_loops()` senza sapere perché vengono chiamati.

---

### Scenario 5: Mossa Non Valida

**Punto di partenza**: Giocatore tenta di spostare una carta su una pila non compatibile.

**Flusso**:

1. **GameEngine**: Restituisce esito INVALID alla mossa tentata
   → **GameplayController**: Crea `AudioEvent(event_type=INVALID_MOVE, source_pile=N, destination_pile=M)`

2. **AudioManager**: Tipo evento INVALID_MOVE → seleziona suono `invalid_move.wav`, bus Gameplay
   → Panning calcolato sulla destinazione tentata (per orientamento spaziale)

3. **Output**: Suono di rifiuto secco nella direzione tentata
   → NVDA (in parallelo): legge la descrizione dell'errore

---

### Scenario 6: Vittoria (Clip Vocale Campionata)

**Punto di partenza**: L'ultima carta viene posata sulla quarta Fondazione, completando il gioco.

**Flusso**:

1. **GameEngine**: Restituisce evento GAME_WON
   → **GameplayController**: Crea `AudioEvent(event_type=GAME_WON, destination_pile=indice_fondazione)`

2. **AudioManager**: Tipo GAME_WON → due azioni in sequenza:
   - Riproduce `foundation_drop.wav` (bus Gameplay) per l'ultima carta
   - Dopo breve pausa, riproduce clip vocale campionata `victory.wav` (bus Voice)

3. **SoundMixer**: Bus Voice ha volume massimo, nessun panning (centro, narrativo)
   → **Output**: Prima il suono di carta sulla fondazione, poi la clip vocale di vittoria

4. **AudioManager**: Chiama `pause_all_loops()` per silenziare Ambient e Music durante la clip

**Nota**: Le clip Voice sono file audio pre-prodotti (registrazioni o sintesi) NON generati da NVDA. NVDA legge testo dinamico - Voice riproduce file statici con voce campionata.

---

### Scenario 7: Avvio Applicazione (Inizializzazione)

**Punto di partenza**: L'applicazione viene avviata da `acs_wx.py`.

**Flusso**:

1. **DIContainer**: Alla prima richiesta di `get_audio_manager()`, istanzia `AudioConfigLoader`
   → **AudioConfigLoader**: Legge `config/audio_config.json`. Se assente o corrotto, usa valori di default hardcodati

2. **DIContainer**: Istanzia `AudioManager(config)` e chiama `initialize()`
   → **AudioManager**: Inizializza `pygame.mixer` con parametri espliciti (44100 Hz, 16-bit, stereo, buffer 512)

3. **SoundCache**: Scansiona la cartella del pack attivo, carica tutti i file WAV in RAM come oggetti `pygame.Sound`
   → Se un file manca: warning nel log, il suono corrispondente viene saltato silenziosamente (no crash)

4. **SoundMixer**: Configura i 5 canali `pygame.mixer.Channel` con i volumi letti dalla config
   → **AudioManager**: Pronto. Segnala disponibilità al DIContainer.

**Cosa cambia**: Tutti i campioni in RAM. Zero letture disco durante la partita.

---

### Scenario 8: Chiusura Applicazione

**Punto di partenza**: Utente chiude il gioco.

**Flusso**:

1. **Presentation Layer**: Intercetta evento di chiusura finestra wxPython
   → **GameplayController / Orchestratore**: Chiama `audio_manager.shutdown()`

2. **AudioManager**: Chiama `save_settings()` → scrive volumi correnti e stato mute in `audio_config.json`
   → **AudioManager**: Stop tutti i canali, `pygame.mixer.quit()`

**Cosa cambia**: Preferenze audio persistite. Nessun leak di risorse audio.

---

## 🔀 Stati e Transizioni

### Stati dell'AudioManager

#### Stato A: Non Inizializzato
- **Descrizione**: Oggetto creato ma `initialize()` non ancora chiamato. pygame.mixer non attivo.
- **Può passare a**: Attivo
- **Trigger**: `initialize()` chiamato dal DIContainer al primo `get_audio_manager()`

#### Stato B: Attivo
- **Descrizione**: pygame.mixer inizializzato, cache caricata, canali pronti. Sistema pienamente operativo.
- **Può passare a**: In Pausa (loop), Shutdown
- **Trigger per pausa**: `pause_all_loops()` (Alt+Tab, apertura mixer/pausa gioco)
- **Trigger per shutdown**: `shutdown()` (chiusura applicazione)

#### Stato C: In Pausa (Loop Sospesi)
- **Descrizione**: I bus Ambient e Music sono sospesi. I bus Gameplay, UI e Voice rimangono operativi per one-shot.
- **Può passare a**: Attivo
- **Trigger**: `resume_all_loops()` (ripristino focus, chiusura mixer)
- **Nota**: I bus one-shot (Gameplay, UI, Voice) non vengono mai messi in pausa - solo i loop.

#### Stato D: Shutdown
- **Descrizione**: pygame.mixer fermato, configurazione salvata, risorse rilasciate.
- **Può passare a**: Non Inizializzato (riavvio app)
- **Trigger**: Chiusura applicazione

### Diagramma Stati (ASCII)

```
[App Start]
      ↓ (DIContainer.get_audio_manager() → initialize())
[Non Inizializzato]
      ↓ (pygame.mixer init + SoundCache load + canali configurati)
[Attivo] ←────────────────────────────┐
      ↓ (pause_all_loops)             │ (resume_all_loops)
[In Pausa - Loop Sospesi] ────────────┘
      ↓ (shutdown)
[Shutdown]
      ↓ (riavvio app)
[Non Inizializzato]
```

### Stati di un AudioBus

```
[Attivo, Volume > 0]
      ↓ (set_bus_volume(0) o toggle_bus_mute)
[Silenziato / Muted]
      ↓ (toggle_bus_mute o set_bus_volume > 0)
[Attivo, Volume > 0]
```

---

## 🎮 Interazione Utente (UX Concettuale)

### Comandi/Azioni Disponibili

**Durante il Gioco**:

- **Ogni azione sulle carte**: Feedback sonoro immediato con panning spaziale corrispondente alla posizione della pila
- **Navigazione tra pile**: Suono di firma sonora diverso per tipo (tableau vs fondazione vs stock)
- **Fine corsa (bordi del tavolo)**: Bumper sonoro (thud) prima che NVDA reagisca
- **Mossa non valida**: Suono di rifiuto nella direzione tentata

**Tasto Rapido `M` - Mixer Accessibile**:

- Apre menu modale navigabile da tastiera
- Frecce su/giù: selezione bus (Gameplay / UI / Ambient / Music / Voice)
- Frecce sinistra/destra: regolazione volume (-5/+5 per pressione)
- Tasto `Spazio`: toggle mute del bus corrente
- Feedback TTS immediato per ogni modifica: *"Volume Gameplay: 75%"*, *"Musica: silenziata"*
- Escape: chiude mixer, salva impostazioni, riprende loop

**Tasto Pausa**:

- Sospende i loop Ambient e Music
- I bus one-shot rimangono operativi (per navigare il menu di pausa)

### Feedback Sistema

| Azione | Feedback Audio | Feedback NVDA |
|--------|----------------|---------------|
| Carta spostata (valido) | Timbre pila destinazione + panning | Descrizione mossa |
| Carta posata su fondazione | Cristallino + panning destra | Descrizione mossa |
| Mossa non valida | Suono rifiuto + panning dest tentata | Messaggio errore |
| Navigazione pile | Timbre tipo pila + panning posizione | Nome pila corrente |
| Fine corsa | Thud centrato | Eventuale messaggio bordo |
| Vittoria | Fondazione + clip Voice | Messaggio vittoria |
| Cambio volume mixer | (silenzio mentre si regola) | *"Volume X: Y%"* |

### Navigazione Concettuale del Tavolo (Esperienza Utente)

**Workflow tipo durante una partita**:

1. Utente si sposta sulla Pila Tableau 4 (centro-tavolo)
   → Sente suono legno/carta al centro dello spazio stereo
   → NVDA legge *"Pila 4: Asso di Cuori scoperto"*

2. Utente preme Enter per selezionare la carta
   → Sente breve clic di selezione UI

3. Utente naviga verso la Fondazione 1
   → Ad ogni passo sente i suoni spostarsi progressivamente verso destra nello spazio stereo
   → La firma cristallina della fondazione lo avvisa di essere arrivato sul tipo corretto

4. Utente preme Enter per posare la carta
   → Sente tintinnio cristallino a destra (Fondazione 1)
   → Ha già capito dall'audio che la mossa è riuscita ancora prima che NVDA legga

---

## 🏗️ Architettura e Integrazione

### Posizione nell'Architettura Clean

Il sistema audio appartiene interamente al layer **Infrastructure**. Non tocca Domain né Application layer direttamente. I controller del layer Application (GameplayController, InputHandler, DialogManager) creano `AudioEvent` e chiamano `audio_manager.play_event()` tramite l'interfaccia pubblica dell'AudioManager, ricevuto via DIContainer.

```
[Domain Layer]         ← Invariato. Nessuna dipendenza audio.
        ↓
[Application Layer]    ← GameplayController, InputHandler, DialogManager
                         Creano AudioEvent, chiamano audio_manager.play_event()
                         Ricevono AudioManager dal DIContainer (iniezione)
        ↓
[Infrastructure Layer] ← AudioManager, SoundMixer, SoundCache, AudioConfigLoader
                         Tutto il codice audio vive qui
        ↓
[Presentation Layer]   ← Binding wx.EVT_ACTIVATE per pause/resume loop
                         Menu modale Mixer Accessibile
```

### Struttura File da Creare

```
src/infrastructure/audio/
    audio_manager.py        ← Classe principale, unico punto di ingresso
    sound_mixer.py          ← Gestione 5 bus pygame.mixer, volumi, panning
    audio_events.py         ← Dataclass AudioEvent + costanti event_type
    sound_cache.py          ← Caricamento e cache RAM campioni WAV

src/infrastructure/config/
    audio_config_loader.py  ← Segue pattern scoring_config_loader.py

config/
    audio_config.json       ← Parametri utente persistenti

assets/sounds/
    default/
        gameplay/
        ui/
        ambient/
        music/
        voice/
```

**Note sulla struttura**:
- `src/infrastructure/audio/` esiste già nel progetto - i nuovi file si aggiungono alla cartella
- `assets/sounds/` è nuova - va creata e documentata nel README
- I file audio binari non vanno tracciati da Git standard; valutare `.gitignore` per gli asset o Git LFS

### Integrazione DIContainer

Si aggiunge il metodo `get_audio_manager()` seguendo il pattern identico di `get_screen_reader()` e `get_profile_service()`: lazy import, lazy init, singleton.

```
DIContainer
    get_audio_manager()     ← NUOVO: lazy singleton, segue pattern get_screen_reader()
    get_screen_reader()     ← Esistente (riferimento pattern)
    get_profile_service()   ← Esistente (riferimento pattern)
    get_settings()          ← Esistente
    ...
```

**Ciclo di vita nel container**:
1. Prima chiamata a `get_audio_manager()`: carica config via `AudioConfigLoader`, crea `AudioManager(config)`, chiama `initialize()`
2. Istanza singleton riutilizzata per tutte le chiamate successive
3. `DIContainer.reset()` chiama `audio_manager.shutdown()` prima di rimuovere l'istanza

### Relazione con TtsProvider / ScreenReader

Nessuna sovrapposizione di responsabilità:

| Sistema | Cosa gestisce | Tecnologia |
|---------|---------------|------------|
| TtsProvider / ScreenReader | Testo dinamico generato a runtime, lettura strutturale | NVDA API / SAPI5 pyttsx3 |
| AudioManager (bus Voice) | File audio statici pre-prodotti (clip campionate) | pygame.mixer WAV |
| AudioManager (altri bus) | Feedback sonoro di azioni e spazio di gioco | pygame.mixer WAV |

I due sistemi operano in parallelo e in modo del tutto indipendente. L'AudioManager non conosce TtsProvider e viceversa. Entrambi vengono coordinati dai controller del layer Application.

---

## 🤔 Domande & Decisioni

### Domande Aperte

- [x] ✅ **RISOLTO**: Quale libreria audio? → `pygame.mixer` (panning nativo, canali indipendenti, loop nativi, thread-safe con wxPython)
- [x] ✅ **RISOLTO**: Event bus globale o chiamata diretta? → Chiamata diretta tramite `AudioEvent` dataclass (coerente con architettura esistente, no overengineering)
- [x] ✅ **RISOLTO**: Quante posizioni stereo? → 14 posizioni (7 tableau + 4 fondazioni + stock + waste + menu), formula lineare
- [x] ✅ **RISOLTO**: Il bus Voice si sovrappone a NVDA? → No. Voice = clip pre-registrate statiche. NVDA = testo dinamico a runtime. Sistemi ortogonali.
- [x] ✅ **RISOLTO**: Pattern configurazione JSON? → Identico a `scoring_config.json` + `scoring_config_loader.py`
- [x] ✅ **RISOLTO**: Dove vivono i file audio? → `assets/sounds/<pack_name>/`
- [x] ✅ **RISOLTO**: Come si gestisce file audio mancante? → Warning nel log, suono saltato silenziosamente (degradazione graziosa)
- [x] ✅ **RISOLTO**: Quando si scrivono le impostazioni su disco? → Solo alla chiusura del mixer o del gioco (no I/O per ogni cambio di volume)
- [x] ✅ **RISOLTO**: Git LFS o .gitignore per i file audio binari? → `.gitignore` per WAV/MP3/OGG + `.gitkeep` per preservare struttura cartelle in Git (PLAN v1.1, FASE 1)
- [x] ✅ **RISOLTO**: Inizializzazione `pygame.mixer` in ambiente headless (CI/CD, test)? → Mock completo `mock_pygame_mixer` via `pytest.fixture`; test con `@pytest.mark.unit` escludono GUI e pygame reale (PLAN v1.1, FASE 10)

### Decisioni Prese

- ✅ **pygame.mixer**: Sostituisce simpleaudio del documento originale. Ragione: panning stereo nativo, canali indipendenti, loop nativi, matura e stabile.
- ✅ **Chiamata diretta AudioEvent**: Nessun event bus globale. Ragione: non esiste nel progetto, aggiungerlo per un solo modulo sarebbe overengineering. I controller chiamano direttamente `play_event()`.
- ✅ **Formula panning lineare su 14 posizioni**: Nessun mapping a 3 bucket (sinistra/centro/destra). Ragione: insufficiente per distinguere tutte le posizioni del tavolo.
- ✅ **SoundCache in RAM**: Tutti i WAV pre-caricati all'avvio. Ragione: elimina latenza lettura disco durante il gioco.
- ✅ **Bus Voice per clip statiche**: Confermato. Non sostituisce né duplica NVDA.
- ✅ **Degradazione graziosa**: pygame non disponibile o file assenti → sistema tace senza crashare.
- ✅ **Scrittura config solo a chiusura**: No I/O frequente per ogni cambio volume.
- ✅ **Pausa solo per loop (Ambient/Music)**: I bus one-shot non vengono mai sospesi.
- ✅ **Binding EVT_ACTIVATE in Presentation**: L'AudioManager non conosce wxPython. La pausa/ripresa viene gestita da chi conosce il ciclo di vita della finestra.
- ✅ **Panning audio su buffer 512 sample**: Bassa latenza su Windows 11 garantita.

### Assunzioni

- pygame disponibile come dipendenza Python (da aggiungere a `requirements.txt`)
- File WAV a 16-bit, 44100 Hz, stereo (standard compatibile con pygame.mixer)
- Windows 11 come piattaforma primaria (pygame.mixer supportato)
- Il layer Presentation gestisce gli eventi di finestra wxPython - l'AudioManager è ignaro di wx
- Il DIContainer gestisce il ciclo di vita completo dell'AudioManager (init + shutdown)

---

## 🎯 Opzioni Considerate

### Opzione A: pygame.mixer (✅ SCELTA FINALE)

**Descrizione**: Libreria audio standard con gestione canali, panning nativo tramite `set_volume(left, right)`, loop con `play(-1)`, caricamento WAV via `Sound(file)`.

**Pro**:
- ✅ Panning stereo nativo senza manipolazione PCM manuale
- ✅ Canali indipendenti (`pygame.mixer.Channel`) nativi
- ✅ Loop infiniti nativi (`sound.play(-1)`)
- ✅ Thread-safe con wxPython (audio su thread separato)
- ✅ Libreria matura, documentazione eccellente
- ✅ Possibile init in modalità headless per test (`pygame.mixer.pre_init(0,0,0,0)`)

**Contro**:
- ❌ Aggiunge dipendenza pygame al progetto (peso non trascurabile)
- ❌ Richiede init esplicito con parametri corretti per bassa latenza

---

### Opzione B: simpleaudio (❌ SCARTATA)

**Descrizione**: Libreria del documento originale. Riproduce buffer WAV e basta.

**Perché scartata**:
- ❌ Nessun canale indipendente nativo
- ❌ Nessun loop nativo
- ❌ Nessun panning nativo → richiederebbe manipolazione manuale byte PCM
- ❌ API troppo bassa per il design richiesto

---

### Opzione C: Event Bus Globale (❌ SCARTATA per la fase corrente)

**Descrizione**: Introdurre un publisher/subscriber globale per gli eventi audio.

**Perché scartata**:
- ❌ Non esiste nel progetto - aggiungerlo solo per l'audio è overengineering
- ❌ Aumenta complessità senza benefici tangibili nella fase attuale
- ✅ Rimane una **estensione futura valida** se in futuro altri sistemi beneficiano di eventi di gioco

---

## ✅ Design Freeze Checklist

Questo design è pronto per la fase tecnica (PLAN) quando:

- [x] Tutti gli scenari principali mappati (move success, invalid, boundary, vittoria, init, shutdown, mixer, focus)
- [x] Stati del sistema chiari (non init, attivo, in pausa, shutdown)
- [x] Flussi logici coprono tutti i casi d'uso rilevanti per l'accessibilità
- [x] Decisioni tecniche principali confermate (pygame, direct call, panning lineare)
- [x] UX del mixer accessibile definita (navigazione tastiera + feedback TTS)
- [x] Integrazione architetturale definita (layer, file, DIContainer, pattern JSON)
- [x] Relazione con TtsProvider chiarita (sistemi ortogonali, nessuna sovrapposizione)
- [x] Domande critiche risolte (7/9 - 2 aperte rimandate a PLAN)
- [x] Opzioni valutate e motivate (3 opzioni analizzate)
- [x] Degradazione graziosa definita

**Next Step**: Piano tecnico completato — `docs/3 - coding plans/PLAN_audio_system_v3.4.0.md` (v1.1, post-review, stato READY). Pronto per implementazione sul branch `feature/audio-system`.

---

## 📝 Note di Brainstorming

### Idee Future (Post-Prima Implementazione)

- **EventBus leggero nell'Application Layer**: Se altri sistemi (statistiche live, achievements) beneficiano di eventi di gioco, l'EventBus diventa la soluzione naturale. AudioManager diventerebbe un subscriber tra tanti.
- **Profili audio per utente**: Integrare le preferenze audio nel sistema profili esistente. Ogni profilo ha il suo set di volumi indipendente.
- **Sound Pack scaricabili**: Meccanismo di distribuzione pack audio aggiuntivi senza aggiornare l'applicazione.
- **Variazione dinamica timbri**: Varianti sonore leggere per la stessa azione (evita ripetitività su lunghe sessioni) - es. 3-4 varianti random di `card_move.wav`.
- **Audio 3D verticale**: Usare variazioni di pitch per comunicare l'altezza dello stack (pila alta = tono più acuto) - informazione aggiuntiva senza NVDA.
- **Feedback ritmico per combo**: Quando più carte vengono spostate in sequenza rapida, leggera variazione ritmica nel feedback.
- **Compressione audio intelligente**: Riduzione automatica del volume Ambient quando arriva un feedback Gameplay (ducking), per non coprire il suono di gioco.

### Accessibilità - Principi Chiave

- Il suono non sostituisce NVDA: lo **integra e lo anticipa**
- Il panning non è decorazione: è **informazione topografica**
- La firma sonora non è estetica: è **codifica semantica del tipo di pila**
- La latenza è critica: l'audio deve arrivare **prima** della lettura NVDA per essere utile
- La degradazione graziosa è obbligatoria: sistema audio assente = gioco comunque giocabile

### Collegamento Feature Esistenti

- **Scoring System v2.0**: L'evento GAME_WON già esiste nel GameEngine - l'AudioManager si aggancia allo stesso punto
- **Timer System**: L'evento TIMER_WARNING e TIMER_EXPIRED possono triggerare clip Voice o suoni UI dedicati
- **Profile System**: Base per future preferenze audio per profilo
- **Logging categorizzato** (in design): Aggiungere categoria `audio` per debug del sistema audio

---

## 📚 Riferimenti Contestuali

### File di Riferimento nel Codebase

| File | Rilevanza |
|------|-----------|
| `src/infrastructure/audio/tts_provider.py` | Pattern provider con fallback, degradazione graziosa - da seguire |
| `src/infrastructure/audio/screen_reader.py` | Pattern wrapper infrastrutturale |
| `src/infrastructure/config/scoring_config_loader.py` | Pattern loader JSON da replicare per audio_config_loader.py |
| `config/scoring_config.json` | Schema JSON di riferimento per audio_config.json |
| `src/infrastructure/di_container.py` | Pattern lazy singleton da seguire per get_audio_manager() |
| `src/application/gameplay_controller.py` | Punto di integrazione principale per eventi audio gameplay |
| `src/application/input_handler.py` | Punto di integrazione per navigazione e bumper |
| `src/application/dialog_manager.py` | Punto di integrazione per eventi UI |

### Vincoli da Rispettare

- **Zero modifiche al Domain Layer**: La logica di gioco non sa che esiste un sistema audio
- **Separazione netta da NVDA**: TtsProvider e AudioManager operano in parallelo, mai in cascata
- **Backward compatibility**: Se pygame non disponibile, l'applicazione funziona normalmente senza audio
- **Clean Architecture**: Il layer di Infrastructure non importa mai da Application o Domain (dipendenze verso l'interno)
- **Coerenza stile**: Nomi, commenti, docstring seguono il pattern già presente nel codebase

---

## 🎯 Risultato Finale Atteso (High-Level)

Una volta implementato, il giocatore non vedente potrà:

✅ Percepire la **posizione orizzontale** di ogni pila del tavolo tramite il campo stereo, senza interrogare NVDA  
✅ Identificare il **tipo di pila** (tableau / fondazione / stock) dal timbro del suono ancora prima della lettura  
✅ Ricevere **conferma immediata** di ogni mossa riuscita o fallita in <50ms, prima che NVDA inizi la lettura  
✅ Percepire i **confini del tavolo** tramite bumper sonoro fisico  
✅ **Personalizzare i volumi** di ogni bus in modo indipendente tramite mixer accessibile da tastiera  
✅ **Sentire clip vocali** campionate per eventi rilevanti (vittoria, eventi speciali)  
✅ Avere **preferenze persistite** tra una sessione e l'altra  
✅ **Cambiare sound pack** senza modificare nulla nel codice  
✅ Continuare a giocare normalmente anche **senza sistema audio** (degradazione graziosa)

---

**Fine Design Document**

---

## 🎯 Status Progetto

**Design**: ✅ FROZEN  
**Piano Tecnico**: ✅ READY (`docs/3 - coding plans/PLAN_audio_system_v3.4.0.md` — v1.1, post-review)  
**Implementazione**: ⏳ PENDING  
**Testing**: ⏳ PENDING  
**Deploy**: ⏳ PENDING

---

**Document Version**: v1.2 (Allineato a PLAN v1.1 — constant-power panning, DRY JSON, domande aperte risolte, nome classe corretto)  
**Data Freeze**: 2026-02-22  
**Ultimo Aggiornamento**: 2026-02-22  
**Autore**: AI Assistant + Nemex81  
**Filosofia**: "L'audio non abbellisce il gioco - lo rende leggibile nello spazio"
