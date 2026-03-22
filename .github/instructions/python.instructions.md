---
applyTo: "**/*.py"
---

# Python Standards — Solitario Classico Accessibile

## Type Hints (Mypy strict mode REQUIRED)

- Ogni metodo pubblico con return type + parametri annotati
- `mypy src/ --strict --python-version 3.8` deve dare 0 errori
- No `Any`, no implicit returns, no `# type: ignore` senza commento

## Naming Conventions

- Variabili e funzioni: `snake_case`
- Classi: `PascalCase`
- Costanti: `UPPER_SNAKE_CASE`
- Attributi privati: prefisso `_` (es. `_handle_crash`)

## Logging semantico categorizzato

Usa SEMPRE i logger categorizzati, mai `print()` in produzione:

```python
_game_logger  = logging.getLogger('game')    # partita, mosse, stato
_ui_logger    = logging.getLogger('ui')      # navigazione, focus, eventi
_error_logger = logging.getLogger('error')   # eccezioni, fallback
_timer_logger = logging.getLogger('timer')   # lifecycle, timeout
```

Output: `logs/game_logic.log`, `logs/ui_events.log`,
        `logs/errors.log`, `logs/timer.log`

## Error Handling

RAISE Exception quando:
- Violazione contratto API (parametro None su campo non-null)
- Errore logico interno non recuperabile
- Stato inconsistente del sistema

LOG ERROR + Fallback quando:
- I/O fallisce (filesystem, network, pygame.mixer)
- Feature non critica (audio opzionale)
- Risorsa esterna non disponibile

## Clean Architecture — Regole Layer

- `src/domain/`: zero dipendenze esterne, solo entity e business rules
- `src/application/`: dipende solo da domain, use cases e game engine
- `src/infrastructure/`: implementa interfacce definite in domain
- `src/presentation/`: dipende da application, gestisce dialog e view

MAI importare da un layer superiore verso uno inferiore.

## Critical Warnings

- `profile_000` è intoccabile — è il fallback guest del sistema
- Timer: `VICTORY` = entro limite; `VICTORY_OVERTIME` = oltre (PERMISSIVE)
- `draw_count`: `GameService.draw_count` (stats) ≠ `ScoringService.stock_draw_count` (penalità)
- `Pile.count()` non esiste → usa `pile.get_card_count()`
- DI: usa SEMPRE `self.container.get_audio_manager()`, non istanziare direttamente
