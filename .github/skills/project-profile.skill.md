---
skill: project-profile
scope: [Agent-Welcome]
description: >
  Struttura canonica di project-profile.md,
  matrice componenti language-specific,
  template instructions per linguaggi non-Python.
---

# Skill: project-profile

## Struttura Canonica project-profile.md

Usa questa struttura quando generi o aggiorni
`.github/project-profile.md`.

Il frontmatter YAML deve essere la prima sezione
del file. Il campo `initialized` deve essere
sempre in prima riga.

Frontmatter obbligatorio:

  initialized: true/false
  project_name: "Nome Progetto"
  version: "0.1.0"
  primary_language: "Python"
  secondary_languages: ["C"]
  ui_framework: "wxPython"
  test_runner: "pytest"
  build_system: "cx_freeze"
  architecture: "clean-architecture-4-layer"
  accessibility: true/false
  platform: "Windows"
  screen_reader: "NVDA"

Valori ammessi per architecture:
- "clean-architecture-4-layer"
- "mvc"
- "mvvm"
- "layered"
- "none"

Per campi non applicabili usa stringa vuota ""
o lista vuota []. Non usare null o None.

---

## Matrice Componenti per Linguaggio

Usa questa matrice in OP-1 (setup) e OP-2
(aggiornamento linguaggio primario) per determinare
quali componenti language-specific attivare.

| Linguaggio primario | Instructions file | Azione |
| ------------------- | ----------------- | ------ |
| Python | python.instructions.md | Già esiste — nessuna azione |
| C / C++ | cpp.instructions.md | Generare da template sezione sotto |
| JavaScript | js.instructions.md | Generare da template sezione sotto |
| TypeScript | ts.instructions.md | Generare da template sezione sotto |
| C# | csharp.instructions.md | Generare da template sezione sotto |
| Altro | <lang>.instructions.md | Template generico + avviso utente |

Regola: se il file instructions esiste già
non sovrascriverlo. Avvisa l'utente che esiste
e chiedi se vuole mantenerlo o rigenerarlo.

---

## Template Instructions per Linguaggi non-Python

Usa questi template per generare il file instructions
del linguaggio dichiarato dall'utente in OP-1.
Sostituisci i placeholder <LANG> e <EXTENSION>.

### Template C / C++

  ---
  applyTo: "**/*.<EXTENSION>"
  ---
  # Standard <LANG> — <NOME PROGETTO>

  ## Naming Conventions
  - Variabili e funzioni: snake_case
  - Classi e struct: PascalCase
  - Costanti: UPPER_SNAKE_CASE
  - File header: .h / File implementazione: .cpp

  ## Qualità Codice
  - Ogni funzione ha responsabilità singola
  - Nessuna funzione supera 40 righe
  - Commenti in italiano, codice in inglese
  - Nessun magic number: usa costanti nominate

  ## Build
  - Standard: C17 / C++17 o superiore
  - Warning trattati come errori (-Wall -Wextra)

  ## Note
  (personalizza in base al progetto)

### Template JavaScript / TypeScript

  ---
  applyTo: "**/*.<EXTENSION>"
  ---
  # Standard <LANG> — <NOME PROGETTO>

  ## Naming Conventions
  - Variabili e funzioni: camelCase
  - Classi: PascalCase
  - Costanti: UPPER_SNAKE_CASE
  - File: kebab-case

  ## Qualità Codice
  - Prefer const su let, mai var
  - Ogni funzione ha responsabilità singola
  - Nessuna funzione supera 40 righe
  - Commenti in italiano, codice in inglese

  ## Note
  (personalizza in base al progetto)

### Template C#

  ---
  applyTo: "**/*.cs"
  ---
  # Standard C# — <NOME PROGETTO>

  ## Naming Conventions
  - Metodi e proprietà pubbliche: PascalCase
  - Variabili locali e parametri: camelCase
  - Costanti: UPPER_SNAKE_CASE
  - Namespace: PascalCase

  ## Qualità Codice
  - Ogni classe ha responsabilità singola
  - Nessun metodo supera 40 righe
  - Commenti in italiano, codice in inglese
  - Usa nullable reference types

  ## Note
  (personalizza in base al progetto)

### Template Generico (linguaggi non coperti)

  ---
  applyTo: "**/*.<EXTENSION>"
  ---
  # Standard <LANG> — <NOME PROGETTO>

  ## Naming Conventions
  (da completare manualmente)

  ## Qualità Codice
  - Ogni funzione ha responsabilità singola
  - Nessuna funzione supera 40 righe
  - Commenti in italiano, codice in inglese

  ## Note
  Questo template è stato generato automaticamente
  da Agent-Welcome per il linguaggio <LANG>.
  Completare le sezioni mancanti manualmente.
