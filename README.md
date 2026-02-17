# Solitario Classico Accessibile

Un gioco di carte Solitario (Klondike) in versione accessibile per non vedenti, sviluppato in Python con supporto per screen reader.

**Versione Corrente**: 3.1.0 (Profile System + Stats Presentation UI Complete)

## 🎯 Caratteristiche

- **Accessibilità completa**: Supporto per screen reader con output testuale dettagliato
- **Navigazione intuitiva**: Sistema di cursore per navigare tra le pile di carte
- **Feedback vocale**: Descrizioni in italiano di ogni azione e stato del gioco
- **Sistema profili utente** (v3.0.0): Gestione profili persistenti con statistiche aggregate
- **Presentazione statistiche** (v3.1.0): UI completa per visualizzazione stats, leaderboard, gestione profili
- **Timer system** (v2.7.0): Modalità STRICT/PERMISSIVE con overtime tracking
- **Due mazzi supportati**: 
  - **Mazzo francese** (♥♦♣♠) - 52 carte: Asso, 2-10, Jack, Regina, Re per ogni seme
  - **Mazzo napoletano** (🍷🪙🗡️🏑) - 40 carte autentiche: Asso, 2-7, Regina (8), Cavallo (9), Re (10) per ogni seme
- **Sistema punti completo**: Scoring system v1.5.2 con 5 livelli di difficoltà e statistiche persistenti
- **Undo/Redo**: Possibilità di annullare e ripetere le mosse
- **Architettura modulare**: Design pulito con separazione dei livelli (Clean Architecture)

## 👤 Profile System (v3.0.0 Backend + v3.1.0 UI)

Il gioco ora supporta **profili utente persistenti** con statistiche aggregate e gestione completa da interfaccia grafica.

### Funzionalità Backend (v3.0.0)

- **UserProfile**: Profili JSON con metadata (nome, creazione, ultimo accesso)
- **Statistiche aggregate**: 4 categorie (Globali, Timer, Difficoltà, Scoring)
- **Session tracking**: Registrazione automatica di ogni partita completata
- **Crash recovery**: Rilevamento sessioni orfane da chiusura forzata app
- **Atomic writes**: Scritture JSON atomiche per prevenire corruzione dati
- **Guest profile**: Profilo "Ospite" (profile_000) con protezione eliminazione

### Gestione Profili UI (v3.1.0 - Phase 10)

Accesso tramite menu principale: **"Gestione Profili"** (6° pulsante)

**6 Operazioni Disponibili:**

1. **Crea Nuovo Profilo**
   - Input nome con validazione (no vuoti, max 30 caratteri, no duplicati)
   - Auto-switch al nuovo profilo dopo creazione
   - TTS: "Profilo creato: {nome}. Attivo."

2. **Cambia Profilo**
   - Dialog scelta con anteprima statistiche (vittorie/partite)
   - Profilo corrente marcato con "[ATTIVO]"
   - Salvataggio automatico prima del cambio

3. **Rinomina Profilo**
   - Input pre-compilato con nome corrente
   - Validazione + protezione profilo guest
   - Aggiornamento real-time UI

4. **Elimina Profilo**
   - Dialog conferma con safeguards:
     - Blocco eliminazione profilo guest
     - Blocco eliminazione ultimo profilo rimasto
   - Auto-switch a guest dopo eliminazione

5. **Statistiche Dettagliate** ⭐
   - Apre DetailedStatsDialog (3 pagine)
   - Navigazione PageUp/PageDown
   - ESC torna a Gestione Profili (non menu principale)

6. **Imposta Predefinito**
   - Marca profilo per caricamento automatico all'avvio app
   - TTS: "Profilo predefinito: {nome}"

**Accessibilità NVDA:**
- Navigazione solo tastiera (TAB, ENTER, ESC)
- TTS announcements per tutte le operazioni
- Focus management automatico dopo ogni azione
- Messaggi errore chiari con audio feedback

