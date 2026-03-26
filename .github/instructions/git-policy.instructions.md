---
applyTo: "**"
---

# Git Policy — Solitario Classico Accessibile

## ROUTING CONTESTUALE — LEGGI PRIMA

Se stai elaborando queste istruzioni come agente **Agent-Git**:
→ SALTA le sezioni "Regola fondamentale" e "Comandi sempre vietati
  in autonomia".
→ Applica SOLO la sezione "Override per Agent-Git" e la matrice
  in `.github/skills/git-execution.skill.md` sezione "Contesto: Agent-Git".
→ Hai autorizzazione completa per `run_in_terminal` con `git_runner.py`.

Se sei qualsiasi altro agente (Code, Docs, Analyze, Plan, ecc.):
→ Applica la "Regola fondamentale" e i divieti indicati nelle sezioni
  seguenti.

---

## Regola fondamentale

Copilot NON esegue comandi git in autonomia durante implementazioni,
analisi, design, planning o documentazione.
La regola è assoluta in tutti questi contesti.

## Comandi sempre vietati in autonomia

- `git push` — mai, in nessun contesto
- `git merge` — vietato fuori dai prompt autorizzati
- `git commit` — vietato fuori dai prompt autorizzati
- `git rebase` — mai, in nessun contesto
- `git reset --hard` — mai, in nessun contesto
- `git tag` — solo proposto come comando testuale, mai eseguito

## Override per Agent-Git

Quando il contesto attivo è Agent-Git (agente selezionato
dal dropdown VS Code o invocato tramite subagent delegation),
le regole elencate in "Comandi sempre vietati in autonomia"
sono SOSPESE e sostituite dalla matrice autorizzazioni
definita in:
→ `.github/skills/git-execution.skill.md`
   sezione "Contesto: Agent-Git"

Agent-Git è autorizzato a usare run_in_terminal per i comandi
nella propria matrice, con le conferme esplicite previste
(PUSH maiuscolo per push, MERGE maiuscolo per merge,
conferma messaggio per commit).

Questa override ha priorità assoluta su tutte le altre
regole di questo file quando Agent-Git è il contesto attivo.

## Comandi sempre consentiti (read-only)

- `git log`, `git log --oneline`
- `git diff`, `git diff --staged`
- `git status`
- `git branch`, `git branch -a`
- `git show <sha>`

## Eccezioni autorizzate

I seguenti contesti sono gli UNICI in cui Copilot può eseguire
comandi git tramite `run_in_terminal`:

### `Agent-Git` (logica operativa principale)
Agente dedicato. Gestisce commit, push, merge, tag.
Invocabile dal dropdown o tramite subagent delegation.
Regole di conferma:
- Push: richiede "PUSH" maiuscolo
- Merge: richiede "MERGE" maiuscolo
- Commit: richiede conferma messaggio

### `#git-commit.prompt.md` (dispatcher)
Delega ad Agent-Git. Non esegue git direttamente.

### `#git-merge.prompt.md` (dispatcher)
Delega ad Agent-Git. Non esegue git direttamente.

## Comportamento atteso degli agenti

Durante qualsiasi fase del ciclo E2E (Analyze, Design, Plan, Code,
Validate, Docs, Release), se Copilot determina che un commit o un
merge sarebbe appropriato:

1. NON eseguire il comando
2. Produrre un blocco testuale con i comandi proposti:
   ```bash
   # Comandi da eseguire manualmente:
   git add src/application/game_service.py
   git commit -m "feat(application): aggiungi metodo draw_card"
   ```
3. Comunicare: "Comandi proposti sopra. Eseguili nel terminale
   quando sei pronto, poi confermami per procedere."

## Protezione eliminazione file

Qualsiasi operazione che elimina file o directory è soggetta
alla procedura definita in:
→ `.github/skills/file-deletion-guard.skill.md`

Questa regola si applica in TUTTI i contesti git, inclusi:
- Risoluzione conflitti durante merge
- Operazioni `git rm` o `git clean`

Nessun agente può bypassare questa procedura.

## Riferimento skill

Per la lista tecnica completa dei comandi autorizzati per contesto:
→ `.github/skills/git-execution.skill.md`
