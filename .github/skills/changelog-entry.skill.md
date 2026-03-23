---
name: changelog-entry
description: >
  Regole per generare una voce CHANGELOG da un git diff.
  Determina sezione, formato e contenuto della voce
  da inserire in [Unreleased] di CHANGELOG.md.
  Richiamabile da Agent-Git durante OP-2 (Commit).
---

# Skill: Changelog Entry

## Scopo

Fornire le regole per costruire automaticamente una voce
CHANGELOG appropriata analizzando il diff staged.
La voce viene applicata senza conferma utente.

## Regole di classificazione sezione

Analizza il tipo di commit dedotto dal diff e assegna
la sezione CHANGELOG corrispondente:

| Tipo dedotto dal diff | Sezione CHANGELOG |
|-----------------------|-------------------|
| Nuova funzionalità, nuovo file, nuovo modulo | ### Added |
| Correzione bug, fix comportamento errato | ### Fixed |
| Modifica a funzionalità esistente, refactor | ### Changed |
| Rimozione funzionalità o file | ### Removed |
| Aggiornamento dipendenze, config, build | ### Changed |
| Solo documentazione (.md, docstring) | ### Changed |

## Formato voce

La voce deve essere una singola riga o blocco indentato:

```
- `<modulo/file principale>`: <descrizione concisa azione>.
  <dettaglio opzionale se la modifica è complessa>.
```

Regole di scrittura:
- Inizia con il nome del modulo o file più significativo
  tra backtick, seguito da due punti
- Descrizione in italiano, tono tecnico, max 15 parole
- Evita verbi generici ("aggiornato", "modificato"):
  usa verbi specifici ("aggiunge", "corregge", "rimuove",
  "espone", "rinomina", "sostituisce")
- Se il diff tocca più file con lo stesso scopo,
  raggruppa in una voce sola
- Se il diff tocca file con scopi diversi,
  genera una voce per gruppo logico

## Formato output per Agent-Git

Dopo aver applicato la voce a CHANGELOG.md, Agent-Git
mostra il seguente blocco (già definito in Agent-Git OP-2):

```
CHANGELOG — Voce applicata:
──────────────────────────────────────────
<voce applicata>
──────────────────────────────────────────
```

## Struttura CHANGELOG.md di riferimento

```markdown
# Changelog
Formato: [Keep a Changelog](https://keepachangelog.com/)

## [Unreleased]

### Added
### Fixed
### Changed
### Removed
```

Se il file non esiste, Agent-Git lo crea con questa struttura
prima di applicare la voce. Le sezioni vuote possono essere
omesse se non ci sono voci.

## Agenti che usano questa skill

- Agent-Git: passo 3 di OP-2 (Commit)