### Statistiche Presentation (v3.1.0 - Phase 1-9)

**5 Dialog Statistiche:**

1. **VictoryDialog** (fine partita vinta)
   - Outcome sessione (tempo, mosse, punteggio)
   - Riepilogo profilo (vittorie totali, winrate)
   - Rilevamento nuovi record (miglior tempo, miglior punteggio)
   - Prompt rivincita

2. **AbandonDialog** (fine partita abbandonata)
   - EndReason classification (nuovo gioco, uscita, timeout)
   - Impatto su statistiche spiegato
   - Opzione ritorno menu

3. **GameInfoDialog** (durante partita - tasto **I**)
   - Progresso partita corrente (tempo, mosse, score)
   - Riepilogo profilo real-time
   - Non blocca gameplay

4. **DetailedStatsDialog** (3 pagine - via Gestione Profili o tasto **U**)
   - **Pagina 1**: Statistiche globali (partite, vittorie, winrate, best time/score, media mosse)
   - **Pagina 2**: Statistiche timer (partite con timer, vittorie, timeout, overtime, media tempo)
   - **Pagina 3**: Statistiche scoring/difficoltà (breakdown per livello, punteggi medi)
   - Navigazione: PageUp/PageDown, ESC per chiudere

5. **LeaderboardDialog** (menu **L - Leaderboard Globale**)
   - Top 10 giocatori in 5 categorie:
     - Vittoria più veloce
     - Miglior winrate
     - Punteggio più alto
     - Partite giocate
     - Miglior vittoria con timer

**Menu Integration (Phase 9.1-9.2):**
- **U - Ultima Partita**: Apre LastGameDialog (riepilogo ultima partita completata)
- **L - Leaderboard Globale**: Apre LeaderboardDialog (classifica top 10)
- **Gestione Profili**: 6° pulsante menu principale (CRUD + stats + default)

### Storage Paths

```
~/.solitario/
├── profiles/
│   ├── profile_000.json          # Guest profile (protected)
│   ├── profile_{uuid}.json       # User profiles
│   └── profiles_index.json       # Profile index (lightweight)
├── .sessions/
│   └── active_session.json       # Crash recovery tracking
└── scores.json                   # Legacy score storage (deprecated)
```

### Statistics Categories

**GlobalStats:**
- Total games, victories, defeats
- Winrate, best victory time, best score
- Average moves, total undo/hint usage

**TimerStats:**
- Timer games, timer victories, timeouts
- Overtime games, average time, best timed victory

**DifficultyStats:**
- Games per difficulty level (1-5)
- Victories per level
- Average scores per level

**ScoringStats:**
- Scoring games, total score, average score
- Deck type usage (French/Neapolitan)
- Draw count distribution (1/2/3 cards)

## ⏱️ Timer System (v2.7.0)

Modalità timer con gestione avanzata scadenza tempo.

**Caratteristiche:**
- **EndReason enum**: 6 classificazioni fine partita (VICTORY, VICTORY_OVERTIME, ABANDON_NEW_GAME, ABANDON_EXIT, ABANDON_APP_CLOSE, TIMEOUT_STRICT)
- **Modalità STRICT**: Game over automatico allo scadere del timer (TIMEOUT_STRICT)
- **Modalità PERMISSIVE**: Continua gameplay dopo scadenza con tracking overtime (penalità -100 punti/minuto)
- **TTS announcements**: Notifica singola alla scadenza ("Tempo scaduto!" / "Tempo scaduto! Il gioco continua con penalità.")
- **Overtime tracking**: Calcolo secondi oltre limite tempo (solo PERMISSIVE)
- **Victory classification**: Vittorie in overtime auto-convertite a VICTORY_OVERTIME

**Comandi:**
- **T**: Mostra tempo (contestuale: trascorso se timer OFF, rimanente se timer ON)
- **F2**: Attiva/disattiva timer
- **F3/F4**: Decrementa/incrementa timer (-5/+5 minuti)

