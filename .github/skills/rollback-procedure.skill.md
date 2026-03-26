<!-- markdownlint-disable MD041 -->

---
name: rollback-procedure
description: >
  Procedura standard per gestire fallimenti dopo commit parziali nel ciclo
  E2E. Distingue tra commit già pushati (richiedono git revert) e commit
  solo locali (git reset --soft). Richiamabile da Agent-Orchestrator e
  Agent-Git quando una fase fallisce dopo che commit precedenti sono stati
  eseguiti.
---

# Skill: Rollback Procedure E2E

## Principio

Quando una fase del ciclo E2E fallisce dopo che commit parziali sono già
stati creati, il framework deve scegliere tra tre strategie:

| Situazione | Strategia |
|---|---|
| Commit già pushato su origin | `git revert <sha>` — crea un commit inverso |
| Commit solo locale (non pushato) | `git reset --soft HEAD~N` — rimuove commit senza perdere modifiche |
| Fallimento logico senza commit | Corrèggi e continua, nessun rollback necessario |

---

## Decision Tree

```
Fase X fallisce dopo commit?
│
├─ NO: corrèggi il problema e riprova la fase.
│
└─ SI: eseguito push di questi commit?
   │
   ├─ SI (commit su origin): usa git revert
   │   → Delega ad Agent-Git OP-6 (Revert)
   │   → Il commit inverso mantiene la storia intatta
   │   → Non usare mai git reset --hard su commit pushati
   │
   └─ NO (solo local): usa git reset --soft
       → Delega ad Agent-Git OP-6 (Reset soft)
       → Le modifiche tornano in staging, il commit viene rimosso
       → Poi correggi e ricrea il commit quando il problema è risolto
```

---

## Procedura per Agent-Orchestrator

Quando una fase fallisce e sono presenti commit parziali:

1. Esegui: `git log --oneline -5` tramite Agent-Git per identificare
   i commit della fase fallita.

2. Esegui: `git status` per verificare se ci sono modifiche non committate
   che potrebbero essere perse.

3. Chiedi all'utente:
   ```
   ROLLBACK RICHIESTO
   ──────────────────────────────────────────
   La fase <X> ha fallito dopo i seguenti commit:
   <sha> <messaggio>
   
   Questi commit sono stati pushati su origin? [SI / NO]
   ──────────────────────────────────────────
   ```

4. In base alla risposta:
   - Risposta "SI" (pushati): delega ad Agent-Git con OP-6 Revert
   - Risposta "NO" (solo locali): delega ad Agent-Git con OP-6 Reset soft
   - Risposta "STOP": blocca il workflow, mantieni lo stato attuale
     e chiedi istruzioni all'utente.

5. Dopo il rollback: aggiorna `docs/5 - todolist/TODO_<feature>_vX.Y.Z.md`
   rimuovendo la spunta della fase annullata.

---

## Procedura per Agent-Git (OP-6)

### Modalità Revert (commit pushato)

Richiede conferma esplicita: "REVERT" maiuscolo dall'utente.

```bash
python scripts/git_runner.py revert --sha <commit-sha>
```

Equivale a: `git revert <sha> --no-edit`

Output atteso:
```
GIT_RUNNER: REVERT OK
──────────────────────────────────────────
Creato commit di revert per <sha>: <nuovo-sha>
──────────────────────────────────────────
```

### Modalità Reset Soft (commit locale)

Richiede conferma esplicita: "RESET" maiuscolo dall'utente.
Parametro N = numero di commit da rimuovere (default: 1).

```bash
python scripts/git_runner.py reset-soft --count <N>
```

Equivale a: `git reset --soft HEAD~N`

Output atteso:
```
GIT_RUNNER: RESET_SOFT OK
──────────────────────────────────────────
Rimossi <N> commit locali. Modifiche ora in staging.
──────────────────────────────────────────
```

---

## Vincoli inviolabili

- MAI usare `git reset --hard`: perde modifiche non committate permanentemente.
- MAI eseguire revert su commit di altri collaboratori senza accordo esplicito.
- MAI usare `git reset --soft` su commit già pushati: creerebbe divergenza
  irreversibile con origin.
- Se il numero di commit da revertire è > 3, fermarsi e chiedere
  istruzioni all'utente: la situazione è complessa e potrebbe richiedere
  una strategia diversa.
