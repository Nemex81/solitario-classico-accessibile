# ADR 002: Immutable State

## Status

Accepted

## Context

Game state management is critical in a card game. Mutable state can lead to bugs, race conditions, and difficulty implementing undo/redo functionality. We needed a way to manage game state that is predictable and safe.

## Decision

We decided to make **all game state immutable** using Python's `dataclass` with `frozen=True`. All state modifications create new instances rather than mutating existing ones.

## Consequences

### Positive

- **Predictability**: State changes are explicit and traceable
- **Thread Safety**: No risk of concurrent modification
- **Undo/Redo**: Easy to implement by storing state history
- **Debugging**: State at any point can be inspected without side effects
- **Testing**: No setup/teardown needed, each test gets fresh state

### Negative

- **Memory Overhead**: Creates new objects for every change
- **Performance**: Copying large structures can be expensive

## References

- Immutable Data Structures in Python
- Functional Programming Principles
