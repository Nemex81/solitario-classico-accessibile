sistema inizializzazione progetto (Agent-Welcome) 

Si tratta di una feature strutturale che tocca
componenti core del framework.

Leggi TUTTO prima di scrivere qualsiasi file.
L'ordine di lettura è obbligatorio.


=== ANALISI PRELIMINARE OBBLIGATORIA ===

Leggi nell'ordine:

1. .github/copilot-instructions.md
   — per capire la struttura attuale e dove inserire
     la sezione "Contesto Progetto"
2. .github/AGENTS.md
   — per capire struttura lista agenti, contatore,
     sezioni skills e prompt files
3. .github/agents/README.md
   — modello per aggiungere riga Agent-Welcome
4. .github/skills/README.md
   — per aggiungere project-profile.skill.md
     e riga tabella Agent-Welcome
5. .github/prompts/README.md
   — per aggiungere i 2 nuovi prompt
6. .github/instructions/README.md
   — per aggiungere project-init-gate.instructions.md
7. .github/README.md
   — per aggiungere project-profile.md nella struttura
8. .github/FRAMEWORK_CHANGELOG.md
   — per aggiornare sezione [Unreleased]

Solo dopo aver letto tutti e 8 i file procedi
con le operazioni nell'ordine indicato.


=== OPERAZIONE 1 — CREA project-profile.md ===
Path: .github/project-profile.md

Crea il file con questo contenuto esatto:

---
initialized: false
project_name: ""
version: ""
primary_language: ""
secondary_languages: []
ui_framework: ""
test_runner: ""
build_system: ""
architecture: ""
accessibility: false
platform: ""
screen_reader: ""
---

# Profilo Progetto

> Questo file è la source of truth del progetto.
> Compilato da Agent-Welcome durante il setup iniziale.
> Non modificare manualmente i valori del frontmatter YAML.

## Identità

- **Nome**: —
- **Versione corrente**: —
- **Descrizione**: —

## Stack Tecnico

- **Linguaggio primario**: —
- **Linguaggi secondari**: —
- **Framework UI**: —
- **Test runner**: —
- **Build system**: —
- **Piattaforma target**: —

## Architettura

- **Pattern**: —
- **Layer**: —
- **Riferimento**: —

## Accessibilità

- **Richiesta**: —
- **Screen reader**: —
- **Standard**: —
- **Riferimento**: —

## Componenti Framework Attivi

Instructions language-specific attive per questo progetto:
- (da compilare durante setup)

## Note Progetto

