---
initialized: true
project_name: "solitario-classico-accessibile"
version: "3.6.0"
primary_language: "Python"
secondary_languages: []
ui_framework: "wxPython"
test_runner: "pytest"
build_system: "cx_freeze"
architecture: "clean-architecture"
accessibility: true
framework_edit_mode: false
verbosity: "collaborator"
personality: "pragmatico"
platform: "Windows"
screen_reader: "NVDA"

# Profilo Progetto

> Questo file è la source of truth del progetto.
> Compilato da Agent-Welcome durante il setup iniziale.
> Non modificare manualmente i valori del frontmatter YAML.

## Identità

- **Nome**: solitario-classico-accessibile
- **Versione corrente**: 3.6.0
- **Descrizione**: Solitario classico accessibile con supporto NVDA e test automatizzati.

## Stack Tecnico

- **Linguaggio primario**: Python
- **Linguaggi secondari**: 
- **Framework UI**: wxPython
- **Test runner**: pytest
- **Build system**: cx_freeze
- **Piattaforma target**: Windows

## Architettura

- **Pattern**: —
- **Layer**: —
- **Riferimento**: —

## Accessibilità

- **Richiesta**: Accessibilità per utenti non vedenti (NVDA)
- **Screen reader**: NVDA
- **Standard**: WCAG/ARIA where applicable
- **Riferimento**: docs/ARCHITECTURE.md, .github/instructions/ui.instructions.md

## Componenti Framework Attivi

Instructions language-specific attive per questo progetto:
- `python.instructions.md` (attivo)


## Note Progetto

- **Framework Edit Mode**: Variabile di controllo sicurezza. Se `false`,
  i componenti del framework sono protetti da modifiche accidentali.
  Modificabile solo tramite il prompt `#framework-unlock`.
- **Verbosity**: Livello di verbosita comunicativa globale degli
    agenti. Valori: `tutor` | `collaborator` | `nerd`. Default:
    `collaborator`. Modificabile tramite `#verbosity`.
    Override temporaneo di sessione: dichiaralo verbalmente in chat
    senza modificare questo file.
- **Personality**: Postura operativa e stile relazionale degli
    agenti. Valori: `mentor` | `pragmatico` | `reviewer` |
    `architect`. Default: `pragmatico`. Modificabile tramite
    `#personality`. Override temporaneo di sessione: dichiaralo
    verbalmente in chat senza modificare questo file.

framework_edit_mode: true

(spazio per note contestuali — aggiornabile tramite
`#project-update` in qualsiasi momento)
