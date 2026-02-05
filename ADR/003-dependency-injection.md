# ADR 003: Dependency Injection Container

## Status

Accepted

## Context

Components in different layers need to depend on abstractions rather than concrete implementations. Manual dependency wiring leads to tight coupling and makes testing difficult.

## Decision

We implemented a **simple Dependency Injection (DI) Container** that manages component lifecycle and resolves dependencies automatically.

## Consequences

### Positive

- **Loose Coupling**: Components depend on abstractions, not concrete classes
- **Testability**: Easy to inject mocks and test doubles
- **Configuration**: One place to configure all dependencies

### Negative

- **Magic**: Implicit dependency resolution can be less obvious
- **Debugging**: Stack traces may be deeper

## References

- Dependency Injection Pattern
- Inversion of Control Principle
