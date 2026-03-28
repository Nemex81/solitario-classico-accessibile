<!-- markdownlint-disable MD029 MD031 MD032 MD040 MD060 -->

# project-doc-bootstrap — Skill operativa per il bootstrap documentale core

Questa skill definisce il contratto operativo per il bootstrap dei documenti
core del progetto a partire dai template canonici del framework.
E invocata da Agent-Welcome in OP-4. Non e documentazione passiva:
e il protocollo di azione che Agent-Welcome esegue per creare i documenti
core del progetto a partire dalle strutture canoniche in `.github/templates/`.

---

## Template e destinazioni

I template canonici per il bootstrap documentale core si trovano in
`.github/templates/`. Ogni template ha una destinazione e un livello precisi.

| Template | Destinazione | Livello | Note |
|----------|--------------|---------|------|
| `.github/templates/api.md` | `docs/API.md` | 2 — Core docs | |
| `.github/templates/architecture.md` | `docs/ARCHITECTURE.md` | 2 — Core docs | |
| `.github/templates/changelog.md` | `CHANGELOG.md` | 2 — Core docs | root del repository |
| `.github/templates/project.instructions.md` | `.github/instructions/project.instructions.md` | 3 — Istruzioni progetto | richiede framework_edit_mode: true |
| `.github/templates/copilot-instructions.md` | `.github/copilot-instructions.md` | RIPRISTINO | solo su richiesta esplicita, mai durante bootstrap standard |

---

## Livelli di bootstrap

Agent-Welcome propone all'utente 3 livelli di bootstrap documentale core.
L'utente sceglie esplicitamente prima che venga scritto qualsiasi file.

### Livello 1 — Solo struttura docs/

Equivale a OP-3: crea cartelle e README orientativi.
Nessun documento core viene creato da questo livello.
Delegato a docs_manager.skill.md sezione "Bootstrap struttura docs/".

### Livello 2 — Struttura + documenti core

Crea struttura docs/ (se non esiste) piu:

- `docs/API.md` — da `.github/templates/api.md`
- `docs/ARCHITECTURE.md` — da `.github/templates/architecture.md`
- `CHANGELOG.md` — da `.github/templates/changelog.md`

Placeholder sostituiti: `{{NOME_PROGETTO}}` letto da `project_name`
in `.github/project-profile.md`.

### Livello 3 — Struttura + documenti core + istruzioni progetto

Tutto il Livello 2 piu:

- `.github/instructions/project.instructions.md`
  — da `.github/templates/project.instructions.md`

Placeholder sostituiti: `{{NOME_PROGETTO}}`, `{{LINGUAGGIO_PRIMARIO}}`,
`{{FRAMEWORK_UI}}`, `{{TEST_RUNNER}}` letti da `project-profile.md`.

Richiede `framework_edit_mode: true`.
Se il flag e false: interrompere il bootstrap al livello 2 e comunicare:
"Per creare project.instructions.md e richiesto lo sblocco framework.
 Usa #framework-unlock, poi ripeti OP-4 livello 3."

---

## Regola additiva (no overwrite implicito)

Il bootstrap documentale core e SEMPRE additivo.

Per ogni file da creare:

1. Verificare se il file esiste gia nel path di destinazione.
2. Se esiste: NON sovrascrivere. Segnalare all'utente con:
   `[SALTATO] <path> gia esistente — nessuna modifica applicata.`
3. Se non esiste: creare il file, sostituire i placeholder, salvare.

Questa regola si applica a tutti i livelli senza eccezioni automatiche.

---

## Idempotenza

Il processo di bootstrap puo essere ripetuto senza effetti collaterali.
Eseguire il bootstrap su un progetto gia configurato non modifica nulla:
tutti i file esistenti vengono segnalati come SALTATI.

---

## Ripristino copilot-instructions (competenza separata)

Il template `.github/templates/copilot-instructions.md` NON viene compilato
durante il bootstrap standard (Livelli 1, 2, 3). E usato SOLO per la
competenza di ripristino esplicito documentata in Agent-Welcome — sezione
"Competenza: Ripristino copilot-instructions".

Questa competenza:

- Si attiva solo su richiesta esplicita dell'utente (parola chiave RIPRISTINA)
- Richiede sempre framework_edit_mode: true
- Non viene mai eseguita automaticamente
- E separata da OP-1, OP-2, OP-3 e OP-4

---

## Placeholder dichiarati

| Placeholder | Sorgente | Template che lo usano |
|-------------|----------|-----------------------|
| `{{NOME_PROGETTO}}` | `project_name` in `project-profile.md` | api.md, architecture.md, changelog.md, project.instructions.md, copilot-instructions.md |
| `{{VERSIONE_FRAMEWORK}}` | versione corrente del framework | copilot-instructions.md |
| `{{PROFILO_UTENTE}}` | sezione Profilo Utente di project-profile | copilot-instructions.md |
| `{{LINGUAGGIO_PRIMARIO}}` | `primary_language` in `project-profile.md` | project.instructions.md |
| `{{FRAMEWORK_UI}}` | `ui_framework` in `project-profile.md` | project.instructions.md |
| `{{TEST_RUNNER}}` | `test_runner` in `project-profile.md` | project.instructions.md |
