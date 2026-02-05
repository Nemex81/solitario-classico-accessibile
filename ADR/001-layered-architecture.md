# ADR 001: Layered Architecture

## Status

Accepted

## Context

The original codebase had tightly coupled components with business logic mixed with UI code and infrastructure concerns. This made the code difficult to test, maintain, and extend. We needed a clear architectural pattern to organize the code.

## Decision

We decided to implement a **layered architecture** with four distinct layers:

1. **Domain Layer**: Pure business logic with no external dependencies
2. **Application Layer**: Use case orchestration and coordination
3. **Presentation Layer**: Output formatting and display logic
4. **Infrastructure Layer**: Technical concerns (DI, UI, persistence)

Key rules:
- Each layer has clear responsibilities
- Dependencies flow in one direction (down the stack)
- Domain layer is completely independent
- Cross-layer communication through interfaces (Protocols)

## Consequences

### Positive

- **Separation of Concerns**: Each layer has a single, well-defined responsibility
- **Testability**: Layers can be tested independently with mocking
- **Maintainability**: Changes in one layer don't affect others
- **Flexibility**: Easy to swap implementations (e.g., different UI frameworks)
- **Domain Focus**: Business logic is isolated and easy to understand

### Negative

- **More Boilerplate**: Additional interfaces and abstraction layers
- **Learning Curve**: Team needs to understand layered architecture
- **Overhead**: Simple features may require changes in multiple layers

### Neutral

- **Code Organization**: More files and directories to manage
- **Type System**: Heavy use of protocols and type hints

## Alternatives Considered

1. **MVC Pattern**: Too UI-focused, doesn't separate domain well
2. **Hexagonal Architecture**: More complex, overkill for this project
3. **Flat Structure**: Original approach, led to coupling issues

## References

- Clean Architecture by Robert C. Martin
- Domain-Driven Design by Eric Evans
