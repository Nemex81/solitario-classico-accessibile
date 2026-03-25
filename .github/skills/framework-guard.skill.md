---
name: framework-guard
description: >
  Guardia standardizzata per bloccare modifiche accidentali ai
  componenti protetti del framework quando framework_edit_mode e false.
  Importabile dagli agenti che possono toccare file in .github/.
used_by:
  - Agent-FrameworkDocs
  - Agent-Release
  - Agent-Welcome
  - Agent-Orchestrator
  - Agent-Docs
---

# Skill: Framework Guard

Scopo: impedire modifiche accidentali ai componenti cardine del framework
quando `.github/project-profile.md` dichiara `framework_edit_mode: false`.

---

## Path protetti canonici

La guardia si applica ai seguenti path in scrittura:

- `.github/copilot-instructions.md`
- `.github/project-profile.md`
- `.github/instructions/**`
- `.github/prompts/**`
- `.github/skills/**`
- `.github/agents/**`
- `.github/AGENTS.md`
- `.github/FRAMEWORK_CHANGELOG.md` (solo in scrittura non autorizzata)

La lettura dei path sopra e sempre consentita se il task la richiede.

---

## Procedura obbligatoria

Prima di creare, modificare o sovrascrivere un path protetto:

1. Leggi `.github/project-profile.md`.
2. Verifica il valore di `framework_edit_mode` nel frontmatter YAML.
3. Se il valore e `true`, procedi solo entro il perimetro dichiarato
   dall'utente per la sessione corrente.
4. Se il valore e `false`, interrompi l'operazione e mostra il messaggio
   di blocco standard.

---

## Messaggio di blocco standard

Mostra questo blocco senza abbreviazioni:

```text
FRAMEWORK GUARD — MODIFICA BLOCCATA
────────────────────────────────────────
File richiesto : <path protetto>
Motivo         : framework_edit_mode=false in .github/project-profile.md
Azione         : usa il prompt #framework-unlock per autorizzare
                 temporaneamente le modifiche dichiarate.
Vincolo        : nessun agente puo impostare framework_edit_mode=true
                 autonomamente.
────────────────────────────────────────
```

Se i file richiesti sono piu di uno, sostituisci `File richiesto` con
`File richiesti` ed elenca ogni path su una riga separata.

---

## Regole invarianti

- La skill NON ha capacita di sblocco.
- Nessun agente puo impostare `framework_edit_mode: true` autonomamente.
- L'unico canale di sblocco e il prompt `#framework-unlock` invocato
  esplicitamente dall'utente.
- Lo sblocco non autorizza modifiche collaterali: ogni scrittura deve
  restare nel perimetro dichiarato dall'utente.
- Se durante il task emerge un ulteriore file protetto non dichiarato,
  l'agente deve fermarsi e chiedere un nuovo sblocco esplicito.

---

## Integrazione con altre guardie

Questa skill NON sostituisce le guardie gia esistenti:

- `framework-scope-guard.skill.md` resta responsabile dei limiti
  degli agenti read-only e dei messaggi fuori scope.
- `file-deletion-guard.skill.md` resta responsabile di qualsiasi
  eliminazione di file o directory, anche quando un path e gia protetto
  da Framework Guard.

Ordine pratico:
1. Verifica se il file rientra nei path protetti del framework.
2. Se la modifica implica eliminazione, applica anche `file-deletion-guard`.
3. Se l'agente e read-only, applica anche `framework-scope-guard`.
