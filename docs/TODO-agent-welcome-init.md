# TODO: Implementazione Agent-Welcome — Sistema Inizializzazione Progetto

> **Piano completo di riferimento**:
> [`docs/3 - coding plans/piano inizializzazione framework.md`](3%20-%20coding%20plans/piano%20inizializzazione%20framework.md)
> Consultare sempre all'inizio di ogni fase prima di iniziare le operazioni.

---

## FASE 1 — Nuovi file (OP 1-6)

### OP-1: Crea .github/project-profile.md

- [x] Creare il file con frontmatter YAML (initialized: false) e sezioni Markdown
- [ ] Commit: `chore(.github): aggiunge project-profile.md — stato iniziale non inizializzato`

### OP-2: Crea .github/instructions/project-init-gate.instructions.md

- [x] Creare il file con applyTo: "**", messaggio blocco e eccezione Agent-Welcome
- [ ] Commit: `feat(.github): aggiunge project-init-gate.instructions.md — gate inizializzazione`

### OP-3: Crea .github/skills/project-profile.skill.md

- [x] Creare il file con struttura canonica, matrice linguaggi, tutti i template (C, JS/TS, C#, generico)
- [ ] Commit: `feat(.github): aggiunge project-profile.skill.md — matrice linguaggi e template`

### OP-4: Crea .github/agents/Agent-Welcome.md

- [x] Creare il file con OP-1 (setup), OP-2 (aggiornamento), Regole Invarianti, Riferimenti Skills
- [ ] Commit: `feat(.github): aggiunge Agent-Welcome.md — agente setup profilo progetto`

### OP-5: Crea .github/prompts/project-setup.prompt.md

- [x] Creare il file con frontmatter e corpo che invoca Agent-Welcome OP-1
- [ ] Commit: `feat(.github): aggiunge project-setup.prompt.md`

### OP-6: Crea .github/prompts/project-update.prompt.md

- [x] Creare il file con input opzionale update_request e corpo che invoca Agent-Welcome OP-2
- [ ] Commit: `feat(.github): aggiunge project-update.prompt.md`

---

## FASE 2 — Modifica file esistenti (OP 7-11)

### OP-7: Modifica .github/copilot-instructions.md

- [x] Leggere copilot-instructions.md per individuare punto di inserimento
- [x] Inserire sezione "## Contesto Progetto" come PRIMA sezione del file
- [ ] Commit: `feat(.github): aggiunge gate inizializzazione in copilot-instructions.md`

### OP-8: Aggiorna .github/AGENTS.md (5 sub-modifiche)

- [x] 8a: contatore da 12 a 13 agenti nel corpo del file
- [x] 8b: voce Agent-Welcome in CIMA alla lista agenti nativi
- [x] 8c: project-profile.skill.md nella lista testuale skills (dopo accessibility-output)
- [x] 8d: riga Agent-Welcome in CIMA alla tabella agenti/skills
- [x] 8e: 2 nuovi prompt in CIMA alla sezione Prompt Files
- [ ] Commit: `docs(.github): aggiorna AGENTS.md — Agent-Welcome, 13 agenti, nuove skill e prompt`

### OP-9: Aggiorna file indice sottocartelle (4 sub-modifiche)

- [x] 9a: agents/README.md — Agent-Welcome in CIMA alla lista
- [x] 9b: skills/README.md — project-profile.skill.md in lista + riga tabella Agent-Welcome
- [x] 9c: prompts/README.md — CREA il file (non esiste) con tutti i prompt + 2 nuovi in cima
- [x] 9d: instructions/README.md — project-init-gate dopo git-policy
- [ ] Commit: `docs(.github): aggiorna README sottocartelle — Agent-Welcome e nuovi componenti`

### OP-10: Aggiorna .github/README.md

- [x] Aggiungere voce project-profile.md PRIMA di `agents/` nella sezione struttura
- [ ] Commit: `docs(.github): aggiunge project-profile.md in struttura .github/README.md`

### OP-11: Aggiorna .github/FRAMEWORK_CHANGELOG.md

- [x] Aggiungere blocco ### Added con 6 voci PRIMA di ### Fixed esistente
- [x] Aggiungere 2 voci a ### Changed esistente
- [ ] Commit: `docs(.github): aggiorna FRAMEWORK_CHANGELOG.md — Agent-Welcome system`

---

## FASE 3 — Verifica finale (14 checkpoint)

- [x] .github/project-profile.md esiste con initialized: false
- [x] .github/instructions/project-init-gate.instructions.md esiste con applyTo: "**"
- [x] .github/skills/project-profile.skill.md esiste con matrice e tutti i template
- [x] .github/agents/Agent-Welcome.md esiste con OP-1, OP-2 e Regole Invarianti
- [x] .github/prompts/project-setup.prompt.md esiste senza input obbligatori
- [x] .github/prompts/project-update.prompt.md esiste con input opzionale update_request
- [x] copilot-instructions.md ha "Contesto Progetto" come PRIMA sezione
- [x] AGENTS.md: contatore 13, Agent-Welcome in cima, project-profile.skill.md nelle skills
- [x] agents/README.md ha Agent-Welcome in cima
- [x] skills/README.md ha project-profile.skill.md e riga Agent-Welcome in tabella
- [x] prompts/README.md ha i 2 nuovi prompt in cima
- [x] instructions/README.md ha project-init-gate
- [x] .github/README.md ha project-profile.md nella struttura cartella
- [x] FRAMEWORK_CHANGELOG.md ha blocco ### Added con tutte e 6 le voci nuove