### Victory Flow & Native Dialogs (v1.6.0-v1.6.1)

Il gioco supporta dialog box native accessibili in **tutti i contesti interattivi**.

**Contesti Dialog Nativi** (v1.6.1):
1. ✅ **Vittoria/Sconfitta**: Report finale completo + prompt rivincita (con stats profilo v3.1.0)
2. ✅ **ESC durante gameplay**: "Vuoi abbandonare la partita?"
3. ✅ **N durante gameplay**: "Nuova partita?" (conferma abbandono)
4. ✅ **ESC in menu di gioco**: "Vuoi tornare al menu principale?"
5. ✅ **ESC in menu principale**: "Vuoi uscire dall'applicazione?"
6. ✅ **Chiusura opzioni (modificate)**: "Salvare le modifiche?"

**Caratteristiche**:
- ✨ **Dialog native wxPython**: Accessibili a screen reader (NVDA, JAWS)
- 📊 **Statistiche complete** (v3.1.0): Profilo, vittorie, winrate, nuovi record
- 🎉 **Report finale dettagliato**: Timer, mosse, rimischiate, statistiche semi, punteggio
- ⚡ **Double-ESC**: Abbandono rapido (premi ESC 2 volte entro 2 secondi)
- 🔄 **UX coerente**: Stesso pattern di dialogs in tutta l'app
- 🐞 **Debug command**: CTRL+ALT+W simula vittoria (solo per test)

**Configurazione**:

```python
# Abilita dialog native (accessibili NVDA/JAWS)
engine = GameEngine.create(use_native_dialogs=True)

# Oppure usa solo TTS (default)
engine = GameEngine.create(use_native_dialogs=False)
```

**Nota**: Se wxPython non è disponibile, l'applicazione degrada automaticamente a modalità TTS-only.

**Accessibilità**:
- Tutti i dialog sono navigabili solo da tastiera (Tab, Enter, ESC)
- Compatibili con NVDA, JAWS (testato su Windows)
- Report ottimizzato per screen reader (frasi brevi, punteggiatura chiara)
- Shortcut keys: S=Sì, N=No, ESC=Annulla

## 📦 Installazione

### Prerequisiti

- Python 3.11 o superiore
- pip (gestore pacchetti Python)
- **wxPython 4.1+** (per interfaccia audiogame)

### Setup

```bash
# Clona il repository
git clone https://github.com/Nemex81/solitario-classico-accessibile.git
cd solitario-classico-accessibile

# Installa le dipendenze
pip install -r requirements.txt

# Installa le dipendenze di sviluppo (opzionale)
pip install -r requirements-dev.txt
```

**Note v2.0.0**:
- ✅ **pygame removed**: The game now uses wxPython exclusively
- ✅ **Improved accessibility**: Better NVDA/JAWS screen reader integration
- ✅ **Lighter dependencies**: -2 packages removed (pygame, pygame-menu)

### ✨ Versione Clean Architecture (Consigliata) - **v3.1.0 wxPython-only**

```bash
python test.py
```

**Caratteristiche v3.1.0**:
- ✅ **wxPython-only**: Evento loop wxPython nativo (no pygame)
- ✅ **Profile System completo**: CRUD profili + statistiche persistenti (v3.0.0 + v3.1.0)
- ✅ **Stats Presentation UI**: 5 dialogs (Victory, Abandon, GameInfo, DetailedStats, Leaderboard)
- ✅ **Timer System avanzato**: STRICT/PERMISSIVE modes, overtime tracking (v2.7.0)
- ✅ Architettura Clean completa (`src/` modules)
- ✅ Dependency Injection
- ✅ Testabilità elevata (≥88% coverage)
- ✅ Manutenibilità ottimale
- ✅ 100% compatibile con versioni precedenti (stesso gameplay)
- ✅ Migliore accessibilità NVDA/JAWS