(spazio per note contestuali — aggiornabile tramite
#project-update in qualsiasi momento)

Commit proposto:
chore(.github): aggiunge project-profile.md — stato iniziale non inizializzato


=== OPERAZIONE 2 — CREA project-init-gate.instructions.md ===
Path: .github/instructions/project-init-gate.instructions.md

Crea il file con questo contenuto esatto:

---
applyTo: "**"
---

# Gate Inizializzazione Progetto — Framework Copilot

## Condizione di attivazione

Questo gate si attiva quando `.github/project-profile.md`
contiene `initialized: false` oppure il file non esiste.

## Comportamento obbligatorio

INTERROMPI qualsiasi altra operazione e comunica
questo messaggio all'utente, senza modifiche:

---
Questo framework non è ancora configurato per il progetto
corrente.

Prima di procedere con qualsiasi operazione esegui
il setup iniziale:

  1. Scrivi  #project-setup  nella chat
  2. Seleziona  project-setup.prompt.md  dal file picker
  3. Segui il percorso guidato (circa 2 minuti)

Il setup configura il framework per il tuo stack tecnico
specifico e abilita tutti gli agenti per il tuo progetto.
---

## Eccezione

L'unico agente autorizzato a operare con
`initialized: false` è Agent-Welcome.
Quando il contesto attivo è Agent-Welcome,
questo gate è sospeso.

## Riferimento

Trigger globale in: `.github/copilot-instructions.md`
sezione "Contesto Progetto"

Commit proposto:
feat(.github): aggiunge project-init-gate.instructions.md — gate inizializzazione


=== OPERAZIONE 3 — CREA project-profile.skill.md ===
Path: .github/skills/project-profile.skill.md

Crea il file con questo contenuto esatto:

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

Commit proposto:
feat(.github): aggiunge project-profile.skill.md — matrice linguaggi e template


=== OPERAZIONE 4 — CREA Agent-Welcome.md ===
Path: .github/agents/Agent-Welcome.md

Crea il file con questo contenuto esatto:

---
name: Agent-Welcome
description: >
  Agente di setup e manutenzione del profilo progetto.
  Raccoglie le informazioni fondamentali sul progetto,
  genera .github/project-profile.md come source of truth
  centralizzata, adatta i componenti language-specific
  del framework in base allo stack dichiarato.
  Non partecipa al ciclo E2E. Invocabile solo manualmente
  o tramite #project-setup.prompt.md e
  #project-update.prompt.md.
tools:
  - read_file
  - create_file
  - replace_string_in_file
model:
  - gpt-5-mini (copilot)
  - Raptor mini (copilot)
---

# Agent-Welcome

Scopo: setup iniziale e aggiornamento del profilo progetto.
Non scrive codice applicativo. Non esegue git direttamente.
Delega i commit ad Agent-Git al termine di ogni operazione.

---

## Trigger di Attivazione

- Invocazione manuale dal dropdown agenti VS Code
- Subagent delegation da #project-setup.prompt.md (OP-1)
- Subagent delegation da #project-update.prompt.md (OP-2)

---

## OP-1: Setup Iniziale

Attiva quando .github/project-profile.md non esiste
o contiene initialized: false.

### Passo 1 — Verifica stato

Leggi .github/project-profile.md.
Se initialized: true interrompi e comunica:
"Il profilo progetto è già configurato.
Usa #project-update per modificarlo."

### Passo 2 — Raccolta informazioni

Poni le domande in sequenza, una alla volta.
Attendi risposta prima di procedere alla successiva.
Usa questo formato per ogni domanda:

  SETUP PROGETTO — Passo N/7
  ──────────────────────────────────────────
  <domanda>
  ──────────────────────────────────────────

Domande in ordine:

  Passo 1/7 — Nome del progetto?

  Passo 2/7 — Descrizione breve (1-2 righe)?

  Passo 3/7 — Linguaggio primario?
  (es: Python / C / C++ / JavaScript /
       TypeScript / C# / altro)

  Passo 4/7 — Linguaggi secondari?
  (invio per nessuno)

  Passo 5/7 — Framework UI?
  (es: wxPython / Qt / Tkinter / Electron /
       WinForms / nessuno)

  Passo 6/7 — Test runner?
  (es: pytest / unittest / Jest / NUnit /
       GoogleTest / nessuno)

  Passo 7/7 — Build system?
  (es: cx_freeze / PyInstaller / CMake /
       npm / nessuno)

### Passo 3 — Riepilogo con conferma

Mostra riepilogo in questo formato esatto:

  SETUP PROGETTO — Riepilogo
  ──────────────────────────────────────────
  Nome            : <valore>
  Descrizione     : <valore>
  Linguaggio      : <primario> + <secondari o "nessuno">
  Framework UI    : <valore o "nessuno">
  Test runner     : <valore o "nessuno">
  Build system    : <valore o "nessuno">
  ──────────────────────────────────────────
  Confermi? Rispondi:
  "ok" per procedere
  "modifica <campo>" per correggere un valore
  ──────────────────────────────────────────

Se "modifica": riproponi solo le domande
per i campi indicati, poi riproponi il riepilogo.
Attendi "ok" prima di procedere.

### Passo 4 — Selezione componenti language-specific

Consulta la matrice in:
→ .github/skills/project-profile.skill.md
sezione "Matrice Componenti per Linguaggio"

Determina quale instructions file attivare
in base al linguaggio primario dichiarato.

### Passo 5 — Generazione file

Genera .github/project-profile.md compilando
tutti i campi con i valori raccolti.
Imposta initialized: true.
Usa la struttura canonica in:
→ .github/skills/project-profile.skill.md
sezione "Struttura Canonica project-profile.md"

Se il linguaggio primario non è Python:
genera il file instructions appropriato in
.github/instructions/ usando il template in:
→ .github/skills/project-profile.skill.md
sezione "Template Instructions per Linguaggi non-Python"

Se il file instructions esiste già:
non sovrascrivere — avvisa l'utente e chiedi
conferma prima di procedere.

### Passo 6 — Comunicazione completamento

  SETUP COMPLETATO
  ──────────────────────────────────────────
  File generati/modificati:
  - .github/project-profile.md       [GENERATO]
  - .github/instructions/<lang>.md   [GENERATO — se applicabile]
  ──────────────────────────────────────────
  Chiamo Agent-Git per il commit iniziale.
  ──────────────────────────────────────────

### Passo 7 — Commit

Delega ad Agent-Git con modalità SOLO_COMMIT.
Messaggio commit:
chore(.github): setup profilo progetto — <project_name>

---

## OP-2: Aggiornamento Profilo

Attiva quando .github/project-profile.md esiste
con initialized: true.

### Passo 1 — Verifica input

Se l'utente non ha specificato cosa aggiornare,
mostra questo help prima di procedere:

  project-update — Uso corretto
  ──────────────────────────────────────────
  Specifica cosa vuoi aggiornare. Esempi:

    "aggiungi linguaggio secondario Rust"
    "cambia build system da cx_freeze a PyInstaller"
    "aggiorna descrizione progetto"
    "aggiungi note: il modulo X è deprecato"

  Oppure scrivi "tutto" per rivedere
  l'intero profilo campo per campo.
  ──────────────────────────────────────────

### Passo 2 — Lettura stato corrente

Leggi .github/project-profile.md.
Mostra i valori attuali dei campi da modificare
in un blocco riepilogo.

### Passo 3 — Raccolta modifiche

Poni le domande solo per i campi da aggiornare.
Se l'utente scrive "tutto": ripercorri tutte
le 7 domande di OP-1 mostrando il valore attuale
come default per ogni campo.

### Passo 4 — Riepilogo modifiche con conferma

  AGGIORNAMENTO PROFILO — Riepilogo modifiche
  ──────────────────────────────────────────
  <campo>  :  <valore precedente>  →  <valore nuovo>
  ──────────────────────────────────────────
  Confermi? "ok" per applicare / "annulla" per abortire
  ──────────────────────────────────────────

### Passo 5 — Applicazione modifiche

Aggiorna .github/project-profile.md con i nuovi valori.

Se il linguaggio primario è cambiato:
consulta la matrice in project-profile.skill.md
e aggiorna i componenti language-specific.
Avvisa l'utente di quali instructions file
vengono aggiunti.

### Passo 6 — Commit

Delega ad Agent-Git con modalità SOLO_COMMIT.
Messaggio commit:
chore(.github): aggiorna profilo progetto — <campi modificati>

---

## Regole Invarianti

- MAI modificare file fuori da .github/ e da
  .github/instructions/<lang>.instructions.md
- MAI eseguire git direttamente: delegare sempre
  ad Agent-Git
- MAI sovrascrivere dati senza riepilogo con
  conferma esplicita "ok" dell'utente
- MAI sovrascrivere un instructions file esistente
  senza conferma esplicita
- Se un linguaggio non è in matrice: generare
  template generico e avvisare l'utente
- Non partecipa al ciclo E2E
- Non viene mai invocato da Agent-Orchestrator

---

## Riferimenti Skills

- Struttura profilo e matrice componenti:
  → .github/skills/project-profile.skill.md
- Standard output accessibile:
  → .github/skills/accessibility-output.skill.md
- Protezione eliminazione file:
  → .github/skills/file-deletion-guard.skill.md

Commit proposto:
feat(.github): aggiunge Agent-Welcome.md — agente setup profilo progetto


=== OPERAZIONE 5 — CREA project-setup.prompt.md ===
Path: .github/prompts/project-setup.prompt.md

Crea il file con questo contenuto esatto:

---
mode: agent
model:
  - gpt-5-mini (copilot)
  - Raptor mini (copilot)
description: >
  Setup iniziale del framework per il progetto corrente.
  Raccoglie le informazioni fondamentali e genera
  .github/project-profile.md come source of truth.
  Eseguire PRIMA di qualsiasi altra operazione
  su un nuovo progetto.
---

# Project Setup — Inizializzazione Framework

Sei Agent-Welcome. Avvia OP-1: Setup Iniziale.

Leggi .github/project-profile.md.
Se initialized: true comunica che il progetto
è già configurato e suggerisci #project-update.
Se initialized: false o il file non esiste:
procedi con il flusso guidato OP-1 completo.

Commit proposto:
feat(.github): aggiunge project-setup.prompt.md


=== OPERAZIONE 6 — CREA project-update.prompt.md ===
Path: .github/prompts/project-update.prompt.md

Crea il file con questo contenuto esatto:

---
mode: agent
model:
  - gpt-5-mini (copilot)
  - Raptor mini (copilot)
description: >
  Aggiorna uno o più campi del profilo progetto.
  Se non specifichi cosa aggiornare, Agent-Welcome
  mostra un help con esempi d'uso.
inputs:
  - id: update_request
    description: >
      Cosa vuoi aggiornare nel profilo progetto?
      (opzionale — lascia vuoto per vedere il help)
    required: false
---

# Project Update — Aggiornamento Profilo Progetto

Sei Agent-Welcome. Avvia OP-2: Aggiornamento Profilo.

Input ricevuto: ${input:update_request}

Se l'input è vuoto o non specificato:
mostra il blocco help di OP-2 prima di procedere.
Se l'input contiene una richiesta specifica:
procedi direttamente con OP-2 per i campi indicati.

Commit proposto:
feat(.github): aggiunge project-update.prompt.md


=== OPERAZIONE 7 — MODIFICA copilot-instructions.md ===
Path: .github/copilot-instructions.md

Leggi il file per capire dove si trova la prima
sezione di contenuto. Inserisci questo blocco
come PRIMA sezione del file, prima di qualsiasi
altro contenuto esistente (dopo eventuali
metadati di versione se presenti):

## Contesto Progetto

Leggi `.github/project-profile.md` prima di
qualsiasi operazione. È la source of truth per
nome, stack tecnico e architettura del progetto.
Non usare valori hardcoded in questo file come
riferimento al progetto corrente.
Se `initialized: false`: interrompi e segui
→ `.github/instructions/project-init-gate.instructions.md`

Non aggiungere altro. Non modificare il resto del file.

Commit proposto:
feat(.github): aggiunge gate inizializzazione in copilot-instructions.md


=== OPERAZIONE 8 — AGGIORNA AGENTS.md ===
Path: .github/AGENTS.md

Modifica 8a — Intestazione:
Aggiorna il contatore nel corpo del file da 12 a 13:
"Questo framework orchestra lo sviluppo del progetto
tramite 13 agenti specializzati"

Modifica 8b — Lista agenti nativi:
Aggiungi questa voce in CIMA alla lista agenti,
PRIMA di Agent-Orchestrator:

- [Agent-Welcome](agents/Agent-Welcome.md) — Setup profilo progetto
  Agente di inizializzazione. Raccoglie le info fondamentali
  del progetto, genera .github/project-profile.md come
  source of truth, adatta i componenti language-specific.
  Non partecipa al ciclo E2E. Invocabile dal dropdown o
  tramite #project-setup.prompt.md e #project-update.prompt.md.
  Modelli: gpt-5-mini, Raptor mini.

Modifica 8c — Sezione Agent Skills, lista testuale:
Aggiungi questa voce dopo accessibility-output.skill.md:
- `project-profile.skill.md` — struttura project-profile.md,
  matrice componenti per linguaggio, template instructions

Modifica 8d — Sezione Agent Skills, tabella agenti:
Aggiungi riga Agent-Welcome in CIMA alla tabella:
| Agent-Welcome | project-profile, accessibility-output, file-deletion-guard |

Modifica 8e — Sezione Prompt Files:
Aggiungi queste due voci in CIMA alla lista prompt:
- `#project-setup.prompt.md` — Setup iniziale framework
  per nuovo progetto. Da eseguire prima di qualsiasi
  altra operazione. Delega ad Agent-Welcome OP-1.
- `#project-update.prompt.md` — Aggiorna campi del
  profilo progetto. Delega ad Agent-Welcome OP-2.

Commit proposto:
docs(.github): aggiorna AGENTS.md — Agent-Welcome, 13 agenti, nuove skill e prompt


=== OPERAZIONE 9 — AGGIORNA FILE INDICE SOTTOCARTELLE ===

Esegui queste 4 micro-modifiche in sequenza.
Leggi ogni file prima di modificarlo.

9a — .github/agents/README.md
Aggiungi in CIMA alla lista agenti:
- [`Agent-Welcome`](Agent-Welcome.md) — Setup e manutenzione profilo progetto

9b — .github/skills/README.md
Lista skills: aggiungi dopo accessibility-output.skill.md:
- `project-profile.skill.md` — struttura profilo progetto,
  matrice componenti language-specific, template instructions

Tabella agenti: aggiungi riga in CIMA:
| Agent-Welcome | project-profile, accessibility-output, file-deletion-guard |

9c — .github/prompts/README.md
Aggiungi in CIMA alla lista prompt:
- `project-setup.prompt.md` — setup iniziale framework
  (nessun input — flusso guidato Agent-Welcome OP-1)
- `project-update.prompt.md` — aggiornamento profilo progetto
  (input opzionale — help automatico se vuoto)

9d — .github/instructions/README.md
Lista file: aggiungi questa voce dopo git-policy.instructions.md:
- `project-init-gate.instructions.md` — gate di inizializzazione
  progetto. Intercetta initialized: false e guida l'utente
  al setup. (applyTo: `**` — attivo in tutti i contesti)

Commit proposto:
docs(.github): aggiorna README sottocartelle — Agent-Welcome e nuovi componenti


=== OPERAZIONE 10 — AGGIORNA .github/README.md ===
Path: .github/README.md

Nella sezione "## Struttura della cartella .github/"
aggiungi questa voce PRIMA della voce `agents/`:

- `project-profile.md` — profilo progetto: source of truth
  per nome, stack tecnico e architettura. Campo
  `initialized: false` di default. Compilato da
  Agent-Welcome durante il setup iniziale.

Commit proposto:
docs(.github): aggiunge project-profile.md in struttura .github/README.md


=== OPERAZIONE 11 — AGGIORNA FRAMEWORK_CHANGELOG.md ===
Path: .github/FRAMEWORK_CHANGELOG.md

Nella sezione ## [Unreleased], aggiungi un blocco
### Added PRIMA del blocco ### Fixed esistente
con queste voci:

### Added

- `project-profile.md`: nuovo file — source of truth
  profilo progetto. Frontmatter YAML con campo
  `initialized` in prima riga per intercettazione
  rapida dello stato. Distribuito con initialized: false.
  Compilato da Agent-Welcome in OP-1.
- `Agent-Welcome.md`: nuovo agente — setup iniziale
  e aggiornamento profilo progetto. Flusso guidato
  in 7 passi con conferma riepilogo prima di scrivere
  qualsiasi file. Modelli gpt-5-mini e Raptor mini.
  Non partecipa al ciclo E2E. Delega git ad Agent-Git.
- `project-profile.skill.md`: nuova skill — struttura
  canonica project-profile.md, matrice componenti
  per linguaggio (Python, C/C++, JS, TS, C#, generico),
  template instructions per linguaggi non-Python.
  Referenziata da Agent-Welcome.
- `project-setup.prompt.md`: nuovo prompt — entry point
  setup iniziale framework. Nessun input richiesto.
  Flusso guidato gestito da Agent-Welcome OP-1.
  Da eseguire come primo comando su qualsiasi progetto.
- `project-update.prompt.md`: nuovo prompt — entry point
  aggiornamento profilo progetto. Input opzionale:
  se vuoto mostra help con esempi d'uso. Delega
  ad Agent-Welcome OP-2.
- `project-init-gate.instructions.md`: nuova instruction
  (applyTo: "**") — gate di inizializzazione attivo
  in tutti i contesti. Intercetta initialized: false
  e guida l'utente al setup con messaggio strutturato.
  Eccezione: Agent-Welcome opera sempre senza blocco.

### Changed (aggiunta a blocco Changed esistente)

- `copilot-instructions.md`: aggiunta sezione
  "Contesto Progetto" in prima posizione. Trigger
  gate inizializzazione con riferimento a
  project-init-gate.instructions.md. Riferimento
  dinamico a project-profile.md come source of truth.
- `AGENTS.md`: contatore aggiornato da 12 a 13 agenti.
  Agent-Welcome aggiunto in cima alla lista.
  project-profile.skill.md aggiunta a lista skills
  e tabella agenti.

Commit proposto:
docs(.github): aggiorna FRAMEWORK_CHANGELOG.md — Agent-Welcome system


=== VERIFICA FINALE ===

Prima di proporre i commit, verifica:

[ ] .github/project-profile.md esiste con initialized: false
[ ] .github/instructions/project-init-gate.instructions.md
    esiste con applyTo: "**"
[ ] .github/skills/project-profile.skill.md esiste
    con matrice linguaggi e tutti i template
[ ] .github/agents/Agent-Welcome.md esiste con
    OP-1 e OP-2 complete e Regole Invarianti
[ ] .github/prompts/project-setup.prompt.md esiste
    senza input obbligatori
[ ] .github/prompts/project-update.prompt.md esiste
    con input opzionale update_request
[ ] copilot-instructions.md ha sezione "Contesto Progetto"
    come PRIMA sezione del file
[ ] AGENTS.md ha contatore 13, Agent-Welcome in cima
    alla lista, project-profile.skill.md nelle skills
[ ] agents/README.md ha Agent-Welcome in cima
[ ] skills/README.md ha project-profile.skill.md
    e riga Agent-Welcome in tabella
[ ] prompts/README.md ha i 2 nuovi prompt in cima
[ ] instructions/README.md ha project-init-gate
[ ] .github/README.md ha project-profile.md
    nella struttura cartella
[ ] FRAMEWORK_CHANGELOG.md ha blocco ### Added
    con tutte e 6 le voci nuove

=== FINE OPERAZIONI ===

Mostrami i commit proposti in ordine (1 per
operazione o raggruppati dove logico), pronti
per Agent-Git. Nessun altro output aggiuntivo.