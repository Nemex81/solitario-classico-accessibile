# ADR 001: Layered Architecture

## Status

Accepted

## Context

Il progetto Solitario Classico Accessibile necessita di un'architettura che:

1. Separi la logica di business dall'interfaccia utente
2. Permetta facile testing di ogni componente
3. Supporti future modifiche dell'UI (GUI, CLI, Web)
4. Mantenga il codice manutenibile nel tempo

## Decision

Adottiamo una **Clean Architecture** (Architettura a cipolla) con quattro layer:

1. **Domain Layer** - Core business logic
   - Models: Card, Pile, GameState
   - Rules: MoveValidator
   - Services: GameService

2. **Application Layer** - Use cases
   - GameController
   - Commands (undo/redo)

3. **Presentation Layer** - Output formatting
   - GameFormatter (accessibilità)

4. **Infrastructure Layer** - External concerns
   - DIContainer
   - Accessibility tools
   - UI implementations

### Dipendenze

Le dipendenze puntano verso l'interno:
- Infrastructure → Application → Domain
- Presentation → Domain

Il Domain Layer non dipende da nessun altro layer.

## Consequences

### Positive

- **Testabilità**: Ogni layer può essere testato in isolamento
- **Manutenibilità**: Modifiche localizzate in un solo layer
- **Flessibilità**: L'UI può essere cambiata senza toccare il domain
- **Riusabilità**: Il domain può essere riusato in altri contesti

### Negative

- **Complessità iniziale**: Più file e struttura da creare
- **Indirezione**: Il flusso dei dati attraversa più layer
- **Over-engineering potenziale**: Per progetti piccoli potrebbe essere eccessivo

## Alternatives Considered

1. **MVC tradizionale**: Scartato per il coupling più stretto
2. **Monolitico**: Scartato per difficoltà di testing
3. **Microservizi**: Scartato perché over-engineering per un gioco locale