**Legacy pygame version** (deprecated):
```bash
python test_pygame_legacy.py
```
- ⚠️ pygame-based entry point (deprecated in v2.0.0)
- ⚠️ Kept for reference only

### 🔧 Versione Legacy (Compatibilità)

```bash
python acs.py
```

**Caratteristiche**:
- ⚠️ Architettura monolitica (`scr/` modules)
- ⚠️ Funzionale ma deprecata
- ℹ️ Nessun ulteriore sviluppo
- ℹ️ Mantenuta per backward compatibility

## 🏛️ Architettura

Il progetto segue una **Clean Architecture** (implementata in branch `refactoring-engine`) con separazione completa delle responsabilità:

```
┌─────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                      │
│    (GameFormatter, StatsFormatter - Output Formatting)     │
├─────────────────────────────────────────────────────────┤
│                  APPLICATION LAYER                       │
│    (GameEngine, ProfileService, Controllers, Timer)       │
├─────────────────────────────────────────────────────────┤
│                    DOMAIN LAYER                          │
│  (Models: Card/Deck/Table/Profile, Rules, Services)      │
├─────────────────────────────────────────────────────────┤
│                INFRASTRUCTURE LAYER                      │
│  (ScreenReader, TTS, wxPython UI, Storage, DI Container) │
└─────────────────────────────────────────────────────────┘
```

### UI Architecture (v1.7.3)

**Single-Frame Panel-Swap Pattern** (wxPython standard):
- **1 Frame**: `SolitarioFrame` (600x450, visible and centered)
- **Panel Container**: Hosts multiple panels
- **Panel Swap**: MenuPanel ↔ GameplayPanel via Show/Hide
- **Benefits**: Native TAB navigation, proper NVDA focus, standard wxPython UX

```
SolitarioFrame (single window)
└── panel_container (wx.Panel)
    ├── MenuPanel (wx.Panel - shown/hidden)
    └── GameplayPanel (wx.Panel - shown/hidden)
```

### Struttura Directory

```
solitario-classico-accessibile/
├── test.py                    # ✨ Entry point Clean Architecture
├── acs.py                     # 🔧 Entry point legacy
│
├── src/                       # 🆕 Clean Architecture (v3.1.0)
│   ├── domain/               # Core business logic
│   │   ├── models/          # Card, Deck, Pile, Table, Scoring, Profile, GameEnd
│   │   ├── rules/           # SolitaireRules, MoveValidator
│   │   └── services/        # GameService, ScoringService
│   ├── application/         # Use cases & orchestration
│   │   ├── game_engine.py       # Main controller + ProfileService integration
│   │   ├── profile_service.py   # Profile CRUD + statistics aggregation
│   │   ├── session_tracker.py   # Crash recovery
│   │   ├── input_handler.py     # Keyboard → Commands
│   │   ├── game_settings.py     # Configuration
│   │   └── timer_manager.py     # Timer logic
│   ├── infrastructure/      # External adapters
│   │   ├── accessibility/   # ScreenReader + TTS
│   │   ├── storage/         # ProfileStorage, SessionStorage, ScoreStorage (JSON)
│   │   ├── ui/             # wxPython single-frame UI + ProfileMenuPanel
│   │   └── di_container.py # Dependency Injection
│   └── presentation/        # Output formatting
│       ├── formatters/      # GameFormatter, ScoreFormatter, StatsFormatter
│       └── dialogs/         # Victory, Abandon, GameInfo, DetailedStats, Leaderboard, LastGame
│
├── scr/                       # Legacy monolithic (v1.3.3)
│   ├── game_engine.py        # 43 KB monolith
│   ├── game_table.py
│   ├── decks.py
│   └── ...
│
├── tests/
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests (Clean Arch)
│
└── docs/
    ├── ARCHITECTURE.md       # Architecture details
    ├── API.md                # API reference
    ├── CHANGELOG.md          # Version history
    ├── TODO.md               # Implementation tracking
    └── ...
```

