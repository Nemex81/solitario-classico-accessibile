<!-- markdownlint-disable MD041 -->

---
name: semantic-gate
description: >
  Criteri minimi osservabili da verificare prima di avanzare tra le fasi
  Analyze, Design e Plan nel ciclo E2E. Ogni criterio richiede la presenza
  di sezioni con nomi esatti nel documento prodotto dalla fase precedente.
  Richiamabile da Agent-Orchestrator in Fase 1, 2 e 3.
---

# Skill: Semantic Gate

## Principio

I gate strutturali (`validate_gates.py`) verificano il frontmatter YAML.
I gate semantici verificano la qualità minima del *contenuto*.
Un findings report con frontmatter valido ma sezioni mancanti non può
avanzare a Design. Un DESIGN non REVIEWED non può avanzare a Planning.

---

## Gate 1 — Findings (Analyze → Design)

### Sezioni obbligatorie nel findings report

Il documento prodotto da Agent-Analyze deve contenere **tutte**
le seguenti sezioni (titoli esatti, case-insensitive):

| Sezione attesa | Criterio di accettazione |
|---|---|
| `Componenti coinvolti` | Almeno un componente nominato con path o modulo |
| `Dipendenze` | Almeno una dipendenza tra componenti o layer |
| `Rischi` | Almeno un rischio identificato (anche "nessun rischio rilevante" è accettabile se motivato) |
| `Vincoli accessibilità NVDA` | Presenza esplicita; "nessun impatto UI" è accettabile |

### Procedura di verifica (Agent-Orchestrator, Fase 1)

1. Dopo la produzione del findings report, leggi il contenuto.
2. Verifica la presenza di ciascuna sezione per nome.
3. Se una o più sezioni mancano:
   - NON avanzare a Design.
   - Richiedi ad Agent-Analyze: "Il report è incompleto. Aggiungi le
     sezioni mancanti: <lista sezioni assenti>."
   - Ripeti la verifica dopo la risposta.
4. Se tutte le sezioni sono presenti: gate superato, avanza a Design.

---

## Gate 2 — Design (Design → Planning)

### Precondizione per avanzare a Fase 3

Il documento `docs/2 - projects/DESIGN_<feature>.md` deve soddisfare:

| Criterio | Valore atteso |
|---|---|
| `status` nel frontmatter | `REVIEWED` |
| Conferma utente | Esplicita nella chat ("Confermo"/"S"/"ok") |

### Procedura di verifica (Agent-Orchestrator, Fase 2 → Fase 3)

1. Esegui: `python scripts/validate_gates.py --check-design "docs/2 - projects/DESIGN_<feature>.md"`
2. Exit code atteso: 0
3. Leggi frontmatter del file: verificare `status: REVIEWED`.
4. Se status è `DRAFT` o assente:
   - Mostra il DESIGN all'utente.
   - Chiedi: "Approvare e impostare status: REVIEWED per procedere al planning?"
   - Attendi conferma esplicita prima di aggiornare il frontmatter.
5. Se status è `REVIEWED` e gate CLI passa: avanza a Planning.

---

## Gate 3 — Plan (Planning → Codifica)

### Precondizione per avanzare a Fase 4

Il documento `docs/3 - coding plans/PLAN_<feature>_vX.Y.Z.md` deve soddisfare:

| Criterio | Valore atteso |
|---|---|
| `status` nel frontmatter | `READY` |
| Conferma utente | Esplicita nella chat ("Confermo"/"S"/"ok") |

### Procedura di verifica (Agent-Orchestrator, Fase 3 → Fase 4)

1. Esegui: `python scripts/validate_gates.py --check-plan "docs/3 - coding plans/PLAN_<feature>_vX.Y.Z.md"`
2. Exit code atteso: 0
3. Leggi frontmatter del file: verifica `status: READY`.
4. Se status è `DRAFT` o `REVIEWED` ma non `READY`:
   - Mostra il PLAN all'utente.
   - Chiedi: "Approvare e impostare status: READY per avviare l'implementazione?"
   - Attendi conferma esplicita prima di aggiornare il frontmatter.
5. Se status è `READY` e gate CLI passa: avanza a Codifica.

---

## Note operative

- I nomi di sezione attesi sono case-insensitive ma devono essere titoli Markdown
  riconoscibili (es. `## Componenti coinvolti` o `### Componenti coinvolti`).
- Non bloccare il workflow su criteri soggettivi (es. "il contenuto è abbastanza
  dettagliato"). Blocca solo su criteri binari osservabili (presenza/assenza sezione,
  valore frontmatter).
- L'assenza di un criterio non è un errore dell'utente: è un output incompleto
  dell'agente precedente. Richiedere il completamento prima di procedere.
