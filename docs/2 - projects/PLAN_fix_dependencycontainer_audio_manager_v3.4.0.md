# Piano di correzione: Fix DependencyContainer.get_audio_manager

**Tipo:** Bugfix critico avvio app
**Stato:** DRAFT
**Versione target:** v3.4.0
**Data:** 2026-02-23

---

## Executive Summary

L'applicazione non si avvia a causa di un errore `AttributeError: 'DependencyContainer' object has no attribute 'get_audio_manager'` nel costruttore di `SolitarioController`. Il metodo è richiesto per la risoluzione delle dipendenze audio secondo Clean Architecture.

---

## Problema/Obiettivo

- **Problema:** Il metodo `get_audio_manager` manca in `DependencyContainer`, causando crash immediato all'avvio.
- **Obiettivo:** Implementare il metodo secondo le regole di DI, garantendo lazy loading e singleton, e assicurare la corretta iniezione nei consumer.

---

## File coinvolti

- [src/infrastructure/di/dependency_container.py] (MODIFY): aggiunta metodo `get_audio_manager` e gestione istanza singleton.
- [docs/API.md] (MODIFY): aggiunta firma pubblica se non già presente.
- [docs/TODO.md] (MODIFY): aggiornamento stato task.
- [tests/infrastructure/test_dependency_container.py] (MODIFY/CREATE): test unitario per risoluzione audio_manager.

---

## Fasi di implementazione

1. **Aggiungi metodo `get_audio_manager`** in `DependencyContainer`:
   - Lazy load, istanza singleton.
   - Caricamento config audio da file.
   - Gestione errori/logging.
2. **Aggiorna/crea test unitario** per verifica risoluzione e singleton.
3. **Aggiorna docs/API.md** con firma pubblica se necessario.
4. **Aggiorna docs/TODO.md**: spunta fase dopo ogni commit.
5. **Test end-to-end**: avvio app, verifica assenza crash.

---

## Test plan

- Test unitario: istanzia container, chiama `get_audio_manager` più volte, verifica singleton e tipo.
- Test integrazione: avvio app, verifica che venga istanziato senza errori.

---

## Criteri di completamento

- L'app si avvia senza crash.
- Test unitari e di integrazione passano.
- Documentazione aggiornata.

---

**Link design:** N/A (bugfix architetturale)

**Responsabile:** Copilot Agent