### Dipendenze tra Layer

Segue la **Dependency Rule** di Clean Architecture:

```
Infrastructure ──────┐
                     ├──→ Application ──→ Domain (Core)
Presentation ────────┘
```

- **Domain**: Zero dipendenze esterne (logica pura)
- **Application**: Dipende solo da Domain
- **Infrastructure/Presentation**: Dipendono da Application e Domain

Per dettagli completi: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 🎮 Utilizzo Programmatico

### API Clean Architecture

```python
from src.infrastructure.di_container import get_container

# Bootstrap via Dependency Injection
container = get_container()

# Configurazione
settings = container.get_settings()
settings.deck_type = "neapolitan"  # o "french"
settings.timer_enabled = True
settings.timer_minutes = 15
settings.scoring_enabled = True  # ✨ v1.5.2

# Crea componenti
deck = container.get_deck()  # Usa settings.deck_type
input_handler = container.get_input_handler()
formatter = container.get_formatter(language="it")
profile_service = container.get_profile_service()  # ✨ v3.0.0

# Il resto viene orchestrato dall'Application layer
```

### ⌨️ Comandi Tastiera (Audiogame)

#### Navigazione
- **Frecce SU/GIÙ**: Naviga carte nella pila
- **Frecce SINISTRA/DESTRA**: Cambia pila
- **Numeri 1-7**: Vai alla pila base + **doppio tocco seleziona** ✨
- **SHIFT+1-4**: Vai alla pila semi + **doppio tocco seleziona** ✨
- **SHIFT+S**: Sposta cursore su scarti ✨
- **SHIFT+M**: Sposta cursore su mazzo ✨

#### Azioni di Gioco
- **INVIO**: Seleziona carta / Pesca dal mazzo
- **CANC**: Annulla selezione
- **A**: Auto-mossa verso fondazioni

#### Informazioni
- **H**: Aiuto comandi completo
- **S**: Statistiche partita
- **I**: GameInfo dialog (stats partita corrente + profilo) ✨ v3.1.0
- **P**: Mostra punteggio corrente ✨ (v1.5.2)
- **SHIFT+P**: Ultimi 5 eventi scoring ✨ (v1.5.2)
- **T**: Mostra tempo (contestuale: trascorso/rimanente) ✨ v2.7.0

#### Statistiche e Profili (v3.1.0)
- **U**: Ultima Partita (LastGameDialog) ✨
- **L**: Leaderboard Globale (top 10) ✨
- **Menu → Gestione Profili**: ProfileMenuPanel (6 operazioni) ✨

#### Impostazioni
- **N**: Nuova partita
- **O**: Apri menu opzioni
- **F1**: Cambia tipo mazzo (francese/napoletano)
- **F2**: Attiva/disattiva timer
- **F3**: Decrementa timer (-5 min)
- **F4**: Incrementa timer (+5 min)
- **F5**: Alterna modalità riciclo scarti
- **ESC**: Torna al menu principale

## 🎴 Mazzi di Carte

### Mazzo Francese (52 carte)
- **Semi**: Cuori (♥), Quadri (♦), Fiori (♣), Picche (♠)
- **Valori**: Asso (1), 2-10, Jack (11), Regina (12), Re (13)
- **Vittoria**: 13 carte per seme × 4 semi = 52 carte totali
- **Bonus scoring**: +150 punti ✨

### Mazzo Napoletano (40 carte)
- **Semi**: Bastoni (🏑), Coppe (🍷), Denari (🪙), Spade (🗡️)
- **Valori**: Asso (1), 2-7, Regina (8), Cavallo (9), Re (10)
- **Vittoria**: 10 carte per seme × 4 semi = 40 carte totali
- **Bonus scoring**: +0 punti (baseline)

**Caratteristiche**: Il gioco adatta automaticamente le regole di vittoria e la distribuzione delle carte in base al mazzo selezionato.

