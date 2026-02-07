# ADR 002: Immutable State

## Status

Accepted

## Context

La gestione dello stato del gioco è centrale per il funzionamento dell'applicazione. Dobbiamo decidere se lo stato debba essere:

1. **Mutabile**: Modificato in-place
2. **Immutabile**: Ogni modifica crea un nuovo oggetto

Considerazioni:
- Il gioco ha bisogno di undo/redo
- Lo stato include molte strutture dati (7 tableaus, 4 foundations, stock, waste)
- L'accessibilità richiede snapshot consistenti dello stato

## Decision

Adottiamo il pattern **Immutable State** con copy-on-write:

```python
@dataclass(frozen=True)
class GameState:
    foundations: Tuple[Tuple[str, ...], ...]
    tableaus: Tuple[Tuple[str, ...], ...]
    stock: Tuple[str, ...]
    waste: Tuple[str, ...]
    
    def with_move(self, **kwargs) -> "GameState":
        """Crea un nuovo stato con i campi modificati."""
        return GameState(
            foundations=kwargs.get('foundations', self.foundations),
            # ...altri campi
        )
```

### Implementazione

- `frozen=True` in dataclass previene modifiche accidentali
- Usiamo `Tuple` invece di `List` per le collezioni
- Il metodo `with_move()` implementa copy-on-write
- Ogni modifica restituisce un nuovo `GameState`

## Consequences

### Positive

- **Undo/Redo naturale**: Basta salvare i riferimenti agli stati precedenti
- **Thread safety**: Nessun problema di concorrenza
- **Debugging facilitato**: Lo stato non cambia sotto i piedi
- **Snapshot gratuiti**: Ogni stato è uno snapshot
- **Prevedibilità**: Nessun side effect nascosto

### Negative

- **Memory overhead**: Nuovi oggetti per ogni mossa
- **Performance**: Copia strutture dati (mitigato da structural sharing)
- **Verbosità**: Più codice per le modifiche

### Mitigations

1. Python ottimizza le tuple immutabili
2. Le stringhe delle carte sono interned
3. Structural sharing quando possibile
4. Il numero di mosse è limitato nel Klondike

## Alternatives Considered

1. **Stato mutabile con deepcopy per undo**: Scartato per complessità e bug potenziali
2. **Event sourcing**: Considerato ma over-engineering per questo caso
3. **Memento pattern tradizionale**: Scartato perché meno elegante con dataclass
