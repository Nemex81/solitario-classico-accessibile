---
applyTo: "src/domain/**/*.py"
---

# Domain Layer Rules — Solitario Classico Accessibile

## Regola fondamentale

Il domain layer ha ZERO dipendenze esterne.
Non importare mai da `application`, `infrastructure`, `presentation`,
né da librerie di terze parti (pygame, wx, ecc.).

## Contenuto consentito

- Entity e value objects
- Business rules pure
- Interfacce (protocolli/ABC) che l'infrastructure implementerà
- Eccezioni di dominio custom

## Vietato

- Import da altri layer del progetto
- Import di librerie UI (wx, tkinter, ecc.)
- Import di librerie I/O (pygame, sqlite3 usato direttamente, ecc.)
- Logica di persistenza o rete

## Se hai bisogno di una dipendenza esterna nel domain

Definisci un'interfaccia (ABC o Protocol) nel domain.
L'implementazione concreta va in `src/infrastructure/`.
Il wiring avviene tramite DI Container in `src/application/`.