## 🏆 Sistema Punti v1.5.2

Il gioco include un sistema di punteggio completo basato sullo standard Microsoft Solitaire, con 5 livelli di difficoltà e statistiche persistenti.

### Eventi Scoring

| Evento | Punti | Descrizione |
|--------|-------|-------------|
| Scarto → Fondazione | **+10** | Carta spostata da pile scarti a fondazione |
| Tableau → Fondazione | **+10** | Carta spostata da pile base a fondazione |
| Carta Rivelata | **+5** | Carta scoperta dopo una mossa |
| Fondazione → Tableau | **-15** | Penalità per spostamento indietro |
| Riciclo Scarti | **-20** | Penalità dopo il 3° riciclo |

### Sistema Difficoltà v2.4.0 (5 Livelli con Preset)

Il gioco implementa un sistema di preset intelligenti che bloccano progressivamente le opzioni per garantire coerenza e fair play.

| Livello | Nome | Moltiplicatore | Opzioni Bloccate | Descrizione |
|---------|------|----------------|------------------|-------------|
| 1 | **Principiante** | 1.0x | 1 (Timer OFF) | Ideale per imparare, nessun limite di tempo |
| 2 | **Facile** | 1.25x | 1 (Timer PERMISSIVE) | Timer con malus punti, molto personalizzabile |
| 3 | **Normale** | 1.5x | 1 (Draw=3) | Regole Vegas standard, 3 carte obbligatorie |
| 4 | **Esperto** | 2.0x | 5 opzioni | Time Attack 30 minuti, senza suggerimenti |
| 5 | **Maestro** | 2.5x | 6 opzioni | **Tournament Mode**: 15 min strict, tutto bloccato |

#### Dettagli Preset

**Livello 1 - Principiante**:
- ✅ Personalizzabile: Carte pescate, Riciclo, Punti, Suggerimenti
- 🔒 Bloccato: Timer (sempre OFF per principianti)
- 🎯 Obiettivo: Imparare il gioco senza pressione temporale

**Livello 2 - Facile**:
- ✅ Personalizzabile: Timer durata, Carte pescate, Riciclo, Punti, Suggerimenti
- 🔒 Bloccato: Modalità Timer (PERMISSIVE - continua con malus)
- 🎯 Obiettivo: Partite casual con possibilità di recupero

**Livello 3 - Normale**:
- ✅ Personalizzabile: Timer, Modalità Timer, Riciclo, Punti, Suggerimenti
- 🔒 Bloccato: Carte Pescate (3 - standard Vegas)
- 🎯 Obiettivo: Esperienza Solitaire classica Vegas

**Livello 4 - Esperto**:
- ✅ Personalizzabile: Sistema Punti (può essere disattivato per focus su tempo)
- 🔒 Bloccato: Timer (30 min), Draw (3), Riciclo (Inversione), Suggerimenti (OFF), Modalità Timer (PERMISSIVE)
- 🎯 Obiettivo: Time Attack Challenge - completa in 30 minuti

**Livello 5 - Maestro**:
- ✅ Personalizzabile: Solo Tipo Mazzo (estetica)
- 🔒 Bloccato: **TUTTO** (Timer 15min STRICT, Draw 3, Inversione, Punti ON, Suggerimenti OFF)
- 🎯 Obiettivo: **Modalità Tournament** - regole uniformi per competizioni ufficiali
- 🛡️ Anti-Cheat: Preset riapplicato automaticamente al caricamento salvataggi

### Bonus Punti

**Mazzo**:
- Mazzo francese (52 carte): **+150 punti**
- Mazzo napoletano (40 carte): **+0 punti** (baseline)

**Carte Pescate** (solo livelli 1-3):
- Draw 1 carta: **+0 punti** (baseline)
- Draw 2 carte: **+100 punti**
- Draw 3 carte: **+200 punti**

