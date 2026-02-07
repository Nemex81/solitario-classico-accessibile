# ADR 003: Dependency Injection

## Status

Accepted

## Context

L'applicazione ha diverse dipendenze tra componenti:

- `GameController` dipende da `GameService` e `GameFormatter`
- `GameService` dipende da `MoveValidator`
- L'UI potrebbe dipendere da `GameController`

Problemi da risolvere:

1. Come gestire la creazione delle dipendenze?
2. Come permettere testing con mock objects?
3. Come evitare dipendenze hard-coded?

## Decision

Implementiamo un **Simple DI Container** custom:

```python
class DIContainer:
    def __init__(self):
        self._instances = {}
    
    def get_game_service(self) -> GameService:
        if 'game_service' not in self._instances:
            validator = self.get_move_validator()
            self._instances['game_service'] = GameService(validator)
        return self._instances['game_service']
    
    def get_game_controller(self) -> GameController:
        # Costruisce con dipendenze iniettate
        ...
```

### Caratteristiche

1. **Singleton by default**: Le istanze sono riusate
2. **Lazy initialization**: Creazione on-demand
3. **Type-safe**: Metodi tipizzati per ogni componente
4. **Configurabile**: Supporto per lingue diverse
5. **Resettabile**: Per testing

### Utilizzo

```python
# Applicazione
container = get_container()
controller = container.get_game_controller()

# Testing
container = DIContainer()
container._instances['validator'] = MockValidator()
service = container.get_game_service()  # Usa mock
```

## Consequences

### Positive

- **Testabilità**: Facile iniezione di mock
- **Loose coupling**: Componenti non si conoscono direttamente
- **Single source of truth**: Configurazione centralizzata
- **Flessibilità**: Facile cambiare implementazioni

### Negative

- **Service locator anti-pattern**: Il container è un registro globale
- **Hidden dependencies**: Le dipendenze non sono esplicite nel costruttore
- **Startup cost**: Inizializzazione può essere complessa

### Mitigations

1. Metodi espliciti per ogni dipendenza (type-safe)
2. Documentazione chiara delle dipendenze
3. Test che verificano il wiring corretto

## Alternatives Considered

1. **Framework DI (injector, dependency_injector)**: Scartati per semplicità
2. **Pure manual injection**: Scartato per verbosità
3. **Global singletons**: Scartato per testing difficile
4. **Factory pattern**: Considerato ma meno flessibile

## Notes

In futuro, se la complessità aumenta, potremmo considerare:
- `dependency_injector` library
- Protocol-based injection
- Scope management (request, session, singleton)
