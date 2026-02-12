# Solitario Classico Accessibile

Un gioco di carte Solitario (Klondike) in versione accessibile per non vedenti, sviluppato in Python con supporto per screen reader.

## 🎯 Caratteristiche

- **Accessibilità completa**: Supporto per screen reader con output testuale dettagliato
- **Navigazione intuitiva**: Sistema di cursore per navigare tra le pile di carte
- **Feedback vocale**: Descrizioni in italiano di ogni azione e stato del gioco
- **Due mazzi supportati**: 
  - **Mazzo francese** (♥♦♣♠) - 52 carte: Asso, 2-10, Jack, Regina, Re per ogni seme
  - **Mazzo napoletano** (🍷🪙🗡️🏑) - 40 carte autentiche: Asso, 2-7, Regina (8), Cavallo (9), Re (10) per ogni seme
- **Sistema punti completo**: Scoring system v1.5.2 con 5 livelli di difficoltà e statistiche persistenti
- **Undo/Redo**: Possibilità di annullare e ripetere le mosse
- **Architettura modulare**: Design pulito con separazione dei livelli (Clean Architecture)

### Victory Flow & Native Dialogs (v1.6.0-v1.6.1)

Il gioco ora supporta dialog box native accessibili in **tutti i contesti interattivi**.

**Contesti Dialog Nativi** (v1.6.1):
1. ✅ **Vittoria/Sconfitta**: Report finale completo + prompt rivincita
2. ✅ **ESC durante gameplay**: "Vuoi abbandonare la partita?"
3. ✅ **N durante gameplay**: "Nuova partita?" (conferma abbandono)
4. ✅ **ESC in menu di gioco**: "Vuoi tornare al menu principale?"
5. ✅ **ESC in menu principale**: "Vuoi uscire dall'applicazione?"
6. ✅ **Chiusura opzioni (modificate)**: "Salvare le modifiche?"

**Caratteristiche**:
- ✨ **Dialog native wxPython**: Accessibili a screen reader (NVDA, JAWS)
- 📊 **Statistiche complete**: Tracciamento carte per seme, semi completati, percentuale completamento
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

### ✨ Versione Clean Architecture (Consigliata) - **v2.0.0 wxPython-only**

```bash
python test.py
```

**Caratteristiche v2.0.0**:
- ✅ **wxPython-only**: Evento loop wxPython nativo (no pygame)
- ✅ Architettura Clean completa (`src/` modules)
- ✅ Dependency Injection
- ✅ Testabilità elevata
- ✅ Manutenibilità ottimale
- ✅ Tutte le feature v1.6.1
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

## 🏗️ Architettura

Il progetto segue una **Clean Architecture** (implementata in branch `refactoring-engine`) con separazione completa delle responsabilità:

```
┌─────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                      │
│         (GameFormatter - Output Formatting)              │
├─────────────────────────────────────────────────────────┤
│                  APPLICATION LAYER                       │
│    (Controllers, InputHandler, Settings, Timer)          │
├─────────────────────────────────────────────────────────┤
│                    DOMAIN LAYER                          │
│  (Models: Card/Deck/Table, Rules, Services - Pure BL)   │
├─────────────────────────────────────────────────────────┤
│                INFRASTRUCTURE LAYER                      │
│  (ScreenReader, TTS, Menu, DI Container - Adapters)     │
└─────────────────────────────────────────────────────────┘
```

### Struttura Directory

