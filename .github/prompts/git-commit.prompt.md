<!--
DISPATCHER — git-commit
Questo prompt raccoglie il contesto e delega ad Agent-Git.
Autorizzazione git ereditata da Agent-Git.
Riferimento policy: .github/instructions/git-policy.instructions.md
Riferimento skill: .github/skills/git-execution.skill.md
-->

***
mode: agent
model: gpt-5-mini
description: >
  Dispatcher per operazioni di commit. Raccoglie contesto e delega
  ad Agent-Git per l'esecuzione. Attivare con #git-commit o dal
  file picker. Indipendente dal ciclo agenti.
tools:
  - agent
***

# git-commit — Dispatcher

Sei un dispatcher leggero. Il tuo unico compito è raccogliere
il contesto necessario e delegare l'operazione ad Agent-Git.

## Esecuzione

1. Esegui `git status` per verificare che ci siano modifiche.
   Se non ci sono: termina con "Nessuna modifica rilevata."

2. Delega ad Agent-Git con questo prompt:
   "Esegui OP-2 (Commit). Contesto: operazione avviata da
   git-commit.prompt.md dall'utente."

3. Non duplicare logica già presente in Agent-Git.
   Non eseguire git direttamente in questo prompt.