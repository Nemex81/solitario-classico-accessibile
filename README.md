# Solitario Classico Accessibile

Un gioco di carte Solitario (Klondike) in versione accessibile per non vedenti, sviluppato in Python con supporto per screen reader.

## 🎯 Caratteristiche

- **Accessibilità completa**: Supporto per screen reader con output testuale dettagliato
- **Navigazione intuitiva**: Sistema di cursore per navigare tra le pile di carte
- **Feedback vocale**: Descrizioni in italiano di ogni azione e stato del gioco
- **Due mazzi supportati**: 
  - **Mazzo francese** (♥♦♣♠) - 52 carte: Asso, 2-10, Jack, Regina, Re per ogni seme
  - **Mazzo napoletano** (🍷🪙🗡️🏑) - 40 carte autentiche: Asso, 2-7, Regina (8), Cavallo (9), Re (10) per ogni seme
- **Undo/Redo**: Possibilità di annullare e ripetere le mosse
- **Architettura modulare**: Design pulito con separazione dei livelli (Clean Architecture)

## 📦 Installazione

### Prerequisiti

- Python 3.11 o superiore
- pip (gestore pacchetti Python)
- PyGame (per interfaccia audiogame)

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

## 🚀 Avvio

### ✨ Versione Clean Architecture (Consigliata)

```bash
python test.py
```

**Caratteristiche**:
- ✅ Architettura Clean completa (`src/` modules)
- ✅ Dependency Injection
- ✅ Testabilità elevata
- ✅ Manutenibilità ottimale
- ✅ Tutte le feature v1.3.3

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
├── src/                       # 🆕 Clean Architecture (v2.0)
│   ├── domain/               # Core business logic
│   │   ├── models/          # Card, Deck, Pile, Table
│   │   ├── rules/           # SolitaireRules, MoveValidator
│   │   └── services/        # GameService
│   ├── application/         # Use cases & orchestration
│   │   ├── input_handler.py      # Keyboard → Commands
│   │   ├── game_settings.py      # Configuration
│   │   ├── timer_manager.py      # Timer logic
│   │   └── gameplay_controller.py # Main controller
│   ├── infrastructure/      # External adapters
│   │   ├── accessibility/   # ScreenReader + TTS
│   │   ├── ui/             # PyGame Menu
│   │   └── di_container.py # Dependency Injection
│   └── presentation/        # Output formatting
│       └── game_formatter.py # Italian localization
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
    ├── REFACTORING_PLAN.md  # 13-commit plan
    ├── MIGRATION_GUIDE.md   # scr/ → src/ guide
    └── COMMITS_SUMMARY.md   # Commit log
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

#### Impostazioni (v1.3.3)
- **N**: Nuova partita
- **F1**: Cambia tipo mazzo (francese/napoletano)
- **F2**: Attiva/disattiva timer
- **F3**: Decrementa timer (-5 min)
- **F4**: Incrementa timer (+5 min)
- **F5**: Alterna modalità riciclo scarti
- **ESC**: Torna al menu principale

Per documentazione completa: Vedi sezione legacy nel README originale.

## 🃏 Mazzi di Carte

### Mazzo Francese (52 carte)
- **Semi**: Cuori (♥), Quadri (♦), Fiori (♣), Picche (♠)
- **Valori**: Asso (1), 2-10, Jack (11), Regina (12), Re (13)
- **Vittoria**: 13 carte per seme × 4 semi = 52 carte totali

### Mazzo Napoletano (40 carte)
- **Semi**: Bastoni (🏑), Coppe (🍷), Denari (🪙), Spade (🗡️)
- **Valori**: Asso (1), 2-7, Regina (8), Cavallo (9), Re (10)
- **Vittoria**: 10 carte per seme × 4 semi = 40 carte totali

**Caratteristiche**: Il gioco adatta automaticamente le regole di vittoria e la distribuzione delle carte in base al mazzo selezionato.

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

**🎉 v2.0.0-beta** - Clean Architecture implementation complete!
