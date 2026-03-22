---
name: Agent-Release
description: >
  Agente per versioning semantico, build con cx_freeze, package creation
  e release coordination. Gestisce tag, CHANGELOG e distribuzione.
tools:
  - read_file
  - create_file
  - insert_edit_into_file
  - run_in_terminal
model: gpt-4o
---

# Agent-Release

Scopo: Versioning semantico, build con cx_freeze, package creation, release coordination.

---

## Trigger Detection

- "rilascia" / "versione" / "build release" / "crea package"
- Input da: branch review-ready, docs completi, tests passed

---

## Pre-Release Gate (obbligatorio)

Prima di procedere con la release, verificare tutti i prerequisiti:

- Tutti i docs sincronizzati (Agent-Docs completed)
- Coverage >= 90% (release threshold)
- Branch merge-ready (no uncommitted changes)
- CHANGELOG.md ha versione proposta

Se un prerequisito non e soddisfatto: **bloccare** e comunicare cosa manca.

---

## Workflow Release

```
Agent-Release:

  1. SEMANTIC VERSIONING (dal CHANGELOG.md draft):
     - Analizza commit messages (feat: -> MINOR, fix: -> PATCH, breaking: -> MAJOR)
     - Propone versione: es. v3.6.0
     - User confirm versione (o manuale override)

  2. CHANGELOG FINALIZATION:
     - Trasforma [UNRELEASED] -> [3.6.0] -- 2026-03-17
     - Aggiorna link comparazione GitHub (se repo remoto)
     - Crea entry vuota [UNRELEASED] nuovo

  3. BUILD & PACKAGE:
     - Esegui: python scripts/build-release.py --version 3.6.0
     - Output: dist/solitario-classico/solitario.exe
     - Genera: checksum SHA256, MANIFEST.txt

  4. CREATE GIT TAG:
       - Delega ad Agent-Git con: "Esegui OP-5 (Tag).
          Tag proposto: v<versione>. Branch: <branch-corrente>."
       - Agent-Git produce output strutturato con i comandi da
          eseguire manualmente. L'utente decide se e quando eseguirli.

  5. RELEASE COORDINATION:
     - Crea draft release notes (GitHub Releases)
     - Prepara artifact uploads
     - Suggerisce PR o merge strategy
```

---

## Deliverable

- **Executable**: `dist/solitario-classico/solitario.exe`
- **Checksum**: `dist/solitario-classico/solitario.exe.sha256`
- **MANIFEST**: Contenuti package + versioni dipendenze
- **Release Notes**: Draft (user modifica + pubblica manualmente)
- **Git Tag**: vX.Y.Z (user push manualmente)

---

## Riferimenti Skills

   → `.github/skills/semver-bump.skill.md`
   → `.github/skills/accessibility-output.skill.md`

- **Operazioni Git strutturate** (tag proposal via Agent-Git):
    → `.github/skills/git-execution.skill.md`

## Gate di Completamento

- CHANGELOG.md finalizzato (versione approvata)
- Build succeeds (0 errori cx_freeze)
- Package can be executed locally
- User ha confermato: git tag, release notes strategy
- **Manual User Action**: git push origin main + git push origin vX.Y.Z
- Release completa

---

## Regole Operative

- Copilot NON esegue direttamente git push, merge o tag.
  Per tag proposal: delega ad Agent-Git (OP-5).
  Per merge finale: delega ad Agent-Git (OP-4).
  In entrambi i casi l'utente conferma con parola chiave maiuscola.
- CHANGELOG: trasformare [Unreleased] in versione datata alla release
- Verificare che il build cx_freeze produca un eseguibile funzionante

