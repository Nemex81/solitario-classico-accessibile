---
type: design
feature: cx-freeze-frozen-runtime
agent: Agent-Design
status: DRAFT
version: v4.5.1
date: 2026-04-09
---

# DESIGN: cx_Freeze Frozen Runtime Correction v4.5.1

## 1. Idea in 3 righe

Il build cx_Freeze esiste gia e produce l'eseguibile, ma l'avvio frozen resta fragile per tre cause combinate: diagnostica assente con Win32GUI, path runtime ancora dipendenti dal current working directory e dipendenze native/accessibilita non presidiate esplicitamente. Il correttivo proposto non rifonda l'architettura: introduce un bootstrap runtime minimo, rende deterministico il root path dell'app frozen e separa il canale di diagnosi dal canale release. L'obiettivo e trasformare il crash silenzioso in startup osservabile e degradazione controllata, senza refactor ampi del dominio o della UI.

## 2. Attori e Concetti

### Componenti coinvolti

- `acs_wx.py`: entrypoint reale; oggi inizializza il logging prima di ogni altra cosa ma scrive in `logs/` relativo al CWD e intercetta le eccezioni solo dopo `setup_logging()`.
- `setup.py`: definisce il build cx_Freeze con `base="Win32GUI"`, include package Python e duplica `assets/` e `config/` in root e `lib/`.
- `src/infrastructure/config/audio_config_loader.py`: usa `config/audio_config.json` tramite path relativo puro.
- `src/infrastructure/config/scoring_config_loader.py`: usa `Path("config/scoring_config.json")`, ancora dipendente dal CWD.
- `src/infrastructure/audio/audio_manager.py`: usa `Path("assets/sounds")` come default e salva la config audio ricostruendo un path relativo.
- `src/infrastructure/logging/logger_setup.py` e `src/infrastructure/logging/categorized_logger.py`: usano `Path("logs")`, quindi in frozen i log possono finire fuori dalla cartella del build se l'app e lanciata da shortcut o shell con CWD diverso.
- `src/infrastructure/ui/gameplay_panel.py` e `src/infrastructure/ui/card_image_cache.py`: gia ragionano in termini di base path esplicito o derivato da `__file__`, ma oggi convivono con altri componenti che ragionano per CWD.
- `src/infrastructure/accessibility/tts_provider.py`: incapsula NVDA e SAPI5 (`pyttsx3`) e puo fallire in fase di init per assenza provider, COM o dipendenze non congelate.

### Concetti chiave

- `runtime root`: directory canonica da cui derivare `assets/`, `config/` e `logs/`; in frozen deve coincidere con la cartella dell'eseguibile, non con il CWD.
- `bootstrap diagnostico`: inizializzazione minima e anticipata che rende sempre osservabile l'errore di startup, anche se il build GUI non apre una console.
- `release executable` vs `diagnostic executable`: due modalita di avvio dello stesso artefatto applicativo, con differenza solo nel canale diagnostico, non nella logica di business.
- `graceful degradation`: audio PCM e TTS/NVDA non devono poter abortire l'intera applicazione durante l'avvio frozen.

## 3. Flussi Concettuali

### 3.1 Flusso di avvio corretto in build frozen

1. L'eseguibile frozen determina immediatamente il `runtime root`.
2. Prima di creare controller wx o provider TTS, il bootstrap apre un file di log diagnostico nel `runtime root`.
3. Config, asset audio, immagini e log applicativi vengono risolti tutti a partire dallo stesso root canonico.
4. I sottosistemi opzionali (`pygame`, NVDA, SAPI5) vengono inizializzati con gestione esplicita degli errori e fallback non bloccante.
5. Se l'avvio fallisce, l'errore resta sempre ispezionabile in file oppure nella variante console di diagnosi.

### 3.2 Flusso di avvio diagnostico

```text
Build cx_Freeze
  -> eseguibile GUI per uso normale
  -> eseguibile/flag console per smoke test e diagnosi startup

Avvio diagnostico
  -> bootstrap runtime path
  -> log startup immediato
  -> init wx/TTS/audio
  -> se crash: stack trace persistita e visibile
```

### 3.3 Flusso di degradazione accessibile

1. Il bootstrap prova NVDA in modalita `auto`.
2. Se NVDA non e disponibile o fallisce nel frozen build, tenta SAPI5.
3. Se anche SAPI5 fallisce, l'app resta avviabile con `ScreenReader` nullo/dummy e log esplicito.
4. L'audio `pygame` segue la stessa regola: fallimento del mixer o DLL mancanti non blocca il frame wx ne il gameplay base.

## 4. Decisioni Architetturali

### 4.1 Introdurre un unico resolver di path runtime, limitato allo startup-critical path

Decisione: introdurre un componente minimale di runtime path resolution, usato solo dai punti che oggi dipendono dal CWD (`acs_wx.py`, loader config, `AudioManager`, logging e bootstrap immagini dove necessario).

Motivazione: il problema principale non e che manchino i file nel build, ma che parti dell'app li cercano da basi diverse. Continuare a duplicare cartelle nel package riduce il rischio ma non elimina la dipendenza dal CWD. Un resolver unico corregge la causa radice senza rifattorizzare i layer al di fuori del perimetro frozen.

Conseguenza pratica:

- `config/` e `assets/` restano inclusi nel build come oggi.
- I consumer smettono di assumere `Path(".")` o `Path("logs")`.
- Il container o l'entrypoint passa il base path corretto ai componenti infrastrutturali gia predisposti a riceverlo.

### 4.2 Aggiungere bootstrap diagnostico prima del logging applicativo standard

Decisione: introdurre un micro-bootstrap di startup che scriva sempre un log diagnostico nel `runtime root` prima di `setup_logging()` e prima della costruzione di `SolitarioController`.

