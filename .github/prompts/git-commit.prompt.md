<!--
WRAPPER AGENT — git-commit
Questo prompt raccoglie il contesto e delega ad Agent-Git.
Non esegue operazioni git direttamente.
Autorizzazione git ereditata da Agent-Git.
Riferimento policy: .github/instructions/git-policy.instructions.md
Riferimento skill: .github/skills/git-execution.skill.md
Parametro opzionale: push_flag
   - lascia vuoto → solo commit (OP-2)
   - scrivi PUSH   → commit + push immediato in OP-2
-->

---
agent: agent
description: >
  Wrapper agent per operazioni di commit. Raccoglie contesto e delega
  ad Agent-Git per l'esecuzione. Parametro opzionale: inserisci
  PUSH per eseguire anche il push dopo il commit. Lascia vuoto
  per solo commit. Attivare con #git-commit o dal file picker.
  Indipendente dal ciclo agenti.
---

# git-commit — Wrapper Agent

Sei un wrapper agent leggero. Il tuo unico compito è raccogliere
il contesto necessario e delegare l'operazione ad Agent-Git.

## Input opzionale

push_flag: ${input:Parametro opzionale — lascia vuoto per solo commit, scrivi PUSH per commit + push automatico}

## Esecuzione

1. Leggi il valore di push_flag:
   - Se push_flag è vuoto o non è "PUSH": imposta modalità = SOLO_COMMIT
   - Se push_flag è esattamente "PUSH" (maiuscolo): imposta modalità = COMMIT_E_PUSH

2. Invoca Agent-Git passando esattamente questo prompt:

   Se modalità = SOLO_COMMIT:
   ```
   Esegui OP-2 (Commit). Contesto: operazione avviata da
   git-commit.prompt.md. Modalità: SOLO_COMMIT.
   Al termine di OP-2 chiedi all'utente se vuole fare push.
   ```

   Se modalità = COMMIT_E_PUSH:
   ```
   Esegui OP-2 (Commit). Contesto: operazione avviata da
   git-commit.prompt.md con parametro PUSH. Modalità: COMMIT_E_PUSH.
   Esegui commit e push nello stesso comando tramite
   `python scripts/git_runner.py commit --message "<msg>" --push`.
   Non richiedere un secondo gate PUSH: il parametro PUSH del wrapper
   costituisce conferma implicita per il push.
   ```

3. Se Agent-Git non è disponibile nel contesto corrente, INTERROMPI
   e comunica all'utente:
   "Agent-Git non disponibile. Selezionalo dal dropdown agenti e riprova."
   Non proporre comandi git manuali come fallback.

4. Non duplicare logica già presente in Agent-Git.
   Non eseguire git commit o git push direttamente in questo prompt.