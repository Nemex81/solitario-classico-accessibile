---
name: semver-bump
description: >
  Logica SemVer per determinare il tipo di bump di versione.
  Richiamabile da Agent-Release e Agent-FrameworkDocs per
  proporre la versione corretta prima di ogni release.
---

# Skill: SemVer Bump

## Regole di bump

**MAJOR** (X.0.0): breaking change — richiede aggiornamento di
  codice esistente da parte degli utilizzatori. Esempi:
  - Rimossa API pubblica esistente
  - Cambio firma metodo pubblico incompatibile
  - Cambio struttura dati persistita (profili, config)

**MINOR** (0.X.0): nuova funzionalità retrocompatibile. Esempi:
  - Nuovo agente aggiunto al framework
  - Nuova feature di gioco opzionale
  - Nuovo prompt o skill aggiunto

**PATCH** (0.0.X): bugfix o manutenzione retrocompatibile. Esempi:
  - Correzione bug senza cambio API
  - Fix documentazione
  - Aggiornamento dipendenza patch-level

## Procedura di bump

1. Leggi `CHANGELOG.md` (progetto) o `FRAMEWORK_CHANGELOG.md` (framework)
   sezione `[Unreleased]`
2. Classifica ogni voce: feat → MINOR, fix → PATCH, breaking → MAJOR
3. Applica la regola più alta tra tutte le voci presenti
4. Proponi la versione risultante con motivazione esplicita

## Output atteso

```
Versione corrente: vX.Y.Z
Voci [Unreleased]: N feat, M fix, K breaking
Bump suggerito: MINOR → vX.(Y+1).0
Motivazione: presenza di feat senza breaking changes
```