Motivazione: oggi `base="Win32GUI"` elimina la console e il logging standard e a sua volta relativo al CWD. Se l'errore si verifica nelle prime fasi, l'effetto percepito e un crash silenzioso. Il bootstrap anticipato rende il failure mode osservabile senza cambiare il modello applicativo.

Conseguenza pratica:

- In release GUI l'utente non vede una console, ma il file diagnostico esiste sempre.
- Durante correzione e QA si puo usare una variante console per vedere immediatamente traceback e warning di packaging.

### 4.3 Mantenere Win32GUI per release, ma affiancare una variante di diagnosi

Decisione: non eliminare `Win32GUI` dalla build finale; affiancare invece una modalita di build o un secondo executable console-only destinato a smoke test e debug del frozen startup.

Motivazione: il problema non e la GUI in se, ma l'assenza di osservabilita durante l'indagine. Forzare sempre la console penalizzerebbe l'esperienza utente; non avere una variante diagnostica rende invece cieco il debugging. Il dual-path e la soluzione piu pragmatica.

### 4.4 Rendere opzionali e non bloccanti TTS e audio PCM in startup frozen

Decisione: trattare `pygame`, NVDA e SAPI5 come capability opzionali durante l'avvio frozen. Se falliscono, il processo continua con log esplicito e fallback sicuro.

Motivazione: il progetto e accessibile, ma l'accessibilita non deve tradursi in un hard crash all'avvio quando un provider esterno non e disponibile o non e stato congelato correttamente. La perdita temporanea di una capability e preferibile all'impossibilita totale di aprire l'app.

Conseguenza pratica:

- `pygame` assente o SDL2 incompleta -> audio disabilitato, app avviabile.
- NVDA non attivo o non inizializzabile -> fallback SAPI5.
- SAPI5/pyttsx3 non inizializzabile -> app avviabile senza TTS, con evidence nel log.

### 4.5 Verifica esplicita delle dipendenze native pygame nel packaging

Decisione: il correttivo deve includere un controllo dedicato sulle DLL native di `pygame`/SDL2 nella cartella frozen, con failure del processo di validazione se mancanti.

Motivazione: il package Python `pygame` puo risultare incluso mentre una parte delle DLL native necessarie al mixer resta assente o non risolvibile a runtime. Questo e coerente con i findings sul crash iniziale e con il fatto che l'audio viene toccato molto presto nel bootstrap applicativo.

Conseguenza pratica:

- Il build non e considerato valido solo perche `solitario.exe` esiste.
- La checklist correttiva deve verificare presenza e caricamento delle DLL SDL2 richieste dal ramo audio usato dal progetto.

## 5. Perimetro del Correttivo

### Incluso

- Determinazione canonica del `runtime root` per sorgente e frozen build.
- Riallineamento dei path di config, asset audio e logs al root runtime.
- Diagnostica startup anticipata per build GUI.
- Variante console o flag equivalente per debugging frozen.
- Hardening di init per `pygame`, NVDA e `pyttsx3`.
- Verifica packaging delle DLL native richieste da `pygame`.

### Escluso

- Refactor esteso dei layer applicativi non coinvolti nell'avvio.
- Riprogettazione del sistema audio o del sistema TTS.
- Spostamento dei dati utente in `%APPDATA%` o redesign completo della persistenza.
- Cambio del tool di packaging (`PyInstaller`, `Nuitka`, ecc.).

## 6. Vincoli

- Nessuna modifica a `.github/**`.
- Correttivo minimale e pragmatico: intervenire solo sui punti che impattano l'avvio frozen.
- Compatibilita con build `cx_Freeze` esistente e con il design storico [DESIGN_cx-freeze-setup_v4.5.0.md](DESIGN_cx-freeze-setup_v4.5.0.md).
- Compatibilita Windows prioritaria.
- NVDA e accessibilita restano requisito di qualita, ma con degradazione controllata in caso di provider non disponibile.

## 7. Impatto su Accessibilita

Il frozen build corretto non deve assumere che NVDA o SAPI5 siano sempre inizializzabili. La regola architetturale e:

- accessibilita preferita, non fragile;
- fallback ordinato NVDA -> SAPI5 -> dummy/no-op;
- nessun crash globale dovuto al solo canale TTS;
- evidenza diagnostica chiara quando il canale accessibile si degrada.

Questo preserva il requisito utente piu importante: l'app deve almeno aprirsi e lasciare traccia leggibile del motivo per cui una capability accessibile non e disponibile nel build frozen.

## 8. Rischi e Vincoli Residui

- `accessible_output2` e `pyttsx3` dipendono da componenti Windows/COM non completamente controllabili dal package; il correttivo riduce il crash, non garantisce feature parity assoluta tra ambiente sorgente e frozen.
- Alcune DLL `pygame` possono risultare presenti ma comunque non caricabili per differenze di runtime Windows; serve validazione su macchina pulita, non solo sul dev box.
- Finche il progetto mantiene doppi pattern di path resolution, ogni nuovo modulo introdotto senza usare il resolver comune puo reintrodurre regressioni frozen.
- Il log diagnostico aiuta a spiegare il crash, ma non sostituisce uno smoke test reale del `.exe` su sistema esterno all'ambiente di sviluppo.

## 9. Esito Atteso

Il progetto conserva il packaging cx_Freeze gia introdotto, ma sostituisce l'attuale startup opaco con un avvio frozen deterministico, ispezionabile e resistente al fallimento dei sottosistemi opzionali. Il risultato atteso non e una nuova architettura, ma una correzione mirata che consenta a `solitario.exe` di partire correttamente o, in caso di errore, di fallire in modo leggibile e diagnosticabile.
