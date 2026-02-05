# Solitario Classico Accessibile

Un'implementazione accessibile del gioco del Solitario Classico (Klondike) in Python, con supporto per screen reader e architettura modulare.

## 🎯 Caratteristiche

- **Accessibilità completa**: Supporto screen reader con output vocale
- **Architettura modulare**: Design Domain-Driven con separazione dei layer
- **Type-safe**: Type hints completi con verifica mypy strict
- **Test completi**: 140+ test con coverage >92%
- **Mazzi multipli**: Supporto per mazzi francesi e napoletani
- **Pattern moderni**: Dependency Injection, Command Pattern per undo/redo

## 📦 Installazione

### Requisiti

- Python 3.11 o superiore
- pip

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

### Avvio del gioco

```bash
python acs.py
```

### Utilizzo programmatico

```python
from src.infrastructure.di_container import DIContainer

# Inizializza il container DI
container = DIContainer()

# Ottieni il controller di gioco
controller = container.get_game_controller()

# Inizia una nuova partita
formatted_state = controller.start_new_game()
print(formatted_state)

# Esegui mosse
success, message = controller.execute_move("draw")
print(message)
```

## 🏗️ Architettura

Il progetto segue un'architettura a strati (layered architecture) con principi Domain-Driven Design.

Per maggiori dettagli, consulta [ARCHITECTURE.md](ARCHITECTURE.md).

## 🧪 Testing

```bash
# Esegui tutti i test
pytest

# Test con coverage
pytest --cov=src --cov-report=term-missing
```

## 📚 Documentazione

- [ARCHITECTURE.md](ARCHITECTURE.md) - Dettagli architetturali
- [API.md](API.md) - Documentazione API
- [ADR/](ADR/) - Architecture Decision Records

## 📞 Contatti

Repository: [https://github.com/Nemex81/solitario-classico-accessibile](https://github.com/Nemex81/solitario-classico-accessibile)
