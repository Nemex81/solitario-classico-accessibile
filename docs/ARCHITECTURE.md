    ## AudioManager e DIContainer (Infrastructure Layer)

    **AudioManager** è l'orchestratore del sistema audio:
    - Riceve `AudioEvent` dai controller Application
    - Consulta `SoundCache` per asset e mapping
    - Delega la riproduzione a `SoundMixer` (bus, panning, mute)
    - Gestisce ciclo di vita, pause, resume, shutdown, salvataggio settings

    **Pattern DIContainer:**
    - Accesso singleton lazy-loaded: `container.get_audio_manager()`
    - Shutdown sicuro: `container.shutdown_audio_manager()`
    - Nessuna dipendenza verso Domain/Application

    **Cross-reference:** vedi [API.md](API.md#audiomanager)

    │   ├── audio/
    │   │   ├── audio_events.py    # AudioEventType & AudioEvent (entry point dati eventi audio, v3.4.0)
    │   │   ├── audio_manager.py   # AudioManager orchestratore audio (gestione eventi, bus, panning, v3.4.0)
    │   │   └── ...                # Altri moduli audio (SoundCache, SoundMixer)
# Architettura del Sistema

## 📀 Panoramica

Il Solitario Classico Accessibile utilizza una **Clean Architecture** (architettura a cipolla) che separa le responsabilità in livelli distinti, garantendo:

- **Testabilità**: Ogni componente può essere testato in isolamento
- **Manutenibilità**: Le modifiche in un livello non impattano gli altri
- **Flessibilità**: Facile sostituzione di componenti (es. UI)
- **Indipendenza dal framework**: Il core non dipende da librerie esterne

## 🏛️ Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │     GameFormatter, StatsFormatter (v3.1.0)          │    │
│  │  - Formattazione stato per screen reader            │    │
│  │  - Statistiche formattate (metodi summary/detailed) │    │
│  │  - Localizzazione italiano                          │    │
│  │  - Output accessibile                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │     Dialogs (v3.1.0)                                │    │
│  │  - VictoryDialog, AbandonDialog, GameInfoDialog     │    │
│  │  - DetailedStatsDialog, LeaderboardDialog           │    │
│  │  - LastGameDialog                                   │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│  ┌───────────────────┐  ┌────────────────────────────┐     │
│  │  GameController   │  │     Command Pattern        │     │
│  │  - Orchestrazione │  │  - MoveCommand             │     │
│  │  - Use cases      │  │  - DrawCommand             │     │
│  │  - State mgmt     │  │  - CommandHistory          │     │
│  │  - AudioEvent emission for feedback   │          │
│  └───────────────────┘  └────────────────────────────┘     │
│  ┌───────────────────┐  ┌────────────────────────────┐     │
│  │  ProfileService   │  │  SessionTracker (v3.0.0)   │     │
│  │  - CRUD profili   │  │  - Crash recovery          │     │
│  │  - Stats tracking │  │  - Orphaned sessions       │     │
│  └───────────────────┘  └────────────────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐   │
│  │   Models    │  │   Rules     │  │    Services       │   │
│  │  - Card     │  │  - Move     │  │  - GameService    │   │
│  │  - Pile     │  │    Validator│  │  - Orchestration  │   │
│  │  - GameState│  │             │  │  - ScoringService │   │
│  │  - Profile  │  │             │  │  - StatsAggregator│   │
│  │  - Session  │  │             │  │                   │   │
│  └─────────────┘  └─────────────┘  └───────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 Protocol Interfaces                  │   │
│  │  - MoveValidatorProtocol                            │   │
│  │  - GameServiceProtocol                              │   │
│  │  - FormatterProtocol                                │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   DIContainer                        │   │
│  │  - Dependency Injection                             │   │
│  │  - Component lifecycle                              │   │
│  │  - Configuration                                    │   │
│  │  - Provides AudioManager singleton to controllers    │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │     Storage (v3.0.0)                                │   │
│  │  - ProfileStorage (atomic writes)                   │   │
│  │  - SessionStorage (crash detection)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │     UI Layer (v3.1.0)                               │   │
│  │  - MenuPanel (extended to 6 buttons)                │   │
│  │  - ProfileMenuPanel (6 operations modal)            │   │
│  │  - NVDA accessibility integration                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔊 Side-Effects Isolation: TTS Announcements

### Principio Architetturale

**TTS è un side-effect opzionale gestito SOLO a livello Application Layer.**

```
┌─────────────────────────────────────────────────┐
│ Application Layer (GameEngine)                  │
│ ├─ TTS warnings (_speak() helper)               │ ← UNICO punto di emissione
│ ├─ _announce_draw_threshold_warning()           │
│ └─ _announce_recycle_threshold_warning()        │
└─────────────────────────────────────────────────┘
                    ▼ calls
┌─────────────────────────────────────────────────┐
│ Domain Layer (GameService, ScoringService)      │
│ ├─ draw_cards() → NO TTS                        │ ← Domain puro
│ ├─ recycle_waste() → NO TTS                     │
│ └─ record_event() → NO TTS                      │
└─────────────────────────────────────────────────┘
```

### Garanzie

**✅ Domain Layer Purity:**
- `GameService` e `ScoringService` **MAI** chiamano TTS direttamente
- Ritornano solo `(success, message, data)` tuples
- Testabili senza mock TTS invasivi

**✅ Engine Layer Orchestration:**
- `GameEngine` decide **quando** e **cosa** annunciare
- Guard condizionale: `if success and scoring_enabled and scoring:`
- Helper `_speak()` con triple-guard (safe per test headless)

**✅ Test Isolation:**
```python
# Domain tests (NO TTS dependency)
def test_draw_cards_penalty():
    service = GameService(table, rules, scoring)
    success, msg, cards = service.draw_cards(3)
    assert scoring.stock_draw_count == 3  # ✅ No TTS needed

# Engine tests (TTS optional)
def test_draw_warning_announcement():
    engine = GameEngine.create(audio_enabled=False)  # ← TTS disabled
    success, msg = engine.draw_from_stock()
    # _speak() diventa no-op, test passa ✅
```

### Implementazione: `_speak()` Safe Guard

```python
def _speak(self, message: str, interrupt: bool = False) -> None:
    """Safe TTS adapter con None-check (v2.6.0).
    
    Triple guard per test headless e fail-safe runtime:
    1. screen_reader not None
    2. hasattr(screen_reader, 'tts')
    3. try/except per runtime errors
    """
    if self.screen_reader and hasattr(self.screen_reader, 'tts'):
        try:
            self.screen_reader.tts.speak(message, interrupt=interrupt)
        except Exception as e:
            log.warning_issued("GameEngine", f"TTS speak failed: {e}")
    # Else: no-op (test-safe, no crash)
```

**Perché è importante:**
- ❌ **ANTI-PATTERN:** Domain chiama TTS → test diventano complessi, mock ovunque
- ✅ **PATTERN:** Engine orchestrazione TTS → domain testabile in isolamento

### Flusso Completo: Draw con Warning

```python
# 1. User preme D (21esima carta totale)
GamePlayController._draw_cards()

# 2. Engine chiama domain
success, msg, cards = engine.service.draw_cards(count=1)
# → service.scoring.stock_draw_count = 21 (domain puro)

# 3. Engine decide annuncio (application logic)
if success and self.settings.scoring_enabled:
    engine._announce_draw_threshold_warning()
    # → Legge stock_draw_count da scoring
    # → Genera warning se threshold (21/41)
    # → Chiama _speak() (safe side-effect)

# 4. TTS emissione (opt-in)
if screen_reader:  # ← Guard in _speak()
    tts.speak("AVVISO PUNTEGGIO: Superata soglia 21 pescate...")
```

**Vantaggi:**
- Domain layer testabile senza NVDA/SAPI
- Engine layer può disabilitare TTS senza toccare domain
- Warnings configurabili (`ScoreWarningLevel`) senza refactor domain

## 📁 Struttura delle Directory

```
src/
├── __init__.py
├── application/           # Application Layer
│   ├── __init__.py
│   ├── commands.py       # Command pattern per undo/redo
│   ├── game_controller.py # Controller principale
│   ├── game_engine.py    # Engine con ProfileService integration
│   ├── profile_service.py # Profile CRUD + stats (v3.0.0)
│   ├── session_tracker.py # Crash recovery (v3.0.0)
│   ├── input_handler.py  # Keyboard → Commands
│   ├── game_settings.py  # Configuration
│   ├── main_menu_controller.py  # Main menu navigation logic (v3.4.1)
│   ├── mixer_controller.py  # Audio mixer controller with TTS (v3.4.1)
│   └── timer_manager.py  # Timer logic (v2.7.0)
├── domain/               # Domain Layer (Core)
│   ├── __init__.py
│   ├── interfaces/       # Protocol interfaces
│   │   ├── __init__.py
│   │   └── protocols.py
│   ├── models/           # Entità di dominio
│   │   ├── __init__.py
│   │   ├── card.py      # Card, Rank, Suit
│   │   ├── game_state.py # GameState immutabile
│   │   ├── pile.py      # Pile, PileType
│   │   ├── profile.py   # UserProfile, SessionOutcome (v3.0.0)
│   │   └── game_end.py  # EndReason enum (v2.7.0)
│   ├── rules/           # Business rules
│   │   ├── __init__.py
│   │   └── solitaire_rules.py
│   └── services/        # Domain services
│       ├── __init__.py
│       ├── game_service.py
│       ├── scoring_service.py
│       └── stats_aggregator.py (v3.0.0)
├── infrastructure/       # Infrastructure Layer
│   ├── __init__.py
│   ├── accessibility/   # Screen reader support
│   ├── storage/         # ProfileStorage, SessionStorage (v3.0.0)
│   ├── di_container.py  # Dependency injection
│   └── ui/              # User interface
│       ├── dialogs/     # Native wxPython dialogs (moved from presentation, v3.2.2)
│       │   ├── victory_dialog.py
│       │   ├── abandon_dialog.py
│       │   ├── game_info_dialog.py
│       │   ├── detailed_stats_dialog.py
│       │   ├── leaderboard_dialog.py
│       │   └── last_game_dialog.py
│       ├── widgets/     # Custom wxPython widgets (moved from presentation, v3.2.2)
│       │   └── timer_combobox.py
│       ├── menu_panel.py      # Main menu (6 buttons v3.1.0)
│       ├── gameplay_panel.py  # Gameplay UI
│       ├── board_layout_manager.py # BoardLayoutManager: calcola geometria pixel delle pile; include metodo adattivo per il tableau
│       └── profile_menu_panel.py (v3.1.0) # Profile management modal
└── presentation/        # Presentation Layer
    ├── __init__.py
    └── formatters/
        ├── game_formatter.py
        └── stats_formatter.py (v3.1.0) # Statistiche formattate

tests/                    # Test Suite (v3.5.0 modernized)
├── __init__.py
├── unit/                # Unit tests
│   ├── domain/         # Domain layer tests
│   ├── application/    # Application layer tests
│   └── presentation/   # Presentation layer tests
├── integration/         # Integration tests (v3.5.0)
│   └── test_profile_game_integration.py  # 10 ProfileService+GameEngine tests
├── archive/             # Archived legacy tests (v3.5.0)
│   ├── README.md       # Archival rationale + coverage mapping
│   └── scr/            # 3 legacy monolithic tests (preserved for reference)
│       ├── test_distribuisci_carte_deck_switching.py
│       ├── test_game_engine_f3_f5.py
│       └── test_king_to_empty_base_pile.py
└── conftest.py          # Pytest configuration
```

## 🗂️ Project Structure (Complete Hierarchy)

### Root Directory Overview

```
solitario-classico-accessibile/
├── src/                    # Codice sorgente principale (Clean Architecture layers)
├── tests/                  # Test suite completa (unit, integration, archive)
├── docs/                   # Documentazione tecnica (API, architettura, changelog)
├── acs_wx.py              # Entry point applicazione wxPython
├── requirements.txt        # Dipendenze Python produzione
├── requirements-dev.txt    # Dipendenze sviluppo (pytest, mypy, coverage)
├── pytest.ini             # Configurazione pytest + marker @pytest.mark.gui
├── .gitignore             # Git exclusions (venv, __pycache__, .solitario/)
├── README.md              # Documentazione utente + quick start
└── LICENSE                # Licenza progetto (MIT)
```

**File Root Critici:**

| File | Scopo | Quando Modificare |
|------|-------|-------------------|
| `acs_wx.py` | Entry point wxPython, inizializzazione app, main loop | Cambio framework UI, bootstrap logic |
| `requirements.txt` | Dipendenze runtime (wxPython, pyttsx3, accessibility) | Aggiunta/rimozione librerie produzione |
| `requirements-dev.txt` | Tool sviluppo (pytest, mypy, coverage, black) | Aggiunta tool testing/linting |
| `pytest.ini` | Marker `@pytest.mark.gui`, coverage paths, test discovery | Configurazione CI/CD, test isolation |
| `.gitignore` | Esclusioni Git (venv, profili utente `~/.solitario/`) | Nuovi file temporanei da escludere |

---

### Complete File Tree

```
solitario-classico-accessibile/
│
├── acs_wx.py                           # Entry point wxPython (MainApp, bootstrap)
├── requirements.txt                    # Dipendenze produzione
├── requirements-dev.txt                # Dipendenze sviluppo
├── pytest.ini                          # Configurazione pytest
├── .gitignore                          # Git exclusions
├── README.md                           # Documentazione utente
├── LICENSE                             # Licenza MIT
│
├── src/                                # === SOURCE CODE (Clean Architecture) ===
│   ├── __init__.py
│   │
│   ├── application/                    # === APPLICATION LAYER ===
│   │   ├── __init__.py
│   │   ├── commands.py                # Command Pattern (MoveCommand, DrawCommand, Undo/Redo)
│   │   ├── game_controller.py         # Controller principale (use cases orchestration)
│   │   ├── game_engine.py             # Engine business logic + ProfileService integration
│   │   ├── profile_service.py         # Profile CRUD + stats aggregation (v3.0.0)
│   │   ├── session_tracker.py         # Crash recovery (orphaned sessions detection)
│   │   ├── input_handler.py           # Keyboard input → Command mapping
│   │   ├── game_settings.py           # Configuration management (difficulty, timer, scoring)
│   │   └── timer_manager.py           # Timer logic (STRICT/PERMISSIVE modes, overtime tracking)
│   │
│   ├── domain/                         # === DOMAIN LAYER (Core Business Logic) ===
│   │   ├── __init__.py
│   │   │
│   │   ├── interfaces/                # Protocol interfaces (structural typing)
│   │   │   ├── __init__.py
│   │   │   └── protocols.py          # MoveValidatorProtocol, GameServiceProtocol, FormatterProtocol
│   │   │
│   │   ├── models/                    # Domain entities (immutable dataclasses)
│   │   │   ├── __init__.py
│   │   │   ├── card.py               # Card, Rank, Suit (mazzo francese + napoletano)
│   │   │   ├── game_state.py         # GameState immutable (copy-on-write pattern)
│   │   │   ├── pile.py               # Pile (tableau, foundation, stock, waste)
│   │   │   ├── profile.py            # UserProfile, SessionOutcome (v3.0.0)
│   │   │   ├── game_end.py           # EndReason enum (VICTORY, VICTORY_OVERTIME, ABANDON_*, TIMEOUT_STRICT)
│   │   │   └── statistics.py         # GlobalStats, TimerStats, DifficultyStats, ScoringStats (v3.0.0)
│   │   │
│   │   ├── rules/                     # Business rules validation
│   │   │   ├── __init__.py
│   │   │   └── solitaire_rules.py     # Klondike rules (foundation stacking, tableau stacking, King placement)
│   │   │
│   │   └── services/                  # Domain services (stateless logic)
│   │       ├── __init__.py
│   │       ├── game_service.py       # Game orchestration (draw, recycle, move execution)
│   │       ├── scoring_service.py    # Score calculation (penalties, bonuses, thresholds)
│   │       └── stats_aggregator.py   # Statistics aggregation logic (v3.0.0)
│   │
│   ├── infrastructure/                # === INFRASTRUCTURE LAYER ===
│   │   ├── __init__.py
│   │   │
│   │   ├── accessibility/            # Screen reader support
│   │   │   ├── __init__.py
│   │   │   ├── screen_reader.py     # ScreenReader abstraction (NVDA, SAPI, macOS VoiceOver)
│   │   │   └── tts_engine.py        # TTS wrapper (pyttsx3 integration)
│   │   │
│   │   ├── storage/                  # Persistence layer (v3.0.0)
│   │   │   ├── __init__.py
│   │   │   ├── profile_storage.py   # ProfileStorage (atomic JSON writes, temp-file-rename)
│   │   │   └── session_storage.py   # SessionStorage (crash detection tracking)
│   │   │
│   │   ├── logging/                  # Logging categorizzato (v3.5.0)
│   │   │   ├── __init__.py          # Re-export: setup_logging, setup_categorized_logging, LOGS_DIR, LOG_FILE
│   │   │   ├── categorized_logger.py # setup_categorized_logging() — multi-file RotatingFileHandler (Paradox-style)
│   │   │   ├── logger_setup.py      # Thin wrapper backward-compat → categorized_logger.py (DEPRECATED v3.5.0)
│   │   │   └── game_logger.py       # Helper semantici: ~30 funzioni named per categoria (game/ui/error/timer)
│   │   │
│   │   ├── di_container.py           # Dependency Injection container (singleton factories)
│   │   │
│   │   └── ui/                       # User Interface (wxPython panels)
│   │       ├── __init__.py
│   │       ├── dialogs/              # Native wxPython dialogs (moved from presentation, v3.2.2)
│   │       │   ├── __init__.py
│   │       │   ├── victory_dialog.py    # Victory dialog (outcome + profile summary + new records + rematch prompt)
│   │       │   ├── abandon_dialog.py    # Abandon dialog (EndReason classification + stats impact)
│   │       │   ├── game_info_dialog.py  # Game info dialog (progress + profile snapshot, triggered by I key)
│   │       │   ├── detailed_stats_dialog.py  # Detailed stats dialog (3 pages: Global, Timer, Difficulty/Scoring)
│   │       │   ├── leaderboard_dialog.py     # Leaderboard dialog (Top 10 in 5 categories)
│   │       │   └── last_game_dialog.py       # Last game dialog (recent session summary)
│   │       ├── widgets/              # Custom wxPython widgets (moved from presentation, v3.2.2)
│   │       │   ├── __init__.py
│   │       │   └── timer_combobox.py # Timer duration selector (ComboBox with 0-disabled + time options)
│   │       ├── menu_panel.py         # Main menu panel (6 buttons: Nuova Partita, Opzioni, Ultima Partita, Leaderboard, Gestione Profili, Esci)
│   │       ├── gameplay_panel.py     # Gameplay UI (keyboard navigation, cursor management)
│   │       └── profile_menu_panel.py # Profile management modal (6 operations: Create, Switch, Rename, Delete, Stats, Set Default) [v3.1.0]
│   │
│   └── presentation/                  # === PRESENTATION LAYER ===
│       ├── __init__.py
│       │
│       └── formatters/               # Output formatting (screen reader optimized)
│           ├── __init__.py
│           ├── game_formatter.py    # Game state formatting (card lists, cursor position, move results)
│           └── stats_formatter.py   # Statistics formatting (summary/detailed methods, NVDA-optimized) [v3.1.0]
│
├── tests/                             # === TEST SUITE (v3.5.0 - 88.2% coverage) ===
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration (fixtures, shared setup)
│   │
│   ├── unit/                         # Unit tests (isolated layer testing)
│   │   ├── __init__.py
│   │   │
│   │   ├── domain/                   # Domain layer tests (95%+ coverage)
│   │   │   ├── __init__.py
│   │   │   ├── models/
│   │   │   │   ├── test_card.py     # Card logic (stacking rules, rank/suit validation)
│   │   │   │   ├── test_game_state.py  # GameState immutability, with_move() copy-on-write
│   │   │   │   ├── test_pile.py     # Pile operations (add, remove, get_card_count)
│   │   │   │   └── test_profile.py  # UserProfile, SessionOutcome (v3.0.0)
│   │   │   ├── rules/
│   │   │   │   └── test_solitaire_rules.py  # Klondike rules validation (foundation, tableau, King)
│   │   │   └── services/
│   │   │       ├── test_game_service.py  # Game orchestration logic
│   │   │       ├── test_scoring_service.py  # Score calculation (penalties, bonuses)
│   │   │       └── test_stats_aggregator.py  # Statistics aggregation (v3.0.0)
│   │   │
│   │   ├── application/              # Application layer tests (85%+ coverage)
│   │   │   ├── __init__.py
│   │   │   ├── test_commands.py     # Command Pattern (execute, undo, redo)
│   │   │   ├── test_game_controller.py  # Controller use cases
│   │   │   ├── test_game_engine.py  # Engine orchestration + ProfileService integration
│   │   │   ├── test_profile_service.py  # Profile CRUD + session recording (v3.0.0)
│   │   │   ├── test_session_tracker.py  # Crash recovery (orphaned sessions)
│   │   │   └── test_timer_manager.py    # Timer logic (STRICT/PERMISSIVE, overtime)
│   │   │
│   │   └── presentation/             # Presentation layer tests (70%+ coverage)
│   │       ├── __init__.py
│   │       ├── formatters/
│   │       │   ├── test_game_formatter.py  # Game state formatting
│   │       │   └── test_stats_formatter.py  # Statistics formatting (15 tests, 93% coverage) [v3.1.0]
│   │       └── dialogs/
│   │           └── test_dialogs.py  # Dialog initialization + content validation (v3.1.0)
│   │
│   ├── integration/                  # Integration tests (cross-layer validation) [v3.5.0]
│   │   ├── __init__.py
│   │   └── test_profile_game_integration.py  # 10 tests ProfileService + GameEngine integration
│   │       # Tests: victory updates, abandon updates, timeout handling, stats aggregation,
│   │       #        VICTORY_OVERTIME classification, EndReason coverage, timer mode tracking,
│   │       #        difficulty stats, scoring stats, session history FIFO limit
│   │
│   └── archive/                      # Archived legacy tests (preserved for reference) [v3.5.0]
│       ├── README.md                 # Archival rationale + replacement coverage mapping
│       └── scr/                      # 3 legacy monolithic tests (pre-Clean Architecture)
│           ├── test_distribuisci_carte_deck_switching.py  # Deck switching logic (obsolete)
│           ├── test_game_engine_f3_f5.py                  # Timer F3/F5 adjustments (obsolete)
│           └── test_king_to_empty_base_pile.py            # King placement rules (obsolete)
│
└── docs/                              # === DOCUMENTATION ===
    ├── API.md                        # API reference (GameController, GameEngine, Domain models, v3.1.2)
    ├── ARCHITECTURE.md               # Architettura sistema (Clean Architecture, layers, patterns, v3.5.0)
    ├── CHANGELOG.md                  # Version history completa (v1.0.0 → v3.5.0)
    ├── TODO.md                       # Implementation tracking Feature 1-3 (Profile System roadmap)
    ├── TESTING.md                    # Testing guide (pytest usage, @pytest.mark.gui marker, CI setup) [v3.5.0]
    └── legacy/                       # Documentazione storica (archiviata)
        ├── IMPLEMENTATION_TIMER_STRICT_MODE_SYSTEM_v2.1.md  # Timer STRICT implementation
        ├── AUDIT_CALLAFTER_PATTERNS_v2.1.md                 # CallAfter pattern audit
        └── ...                       # Altri documenti implementazione v2.x
```

---

### Key Directory Purposes

#### `/src/` - Source Code (Clean Architecture)

**Layers Hierarchy:**
```
Presentation ──→ Application ──→ Domain ←── Infrastructure
     ↓               ↓              ↑             ↓
  Dialogs      GameEngine    GameService    Storage/DI
  Formatters   Commands      Rules          UI/Accessibility
```

**Dependency Rules:**
- ✅ **Domain**: No dependencies (pure business logic)
- ✅ **Application**: Depends on Domain only
- ✅ **Presentation**: Depends on Domain + Application
- ✅ **Infrastructure**: Depends on Domain (implements interfaces)

#### `/tests/` - Test Suite (v3.5.0)

**Coverage Targets:**
- **Domain**: ≥ 95% (pure logic, critical path)
- **Application**: ≥ 85% (use cases, orchestration)
- **Infrastructure**: ≥ 70% (external dependencies, UI)
- **Total**: **≥ 88%** (current: **88.2%**)

**Test Isolation:**
- Unit tests: No external dependencies (fast, isolated)
- Integration tests: Cross-layer validation (realistic scenarios)
- `@pytest.mark.gui`: Isolates wxPython tests for CI/CD

**Archival Strategy (v3.5.0):**
- Legacy tests preserved in `/tests/archive/scr/`
- `README.md` documents replacement coverage mapping
- Git history intact (no deletions)

#### `/docs/` - Documentation

**Living Documentation:**
- `API.md`: Public API reference (updated with code changes)
- `ARCHITECTURE.md`: System design (updated with structural changes)
- `CHANGELOG.md`: Version history (updated with releases)
- `TESTING.md`: Testing practices (updated with test tooling changes)

**Legacy Docs:**
- `/docs/legacy/`: Historical implementation documents (v2.x era)
- Preserved for reference, superseded by current docs

---

### File Naming Conventions

**Python Modules:**
- `snake_case.py` (standard PEP 8)
- Suffixes: `_service.py`, `_storage.py`, `_manager.py`, `_formatter.py`

**Test Files:**
- `test_<module_name>.py` (pytest discovery)
- Mirror src structure: `src/domain/models/card.py` → `tests/unit/domain/models/test_card.py`

**Documentation:**
- `UPPERCASE.md` for root docs (README, CHANGELOG, LICENSE)
- `PascalCase.md` for guides (API, ARCHITECTURE, TESTING)

---

### Critical Path Files (Top 10)

| File | Layer | Responsabilità | Complexity |
|------|-------|---------------|------------|
| `src/application/game_engine.py` | Application | Orchestrazione completa gioco + ProfileService | Alta (450+ LOC) |
| `src/domain/services/game_service.py` | Domain | Logica gioco (draw, move, recycle) | Media (300+ LOC) |
| `src/application/profile_service.py` | Application | Profile CRUD + stats aggregation | Media (280+ LOC) |
| `src/infrastructure/ui/profile_menu_panel.py` | Infrastructure | UI gestione profili (6 operations) | Media (267 LOC) |
| `src/presentation/formatters/stats_formatter.py` | Presentation | Statistiche formattate NVDA | Media (250+ LOC) |
| `src/domain/rules/solitaire_rules.py` | Domain | Validazione regole Klondike | Media (200+ LOC) |
| `src/domain/services/scoring_service.py` | Domain | Calcolo punteggio + penalties | Media (180+ LOC) |
| `src/infrastructure/storage/profile_storage.py` | Infrastructure | Persistence atomica JSON | Bassa (150+ LOC) |
| `src/application/timer_manager.py` | Application | Timer STRICT/PERMISSIVE + overtime | Media (140+ LOC) |
| `acs_wx.py` | Root | Entry point wxPython, bootstrap | Bassa (100+ LOC) |

---

## 🧩 Componenti Principali

### Domain Layer

#### Card (`src/domain/models/card.py`)

Rappresentazione immutabile di una carta da gioco.

```python
@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit
    
    def can_stack_on_foundation(self, other: Optional[Card]) -> bool: ...
    def can_stack_on_tableau(self, other: Optional[Card]) -> bool: ...
```

#### GameState (`src/domain/models/game_state.py`)

Stato immutabile del gioco con pattern copy-on-write.

```python
@dataclass(frozen=True)
class GameState:
    foundations: Tuple[Tuple[str, ...], ...]
    tableaus: Tuple[Tuple[str, ...], ...]
    stock: Tuple[str, ...]
    waste: Tuple[str, ...]
    status: GameStatus
    
    def with_move(self, **kwargs) -> GameState: ...
```

#### MoveValidator (`src/domain/rules/solitaire_rules.py`)

Validazione delle mosse secondo le regole del Klondike.

```python
class MoveValidator:
    def can_move_to_foundation(card, foundation_index, state) -> bool: ...
    def can_move_to_tableau(cards, tableau_index, state) -> bool: ...
```

#### GameService (`src/domain/services/game_service.py`)

Orchestrazione della logica di gioco.

```python
class GameService:
    def new_game(config: GameConfiguration) -> GameState: ...
    def move_to_foundation(state, source, target) -> GameState: ...
    def draw_from_stock(state) -> GameState: ...
```

### Application Layer

#### GameController (`src/application/game_controller.py`)

Coordina i use cases e gestisce lo stato dell'applicazione.

```python
class GameController:
    def start_new_game(difficulty, deck_type) -> str: ...
    def execute_move(action, source, target) -> Tuple[bool, str]: ...
    def get_current_state_formatted() -> str: ...
```

#### Command Pattern (`src/application/commands.py`)

Supporto per undo/redo tramite Command pattern.

```python
class Command(ABC):
    def execute(state: GameState) -> GameState: ...
    def undo(state: GameState) -> GameState: ...

class CommandHistory:
    def execute(command, state) -> GameState: ...
    def undo(state) -> GameState: ...
    def redo(state) -> GameState: ...
```

### Presentation Layer

#### GameFormatter (`src/presentation/game_formatter.py`)

Formattazione accessibile per screen reader.

```python
class GameFormatter:
    def format_game_state(state) -> str: ...
    def format_cursor_position(state) -> str: ...
    def format_move_result(success, message) -> str: ...
```

#### StatsFormatter (`src/presentation/formatters/stats_formatter.py` - v3.1.0)

Formattazione statistiche profilo accessibile per NVDA.

**Metodi Principali di Formattazione:**

```python
class StatsFormatter:
    # Summary methods (for dialogs)
    def format_global_stats_summary(stats: GlobalStats) -> str: ...
    def format_session_outcome(outcome: SessionOutcome) -> str: ...
    def format_profile_summary(profile: UserProfile) -> str: ...
    def format_new_records(outcome: SessionOutcome, profile: UserProfile) -> str: ...
    
    # Detailed page methods (for DetailedStatsDialog)
    def format_global_stats_detailed(stats: GlobalStats, profile_name: str) -> str: ...
    def format_timer_stats_detailed(stats: TimerStats) -> str: ...
    def format_scoring_difficulty_stats(
        scoring_stats: ScoringStats, 
        difficulty_stats: DifficultyStats
    ) -> str: ...
    
    # Utility methods
    def format_leaderboard(profiles: List[UserProfile], category: str) -> str: ...
```

**Helper Methods (Formatting):**
```python
# Time formatting
@staticmethod
def format_duration(seconds: float) -> str: ...  # "3 minuti e 45 secondi"

@staticmethod
def format_time_mm_ss(seconds: float) -> str: ...  # "5:25"

# Number formatting
@staticmethod
def format_number(value: int) -> str: ...  # "1.850" (Italian thousands)

@staticmethod
def format_percentage(value: float, decimals: int = 1) -> str: ...  # "54,8%"

# EndReason labels
@staticmethod
def format_end_reason(reason: EndReason) -> str: ...  # "Vittoria", "Tempo scaduto"
```

**Caratteristiche:**
- Localizzazione italiana completa
- Output ottimizzato per NVDA (frasi brevi, punteggiatura chiara)
- Percentuali formattate con virgola decimale (es. `"54,8%"`)
- Tempi formattati estesi (es. `"3 minuti e 45 secondi"`)
- Numeri con separatore migliaia punto (es. `"1.850"`)
- 15 unit tests, 93% coverage

### Infrastructure Layer

#### AudioManager (`src/infrastructure/audio/audio_manager.py`) (v3.4.0)

Orchestratore principale del sistema audio. Riceve `AudioEvent` dai controller Application, consulta `SoundCache`, calcola panning, delega la riproduzione a `SoundMixer`. Gestisce ciclo di vita, pause, resume, shutdown, salvataggio settings.

- **Config JSON-driven:** a partire da v3.5.0 la mappatura evento→file è
  definita in `config/audio_config.json` sotto la chiave `event_sounds`.
  Questo rende il sistema facilmente riconfigurabile senza toccare codice.

**Ruolo architetturale:**
- Unico punto di ingresso per la riproduzione audio
- Gestione mapping evento→bus, varianti, fallback, logging
- Policy bus: Ambient/Music sospesi in pausa, one-shot sempre attivi
- Salvataggio settings persistente in JSON

**Cross-reference:**
- [docs/API.md](docs/API.md): dettagli API pubblica, metodi, signature
- [CHANGELOG.md](CHANGELOG.md): voce Added AudioManager orchestratore audio

### Presentation Layer
- `SolitarioFrame` (main window) ora si binda su `wx.EVT_ACTIVATE` per
  mettere in pausa/riprendere automaticamente i loop ambient e musicali
  attraverso l'`AudioManager`. Questa logica assicura che l'audio non continui
  a suonare quando il giocatore cambia applicazione.
- Il controller principale (`SolitarioController.run`) avvia un evento
  `AMBIENT_LOOP` immediatamente dopo l'inizializzazione dell'`AudioManager`,
  permettendo l'audio ambientale di partire non appena l'app è pronta.

---
#### Logging Categorizzato (`src/infrastructure/logging/`) (v3.5.0)

Sistema di logging multi-file categorizzato in stile Paradox Interactive.
Sostituisce il monolite `solitario.log` con file dedicati per categoria.

**Strategia**: Multi-handler su named loggers Python esistenti. Il routing è
nativo del modulo `logging` — `setup_categorized_logging()` aggiunge solo
i `RotatingFileHandler` dedicati a ciascun logger.

```
acs_wx.py
  └─ setup_logging()  [logger_setup.py — thin wrapper backward-compat]
       └─ setup_categorized_logging()  [categorized_logger.py]
            ├─ logging.getLogger('game')  → logs/game_logic.log   (partita, mosse)
            ├─ logging.getLogger('ui')    → logs/ui_events.log    (UI, dialogs, TTS)
            ├─ logging.getLogger('error') → logs/errors.log       (errori, warnings)
            ├─ logging.getLogger('timer') → logs/timer.log        (lifecycle timer)
            └─ root logger               → logs/solitario.log    (wx, PIL, urllib3)
```

**Proprietà di ogni handler:**
- `RotatingFileHandler`: 5 MB max, 3 backup (`.log.1` / `.log.2` / `.log.3`)
- `propagate = False`: evita duplicazione su `solitario.log`
- Flush immediato (affidabilità in caso di crash)
- Guard anti-doppia-registrazione (`if logger.handlers: continue`)

**Helper semantici (`game_logger.py`):**
```python
from src.infrastructure.logging import game_logger as log

log.game_won(elapsed_time=120, moves_count=45, score=850)   # → game_logic.log
log.panel_switched("menu", "gameplay")                       # → ui_events.log
log.timer_expired()                                          # → timer.log
log.error_occurred("FileIO", "Profile corrupted", exc)      # → errors.log
```

**Estendibilità futura:** decommentare entry in `CATEGORIES` dict + aggiungere
named logger in `game_logger.py`. Zero altre modifiche necessarie.

*Ref: `docs/2 - projects/DESIGN_categorized_logging.md`*

---

#### DIContainer (`src/infrastructure/di_container.py`)

Container per dependency injection.

```python
class DIContainer:
    def get_game_controller() -> GameController: ...
    def get_game_service() -> GameService: ...
    def get_formatter() -> GameFormatter: ...
    def get_profile_service() -> ProfileService: ...
```

## 🔄 Flussi dei Dati

### Nuova Partita

```
User Input
    │
    ▼
GameController.start_new_game()
    │
    ▼
GameService.new_game()
    │
    ▼
Create immutable GameState
    │
    ▼
GameFormatter.format_game_state()
    │
    ▼
Screen Reader Output
```

### Esecuzione Mossa

```
User Input (action)
    │
    ▼
GameController.execute_move()
    │
    ▼
MoveValidator.validate()
    │
    ├── Invalid → Return error message
    │
    └── Valid ─────┐
                   ▼
          GameService.execute()
                   │
                   ▼
          New GameState (immutable)
                   │
                   ▼
          GameFormatter.format_result()
                   │
                   ▼
          Screen Reader Output
```

### Session Recording (v3.0.0)

```
GameEngine.end_game(EndReason)
    │
    ▼
SessionOutcome.create_new(...)
    │
    ▼
ProfileService.record_session(outcome)
    │
    ▼
StatsAggregator.update_all_stats(...)
    │
    ├─→ GlobalStats (games, victories, winrate)
    ├─→ TimerStats (timer games, timeouts)
    ├─→ DifficultyStats (per-level breakdown)
    └─→ ScoringStats (avg scores, deck usage)
    │
    ▼
ProfileStorage.save_profile() [atomic write]
    │
    ▼
Recent sessions cache updated (FIFO 50)
```

### Stats Presentation (v3.1.0)

```
User presses "U" (Last Game)
    │
    ▼
acs_wx.show_last_game_summary()
    │
    ▼
ProfileService.active_profile.recent_sessions[-1]
    │
    ▼
StatsFormatter.format_session_outcome(last_session)
    │
    ▼
LastGameDialog(formatted_text)
    │
    ▼
NVDA reads dialog content
    │
    ▼
ESC returns to main menu
```

### Profile Operations (v3.1.0)

```
User clicks "Gestione Profili"
    │
    ▼
ProfileMenuPanel.ShowModal()
    │
    ├─→ Button 1: Create Profile
    │   ├─→ Input validation (empty, length, duplicates)
    │   ├─→ ProfileService.create_profile(name)
    │   ├─→ ProfileService.load_profile(new_id)
    │   └─→ TTS: "Profilo creato: {name}. Attivo."
    │
    ├─→ Button 2: Switch Profile
    │   ├─→ Choice dialog with stats preview
    │   ├─→ ProfileService.save_active_profile()
    │   ├─→ ProfileService.load_profile(selected_id)
    │   └─→ TTS: "Profilo attivo: {name}"
    │
    ├─→ Button 3: Rename Profile
    │   ├─→ Input validation + guest protection
    │   ├─→ active_profile.profile_name = new_name
    │   ├─→ ProfileService.save_active_profile()
    │   └─→ TTS: "Profilo rinominato: {new_name}"
    │
    ├─→ Button 4: Delete Profile
    │   ├─→ Safeguards (guest block, last profile block)
    │   ├─→ ProfileService.delete_profile(id)
    │   ├─→ ProfileService.load_profile("profile_000")
    │   └─→ TTS: "Profilo eliminato. Profilo attivo: Ospite."
    │
    ├─→ Button 5: View Detailed Stats ⭐
    │   ├─→ DetailedStatsDialog(profile, formatter)
    │   ├─→ 3 pages (Global, Timer, Difficulty/Scoring)
    │   ├─→ PageUp/PageDown navigation
    │   └─→ ESC returns to ProfileMenuPanel
    │
    └─→ Button 6: Set Default Profile
        ├─→ active_profile.is_default = True
        ├─→ ProfileService.save_active_profile()
        └─→ TTS: "Profilo predefinito: {name}"
```

## 🎨 Design Patterns

### 1. Immutable State Pattern

Lo stato del gioco è immutabile. Ogni modifica crea un nuovo oggetto.

```python
# Invece di modificare lo stato esistente
state.score += 10  # ❌ Non funziona

# Si crea un nuovo stato
new_state = state.with_move(score=state.score + 10)  # ✅
```

**Vantaggi:**
- Thread safety
- Facilita undo/redo
- Debugging più semplice
- Nessun side effect

### 2. Command Pattern

Ogni azione è incapsulata in un oggetto Command.

```python
command = MoveCommand(source="tableau_0", target="foundation_0")
history.execute(command, state)
history.undo(state)  # Annulla
history.redo(state)  # Ripristina
```

**Vantaggi:**
- Undo/redo naturale
- Logging delle azioni
- Macro commands

### 3. Dependency Injection

Le dipendenze sono iniettate tramite container.

```python
container = DIContainer()
controller = container.get_game_controller()
```

**Vantaggi:**
- Testabilità (mock injection)
- Loose coupling
- Configurabilità

### 4. Protocol Interfaces

Definizione di interfacce tramite Python Protocol.

```python
class MoveValidatorProtocol(Protocol):
    def can_move_to_foundation(self, card, index, state) -> bool: ...
```

**Vantaggi:**
- Structural typing
- Nessuna ereditarietà richiesta
- Type checking statico

## 📊 Metriche di Qualità (v3.5.0)

| Metrica | Target | Attuale | Stato |
|---------|--------|---------|-------|
| **Test Coverage (Domain)** | ≥ 95% | 96%+ | ✅ |
| **Test Coverage (Application)** | ≥ 85% | 87%+ | ✅ |
| **Test Coverage (Infrastructure)** | ≥ 70% | 72%+ | ✅ |
| **Test Coverage (Total)** | **≥ 88%** | **88.2%** | **✅** |
| **Type Hints** | 100% | 100% | ✅ |
| **Complessità Ciclomatica** | < 10 | ≤ 8 | ✅ |
| **Linee per Metodo** | < 20 | ≤ 18 | ✅ |
| **Import Errors (Tests)** | 0 | 0 | ✅ |
| **Legacy Test Health** | N/A | Archived | ✅ |

### Test Suite Health Evolution

| Version | Total Tests | Import Errors | Coverage | Status |
|---------|-------------|---------------|----------|--------|
| v3.1.2 | ~780 | 17 | ~75% | ⚠️ Degraded |
| v3.5.0 | **790+** | **0** | **88.2%** | **✅ Healthy** |

**v3.5.0 Improvements:**
- ✅ **+10 integration tests** (`test_profile_game_integration.py`)
- ✅ **0 import errors** (17 resolved)
- ✅ **+13.2% coverage** (75% → 88.2%)
- ✅ **3 legacy tests archived** (with documentation)
- ✅ **Test modernization complete** (Clean Architecture aligned)

**v3.5.0 Improvements:**
- ✅ **`@pytest.mark.gui` marker** — isolates wxPython-dependent tests
- ✅ **CI-safe command**: `pytest -m "not gui"` skips ~50 GUI tests
- ✅ **[docs/TESTING.md](TESTING.md)** — comprehensive test guide

### Test Organization Strategy (v3.5.0)

```
tests/
├── unit/               # Isolated unit tests (domain/application/presentation)
│   ├── domain/        # 95%+ coverage - pure business logic
│   ├── application/   # 85%+ coverage - use cases
│   └── presentation/  # 70%+ coverage - formatting/dialogs
│
├── integration/        # Cross-layer integration tests
│   └── test_profile_game_integration.py  # 10 tests ProfileService+GameEngine
│       ├── test_game_victory_updates_profile_stats
│       ├── test_game_abandon_updates_profile_stats
│       ├── test_game_timeout_updates_profile_stats
│       ├── test_multiple_sessions_aggregate_correctly
│       ├── test_victory_overtime_classification
│       ├── test_end_reason_coverage
│       ├── test_timer_mode_tracking
│       ├── test_difficulty_stats_tracking
│       ├── test_scoring_stats_tracking
│       └── test_session_history_limit
│
└── archive/            # Archived legacy tests (preserved for reference)
    ├── README.md      # Archival rationale + replacement coverage mapping
    └── scr/           # 3 legacy monolithic tests (pre-Clean Architecture)
        ├── test_distribuisci_carte_deck_switching.py  # Deck switching logic
        ├── test_game_engine_f3_f5.py                  # Timer F3/F5 adjustments
        └── test_king_to_empty_base_pile.py            # King placement rules
```

**Archival Rationale** (v3.5.0):
- Legacy `scr/` tests obsoleted by Clean Architecture migration
- Functionality **fully covered** by new integration tests
- Files **preserved** (not deleted) with Git history intact
- `tests/archive/scr/README.md` documents replacement coverage mapping

**Coverage Mapping** (Legacy → Modern):

| Legacy Test | Replacement Coverage | Modern Test |
|-------------|----------------------|-------------|
| `test_distribuisci_carte_deck_switching.py` | Deck distribution logic | `test_game_service.py` (unit) |
| `test_game_engine_f3_f5.py` | Timer adjustment UI | `test_timer_manager.py` (unit) |
| `test_king_to_empty_base_pile.py` | King placement rules | `test_solitaire_rules.py` (unit) |

## 🔒 Principi SOLID

### Single Responsibility
- `GameFormatter`: solo formattazione
- `MoveValidator`: solo validazione
- `GameService`: solo orchestrazione
- `StatsFormatter`: solo formattazione statistiche (v3.1.0)
- `ProfileMenuPanel`: solo gestione UI profili (v3.1.0)

### Open/Closed
- Nuove regole aggiungibili senza modificare codice esistente
- Nuovi formatter possono essere creati
- Nuovi dialog statistiche estendibili (v3.1.0)

### Liskov Substitution
- Tutti i Command sono intercambiabili
- Validator può essere sostituito

### Interface Segregation
- Protocol separati per ogni responsabilità
- Client dipendono solo dalle interfacce necessarie

### Dependency Inversion
- Domain non dipende da Infrastructure
- Controller dipende da astrazioni (Protocol)
- ProfileService injected in GameEngine (v3.0.0)

## 🎯 Deferred UI Transitions Pattern (v2.1)

### Overview

A critical architectural pattern for handling UI panel transitions in wxPython
applications. Ensures safe, crash-free transitions by deferring UI operations
until after event handlers complete.

### Problem Statement

Direct UI transitions from event handlers can cause:
- **Nested event loops**: wxPython processes events during UI operations
- **AssertionError**: `wx.GetApp()` returns None during certain lifecycle states
- **RuntimeError**: `wxYield called recursively` when SafeYield used improperly
- **Crashes/hangs**: Unpredictable behavior from synchronous UI manipulation

### Solution: self.app.CallAfter() Pattern

Use the wx.App instance method `CallAfter()` to defer UI transitions:

```python
# ✅ CORRECT: Deferred UI transition
def on_esc_pressed(self):
    """Event handler for ESC key."""
    result = self.show_dialog()
    if result:
        # Schedule UI transition for AFTER handler completes
        self.app.CallAfter(self._safe_return_to_menu)
    # Handler returns immediately

def _safe_return_to_menu(self):
    """Deferred callback - runs AFTER event handler completes."""
    # Safe context: no nested event loop
    self.view_manager.show_panel('menu')
    self.engine.reset_game()
```

### Pattern Flow

```
1. User Action → Event Handler
                    ↓
2. Event Handler → Dialog (modal, blocking)
                    ↓
3. User Confirms → self.app.CallAfter(deferred_method)
                    ↓
4. Handler Returns → Event processing completes
                    ↓
5. [wxPython Idle Loop]
                    ↓
6. Deferred Method → Panel swap, state reset
                    ↓
7. UI Updates Complete → Safe, no nested loops
```

### Why self.app.CallAfter() Works

1. **Direct Instance Method**: No `wx.GetApp()` global lookup needed
2. **Always Available**: `self.app` assigned before MainLoop starts
3. **No Timing Issues**: Python object always exists (not C++ dependent)
4. **Deferred Execution**: Runs in wxPython idle loop, safe context
5. **No Nested Loops**: Event handler completes before UI operations

### Anti-Patterns to AVOID

#### ❌ Anti-Pattern 1: wx.CallAfter()
```python
# WRONG: Global function, depends on wx.GetApp() timing
wx.CallAfter(self._safe_return_to_menu)
# May fail with: AssertionError: No wx.App created yet
```

**Problem**: `wx.CallAfter()` internally calls `wx.GetApp()` which may return
None during app initialization or certain lifecycle transitions.

#### ❌ Anti-Pattern 2: wx.SafeYield()
```python
# WRONG: Creates nested event loop
def show_panel(self, name):
    wx.SafeYield()  # Forces event processing
    panel.Hide()
    panel.Show()
# Causes: RuntimeError: wxYield called recursively
```

**Problem**: When called from deferred callback, creates second nested event
loop. wxPython detects recursion and raises RuntimeError.

#### ❌ Anti-Pattern 3: Direct Panel Swap from Handler
```python
# WRONG: Synchronous UI manipulation in event handler
def on_esc_pressed(self):
    result = self.show_dialog()
    if result:
        self.view_manager.show_panel('menu')  # Direct call
        self.engine.reset_game()
# Risk: Nested loops, timing issues, crashes
```

**Problem**: UI operations during event handling can trigger nested event
loops or access UI state at unsafe times.

### Decision Tree: When to Use Pattern

```
Is this a UI transition? (panel swap, dialog, etc.)
    ├─ NO → Direct call OK
    │       Example: Pure logic, calculations, validation
    │
    └─ YES → Check calling context
            ├─ Event handler (keyboard, timer, callback)
            │   └─ Use self.app.CallAfter(deferred_method)
            │
            ├─ Deferred callback (already in CallAfter context)
            │   └─ Direct call OK (safe context)
            │
            └─ Initialization (run(), on_init())
                └─ Direct call OK (before MainLoop starts)
```

### Implementation Guidelines

#### 1. Separate Event Handlers from Deferred Callbacks

```python
# Event Handler: Shows dialog, schedules defer
def show_abandon_game_dialog(self):
    """Handle ESC key - show dialog and defer transition."""
    result = self.dialog_manager.show_abandon_game_prompt()
    if result:
        self.app.CallAfter(self._safe_abandon_to_menu)

# Deferred Callback: Performs UI transition
def _safe_abandon_to_menu(self):
    """Deferred handler - safe panel transition."""
    self.view_manager.show_panel('menu')
    self.engine.reset_game()
```

#### 2. Name Deferred Callbacks Clearly

Use prefixes to indicate deferred execution:
- `_safe_*`: Deferred UI transition methods
- `_deferred_*`: General deferred operations
- `_on_*`: Event handlers (not deferred)

#### 3. Document Pattern in Docstrings

```python
def _safe_abandon_to_menu(self):
    """Deferred handler for abandon → menu transition.
    
    Called via self.app.CallAfter() from show_abandon_game_dialog().
    Executes AFTER event handler completes, preventing nested loops.
    
    IMPORTANT: Do NOT call directly from event handlers.
    Always use self.app.CallAfter(self._safe_abandon_to_menu).
    
    Version:
        v2.0.9: Uses self.app.CallAfter() pattern
        v2.1: Architectural integration and documentation
    """
```

### Version History

| Version | Change | Impact |
|---------|--------|--------|
| v2.0.3 | Added wx.SafeYield() | ❌ Caused crashes (nested loops) |
| v2.0.4 | Introduced wx.CallAfter() | ⚠️ Timing issues (wx.GetApp()) |
| v2.0.6 | Tried self.frame.CallAfter() | ❌ Version incompatibility |
| v2.0.7 | Reverted to wx.CallAfter() | ⚠️ Still had timing issues |
| v2.0.8 | Removed wx.SafeYield() | ✅ Fixed nested loop crash |
| v2.0.9 | **DEFINITIVE**: self.app.CallAfter() | ✅ Reliable, works always |
| v2.1 | Systematic integration | ✅ Complete architectural pattern |

### Current Implementation Status (v2.1)

#### ✅ test.py (Presentation Layer)
- 4/4 UI transitions use `self.app.CallAfter()`
- Pattern compliance: 100%
- All deferred methods documented

#### ✅ view_manager.py (Infrastructure Layer)
- No wx.SafeYield() (removed v2.0.8)
- Synchronous Hide/Show operations
- Safe for deferred callback context

#### ✅ Application Layer
- Zero instances of CallAfter (correct)
- Clean Architecture separation
- Business logic framework-independent

### Testing Validation

Manual testing scenarios for pattern verification:

#### Test 1: ESC Abandon Game
```
Steps:
1. Start game (Nuova Partita)
2. Press ESC during gameplay
3. Confirm "Sì" to abandon

Expected:
✅ Menu appears instantly
✅ No crash or hang
✅ Console: "Scheduling deferred transition" → "Executing deferred..."
✅ Game state reset properly
```

#### Test 2: Victory Decline Rematch
```
Steps:
1. Complete game (win)
2. Victory dialog appears
3. Click "No" to decline rematch

Expected:
✅ Menu appears instantly
✅ No crash or hang
✅ Smooth transition without flicker
```

#### Test 3: Timer STRICT Expiration
```
Steps:
1. Enable timer STRICT mode (if available)
2. Let timer expire during gameplay
3. Automatic transition to menu

Expected:
✅ Menu appears after timeout message
✅ No crash or hang
✅ Deferred callback executes correctly
```

### References

- **wxPython wx.App.CallAfter()**: Instance method, always available
- **wxPython wx.CallAfter()**: Global function, depends on wx.GetApp()
- **Pattern Documentation**: `docs/IMPLEMENTATION_TIMER_STRICT_MODE_SYSTEM_v2.1.md`
- **Audit Reports**: `docs/AUDIT_CALLAFTER_PATTERNS_v2.1.md`

### Summary

The Deferred UI Transitions Pattern is a critical architectural component
that ensures:
- ✅ Crash-free panel transitions
- ✅ No nested event loops
- ✅ Reliable timing (no wx.GetApp() dependency)
- ✅ Clean separation of event handling and UI operations
- ✅ Maintainable, documented codebase

**Always use `self.app.CallAfter()` for UI transitions from event handlers.**

---

## 👤 Profile System v3.0.0 (Backend)

### Panoramica

Il Profile System introduce gestione profili utente con:
- Persistenza JSON atomica (no corruzione su crash)
- Statistiche aggregate (globali, timer, difficoltà, scoring)
- Session tracking e recovery da dirty shutdown
- Clean Architecture con separazione layer

### Architecture Layers

#### Domain Layer

**Models:**
- `UserProfile`: Identità profilo con preferenze
- `SessionOutcome`: Snapshot immutabile partita completata
- `GlobalStats`, `TimerStats`, `DifficultyStats`, `ScoringStats`: Aggregati statistici

**Services:**
- `ProfileService`: CRUD profili + session recording + aggregazione stats
- `SessionTracker`: Rilevamento sessioni orfane (crash recovery)
- `StatsAggregator`: Logica aggregazione incrementale statistiche

#### Infrastructure Layer

**Storage:**
- `ProfileStorage`: Persistence JSON con atomic writes (temp-file-rename)
- `SessionStorage`: Tracking sessione attiva per crash detection

**DI Container:**
- Factory methods singleton per `ProfileService`, `ProfileStorage`

### Data Flow

#### Session Recording

```
GameEngine.end_game()
  ↓
SessionOutcome.create_new(end_reason=EndReason.VICTORY, ...)
  ↓
ProfileService.record_session(outcome)
  ↓
StatsAggregator.update_all_stats(session, global_stats, timer_stats, ...)
  ↓
ProfileStorage.save_profile(...) [atomic write]
  ↓
Recent sessions cache updated (FIFO 50 limit)
```

#### Crash Recovery

```
App Startup
  ↓
SessionTracker.get_orphaned_sessions()
  ↓
If orphaned sessions found:
  ↓
For each orphaned session:
  ↓
SessionOutcome.create_new(end_reason=EndReason.ABANDON_APP_CLOSE, ...)
  ↓
ProfileService.record_session(outcome) [counted as defeat]
  ↓
SessionTracker.mark_recovered(session_id) [prevent duplicate recovery]
```

### Storage Paths

```
~/.solitario/
├── profiles/
│   ├── profiles_index.json          # Lightweight profile list
│   ├── profile_a1b2c3d4.json       # Full profile + aggregates + recent sessions
│   └── profile_000.json             # Guest profile (non-deletable)
└── .sessions/
    └── active_session.json          # Current active session for crash detection
```

### Data Integrity

**Atomic Writes:**
```python
def _atomic_write_json(path: Path, data: dict):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=2))
    temp.rename(path)  # Atomic on POSIX - no partial writes
```

**Guest Profile Protection:**
- `profile_000` cannot be deleted (raises `ValueError`)
- Always available for users without account

**Session Validation:**
- SessionOutcome validated before aggregation
- Corrupted JSON handled gracefully (fallback to empty state)

**Recent Sessions Cache:**
- Kept in memory + profile JSON (last 50 sessions)
- FIFO eviction policy
- Reduces full session history reads

### Integration Points

**GameEngine Activation (v3.0.0 - Completed):**
```python
def end_game(self, end_reason: Union[EndReason, bool]) -> None:
    # ... game logic ...
    
    # ProfileService integration ACTIVE ✅
    if self.profile_service and self.profile_service.active_profile:
        session_outcome = self._build_session_outcome(end_reason)
        self.profile_service.record_session(session_outcome)
        self.last_session_outcome = session_outcome  # For UI (v3.1.0)
```

**DI Container:**
```python
# Singleton factories
profile_storage = container.get_profile_storage()  # ProfileStorage instance
profile_service = container.get_profile_service()  # ProfileService instance (uses storage + aggregator)
```

---

## 📊 Stats Presentation v3.1.0 (UI Layer)

### Panoramica

Il layer di presentazione statistiche introduce:
- 5 dialog nativi wxPython per visualizzazione stats
- ProfileMenuPanel (gestione profili modal con 6 operazioni)
- StatsFormatter (metodi summary/detailed per diverse pagine)
- Integrazione menu principale (U, L, Gestione Profili)
- Accessibilità NVDA completa

### Architecture Components

#### Presentation Layer: StatsFormatter

**Responsabilità**: Formattazione statistiche localizzate italiano NVDA-optimized.

**Metodi Principali** (vedi sezione Presentation Layer sopra per lista completa)

**Test Coverage**: 15 unit tests, 93% coverage

#### Presentation Layer: Dialogs

**1. VictoryDialog**
- **Trigger**: Fine partita vinta (EndReason.VICTORY o VICTORY_OVERTIME)
- **Content**:
  - Session outcome (formatted via StatsFormatter)
  - Profile summary (vittorie totali, winrate)
  - New records detection (best time, best score)
- **Actions**: Rematch (Yes/No)
- **NVDA**: TTS announcements per outcome + records

**2. AbandonDialog**
- **Trigger**: Fine partita abbandonata (ABANDON_*, TIMEOUT_STRICT)
- **Content**:
  - EndReason classification
  - Impact su statistiche
- **Actions**: Return to menu (OK)
- **NVDA**: EndReason leggibile con descrizione impatto

**3. GameInfoDialog**
- **Trigger**: Tasto **I** durante gameplay
- **Content**:
  - Progresso partita corrente (tempo, mosse, score)
  - Riepilogo profilo real-time
- **Actions**: Continue game (OK)
- **NVDA**: Non blocca gameplay, focus return garantito

**4. DetailedStatsDialog**
- **Trigger**: ProfileMenuPanel button 5 o menu "U - Ultima Partita"
- **Content**: 3 pagine navigabili
  - **Pagina 1**: Global stats (partite, winrate, best time/score, avg moves)
  - **Pagina 2**: Timer stats (timer games, timeouts, overtime, avg time)
  - **Pagina 3**: Difficulty/Scoring stats (breakdown per livello, deck usage)
- **Navigation**: PageUp/PageDown
- **Actions**: ESC close (context-aware: ProfileMenuPanel vs main menu)
- **NVDA**: Page transitions announced ("Pagina 2 di 3: Statistiche Timer")

**5. LeaderboardDialog**
- **Trigger**: Menu "L - Leaderboard Globale"
- **Content**: Top 10 giocatori in 5 categorie
  - Fastest victory (sort by time)
  - Best winrate (sort by %)
  - Highest score (sort by points)
  - Most games played (sort by total)
  - Best timed victory (timer-only games)
- **Actions**: ESC close
- **NVDA**: Rankings announced con player names + stats

**6. LastGameDialog**
- **Trigger**: Menu "U - Ultima Partita"
- **Content**:
  - Session outcome (last completed game)
  - Profile summary snapshot
- **Actions**: ESC close
- **NVDA**: Read-only summary ottimizzato

#### Infrastructure Layer: ProfileMenuPanel

**Modal Dialog** (267 lines) con 6 operazioni complete:

**Architecture Pattern**: Single-responsibility buttons → validation → ProfileService call → real-time UI update

```
ProfileMenuPanel (wx.Dialog, modal)
  ├─ Button 1: Create Profile
  │   └─→ _on_create_profile()
  │       ├─ Input dialog (name validation)
  │       ├─ ProfileService.create_profile(name)
  │       ├─ ProfileService.load_profile(new_id)
  │       ├─ _update_ui() [refresh labels]
  │       └─ TTS: "Profilo creato: {name}. Attivo."
  │
  ├─ Button 2: Switch Profile
  │   └─→ _on_switch_profile()
  │       ├─ Choice dialog (list all profiles with stats)
  │       ├─ ProfileService.save_active_profile()
  │       ├─ ProfileService.load_profile(selected_id)
  │       ├─ _update_ui()
  │       └─ TTS: "Profilo attivo: {name}"
  │
  ├─ Button 3: Rename Profile
  │   └─→ _on_rename_profile()
  │       ├─ Input dialog (pre-filled, validation)
  │       ├─ active_profile.profile_name = new_name
  │       ├─ ProfileService.save_active_profile()
  │       ├─ _update_ui()
  │       └─ TTS: "Profilo rinominato: {new_name}"
  │
  ├─ Button 4: Delete Profile
  │   └─→ _on_delete_profile()
  │       ├─ Confirmation dialog
  │       ├─ Safeguards (guest block, last profile block)
  │       ├─ ProfileService.delete_profile(id)
  │       ├─ ProfileService.load_profile("profile_000")
  │       ├─ _update_ui()
  │       └─ TTS: "Profilo eliminato. Attivo: Ospite."
  │
  ├─ Button 5: View Detailed Stats ⭐
  │   └─→ _on_view_stats()
  │       ├─ DetailedStatsDialog(profile, formatter)
  │       ├─ ShowModal() [nested modal OK wxPython]
  │       └─ ESC returns HERE (not main menu)
  │
  └─ Button 6: Set Default Profile
      └─→ _on_set_default()
          ├─ active_profile.is_default = True
          ├─ ProfileService.save_active_profile()
          ├─ _update_ui()
          └─ TTS: "Profilo predefinito: {name}"
```

**Validation & Safeguards**:

```python
# Create/Rename validation
if not name.strip():
    show_error("Nome vuoto non valido")
if len(name) > 30:
    show_error("Nome troppo lungo (max 30 caratteri)")
if name in existing_names:
    show_error("Nome già esistente")

# Delete safeguards
if profile_id == "profile_000":
    raise ValueError("Cannot delete guest profile")
if len(all_profiles) == 1:
    show_error("Impossibile eliminare ultimo profilo")
```

**UI Update Pattern**:

```python
def _update_ui(self):
    """Aggiorna labels con profilo corrente."""
    if self.profile_service.active_profile:
        name = self.profile_service.active_profile.profile_name
        self.profile_label.SetLabel(f"Profilo Attivo: {name}")
        # ... altri aggiornamenti ...
    self.Layout()  # Ricalcola sizer
```

### NVDA Accessibility Layer

**Focus Management**:
- Tutti i dialog usano `SetFocus()` su primo controllo
- ESC restores focus al chiamante
- TAB navigation standard wxPython

**TTS Announcements**:
- Dialog open: "Gestione Profili. Profilo attivo: {name}"
- Button press: "Creazione profilo..."
- Operation success: "Profilo creato: {name}. Attivo."
- Operation error: "Errore: {reason}"
- Page navigation: "Pagina 2 di 3: Statistiche Timer"

**Screen Reader Optimizations**:
- Button labels verbose ("Crea Nuovo Profilo" not "Crea")
- Error messages actionable ("Nome vuoto. Inserire nome valido.")
- Status announced after every operation
- No decorative elements that confuse NVDA

### Integration with GameEngine (v3.0.0 + v3.1.0)

**End Game Flow**:

```
GameEngine.end_game(EndReason)
  ↓
[v3.0.0] ProfileService.record_session(outcome)  ✅
  ↓
[v3.0.0] Statistics updated, profile saved  ✅
  ↓
[v3.1.0] GameEngine.last_session_outcome = outcome  ✅ NEW!
  ↓
[v3.1.0] if is_victory:
            VictoryDialog(outcome, profile, formatter).ShowModal()
         else:
            AbandonDialog(outcome, formatter).ShowModal()
  ↓
[v3.1.0] User sees stats integrated in native dialog ✅
```

**Menu Integration**:

```
MenuPanel (v3.1.0 extended to 6 buttons)
  ├─ Button 1: Nuova Partita
  ├─ Button 2: Opzioni
  ├─ Button 3: U - Ultima Partita → LastGameDialog ⭐ NEW!
  ├─ Button 4: L - Leaderboard Globale → LeaderboardDialog ⭐ NEW!
  ├─ Button 5: Gestione Profili → ProfileMenuPanel ⭐ NEW!
  └─ Button 6: Esci
```

### Data Flow Example: View Last Game

```
1. User clicks "U - Ultima Partita" in main menu
   ↓
2. acs_wx.show_last_game_summary()
   ↓
3. profile = profile_service.active_profile
   outcome = profile.recent_sessions[-1]
   ↓
4. formatter = StatsFormatter()
   text = formatter.format_session_outcome(outcome)
   summary = formatter.format_profile_summary(profile)
   ↓
5. LastGameDialog(text + summary).ShowModal()
   ↓
6. NVDA reads:
   "Ultima Partita.
    Risultato: Vittoria.
    Tempo: 3 minuti 45 secondi.
    Mosse: 87.
    Punteggio: 1850.
    
    Riepilogo Profilo:
    Vittorie Totali: 23 su 42 partite.
    Percentuale Vittorie: 54.8%."
   ↓
7. User presses ESC → Dialog closes, focus returns to menu
```

### Performance & Quality

**Implementation Time**: ~170 minutes (Copilot Agent)
- Phase 1-8 (core dialogs): ~70 min
- Phase 9 (menu integration): ~30 min
- Phase 10 (ProfileMenuPanel): ~70 min

**vs Manual Estimate**: ~10 hours → **3.5x faster**

**Code Metrics**:
- New files: 8 (StatsFormatter + 6 dialogs + ProfileMenuPanel)
- Total LOC: ~1,800 lines
- Test coverage: StatsFormatter 93% (15 tests)
- Manual NVDA testing: 40+ checklist items (required)

**Zero Technical Debt**:
- ✅ Clean Architecture respected
- ✅ Type hints 100%
- ✅ Logging integration complete
- ✅ NVDA patterns consistent
- ✅ No TODO/FIXME critical

---

*Document Version: 3.2.2*  
*Last Updated: 2026-02-20*  
*Revision: Added complete project structure hierarchy section*
