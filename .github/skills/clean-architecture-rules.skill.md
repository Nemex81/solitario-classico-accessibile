---
name: clean-architecture-rules
description: >
  Regole della Clean Architecture a 4 layer adottata nel progetto.
  Richiamabile da Agent-Analyze, Agent-Design e Agent-Code per
  garantire che analisi, decisioni architetturali e implementazioni
  rispettino i vincoli di dipendenza tra layer.
---

# Skill: Clean Architecture Rules

## Layer e dipendenze consentite

```
Presentation → Application → Domain → Infrastructure
```

Ogni layer può dipendere solo dal layer immediatamente sottostante.
MAI dipendenze verso layer superiori.

## Responsabilità per layer

**Domain** (`src/domain/`):
- Zero dipendenze esterne e da altri layer del progetto
- Contiene: entity, value objects, business rules, interfacce (ABC/Protocol)
- Eccezioni di dominio custom
- Vietato: import da application, infrastructure, presentation,
  pygame, wx, sqlite3 usato direttamente

**Application** (`src/application/`):
- Dipende solo da domain
- Contiene: use cases, game engine, servizi applicativi
- Wiring delle dipendenze tramite DI Container

**Infrastructure** (`src/infrastructure/`):
- Implementa le interfacce definite nel domain
- Contiene: storage, audio, rete, accesso filesystem
- Vietato: business logic (va nel domain o application)

**Presentation** (`src/presentation/`):
- Dipende da application layer
- Contiene: dialog, view logic, event handling wxPython
- Vietato: business logic diretta, accesso diretto a infrastructure

## Regola DI Container

Usa SEMPRE `self.container.get_audio_manager()`.
Non istanziare mai dipendenze direttamente nel presentation layer.
`DIContainer` (app) ≠ `DependencyContainer` (session): non confonderli.

## Segnali di violazione da cercare

- Import cross-layer nella direzione sbagliata
- Business logic nel presentation layer
- Accesso diretto a filesystem o DB nel domain
- Istanziazione diretta di servizi infrastrutturali fuori dal container