```
solitario-classico-accessibile/
├── test.py                    # ✨ Entry point Clean Architecture
├── acs.py                     # 🔧 Entry point legacy
│
├── src/                       # 🆕 Clean Architecture (v1.5.2)
│   ├── domain/               # Core business logic
│   │   ├── models/          # Card, Deck, Pile, Table, Scoring
│   │   ├── rules/           # SolitaireRules, MoveValidator
│   │   └── services/        # GameService, ScoringService
│   ├── application/         # Use cases & orchestration
│   │   ├── input_handler.py      # Keyboard → Commands
│   │   ├── game_settings.py      # Configuration
│   │   ├── timer_manager.py      # Timer logic
│   │   └── gameplay_controller.py # Main controller
│   ├── infrastructure/      # External adapters
│   │   ├── accessibility/   # ScreenReader + TTS
│   │   ├── storage/         # ScoreStorage (JSON)
│   │   ├── ui/             # PyGame Menu
│   │   └── di_container.py # Dependency Injection
│   └── presentation/        # Output formatting
│       └── formatters/      # GameFormatter, ScoreFormatter
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
    ├── IMPLEMENTATION_SCORING_SYSTEM.md  # Scoring guide
    ├── TODO_SCORING.md       # Implementation checklist
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
- **P**: Mostra punteggio corrente ✨ (v1.5.2)
- **SHIFT+P**: Ultimi 5 eventi scoring ✨ (v1.5.2)

#### Impostazioni
- **N**: Nuova partita
- **O**: Apri menu opzioni
- **F1**: Cambia tipo mazzo (francese/napoletano)
- **F2**: Attiva/disattiva timer
- **F3**: Decrementa timer (-5 min)
- **F4**: Incrementa timer (+5 min)
- **F5**: Alterna modalità riciclo scarti
- **ESC**: Torna al menu principale

## 🃏 Mazzi di Carte

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

### Moltiplicatori Difficoltà

| Livello | Nome | Moltiplicatore | Vincoli |
|---------|------|----------------|---------|
| 1 | **Facile** | 1.0x | Nessuno |
| 2 | **Medio** | 1.25x | Nessuno |
| 3 | **Difficile** | 1.5x | Nessuno |
| 4 | **Esperto** | 2.0x | Timer ≥30min, Draw ≥2, Shuffle locked |
| 5 | **Maestro** | 2.5x | Timer 15-30min, Draw=3, Shuffle locked |

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
~/.solitario/scores.json
```

**Contenuto**:
- Ultimi 100 punteggi (LRU cache)
- Best score per difficoltà
- Win rate totale
- Statistiche aggregate (media, totale partite)

**Formato JSON**:
```json
{
  "scores": [
    {
      "total_score": 1250,
      "is_victory": true,
      "difficulty_level": 3,
      "deck_type": "french",
      "elapsed_seconds": 420.5,
      "saved_at": "2026-02-11T00:30:00Z"
    }
  ]
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
- **[docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)** - Guida migrazione scr/ → src/
- **[docs/REFACTORING_PLAN.md](docs/REFACTORING_PLAN.md)** - Piano 13 commits
- **[docs/COMMITS_SUMMARY.md](docs/COMMITS_SUMMARY.md)** - Log dettagliato commits

### Scoring System (v1.5.2)
- **[docs/IMPLEMENTATION_SCORING_SYSTEM.md](docs/IMPLEMENTATION_SCORING_SYSTEM.md)** - Guida implementativa completa
- **[docs/TODO_SCORING.md](docs/TODO_SCORING.md)** - Checklist implementazione 8 fasi

### API Reference
- **[API.md](API.md)** - Documentazione API pubblica
- **[docs/ADR/](docs/ADR/)** - Architecture Decision Records

## 🔄 Stato Migrazione

**Branch corrente**: `refactoring-engine`

✅ **COMPLETA** - Tutti i 13 commit implementati (Feb 8, 2026)

| Fase | Commits | Componenti | Stato |
|------|---------|------------|-------|
| Domain | #1-4 | Models, Rules, Services | ✅ |
| Infrastructure | #5-6 | Accessibility, UI | ✅ |
| Application | #7-8 | Input, Settings, Timer | ✅ |
| Presentation | #9-10 | Formatter, Entry | ✅ |
| Integration | #11 | DI Container | ✅ |
| Testing & Docs | #12-13 | Tests, Documentation | ✅ |

**Feature Parity**: 100% con v1.3.3 legacy

Per dettagli: [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)

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

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT.

## 👥 Contatti

- **Autore**: Nemex81
- **Repository**: [GitHub](https://github.com/Nemex81/solitario-classico-accessibile)
- **Issues**: [GitHub Issues](https://github.com/Nemex81/solitario-classico-accessibile/issues)

---

**🎉 v1.5.2** - Scoring system implementation complete!
