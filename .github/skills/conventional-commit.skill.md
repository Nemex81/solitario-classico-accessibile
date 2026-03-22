---
name: conventional-commit
description: >
  Regole Conventional Commits per il progetto.
  Richiamabile da Agent-Code, git-commit.prompt.md e
  git-merge.prompt.md per garantire commit atomici e coerenti.
---

# Skill: Conventional Commit

## Formato obbligatorio

```
<type>(<scope>): <subject>
```

Soggetto: imperativo, minuscolo, max 72 caratteri, no punto finale.

## Types consentiti

- `feat`: nuova funzionalità
- `fix`: correzione bug
- `docs`: solo documentazione
- `refactor`: refactoring senza cambio funzionale
- `test`: aggiunta o modifica test
- `chore`: manutenzione (dipendenze, config, CI)

## Scopes consentiti

- `domain`, `application`, `infrastructure`, `presentation`
- `docs`, `tests`, `scripts`, `ci`, `framework`

## Regole atomicità

- Un commit = una modifica logica coesa
- Non mescolare fix e feat nello stesso commit
- Ogni commit deve essere compilabile e testabile da solo
- Se il commit chiude un TODO item, specificarlo nel body:
  `Closes TODO: <descrizione item>`

## Esempi corretti

```
feat(domain): aggiungi CardStack con metodo shuffle
fix(presentation): correggi focus su dialog profilo alla chiusura
docs(framework): aggiorna AGENTS.md con Agent-FrameworkDocs
chore(ci): aggiorna soglia coverage a 85%
```
