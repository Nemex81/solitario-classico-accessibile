# Framework Copilot — Guida all'installazione e all'uso

> **Versione corrente**: v1.4.0 — 22 Marzo 2026

---

## Cos'è questo framework

Il Framework Copilot è una toolchain di orchestrazione per GitHub Copilot Chat basata su agenti nativi VS Code. È indipendente dal progetto ospite: può essere importato in qualsiasi repository Python senza modificare il codice applicativo.

Il framework fornisce:

- 9 agenti specializzati con ruoli distinti nel ciclo di sviluppo
- Prompt files per entry point e workflow comuni
- Script Python per automazione e validazione
- Convenzioni di commit, testing e documentazione
- Un sistema di changelog separato (Dual-Track) per framework e progetto

---

## Prerequisiti

- VS Code (versione recente)
- Estensione GitHub Copilot Chat abilitata
- Python 3.8 o superiore
- Git configurato nel repository

---

## Come importare su un nuovo progetto

1. Copia la cartella `.github/` nella root del nuovo repository.
2. Apri `.github/copilot-instructions.md` e adatta le sezioni:
   - "Architettura e Standard di Codifica" — descrive la tua architettura
   - "Critical Warnings" — elenca le trappole specifiche del tuo codice
   - Mantieni invariata la sezione "Framework Copilot" in cima al file
3. Aggiorna `.github/AGENTS.md` con il nome del tuo progetto nel titolo.
4. Lascia invariati gli agenti in `.github/agents/` — funzionano su qualsiasi progetto Python.
5. Avvia il primo task con il comando `#init` in chat (vedi Quick Start).

---

## Struttura della cartella .github/

- `agents/` — file agente nativi VS Code (uno per agente, formato `.md`)
- `prompts/` — prompt files per entry point e workflow
- `workflows/` — workflow GitHub Actions (CI/CD)
- `AGENTS.md` — documentazione di riferimento del framework
- `copilot-instructions.md` — istruzioni globali Copilot per il progetto
- `FRAMEWORK_CHANGELOG.md` — storico delle versioni del framework

## Git Policy

Il framework applica una policy git strutturata a 3 livelli:

- **Regola globale**: `.github/copilot-instructions.md`
   (fonte primaria, sempre caricata)
- **Dettaglio operativo**: `.github/instructions/git-policy.instructions.md`
   (rinforzo contestuale, attivo su tutti i file)
- **Matrice autorizzazioni**: `.github/skills/git-execution.skill.md`
   (riferimento tecnico per Agent-Code e Agent-Orchestrator)

I contesti autorizzati all'esecuzione git diretta sono 3:

- `Agent-Git`: agente dedicato, logica operativa completa
- `#git-commit.prompt.md`: dispatcher leggero → delega ad Agent-Git
- `#git-merge.prompt.md`: dispatcher leggero → delega ad Agent-Git

---

## Quick Start (3 passi)

1. Seleziona l'agente dal dropdown agenti nella chat di VS Code.
2. Scopri gli agenti: leggi `.github/agents/Agent-NAME.md` per la specifica di ciascuno.
3. Avvia un task: scrivi `#init` in chat e seleziona `init.prompt.md` dal file picker.

---

## Regola Dual-Track

Il framework separa nettamente la documentazione del framework da quella del progetto ospite.

**Binario Framework** — gestito da Agent-FrameworkDocs:

- `.github/FRAMEWORK_CHANGELOG.md` traccia le versioni del framework
- `.github/AGENTS.md` documenta gli agenti e le loro versioni
- `.github/README.md` è questa guida

**Binario Progetto** — gestito da Agent-Docs nel ciclo E2E:

- `CHANGELOG.md` della root traccia le versioni del progetto applicativo
- `docs/API.md`, `docs/ARCHITECTURE.md` documentano il codice

I due binari non si incrociano mai. Agent-FrameworkDocs non tocca `CHANGELOG.md` della root. Agent-Docs non tocca `FRAMEWORK_CHANGELOG.md`.

---

## Link utili

- [AGENTS.md](AGENTS.md) — riferimento completo degli agenti e del workflow
- [copilot-instructions.md](copilot-instructions.md) — istruzioni globali Copilot
- [FRAMEWORK_CHANGELOG.md](FRAMEWORK_CHANGELOG.md) — storico versioni framework