**Tempo**:
- **Timer OFF**: Bonus = √(secondi_trascorsi) × 10
- **Timer ON**: Bonus = (tempo_rimanente / tempo_totale) × 1000

**Vittoria**:
- Partita vinta: **+500 punti**
- Partita persa: **+0 punti**

### Formula Finale

```
Punteggio Totale = (
    (Base + Bonus_Mazzo + Bonus_Draw) × Moltiplicatore_Difficoltà
    + Bonus_Tempo + Bonus_Vittoria
)

Clamp a minimum 0 punti
```

### Vincoli Livelli Avanzati

**Livello 4 (Esperto)**:
- Timer minimo: 30 minuti
- Carte pescate: minimo 2
- Modalità riciclo: bloccata su inversione

**Livello 5 (Maestro)**:
- Timer range: 15-30 minuti
- Carte pescate: fissato a 3
- Modalità riciclo: bloccata su inversione

*Nota*: Quando si cambia difficoltà, le impostazioni vengono auto-regolate per rispettare i vincoli.

### Comandi Scoring

- **P**: Mostra punteggio provvisorio corrente con breakdown completo
- **SHIFT+P**: Mostra ultimi 5 eventi scoring con punti guadagnati/persi
- **Opzione Menu #7**: Toggle sistema punti ON/OFF (free-play mode)

### Storage Statistiche

Le statistiche vengono salvate automaticamente in:
```
~/.solitario/scores.json          # Legacy (deprecated v3.0.0)
~/.solitario/profiles/            # ✨ v3.0.0 Profile System
```

**Contenuto Profile JSON**:
```json
{
  "profile_id": "profile_a1b2c3d4",
  "profile_name": "Mario Rossi",
  "created_at": "2026-02-17T20:00:00Z",
  "last_played_at": "2026-02-17T21:30:00Z",
  "is_default": true,
  "global_stats": {
    "total_games": 42,
    "total_victories": 23,
    "total_defeats": 19,
    "winrate": 0.548,
    "best_victory_time_seconds": 225.5,
    "best_score": 1850,
    "avg_moves_per_game": 87.3
  },
  "timer_stats": { ... },
  "difficulty_stats": { ... },
  "scoring_stats": { ... },
  "recent_sessions": [ ... ]
}
```

### Esempi Calcolo

**Esempio 1: Partita Facile Vinta**
```
Base score: 150 punti (15 mosse × 10 punti)
Mazzo francese: +150 punti
Draw 3 carte: +200 punti
Totale pre-multiplier: 500 punti
Moltiplicatore livello 1: ×1.0 = 500 punti
Bonus tempo (timer OFF, 8min): +87 punti
Bonus vittoria: +500 punti
──────────────────────────────
TOTALE: 1087 punti
```

**Esempio 2: Partita Maestro Vinta**
```
Base score: 200 punti (20 mosse × 10 punti)
Mazzo francese: +150 punti
Draw 3 carte: +0 punti (livello 5)
Totale pre-multiplier: 350 punti
Moltiplicatore livello 5: ×2.5 = 875 punti
Bonus tempo (timer ON 18/20min): +900 punti
Bonus vittoria: +500 punti
──────────────────────────────
TOTALE: 2275 punti
```

## 🧪 Testing

```bash
# Esegui tutti i test
pytest tests/ -v

# Esegui test con coverage
pytest tests/ --cov=src --cov-report=term-missing

# Solo test unitari
pytest tests/unit/ -v

# Solo test integrazione (Clean Architecture)
pytest tests/integration/ -v
```

### Coverage Target

| Layer | Coverage Target | Status |
|-------|-----------------|--------|
| Domain | ≥ 95% | ✅ |
| Application | ≥ 85% | ✅ |
| Infrastructure | ≥ 70% | ✅ |
| **Totale** | **≥ 80%** | **✅ 91.47%** |

## 📚 Documentazione

