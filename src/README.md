# 📦 Cartella Refactoring Archiviata

> **⚠️ ATTENZIONE**: Questa cartella è **archiviata** e non viene utilizzata nell'applicazione corrente.

## 🎯 Scopo di Questa Cartella

Questa directory contiene un tentativo di **refactoring completo** del progetto con architettura **Clean Architecture / Domain-Driven Design (DDD)** iniziato nel febbraio 2026.

## 📋 Struttura Architetturale

```
src/
├── domain/          # Logica di business pura (entità, value objects, regole)
│   ├── models/      # Card, Pile, GameState (immutabili)
│   ├── rules/       # MoveValidator con regole del solitario
│   └── services/    # GameService (orchestrazione)
├── application/     # Use cases e application services
├── infrastructure/  # Persistenza, I/O, framework esterni
└── presentation/    # UI layer (Pygame, TUI)
```

## 🛑 Stato del Progetto

- **Stato**: Archiviato / Sospeso
- **Data**: Febbraio 2026
- **Fase raggiunta**: Fase 4 completata (Domain Models + MoveValidator)
- **Coverage**: 93.63% sul domain layer
- **Motivo sospensione**: Priorità data allo sviluppo e miglioramento della versione funzionante in `scr/`

## ✅ Componenti Implementati

### Domain Layer (Completato)
- ✅ `Card` model con rank/suit enums
- ✅ `Pile` model con factory functions
- ✅ `GameState` immutabile con cursor/selection
- ✅ `MoveValidator` con 12+ regole validate
- ✅ Supporto mazzo napoletano (Suit esteso)

### In Progress
- ⏸️ GameService (orchestrazione)
- ⏸️ Application layer
- ⏸️ Infrastructure layer
- ⏸️ Presentation layer

## 📚 Documentazione di Riferimento

Per dettagli completi sul piano di refactoring:
- `REFACTORING_PLAN.md` (se presente nella root)
- Issue #3: "Correzioni Critiche e Completamento Fase 4-12"

## 🔮 Utilizzo Futuro

Questa cartella è mantenuta come:
1. **Backup di sicurezza** del lavoro di refactoring
2. **Riferimento architetturale** per future migrazioni
3. **Documentazione** delle scelte di design esplorate

Se in futuro si decidesse di riprendere la migrazione verso un'architettura più modulare, questo codice fornisce una base solida e testata da cui ripartire.

## 🚀 Versione Corrente Attiva

L'applicazione funzionante si trova in:
- **`scr/`** - Codice principale del gioco
- **`my_lib/`** - Librerie di supporto

---

**Nota**: Non modificare questa cartella. Per contribuire al progetto, lavora sulla struttura `scr/`.
