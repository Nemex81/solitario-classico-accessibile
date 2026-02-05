# Solitario Classico Accessibile

Un gioco di carte Solitario (Klondike) in versione accessibile per non vedenti, sviluppato in Python con supporto per screen reader.

## 🎯 Caratteristiche

- **Accessibilità completa**: Supporto per screen reader con output testuale dettagliato
- **Navigazione intuitiva**: Sistema di cursore per navigare tra le pile di carte
- **Feedback vocale**: Descrizioni in italiano di ogni azione e stato del gioco
- **Due mazzi supportati**: Mazzo francese (♥♦♣♠) e mazzo napoletano (🍷🪙🗡️🏑)
- **Undo/Redo**: Possibilità di annullare e ripetere le mosse
- **Architettura modulare**: Design pulito con separazione dei livelli

## 📦 Installazione

### Prerequisiti

- Python 3.11 o superiore
- pip (gestore pacchetti Python)

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

## 🎮 Utilizzo

### Avvio Rapido

```python
from src.infrastructure.di_container import get_container

# Ottieni il controller tramite dependency injection
container = get_container()
controller = container.get_game_controller()

# Inizia una nuova partita
print(controller.start_new_game())

# Esegui azioni
success, message = controller.execute_move("draw")
print(message)

# Visualizza lo stato corrente
print(controller.get_current_state_formatted())
```

### Azioni Disponibili

| Azione | Descrizione |
|--------|-------------|
| `draw` | Pesca carte dal mazzo |
| `recycle` | Rimescola gli scarti nel mazzo |
| `move_to_foundation` | Sposta una carta alla base |

## 🏗️ Architettura

Il progetto segue una **Clean Architecture** con quattro livelli:

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│     (GameFormatter, Output UI)      │
├─────────────────────────────────────┤
│         Application Layer           │
│  (GameController, Commands, DI)     │
├─────────────────────────────────────┤
│           Domain Layer              │
│ (GameState, Card, Rules, Services)  │
├─────────────────────────────────────┤
│        Infrastructure Layer         │
│    (DIContainer, Accessibility)     │
└─────────────────────────────────────┘
```

Per dettagli completi sull'architettura, consulta [ARCHITECTURE.md](ARCHITECTURE.md).

## 🧪 Testing

```bash
# Esegui tutti i test
pytest tests/ -v

# Esegui test con coverage
pytest tests/ --cov=src --cov-report=term-missing

# Esegui solo test unitari
pytest tests/unit/ -v

# Esegui solo test di integrazione
pytest tests/integration/ -v
```

### Coverage Target

| Metrica | Target | Attuale |
|---------|--------|---------|
| Coverage totale | ≥ 80% | 91.47% |
| Test unitari | ≥ 90% | ✅ |
| Test integrazione | ≥ 5 | 13 |

## 📚 Documentazione

- [ARCHITECTURE.md](ARCHITECTURE.md) - Architettura del sistema
- [API.md](API.md) - Documentazione API pubblica
- [docs/ADR/](docs/ADR/) - Architecture Decision Records

## 🛠️ Sviluppo

### Strumenti

```bash
# Formattazione codice
black src/ tests/
isort src/ tests/

# Type checking
mypy src/ --strict

# Verifica complessità
radon cc src/ -a
```

### Struttura Directory

```
src/
├── application/       # Use cases e controller
│   ├── commands.py    # Pattern Command (undo/redo)
│   └── game_controller.py
├── domain/            # Logica di business
│   ├── interfaces/    # Protocol interfaces
│   ├── models/        # Entità (Card, Pile, GameState)
│   ├── rules/         # Regole di validazione
│   └── services/      # Servizi di dominio
├── infrastructure/    # Dipendenze esterne
│   └── di_container.py
└── presentation/      # Formattazione output
    └── game_formatter.py
```

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT.

## 👥 Contributi

I contributi sono benvenuti! Per favore:

1. Fai fork del repository
2. Crea un branch per la tua feature (`git checkout -b feature/nuova-feature`)
3. Committa le modifiche (`git commit -m 'Aggiungi nuova feature'`)
4. Pusha il branch (`git push origin feature/nuova-feature`)
5. Apri una Pull Request

## 📞 Contatti

- **Autore**: Nemex81
- **Repository**: [GitHub](https://github.com/Nemex81/solitario-classico-accessibile)