### Clean Architecture (src/)
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Dettagli architettura Clean
- **[docs/API.md](docs/API.md)** - API reference (ProfileService, StatsFormatter, etc.)
- **[docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)** - Guida migrazione scr/ → src/
- **[docs/REFACTORING_PLAN.md](docs/REFACTORING_PLAN.md)** - Piano 13 commits
- **[docs/COMMITS_SUMMARY.md](docs/COMMITS_SUMMARY.md)** - Log dettagliato commits

### Profile System (v3.0.0 + v3.1.0)
- **[docs/2 - projects/DESIGN_PROFILE_STATISTICS_SYSTEM.md](docs/2%20-%20projects/DESIGN_PROFILE_STATISTICS_SYSTEM.md)** - Design doc completo
- **[docs/3 - coding plans/IMPLEMENTATION_PROFILE_SYSTEM.md](docs/3%20-%20coding%20plans/IMPLEMENTATION_PROFILE_SYSTEM.md)** - Piano implementazione backend
- **[docs/3 - coding plans/IMPLEMENTATION_STATS_PRESENTATION.md](docs/3%20-%20coding%20plans/IMPLEMENTATION_STATS_PRESENTATION.md)** - Piano implementazione UI
- **[docs/TODO.md](docs/TODO.md)** - Implementation tracking (Feature 1-3 complete)

### Scoring System (v1.5.2)
- **[docs/IMPLEMENTATION_SCORING_SYSTEM.md](docs/IMPLEMENTATION_SCORING_SYSTEM.md)** - Guida implementativa completa
- **[docs/TODO_SCORING.md](docs/TODO_SCORING.md)** - Checklist implementazione 8 fasi

### ADR
- **[docs/ADR/](docs/ADR/)** - Architecture Decision Records

## 🔄 Stato Migrazione

**Branch corrente**: `copilot/implement-profile-system-v3-1-0`

✅ **COMPLETA** - Feature Stack 1-3 implementata (Feb 17, 2026)

| Fase | Features | Stato |
|------|----------|-------|
| Feature 1 | Timer System v2.7.0 | ✅ ~17 min (4.1x faster) |
| Feature 2 | Profile System Backend v3.0.0 | ✅ ~4 hours (1.6x faster) |
| Feature 3 | Stats Presentation UI v3.1.0 | ✅ ~170 min (3.5x faster) |
| **TOTALE** | **Stack Completo** | **✅ ~5.8h vs 16h estimate (2.8x)** |

**Feature Parity**: 100% con v1.3.3 legacy + Profile System + Stats UI

Per dettagli: [docs/TODO.md](docs/TODO.md), [CHANGELOG.md](CHANGELOG.md)

## 🛠️ Sviluppo

### Strumenti

```bash
# Formattazione codice
black src/ tests/
isort src/ tests/

# Type checking
mypy src/ --strict

# Linting
flake8 src/ tests/

# Verifica complessità
radon cc src/ -a -nb
```

### Contributi

I contributi sono benvenuti! Per favore:

1. Fai fork del repository
2. Crea un branch per la tua feature (`git checkout -b feature/nuova-feature`)
3. Committa le modifiche seguendo [Conventional Commits](https://www.conventionalcommits.org/)
4. Aggiungi test per nuove funzionalità
5. Pusha il branch (`git push origin feature/nuova-feature`)
6. Apri una Pull Request

**Per contributi su Clean Architecture**: Leggi prima [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) per capire la separazione tra layer.

## 📜 Licenza

Questo progetto è rilasciato sotto licenza MIT.

## 👥 Contatti

- **Autore**: Nemex81
- **Repository**: [GitHub](https://github.com/Nemex81/solitario-classico-accessibile)
- **Issues**: [GitHub Issues](https://github.com/Nemex81/solitario-classico-accessibile/issues)

---

**🎉 v3.1.0** - Profile System + Stats Presentation UI complete! Feature stack implementation ~5.8 hours (2.8x faster than manual estimate).
