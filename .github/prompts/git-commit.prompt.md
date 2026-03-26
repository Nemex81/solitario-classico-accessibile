<!--
WRAPPER AGENT — git-commit
Questo prompt raccoglie il contesto e delega ad Agent-Git per l'esecuzione.
Se Agent-Git non è disponibile, esecuzione diretta via script Python come fallback.
Parametro di modalità: richiesta inline all'utente al passo 1 (PUSH o NO).
Riferimento policy: .github/instructions/git-policy.instructions.md
Riferimento skill: .github/skills/git-execution.skill.md
-->

---
agent: agent
description: >
  Wrapper agent per operazioni di commit. Chiede se vuoi commit+push o solo
  commit. Raccoglie contesto e delega ad Agent-Git per l'esecuzione.
  Se Agent-Git non è disponibile, esegue fallback diretto via script Python.
  Attivare con #git-commit o dal file picker. Indipendente dal ciclo agenti.
---

# git-commit — Wrapper Agent

Sei un wrapper agent leggero. Il tuo unico compito è raccogliere
il contesto necessario e delegare l'operazione ad Agent-Git.
Se Agent-Git non è disponibile nel contesto VS Code corrente,
attiva un fallback configurato per eseguire lo script direttamente
via `run_in_terminal`.

## Esecuzione

1. Chiedi all'utente: "Vuoi commit + push o solo commit?"
   Attendi risposta: "PUSH" per commit+push, "NO" o vuoto per solo commit.
   - Se risposta è "PUSH" (maiuscolo): imposta modalità = COMMIT_E_PUSH
   - Altrimenti: imposta modalità = SOLO_COMMIT

2. Se modalità = SOLO_COMMIT: procedi con Agent-Git OP-2
   Se modalità = COMMIT_E_PUSH: procedi con Agent-Git OP-2 + push

   Invoca Agent-Git passando esattamente questo prompt:

   Se modalità = SOLO_COMMIT:
   ```
   Esegui OP-2 (Commit). Contesto: operazione avviata da
   git-commit.prompt.md. Modalità: SOLO_COMMIT.
   Al termine di OP-2 chiedi all'utente se vuole fare push.
   ```

   Se modalità = COMMIT_E_PUSH:
   ```
   Esegui OP-2 (Commit). Contesto: operazione avviata da
   git-commit.prompt.md. Modalità: COMMIT_E_PUSH.
   Esegui commit e push nello stesso comando tramite
   `python scripts/git_runner.py commit --message "<msg>" --push`.
   Non richiedere un secondo gate PUSH: la risposta dell'utente
   al passo 1 costituisce conferma implicita per il push.
   ```

3. Se Agent-Git è disponibile nel contesto corrente, procedi con la
   delega ai passi 2a o 2b sopra indicati.
   Se Agent-Git NON è disponibile, attiva fallback:

   Fallback — esecuzione diretta script:
   - Raccogli il contesto (branch, file modificati, file staged)
   - Genera titolo e descrizione seguendo Conventional Commit
   - Mostra riepilogo con conferma: "ok" per procedere, "annulla" per tornare
   - Se "ok": esegui direttamente via run_in_terminal
     - Se modalità SOLO_COMMIT:
       `python scripts/git_runner.py commit --message "<msg>"`
       Al termine di OP-2: chiedi all'utente "Vuoi fare push ora?"
       Se "sì": `python scripts/git_runner.py push --branch <branch_corrente>`
       Se "no": fine
     - Se modalità COMMIT_E_PUSH:
       `python scripts/git_runner.py commit --message "<msg>" --push`
   - Se "annulla": nessuna modifica, riproponi il riepilogo
   - Comunica: "Agent-Git non disponibile in questo contesto. 
     Esecuzione diretta tramite script."

4. Non duplicare logica già presente in Agent-Git.
   Fallback su script diretto preserva la policy: Agent-Git rimane il canale
   primario autorizzato, esecuzione script è il fallback condizionale.